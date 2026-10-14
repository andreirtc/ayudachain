from datetime import date
from uuid import UUID
from typing import Literal
from fastapi import APIRouter,Depends,Header
from pydantic import Field
from .main import actor,result
from .schemas.mvp import StrictModel
from .database import connection
from .commands import execute_command,DomainError
from .actor import require_role
from .services import funds
from .services.access import log_access

router=APIRouter(prefix='/api/v1')


class Signatory(StrictModel):
    printed_name:str=Field(min_length=1,max_length=200)
    printed_role:str=Field(min_length=1,max_length=200)


class AreaLine(StrictModel):
    area_code:str
    area_name:str
    amount_centavos:str=Field(pattern=r'^(0|[1-9][0-9]*)$')


class Release(StrictModel):
    disaster_id:UUID
    source_evidence_id:UUID
    supporting_evidence_ids:list[UUID]=[]
    document_type:str=Field(min_length=1,max_length=200)
    reference_number:str=Field(min_length=1,max_length=200)
    issued_date:date
    amount_centavos:str=Field(pattern=r'^[1-9][0-9]*$')
    purpose:str=Field(min_length=1,max_length=2000)
    covered_area:str=Field(min_length=1,max_length=2000)
    signatories:list[Signatory]=Field(min_length=1,max_length=20)
    area_lines:list[AreaLine]=Field(default=[],max_length=100)
    document_words:str|None=None
    document_figures_centavos:str|None=None


class Correction(Release):
    expected_revision:int=Field(ge=0)
    reason:str=Field(min_length=1,max_length=2000)
    correction_kind:Literal['transcription','source_amendment']


@router.post('/funds/releases')
def release(body:Release,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    require_role(c,'dswd');request=body.model_dump()
    return result(execute_command(c.actor_id,'fund.release',idempotency_key,request,lambda tx:funds.release(tx,request)))


@router.post('/funds/{identity}/corrections')
def correction(identity:UUID,body:Correction,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    require_role(c,'dswd');request=body.model_dump()
    return result(execute_command(c.actor_id,'fund.correct',idempotency_key,dict(request,original_id=identity),lambda tx:funds.correct(tx,identity,request)))


@router.get('/funds')
def ledger(disaster_id:UUID,c=Depends(actor)):
    require_role(c,'dswd','auditor')
    with connection() as db:
        if not db.execute('SELECT 1 FROM disasters WHERE id=%s AND run_id=%s',(disaster_id,c.run_id)).fetchone():raise DomainError(404,'record_unavailable')
        rows=db.execute('SELECT f.*,h.revision head_revision,h.current_entry_id FROM fund_entries f LEFT JOIN fund_heads h ON h.source_root_id=f.source_root_id WHERE f.run_id=%s AND f.disaster_id=%s ORDER BY f.created_at,f.id LIMIT 200',(c.run_id,disaster_id)).fetchall()
        entries=[]
        for row in rows:
            item={k:row[k] for k in ['id','disaster_id','kind','document_type','reference_number','issued_date','purpose','covered_area','amount_review','original_entry_id','correction_set_id','source_root_id','entered_by','approved_by','head_revision','current_entry_id','created_at']}
            item['delta_centavos']=str(row['delta_centavos'])
            item['signatories']=db.execute('SELECT printed_name,printed_role,signature_state FROM fund_signatories WHERE entry_id=%s ORDER BY ordinal',(row['id'],)).fetchall()
            item['evidence']=db.execute('SELECT e.id,e.purpose,l.attachment_role,e.extraction_state,e.signature_state FROM evidence_versions e JOIN evidence_links l ON l.evidence_version_id=e.id WHERE l.fund_entry_id=%s ORDER BY e.uploaded_at,e.id',(row['id'],)).fetchall()
            item['proofs']=db.execute('SELECT c.id,c.kind,j.id job_id,j.state FROM commitments c JOIN anchor_job_items i ON i.commitment_id=c.id JOIN anchor_jobs j ON j.id=i.job_id WHERE c.fund_entry_id=%s OR c.evidence_version_id IN (SELECT evidence_version_id FROM evidence_links WHERE fund_entry_id=%s) ORDER BY c.created_at,c.id',(row['id'],row['id'])).fetchall()
            item['exceptions']=[]
            if any(p['state']!='confirmed' for p in item['proofs']):item['exceptions'].append('not_anchored')
            if row['kind']!='release' or row['current_entry_id']!=row['id']:item['exceptions'].append('corrected')
            if row['amount_review']['amount_overridden']:item['exceptions'].append('amount_overridden')
            if row['amount_review']['words_figures_state']=='disagree':item['exceptions'].append('words_figures_disagree')
            from .services.evidence import original_bytes
            for evidence in db.execute('SELECT e.* FROM evidence_versions e JOIN evidence_links l ON l.evidence_version_id=e.id WHERE l.fund_entry_id=%s',(row['id'],)).fetchall():
                try:original_bytes(evidence)
                except DomainError as error:
                    item['exceptions'].append('document_mismatch' if error.code=='evidence_mismatch' else 'evidence_unavailable')
            for proof in item['proofs']:
                observed=db.execute('SELECT observed_tx_hash,receipt_json FROM anchor_observations WHERE job_id=%s AND verdict=%s ORDER BY checked_at DESC LIMIT 1',(proof['job_id'],'mined_match')).fetchone()
                proof['observed_tx_hash']='0x'+observed['observed_tx_hash'].hex() if observed and observed['observed_tx_hash'] else None
            entries.append(item)
        totals=funds.totals(db,c.run_id,disaster_id)
        refusals=db.execute("SELECT a.id,a.effective_at,a.actor_id,a.action FROM audit_events a JOIN audit_targets t ON t.audit_event_id=a.id JOIN fund_entries f ON f.id=t.fund_entry_id WHERE a.action='fund.duplicate_refused' AND f.disaster_id=%s ORDER BY a.sequence DESC LIMIT 100",(disaster_id,)).fetchall()
    log_access(c,'browse','disaster_id',disaster_id,['fund_ledger','fund_proof_status','fund_totals'])
    return result({'entries':entries,'totals':totals,'duplicate_document_refusals':refusals,'limit':200})
