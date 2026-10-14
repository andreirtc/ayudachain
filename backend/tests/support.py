"""Isolated PostgreSQL harness. Only random test schemas are retired here."""
import os
import secrets
from contextlib import contextmanager
from datetime import datetime,timezone,timedelta
from uuid import uuid4
from pathlib import Path
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from backend.app.config import ROOT,load_local_environment
from backend.app.database import connection
from backend.app.actor import ActorContext
from backend.app.commands import Transaction
from backend.migrations.catalogue import migrate
from backend.scripts.setup_mvp import grant_roles


def fault_manifest_path():
    """Explicit fresh fault deployment; retain older immutable manifests."""
    load_local_environment()
    return Path(os.environ.get("MVP_TEST_DEPLOYMENT_MANIFEST",str(ROOT/".runtime/test-deployment.json"))).resolve()


class Harness:
    def __enter__(self):
        load_local_environment()
        self.saved={k:os.environ.get(k) for k in ['MVP_DATABASE_URL','MVP_OWNER_DATABASE_URL','MVP_INSPECTION_DATABASE_URL','MVP_WORKER_DATABASE_URL','MVP_SCHEMA','MVP_DB_ROLE','MVP_RPC_URL','MVP_DEPLOYMENT_MANIFEST']}
        dsn=os.environ.get('MVP_TEST_DATABASE_URL')
        if not dsn or '/ayudachain_mvp_test' not in dsn: raise RuntimeError('Explicit isolated PostgreSQL test database required')
        self.schema='test_mvp_'+uuid4().hex
        os.environ.update(MVP_DATABASE_URL=dsn,MVP_OWNER_DATABASE_URL=dsn,MVP_INSPECTION_DATABASE_URL=dsn,MVP_WORKER_DATABASE_URL=dsn,MVP_SCHEMA=self.schema,MVP_DB_ROLE='mvp_runtime')
        from backend.app.config import ROOT
        os.environ.update(MVP_RPC_URL='http://127.0.0.1:8555',MVP_DEPLOYMENT_MANIFEST=str(fault_manifest_path()))
        with psycopg.connect(dsn,row_factory=dict_row) as db:
            db.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.schema)))
            db.execute(sql.SQL('SET search_path TO {},public').format(sql.Identifier(self.schema)))
            migrate(db)
            grant_roles(db,self.schema)
            self.seed(db)
        return self

    def __exit__(self,*args):
        dsn=os.environ['MVP_TEST_DATABASE_URL']
        assert self.schema.startswith('test_mvp_') and len(self.schema)==41
        with psycopg.connect(dsn) as db:
            db.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(self.schema)))
        for k,v in self.saved.items():
            if v is None: os.environ.pop(k,None)
            else: os.environ[k]=v

    def connection(self): return connection()

    def seed(self,db):
        self.office,self.run=uuid4(),uuid4()
        db.execute('INSERT INTO field_offices(id,name,revision,check_data_revision) VALUES(%s,%s,0,0)',(self.office,'Invented Field Office'))
        db.execute("INSERT INTO evaluation_runs(id,office_id,namespace,state,clock_mode,clock_offset,created_at) VALUES(%s,%s,%s,'active','wall_clock',interval '0',clock_timestamp())",(self.run,self.office,secrets.token_bytes(32)))
        self.actors={r:uuid4() for r in ['system','dswd','dswd2','barangay','barangay2','beneficiary','beneficiary2','disbursing','disbursing2','auditor','auditor2','pending']}
        c=ActorContext(self.actors['system'],self.run,self.office,'system','Evaluation scheduler',None,None,None,None,'system')
        tx=Transaction(db,c,uuid4())
        self.barangays=[tx.insert('barangays',{'name':n,'zone_description':None})['id'] for n in ['Invented Silong','Invented Sapa','Invented Staffless']]
        self.disasters=[tx.insert('disasters',{'name':n,'external_reference':None,'current_input_version_id':None,'inputs_locked_at':None,'revision':0})['id'] for n in ['Synthetic Typhoon Luntian','Synthetic Flood Talim']]
        self.categories=[tx.insert('damage_categories',{'code':code,'label':label})['id'] for code,label in [('totally_damaged','Totally damaged'),('partially_damaged','Partially damaged')]]
        for label,identity in self.actors.items():
            role=label.rstrip('2') if label!='pending' else 'disbursing'
            version=uuid4()
            tx.insert('actors',{'id':identity,'role':role,'display_name':'Invented '+label,'email':None,'current_version_id':version,'current_member_link_id':None,'revision':0})
            tx.insert('actor_versions',{'id':version,'actor_id':identity,'predecessor_id':None,'status':'pending' if label=='pending' else 'active',
                'barangay_id':self.barangays[0] if role=='barangay' else None,'position':'Punong Barangay' if label=='barangay' else None,
                'nomination_id':None,'approved_by':None,'reason':'Synthetic reference actor'})
            tx.audit('reference.actor',[('actor_version_id',version)])

    def deactivate(self,tx,actor):
        row=tx.get('actors',actor)
        tx.revision(row,0)
        prior=tx.get('actor_versions',row['current_version_id'])
        fields={k:prior[k] for k in ['barangay_id','position','nomination_id','approved_by']}
        version=tx.insert('actor_versions',dict(fields,actor_id=actor,predecessor_id=prior['id'],status='deactivated',reason='test human decision'))
        tx.update('actors',actor,{'current_version_id':version['id'],'revision':1})
        tx.audit('actor.deactivate',[('actor_version_id',version['id'])])
        return [('actor_version_id',version['id'])]

    def register_chain(self):
        from backend.scripts.register_deployment import register
        from backend.app.actor import resolve_identity
        with self.connection() as db:
            tx=Transaction(db,resolve_identity(db,self.actors['system'],system=True),uuid4())
            return register(tx,os.environ.get('MVP_DEPLOYMENT_MANIFEST',str(__import__('backend.app.config',fromlist=['ROOT']).ROOT/'.runtime/deployment.json')))

    def upload(self,purpose,raw=None,actor='dswd',prepared_for=None):
        from backend.app.commands import execute_command
        from backend.app.services.evidence import prepare_upload,save_upload
        raw=raw or synthetic_pdf('Invented evidence '+uuid4().hex)
        item=prepare_upload(raw,'image/png' if raw.startswith(b'\x89PNG') else 'application/pdf')
        ack=execute_command(self.actors[actor],'evidence.upload',str(uuid4()),{'hash':item['byte_sha256'].hex()},lambda tx:save_upload(tx,item,purpose,prepared_for))
        return __import__('uuid').UUID(ack['resources'][0]['id'])

    def drain_anchors(self):
        import subprocess
        from backend.app.config import ROOT
        from backend.app.services.anchors import apply_due_observations
        env=os.environ.copy()
        env['MVP_PRIVATE_KEY']='0x'+'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
        for _ in range(80):
            with self.connection() as db:
                outstanding=db.execute("SELECT count(*) n FROM anchor_jobs WHERE state!='confirmed'").fetchone()['n']
            if not outstanding:return
            result=subprocess.run([env['MVP_NODE'],str(ROOT/'contracts/scripts/anchor_worker.js'),'--once'],env=env,capture_output=True,text=True,timeout=30)
            if result.returncode:raise AssertionError('Actual worker failed; no signing material printed')
            apply_due_observations()
        raise AssertionError('Actual anchors did not finish')


def synthetic_pdf(text):
    # A real one-page text PDF with valid object offsets, parsed by pypdf.
    stream=('BT /F1 10 Tf 40 740 Td ('+text.replace('\\','\\\\').replace('(','\\(').replace(')','\\)').replace('\n',') Tj 0 -16 Td (')+') Tj ET').encode('ascii')
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream']
    out=b'%PDF-1.4\n';offsets=[]
    for i,obj in enumerate(objects,1):
        offsets.append(len(out));out+=str(i).encode()+b' 0 obj\n'+obj+b'\nendobj\n'
    xref=len(out);out+=b'xref\n0 6\n0000000000 65535 f \n'
    for offset in offsets: out+=f'{offset:010d} 00000 n \n'.encode()
    return out+b'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n'+str(xref).encode()+b'\n%%EOF\n'
