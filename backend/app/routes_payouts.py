from uuid import UUID
from typing import Literal
from fastapi import APIRouter,Depends,Header
from pydantic import Field
from .main import actor,result
from .schemas.mvp import StrictModel
from .commands import execute_command,DomainError
from .database import connection
from .services import payouts
from .services.access import log_access

router=APIRouter(prefix='/api/v1')


@router.get('/transactions')
def transactions(disaster_id:UUID,c=Depends(actor)):
    with connection() as db:
        ids=db.execute('SELECT t.id FROM payout_transactions t JOIN entitlements e ON e.id=t.entitlement_id WHERE e.disaster_id=%s AND e.run_id=%s ORDER BY t.created_at,t.id LIMIT 200',(disaster_id,c.run_id)).fetchall();views=[]
        for row in ids:
            try:
                view=payouts.project(db,c,row['id']);views.append({k:view[k] for k in ['id','household_name','business_status','amount_centavos']})
            except DomainError:pass
    log_access(c,'browse','disaster_id',disaster_id,['permitted_transaction_catalogue'])
    return result(views)


class Opening(StrictModel):
    expected_revision:int=Field(ge=0)
    path:Literal['own_device','assisted']
    pin:str|None=Field(default=None,min_length=6,max_length=12,pattern=r'^[0-9]+$')


class IdentityCheck(StrictModel):
    household_id:UUID
    result:Literal['pass','fail']
    accepted_id_type:str|None=Field(default=None,max_length=100)
    person_photo_compared:bool
    reason:str|None=Field(default=None,max_length=5000)
    attempt_id:UUID|None=None


class PIN(StrictModel):
    identity_check_id:UUID
    pin:str=Field(min_length=6,max_length=12,pattern=r'^[0-9]+$')


class Handover(StrictModel):
    expected_revision:int=Field(ge=0)
    attempt_id:UUID
    code:str=Field(pattern=r'^[0-9]{6}$')
    checker_actor_id:UUID|None=None


class Clearance(StrictModel):
    expected_revision:int=Field(ge=0)
    reason:str=Field(min_length=1,max_length=5000)
    evidence_id:UUID|None=None


@router.post('/sessions/{identity}/id-checks')
def check(identity:UUID,body:IdentityCheck,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'identity.check',idempotency_key,dict(req,session_id=identity),lambda tx:payouts.id_check(tx,identity,req)))


@router.post('/households/{identity}/assisted-pin')
def pin(identity:UUID,body:PIN,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'recipient.pin',idempotency_key,dict(req,household_id=identity),lambda tx:payouts.establish_pin(tx,identity,req)))


@router.post('/entitlements/{identity}/attempts')
def open_attempt(identity:UUID,body:Opening,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'attempt.open',idempotency_key,dict(req,entitlement_id=identity),lambda tx:payouts.open_attempt(tx,identity,req)))


@router.post('/transactions/{identity}/handover')
def handover(identity:UUID,body:Handover,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'payout.handover',idempotency_key,dict(req,transaction_id=identity),lambda tx:payouts.handover(tx,identity,req)))


@router.post('/transactions/{identity}/clearances')
def clearance(identity:UUID,body:Clearance,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'attempt.clearance',idempotency_key,dict(req,transaction_id=identity),lambda tx:payouts.clearance(tx,identity,req)))


@router.get('/transactions/{identity}')
def transaction(identity:UUID,c=Depends(actor)):
    with connection() as db:view=payouts.project(db,c,identity)
    log_access(c,'open','transaction_id',identity,['transaction_amount','authorization_history','recorded_handover'])
    return result(view)
