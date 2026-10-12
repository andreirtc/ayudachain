from uuid import UUID
from typing import Literal
from fastapi import APIRouter,Depends,Header
from pydantic import Field
from .main import actor,result
from .schemas.mvp import StrictModel
from .commands import execute_command,DomainError
from .database import connection
from .actor import require_role
from .services import entitlements,registry
from .services.access import log_access

router=APIRouter(prefix='/api/v1')


class Decision(StrictModel):
    expected_revision:int=Field(ge=0)
    reviewed_check_id:UUID
    action:Literal['approve','decline','refer','category_change']
    category_id:UUID|None=None
    reason:str|None=Field(default=None,max_length=5000)
    question:str|None=Field(default=None,max_length=5000)
    response_hours:int|None=Field(default=None,gt=0,le=720)


class BulkItem(StrictModel):
    claim_id:UUID
    expected_revision:int=Field(ge=0)
    reviewed_check_id:UUID
    category_id:UUID


class Bulk(StrictModel):
    claims:list[BulkItem]=Field(min_length=1,max_length=100)
    reason:str|None=None


class Rule(StrictModel):
    category_id:UUID
    day_count:int|None=Field(default=None,gt=0,le=2147483647)
    fixed_centavos:str|None=None
    evidence_id:UUID


class Input(StrictModel):
    disaster_id:UUID
    expected_revision:int=Field(ge=0)
    mode:Literal['wage_formula','fixed_category']
    wage_centavos:str|None=None
    wage_evidence_id:UUID|None=None
    rules:list[Rule]=Field(min_length=1,max_length=100)
    reason:str|None=Field(default=None,max_length=5000)


class ListRequest(StrictModel):
    disaster_id:UUID
    barangay_id:UUID
    expected_revision:int|None=Field(default=None,ge=0)


@router.post('/claims/{identity}/decisions')
def decide(identity:UUID,body:Decision,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'claim.decide',idempotency_key,dict(req,claim_id=identity),lambda tx:entitlements.decide(tx,identity,req)))


@router.post('/claims/bulk-approve')
def bulk(body:Bulk,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'claim.bulk',idempotency_key,req,lambda tx:entitlements.bulk_approve(tx,req)))


@router.post('/amount-inputs')
def inputs(body:Input,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'inputs.save',idempotency_key,req,lambda tx:entitlements.save_inputs(tx,req)))


@router.post('/lists')
def lists(body:ListRequest,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'list.request',idempotency_key,req,lambda tx:entitlements.request_list(tx,req)))


@router.get('/amount-inputs')
def current_inputs(disaster_id:UUID,c=Depends(actor)):
    require_role(c,'dswd','auditor')
    with connection() as db:
        d=db.execute('SELECT id,revision,current_input_version_id FROM disasters WHERE id=%s AND run_id=%s',(disaster_id,c.run_id)).fetchone()
        if not d:raise DomainError(404,'record_unavailable')
        versions=db.execute('SELECT id,predecessor_id,mode,wage_centavos,reason,created_at FROM amount_input_versions WHERE disaster_id=%s ORDER BY created_at,id',(disaster_id,)).fetchall()
        for v in versions:
            if v['wage_centavos'] is not None:v['wage_centavos']=str(v['wage_centavos'])
            v['rules']=db.execute('SELECT category_id,day_count,fixed_centavos FROM amount_rules WHERE input_version_id=%s ORDER BY category_id',(v['id'],)).fetchall()
            for rule in v['rules']:
                if rule['fixed_centavos'] is not None:rule['fixed_centavos']=str(rule['fixed_centavos'])
    log_access(c,'browse','disaster_id',disaster_id,['documented_amount_inputs'])
    return result({'disaster':d,'versions':versions,'anchor_required':True})


@router.get('/entitlements')
def entitlement_list(disaster_id:UUID,c=Depends(actor)):
    require_role(c,'dswd','auditor','beneficiary')
    with connection() as db:
        rows=db.execute('''SELECT e.id,e.household_id,e.business_status,e.hold_reasons,e.revision,e.current_version_id,v.category_id,v.amount_centavos,v.input_version_id,v.calculation,t.id transaction_id FROM entitlements e JOIN entitlement_versions v ON v.id=e.current_version_id JOIN payout_transactions t ON t.entitlement_id=e.id WHERE e.run_id=%s AND e.disaster_id=%s AND (%s OR e.household_id=%s) ORDER BY e.created_at,e.id''',(c.run_id,disaster_id,c.role in {'dswd','auditor'},c.household_id)).fetchall()
        for row in rows:
            if row['amount_centavos'] is not None:row['amount_centavos']=str(row['amount_centavos'])
    log_access(c,'browse','disaster_id',disaster_id,['entitlements','computed_amounts'])
    return result(rows)


@router.get('/lists')
def list_views(disaster_id:UUID,barangay_id:UUID|None=None,c=Depends(actor)):
    with connection() as db:
        if c.role=='barangay':barangay_id=c.barangay_id
        elif c.role=='beneficiary':
            if not c.household_id:raise DomainError(404,'record_unavailable')
            h=registry.household(db,c,c.household_id)
            if h['residence_state']!='confirmed':raise DomainError(403,'confirmed_residence_required')
            if barangay_id not in {None,h['declared_barangay_id']}:raise DomainError(404,'record_unavailable')
            barangay_id=h['declared_barangay_id']
        elif c.role not in {'dswd','auditor'}:raise DomainError(404,'record_unavailable')
        versions=db.execute('''SELECT v.id,v.list_head_id,v.business_status,v.requested_at,v.published_at,h.barangay_id,h.eligibility_revision,h.newest_requested_id,h.current_published_id FROM approved_list_versions v JOIN list_heads h ON h.id=v.list_head_id WHERE h.disaster_id=%s AND h.run_id=%s AND (%s::uuid IS NULL OR h.barangay_id=%s) ORDER BY v.created_at,v.id''',(disaster_id,c.run_id,barangay_id,barangay_id)).fetchall()
        full=c.role in {'dswd','auditor'}
        if not full:versions=[v for v in versions if v['id']==v['current_published_id']]
        for v in versions:
            if full:
                rows=db.execute('SELECT e.id,e.entitlement_id,e.entitlement_version_id,e.frozen_name name,e.frozen_zone zone,c.label category,a.amount_centavos FROM approved_list_entries e JOIN damage_categories c ON c.id=e.display_category_id JOIN entitlement_versions a ON a.id=e.entitlement_version_id WHERE e.list_version_id=%s ORDER BY e.frozen_name,e.id',(v['id'],)).fetchall()
                for row in rows:row['amount_centavos']=str(row['amount_centavos'])
                v['entries']=rows
                v['proofs']=db.execute('SELECT c.id,j.state FROM commitments c JOIN anchor_job_items i ON i.commitment_id=c.id JOIN anchor_jobs j ON j.id=i.job_id WHERE c.list_version_id=%s',(v['id'],)).fetchall()
            else:v['entries']=db.execute('SELECT e.id entry_handle,e.frozen_name name,e.frozen_zone zone,c.label category FROM approved_list_entries e JOIN damage_categories c ON c.id=e.display_category_id WHERE e.list_version_id=%s ORDER BY e.frozen_name,e.id',(v['id'],)).fetchall()
    log_access(c,'browse','disaster_id',disaster_id,['approved_list_versions'])
    return result(versions)
