"""Office-serialized business writes and typed, secret-free acknowledgements."""
import hmac
import json
import os
from datetime import datetime
from uuid import UUID, uuid4
from psycopg import sql
from psycopg.types.json import Jsonb
from .database import connection
from .models.mvp import metadata, TARGETS, ACCESS_TARGETS


class DomainError(Exception):
    def __init__(self, status, code):
        self.status, self.code = status, code
        super().__init__(code)


class RecordedRefusal(DomainError):
    def __init__(self,status,code,resources):
        super().__init__(status,code)
        self.resources=resources


def wire(value):
    if isinstance(value,UUID): return str(value)
    if hasattr(value,'isoformat'): return value.isoformat()
    raise TypeError(type(value).__name__)


class Transaction:
    def __init__(self, db, context, request_id):
        self.db, self.context, self.request_id = db, context, request_id
        self.secret_response = {}
        self.now = db.execute('SELECT clock_timestamp()+clock_offset AS now FROM evaluation_runs WHERE id=%s',(context.run_id,)).fetchone()['now']
        self.wall_now = db.execute('SELECT clock_timestamp() now').fetchone()['now']

    def insert(self, name, values):
        table=metadata.tables[name]
        data=dict(values)
        if 'id' in table.c: data.setdefault('id',uuid4())
        for key,value in [('run_id',self.context.run_id),('office_id',self.context.office_id),('created_by',self.context.actor_id),('identity_assurance',self.context.identity_assurance)]:
            if key in table.c: data.setdefault(key,value)
        if set(data)-set(table.c.keys()): raise ValueError('Unknown typed column')
        args=[Jsonb(v) if table.c[k].type.__class__.__name__=='JSONB' else v for k,v in data.items()]
        q=sql.SQL('INSERT INTO {} ({}) VALUES ({}) RETURNING *').format(sql.Identifier(name),sql.SQL(',').join(map(sql.Identifier,data)),sql.SQL(',').join(sql.Placeholder() for _ in data))
        return self.db.execute(q,args).fetchone()

    def get(self,name,identity):
        row=self.db.execute(sql.SQL('SELECT * FROM {} WHERE id=%s AND run_id=%s AND office_id=%s').format(sql.Identifier(name)),(identity,self.context.run_id,self.context.office_id)).fetchone()
        if not row: raise DomainError(404,'record_unavailable')
        return row

    def revision(self, row, expected):
        if expected is None or row['revision']!=expected: raise DomainError(409,'stale_revision')

    def update(self,name,identity,values):
        if set(values)-set(metadata.tables[name].c.keys()): raise ValueError('Unknown typed column')
        return self.db.execute(sql.SQL('UPDATE {} SET {} WHERE id=%s AND run_id=%s AND office_id=%s RETURNING *').format(sql.Identifier(name),sql.SQL(',').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in values)),(*values.values(),identity,self.context.run_id,self.context.office_id)).fetchone()

    def audit(self,action,targets,reason=None,details=None):
        if not targets or any(k not in TARGETS for k,_ in targets): raise ValueError('Typed audit targets required')
        sequence=self.db.execute("SELECT nextval('audit_sequence') AS n").fetchone()['n']
        event=self.insert('audit_events',{'sequence':sequence,'actor_id':self.context.actor_id,'action':action,'request_id':self.request_id,'reason':reason,'effective_at':self.now,'safe_details':details or {}})
        for slot,identity in targets: self.insert('audit_targets',{'audit_event_id':event['id'],slot:identity})
        return event['id']


def execute_command(actor_id, command_name, key, request, handler, *, system=False):
    from .actor import resolve_identity
    if not key or len(key)>200: raise DomainError(422,'idempotency_key_required')
    if {'role','office_id','run_id','identity_assurance','created_by','actor_id','simulated'}.intersection(request):
        raise DomainError(422,'server_owned_context')
    with connection() as db:
        context=resolve_identity(db,actor_id,system=system)
        db.execute('SELECT id FROM field_offices WHERE id=%s FOR UPDATE',(context.office_id,))
        context=resolve_identity(db,actor_id,system=system)
        if context.role=='auditor': raise DomainError(403,'auditor_read_only')
        secret=os.environ.get('MVP_COMMAND_DIGEST_KEY')
        if not secret or len(secret)<64: raise DomainError(503,'replay_key_unavailable')
        digest=hmac.digest(bytes.fromhex(secret),json.dumps(request,sort_keys=True,separators=(',',':'),default=wire).encode(),'sha256')
        prior=db.execute('SELECT * FROM command_results WHERE actor_id=%s AND command_name=%s AND idempotency_key=%s',(context.actor_id,command_name,key)).fetchone()
        tx=Transaction(db,context,uuid4())
        if prior:
            if not hmac.compare_digest(prior['request_digest'],digest): raise DomainError(409,'idempotency_body_conflict')
            if prior['status_code']>=400: raise DomainError(prior['status_code'],'request_previously_refused')
            refs=db.execute('SELECT * FROM command_result_refs WHERE actor_id=%s AND command_name=%s AND idempotency_key=%s ORDER BY created_at,id',(context.actor_id,command_name,key)).fetchall()
            resources=[{'type':k,'id':str(r[k])} for r in refs for k in ACCESS_TARGETS if r[k] is not None]
            from .projections import authorize_reference
            for ref in resources: authorize_reference(db,context,ref['type'],UUID(ref['id']))
            return {'resources':resources,'replayed':True}
        refusal=None
        try: resources=handler(tx)
        except RecordedRefusal as e:
            refusal=e
            resources=e.resources
        tx.insert('command_results',{'actor_id':context.actor_id,'command_name':command_name,'idempotency_key':key,'request_digest':digest,'status_code':refusal.status if refusal else 200})
        for slot,identity in resources:
            if slot not in ACCESS_TARGETS: raise ValueError('Typed result required')
            tx.insert('command_result_refs',{'actor_id':context.actor_id,'command_name':command_name,'idempotency_key':key,slot:identity})
        db.execute('UPDATE field_offices SET revision=revision+1 WHERE id=%s',(context.office_id,))
        db.execute('SET CONSTRAINTS ALL IMMEDIATE')
        if refusal:
            db.commit() # refusal evidence/counters/key persist without forbidden action
            raise DomainError(refusal.status,refusal.code)
        return {'resources':[{'type':s,'id':str(i)} for s,i in resources], 'replayed':False,**tx.secret_response}
