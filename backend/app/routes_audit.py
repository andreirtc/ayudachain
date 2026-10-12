from uuid import UUID
from fastapi import APIRouter,Depends
from .main import actor,result
from .actor import require_role
from .database import connection
from .commands import DomainError
from .services import audit_views,legacy
from .services.access import log_access

router=APIRouter(prefix='/api/v1')

@router.get('/audit/proofs')
def proofs(c=Depends(actor)):
    require_role(c,'dswd','auditor')
    with connection() as db:
        rows=db.execute('SELECT c.id,c.kind,c.created_at,j.state,j.id job_id FROM commitments c JOIN anchor_job_items i ON i.commitment_id=c.id JOIN anchor_jobs j ON j.id=i.job_id WHERE c.run_id=%s ORDER BY c.created_at,c.id',(c.run_id,)).fetchall()
    log_access(c,'browse','evaluation_run_id',c.run_id,['exact_commitment_version_catalogue'])
    return result(rows)

@router.get('/audit/originals')
def originals(c=Depends(actor)):
    require_role(c,'dswd','auditor')
    with connection() as db:rows=db.execute('SELECT id,purpose,mime_type,created_at,predecessor_id FROM evidence_versions WHERE run_id=%s ORDER BY created_at,id',(c.run_id,)).fetchall()
    log_access(c,'browse','evaluation_run_id',c.run_id,['original_file_version_catalogue'])
    return result(rows)

@router.get('/audit/overview')
def overview(disaster_id:UUID,c=Depends(actor)):return result(audit_views.overview(c,disaster_id))

@router.get('/audit/timeline/{slot}/{identity}')
def timeline(slot:str,identity:UUID,c=Depends(actor)):return result(audit_views.timeline(c,slot,identity))

@router.get('/audit/own-inspections')
def inspections(c=Depends(actor)):return result(audit_views.inspection_history(c))

@router.get('/legacy/records')
def records(c=Depends(actor)):
    require_role(c,'dswd','auditor')
    with connection() as db:rows=db.execute('SELECT id,source_table,source_key,imported_at,deployment_id FROM legacy_records WHERE run_id=%s ORDER BY imported_at,id LIMIT 500',(c.run_id,)).fetchall()
    log_access(c,'browse','evaluation_run_id',c.run_id,['frozen_legacy_record_catalogue'])
    return result({'records':rows,'limit':500,'pivot_eligibility':False,'stored_transaction_strings':'untrusted historical strings'})

@router.get('/legacy/records/{identity}')
def record(identity:UUID,c=Depends(actor)):
    require_role(c,'dswd','auditor')
    with connection() as db:
        row=db.execute('SELECT * FROM legacy_records WHERE id=%s AND run_id=%s',(identity,c.run_id)).fetchone()
        if not row:raise DomainError(404,'record_unavailable')
    log_access(c,'open','evaluation_run_id',c.run_id,['exact_frozen_legacy_fields'])
    return result({'id':row['id'],'source_db_sha256':row['source_db_sha256'].hex(),'source_table':row['source_table'],'original_fields':row['original_fields'],'coverage':'legacy normalized receipt text only; not MVP records','pivot_eligibility':False})

@router.get('/legacy/records/{identity}/integrity')
def check(identity:UUID,c=Depends(actor)):
    require_role(c,'dswd','auditor')
    with connection() as db:
        row=db.execute('SELECT * FROM legacy_records WHERE id=%s AND run_id=%s',(identity,c.run_id)).fetchone()
        if not row:raise DomainError(404,'record_unavailable')
        dep=db.execute('SELECT * FROM deployments WHERE id=%s',(row['deployment_id'],)).fetchone() if row['deployment_id'] else None
        checked=legacy.check(row,dep)
    log_access(c,'integrity','evaluation_run_id',c.run_id,['legacy_receipt_current_integrity'],checked['result'])
    return result(checked)
