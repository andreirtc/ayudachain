from uuid import UUID
from typing import Literal
from fastapi import APIRouter,Depends,Header
from pydantic import Field
from .main import actor,result
from .schemas.mvp import StrictModel
from .database import connection
from .actor import require_role
from .commands import execute_command,DomainError
from .services import outcomes
from .services.access import log_access

router=APIRouter(prefix='/api/v1')


class Answer(StrictModel):
    answer:Literal['received_full','received_less','not_received']
    expected_latest_id:UUID|None=None


class Report(StrictModel):
    text:str=Field(min_length=1,max_length=5000)
    evidence_ids:list[UUID]=Field(default=[],max_length=20)


class CaseAction(StrictModel):
    expected_revision:int=Field(ge=0)
    action:Literal['review','note','resolve']
    text:str=Field(min_length=1,max_length=5000)


class ChallengeAction(StrictModel):
    expected_revision:int=Field(ge=0)
    action:Literal['review','note','substantiate','dismiss']
    text:str=Field(min_length=1,max_length=5000)


@router.post('/transactions/{identity}/outcomes')
def answer(identity:UUID,body:Answer,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'outcome.record',idempotency_key,dict(req,transaction_id=identity),lambda tx:outcomes.answer(tx,identity,req)))


@router.post('/transactions/{identity}/reports')
def report(identity:UUID,body:Report,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'grievance.report',idempotency_key,dict(req,transaction_id=identity),lambda tx:outcomes.report(tx,identity,req)))


@router.get('/transactions/{identity}/private-outcomes')
def private(identity:UUID,c=Depends(actor)):
    with connection() as db:view=outcomes.private_view(db,c,identity)
    log_access(c,'open','transaction_id',identity,['private_outcome_history','private_grievance_history'])
    return result(view)


@router.post('/grievances/{identity}/actions')
def case_action(identity:UUID,body:CaseAction,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'grievance.action',idempotency_key,dict(req,grievance_id=identity),lambda tx:outcomes.case_action(tx,identity,req)))


@router.get('/grievances')
def cases(c=Depends(actor)):
    require_role(c,'dswd','auditor','beneficiary')
    with connection() as db:
        rows=db.execute('SELECT id,transaction_id,household_id,business_status,revision FROM grievances WHERE run_id=%s AND (%s OR household_id=%s) ORDER BY created_at,id',(c.run_id,c.role in {'dswd','auditor'},c.household_id)).fetchall()
        for row in rows:row['history']=db.execute('SELECT id,kind,report_text,resolution,outcome_version_id,created_at FROM grievance_events WHERE grievance_id=%s ORDER BY created_at,id',(row['id'],)).fetchall()
    log_access(c,'browse','evaluation_run_id',c.run_id,['private_grievances'])
    return result(rows)


@router.post('/list-entries/{identity}/challenges')
def challenge(identity:UUID,body:Report,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'challenge.report',idempotency_key,dict(req,list_entry_id=identity),lambda tx:outcomes.challenge(tx,identity,req)))


@router.post('/challenges/{identity}/actions')
def challenge_action(identity:UUID,body:ChallengeAction,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'challenge.action',idempotency_key,dict(req,challenge_id=identity),lambda tx:outcomes.challenge_action(tx,identity,req)))


@router.get('/challenges')
def challenges(c=Depends(actor)):
    require_role(c,'dswd','auditor','beneficiary')
    with connection() as db:
        rows=db.execute('SELECT id,list_entry_id,reporting_household_id,business_status,revision FROM list_challenges WHERE run_id=%s AND (%s OR reporting_household_id=%s) ORDER BY created_at,id',(c.run_id,c.role in {'dswd','auditor'},c.household_id)).fetchall()
        for row in rows:row['history']=db.execute('SELECT id,action,reason,created_at FROM challenge_events WHERE challenge_id=%s ORDER BY created_at,id',(row['id'],)).fetchall()
    log_access(c,'browse','evaluation_run_id',c.run_id,['private_resident_challenges'])
    return result(rows)


@router.get('/outcome-totals')
def totals(disaster_id:UUID,c=Depends(actor)):
    require_role(c,'dswd','auditor')
    with connection() as db:view=outcomes.totals(db,c.run_id,disaster_id)
    log_access(c,'browse','disaster_id',disaster_id,['recorded_handover_totals','latest_private_outcome_totals'])
    return result(view)


@router.post('/transactions/{identity}/notes')
def note(identity:UUID,body:Report,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    require_role(c,'disbursing','dswd')
    def save(tx):
        t,e=__import__('backend.app.services.payouts',fromlist=['can_read']).can_read(tx.db,tx.context,identity)
        if not body.text.strip():raise DomainError(422,'operational_note_required')
        if body.evidence_ids:raise DomainError(422,'operational_note_is_text_only')
        if tx.context.role=='dswd':
            from .actor import require_independent
            require_independent(tx.context,e['household_id'])
        row=tx.insert('transaction_notes',{'transaction_id':t['id'],'actor_id':tx.context.actor_id,'note':body.text})
        tx.audit('transaction.note',[('entitlement_version_id',e['current_version_id'])],details={'note_id':str(row['id'])})
        return [('transaction_id',t['id'])]
    return result(execute_command(c.actor_id,'transaction.note',idempotency_key,dict(body.model_dump(),transaction_id=identity),save))


@router.get('/transactions/{identity}/notes')
def note_history(identity:UUID,c=Depends(actor)):
    require_role(c,'disbursing','dswd','auditor')
    with connection() as db:
        from .services.payouts import can_read
        can_read(db,c,identity)
        rows=db.execute('SELECT id,actor_id,note,created_at FROM transaction_notes WHERE transaction_id=%s AND (%s OR actor_id=%s) ORDER BY created_at,id',(identity,c.role in {'dswd','auditor'},c.actor_id)).fetchall()
    log_access(c,'open','transaction_id',identity,['operational_note_history'])
    return result(rows)
