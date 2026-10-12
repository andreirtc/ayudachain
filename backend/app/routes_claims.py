from uuid import UUID
from typing import Literal
from fastapi import APIRouter,Depends,Header
from pydantic import Field
from .main import actor,result
from .schemas.mvp import StrictModel
from .database import connection
from .commands import execute_command,DomainError
from .services import claims,registry,checks
from .actor import require_role,require_independent
from .services.access import log_access

router=APIRouter(prefix='/api/v1')


def project_flag(db, flag):
    """Historical checks cannot be reconstructed from today's registry facts."""
    scores=flag.get('scores') or {}
    public={k:scores[k] for k in ('name_similarity','address_similarity','birth_date_match','id_number_match','phone_match') if k in scores}
    comparison=scores.get('comparison')
    flag=dict(flag,scores=public,comparison_available=bool(comparison))
    if comparison:
        projected={}
        for side in ('source','candidate'):
            snapshot=comparison[side]
            facts={k:snapshot.get(k) for k in ('household_id','display_id','registry_version_id','household_revision','address','barangay_id')}
            facts['members']=[{k:m.get(k) for k in ('member_id','name','birth_date','is_head')} for m in snapshot.get('members',[])]
            current=db.execute('SELECT current_version_id,revision FROM households WHERE id=%s',(snapshot['household_id'],)).fetchone()
            facts['current_registry_version_id']=current['current_version_id'] if current else None
            facts['current_household_revision']=current['revision'] if current else None
            facts['version_changed']=not current or str(current['current_version_id'])!=snapshot['registry_version_id']
            projected[side]=facts
        flag['comparison']=projected
    elif flag.get('matched_household_id'):
        flag['comparison_unavailable_reason']='This historical check did not retain the compared registry and member evidence. Current records cannot establish what it compared.'
    return flag


class Submission(StrictModel):
    household_id:UUID
    disaster_id:UUID
    stated_category_id:UUID
    damage_description:str=Field(min_length=1,max_length=5000)
    evidence_ids:list[UUID]=Field(default=[],max_length=20)
    new_information:str|None=Field(default=None,max_length=5000)


class Response(StrictModel):
    kind:Literal['endorse','not_endorse','withdraw','reverse','referral_answer']
    parent_response_id:UUID|None=None
    residence_attested:bool|None=None
    affected_attested:bool|None=None
    category_opinion_id:UUID|None=None
    category_disputed:bool=False
    related_declared:bool=False
    reason:str|None=Field(default=None,max_length=5000)
    evidence_ids:list[UUID]=Field(default=[],max_length=20)


class Batch(StrictModel):
    disaster_id:UUID
    barangay_id:UUID
    round_ids:list[UUID]=Field(min_length=1,max_length=100)
    resolution_evidence_id:UUID


class Recheck(StrictModel):
    expected_revision:int=Field(ge=0)


@router.post('/claims/{identity}/recheck')
def recheck(identity:UUID,body:Recheck,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    def apply(tx):
        require_role(tx.context,'dswd')
        row=tx.get('claims',identity);require_independent(tx.context,row['household_id']);tx.revision(row,body.expected_revision)
        submission=tx.get('claim_submissions',row['current_submission_id'])
        check=checks.run(tx,submission,claims.latest_round(tx,row)['id'],'recheck')
        return [('check_run_id',check['id'])]
    return result(execute_command(c.actor_id,'claim.recheck',idempotency_key,dict(body.model_dump(),claim_id=identity),apply))


@router.post('/claims')
def submit(body:Submission,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'claim.submit',idempotency_key,req,lambda tx:claims.submit(tx,req)))


@router.post('/claim-rounds/{identity}/responses')
def respond(identity:UUID,body:Response,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'claim.respond',idempotency_key,dict(req,round_id=identity),lambda tx:claims.respond(tx,identity,req)))


@router.post('/claims/submissions')
def send(body:Batch,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'claim.send',idempotency_key,req,lambda tx:claims.send(tx,req)))


def project_claim(db,c,identity):
    row=db.execute('SELECT * FROM claims WHERE id=%s AND run_id=%s',(identity,c.run_id)).fetchone()
    if not row:raise DomainError(404,'record_unavailable')
    s=db.execute('SELECT * FROM claim_submissions WHERE id=%s',(row['current_submission_id'],)).fetchone()
    v=db.execute('SELECT * FROM household_versions WHERE id=%s',(s['registry_version_id'],)).fetchone()
    if c.role not in {'dswd','auditor'} and not (c.role=='beneficiary' and c.household_id==row['household_id']) and not (c.role=='barangay' and c.barangay_id==v['declared_barangay_id']):raise DomainError(404,'record_unavailable')
    view={k:row[k] for k in ['id','household_id','disaster_id','business_status','revision','resubmissions','current_submission_id','current_decision_id']}
    view['submission']={k:s[k] for k in ['id','registry_version_id','stated_category_id','damage_description','new_information','submitted_at']}
    view['household']={'name':db.execute('SELECT name FROM member_versions WHERE household_version_id=%s AND is_head',(v['id'],)).fetchone()['name'],'address':v['address'],'zone':v['zone'],'barangay_id':v['declared_barangay_id']}
    rounds=db.execute('SELECT id,deadline_at,state,route_kind,primary_snapshot_id,referral_decision_id FROM claim_rounds WHERE submission_id=%s ORDER BY created_at,id',(s['id'],)).fetchall()
    for r in rounds:
        r['responses']=db.execute('SELECT r.id,r.parent_response_id,r.kind,r.residence_attested,r.affected_attested,r.category_opinion_id,r.category_disputed,r.related_declared,r.reason,r.created_at,a.display_name officer_name FROM claim_responses r JOIN actors a ON a.id=r.actor_id WHERE r.round_id=%s ORDER BY r.created_at,r.id',(r['id'],)).fetchall()
    view['rounds']=rounds
    view['decisions']=db.execute('SELECT id,action,category_id,reason,question,created_at FROM claim_decisions WHERE claim_id=%s ORDER BY created_at,id',(row['id'],)).fetchall()
    if c.role in {'dswd','auditor'}:
        check=db.execute('SELECT id,risk_score,algorithm_version,created_at,compared_data_revision,simulation_adapter,simulation_result,simulated FROM check_runs WHERE submission_id=%s ORDER BY created_at DESC,id DESC LIMIT 1',(s['id'],)).fetchone()
        if check:
            check['current_data_revision']=db.execute('SELECT check_data_revision FROM field_offices WHERE id=%s',(c.office_id,)).fetchone()['check_data_revision']
            check['stale']=check['current_data_revision']!=check['compared_data_revision']
            check['flags']=[project_flag(db,f) for f in db.execute('SELECT code,weight,matched_household_id,matched_member_id,matched_link_version_id,scores FROM check_flags WHERE check_run_id=%s ORDER BY code,id',(check['id'],)).fetchall()]
        view['latest_check']=check
    view['anchor_required']=False
    return view


@router.get('/claims')
def queue(disaster_id:UUID,c=Depends(actor)):
    with connection() as db:
        ids=db.execute('SELECT id FROM claims WHERE disaster_id=%s AND run_id=%s ORDER BY created_at,id LIMIT 200',(disaster_id,c.run_id)).fetchall();rows=[]
        for r in ids:
            try:rows.append(project_claim(db,c,r['id']))
            except DomainError:pass
    rows.sort(key=lambda r:-(r.get('latest_check') or {}).get('risk_score',0))
    log_access(c,'browse','disaster_id',disaster_id,['claim_review_queue'])
    return result({'claims':rows,'limit':200})


@router.get('/claims/{identity}')
def detail(identity:UUID,c=Depends(actor)):
    with connection() as db:view=project_claim(db,c,identity)
    log_access(c,'open','claim_id',identity,['claim_submission','responses','decisions'])
    return result(view)
