from datetime import datetime,timezone
from uuid import uuid4
from ..database import connection
from ..commands import Transaction,DomainError
from ..models.mvp import ACCESS_TARGETS


def log_access(context,action,slot,identity,fields,verdict=None):
    if context.role!='auditor': return
    try:
        with connection(purpose='inspection') as db:
            event={'id':uuid4(),'run_id':context.run_id,'office_id':context.office_id,'created_by':context.actor_id,
                'auditor_actor_id':context.actor_id,'action':action,'fields_opened':fields,'success':True,'checked_at':datetime.now(timezone.utc),'integrity_result':verdict,'safe_error':None}
            from psycopg import sql
            keys=list(event)
            db.execute(sql.SQL('INSERT INTO auditor_access_events ({}) VALUES ({})').format(sql.SQL(',').join(map(sql.Identifier,keys)),sql.SQL(',').join(sql.Placeholder() for _ in keys)),list(event.values()))
            if slot not in ACCESS_TARGETS: raise ValueError('Typed access target required')
            db.execute(sql.SQL('INSERT INTO auditor_access_targets(id,run_id,office_id,created_by,access_event_id,{}) VALUES(%s,%s,%s,%s,%s,%s)').format(sql.Identifier(slot)),(uuid4(),context.run_id,context.office_id,context.actor_id,event['id'],identity))
    except Exception: raise DomainError(503,'inspection_logging_unavailable') from None


def authorize_evidence(db,context,identity):
    row=db.execute('SELECT * FROM evidence_versions WHERE id=%s AND run_id=%s AND office_id=%s',(identity,context.run_id,context.office_id)).fetchone()
    if not row: raise DomainError(404,'record_unavailable')
    if context.role in {'dswd','auditor'}: return row
    links=db.execute('SELECT * FROM evidence_links WHERE evidence_version_id=%s',(identity,)).fetchall()
    if not links:
        if row['purpose'] in {'identity_photo','identity_document'}:
            if row['prepared_for_actor_id']==context.actor_id: return row
        elif row['uploaded_by']==context.actor_id: return row
        raise DomainError(404,'record_unavailable')
    from ..projections import authorize_reference
    for link in links:
        if context.role=='barangay' and link['attachment_role']!='damage': continue
        if context.role=='disbursing' and link['attachment_role']!='identity_photo': continue
        for slot in ACCESS_TARGETS:
            if slot in link and link[slot]:
                try:
                    authorize_reference(db,context,slot,link[slot]);return row
                except DomainError: pass
    raise DomainError(404,'record_unavailable')
