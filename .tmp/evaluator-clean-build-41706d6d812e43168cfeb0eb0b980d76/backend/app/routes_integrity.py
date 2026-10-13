from uuid import UUID
from fastapi import APIRouter,Depends,Header
from fastapi.responses import Response
from .main import actor,result
from .database import connection
from .commands import execute_command,DomainError
from .actor import require_role
from .services.integrity import check_saved
from .services.access import log_access
from .schemas.mvp import StrictModel

router=APIRouter(prefix='/api/v1')


class IntegrityRequest(StrictModel): commitment_id: UUID


def allowed_commitment(db,c,identity):
    row=db.execute('SELECT * FROM commitments WHERE id=%s AND run_id=%s AND office_id=%s',(identity,c.run_id,c.office_id)).fetchone()
    if not row: raise DomainError(404,'record_unavailable')
    if c.role in {'dswd','auditor'}: return row
    if row['handover_id']:
        from .services.payouts import can_read
        receipt=db.execute('SELECT transaction_id FROM recorded_handovers WHERE id=%s',(row['handover_id'],)).fetchone()
        if c.role=='disbursing':
            payer=db.execute('SELECT payer_id FROM recorded_handovers WHERE id=%s',(row['handover_id'],)).fetchone()['payer_id']
            if payer!=c.actor_id:raise DomainError(404,'record_unavailable')
        can_read(db,c,receipt['transaction_id']);return row
    if row['outcome_version_id'] and c.role=='beneficiary':
        from .services.outcomes import private_view
        outcome=db.execute('SELECT transaction_id FROM outcome_versions WHERE id=%s',(row['outcome_version_id'],)).fetchone()
        private_view(db,c,outcome['transaction_id']);return row
    raise DomainError(404,'record_unavailable')


@router.post('/integrity/check')
def integrity(body:IntegrityRequest,c=Depends(actor)):
    with connection() as db:
        item=allowed_commitment(db,c,body.commitment_id)
        checked=check_saved(db,item)
    log_access(c,'integrity','commitment_id',body.commitment_id,['canonical_bytes','original_bytes','pinned_chain_record'],checked['result'])
    return result(checked)


@router.get('/commitments/{identity}/material')
def material(identity:UUID,c=Depends(actor)):
    with connection() as db:
        item=allowed_commitment(db,c,identity)
        from .services.integrity import manifest_for
        deployment=db.execute('SELECT * FROM deployments WHERE id=%s',(item['deployment_id'],)).fetchone()
        manifest=manifest_for(deployment)
    log_access(c,'material','commitment_id',identity,['exact_canonical_bytes','deployment_manifest'])
    # Contains all private preimage fields; only wholly authorized readers receive it.
    return result({'canonical_utf8':bytes(item['canonical_bytes']).decode('utf-8'),'deployment':manifest,'public_id':'0x'+item['public_id'].hex(),'content_hash':'0x'+item['content_hash'].hex(),'coverage':'exact canonical envelope and listed originals; selective resident inclusion Pending'})


@router.get('/commitments/{identity}/summary')
def summary(identity:UUID,c=Depends(actor)):
    from .models.mvp import ACCESS_TARGETS
    from .services.evidence_protocol import parse_canonical
    with connection() as db:
        item=allowed_commitment(db,c,identity)
        job=db.execute('SELECT j.state FROM anchor_job_items i JOIN anchor_jobs j ON j.id=i.job_id WHERE i.commitment_id=%s',(identity,)).fetchone()
        try:envelope=parse_canonical(bytes(item['canonical_bytes']))
        except (ValueError,TypeError,KeyError):raise DomainError(503,'evidence_unavailable') from None
        # Opaque exact-version references only; no raw payload, identity or contacts.
        refs=[{'type':key,'id':value} for key,value in item.items() if key in ACCESS_TARGETS and value is not None and key not in {'deployment_id'}]
        files=[{'id':f['id'],'mime_type':f['mime_type'],'byte_length':f['byte_length']} for f in envelope['evidence']]
    log_access(c,'open','commitment_id',identity,['commitment_coverage','exact_version_references'])
    return result({'id':identity,'kind':item['kind'],'created_at':item['created_at'],'submission_state':job['state'] if job else 'unavailable',
        'versions':refs,'originals':files,'coverage':'Exact saved canonical envelope, listed original bytes and pinned chain fields. A match does not prove authentic originals, eligibility or physical cash receipt.'})


class RetryRequest(StrictModel): expected_revision: int | None=None


@router.post('/anchor-jobs/{identity}/retry')
def retry(identity:UUID,body:RetryRequest,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    require_role(c,'dswd')
    def action(tx):
        item=tx.get('anchor_jobs',identity)
        if item['state'] in {'confirmed','conflict','deployment_lost'}: raise DomainError(409,'anchor_not_retryable')
        tx.update('anchor_jobs',identity,{'next_attempt_at':tx.wall_now})
        tx.audit('anchor.retry',[('anchor_job_id',identity)])
        return [('anchor_job_id',identity)]
    return result(execute_command(c.actor_id,'anchor.retry',idempotency_key,{'job_id':identity,**body.model_dump()},action))
