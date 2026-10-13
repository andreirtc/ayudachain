from datetime import date
from uuid import UUID
from typing import Literal
from fastapi import APIRouter,Depends,Header
from pydantic import Field
from .main import actor,result
from .schemas.mvp import StrictModel
from .commands import execute_command,DomainError
from .database import connection
from .actor import require_role
from .services import registry
from .services.access import log_access

router=APIRouter(prefix='/api/v1')


class Member(StrictModel):
    member_id:UUID|None=None
    name:str=Field(min_length=1,max_length=200)
    birth_date:date|None=None
    relationship:str=Field(min_length=1,max_length=100)
    is_head:bool


class Registration(StrictModel):
    beneficiary_actor_id:UUID|None=None
    phone:str|None=Field(default=None,max_length=30)
    declared_barangay_id:UUID
    address:str=Field(min_length=1,max_length=1000)
    zone:str=Field(min_length=1,max_length=200)
    id_type:str|None=Field(default=None,max_length=100)
    id_number:str|None=Field(default=None,max_length=100)
    head_photo_evidence_id:UUID|None=None
    id_evidence_id:UUID|None=None
    members:list[Member]=Field(min_length=1,max_length=30)


class Review(StrictModel):
    expected_revision:int=Field(ge=0)
    action:Literal['residence_confirm','residence_dispute','residence_resolve','field_check','facts_correct','contact_relink','id_check']
    reason:str=Field(min_length=1,max_length=3000)
    beneficiary_actor_id:UUID|None=None
    phone:str|None=Field(default=None,max_length=30)
    accepted_id_type:str|None=Field(default=None,max_length=100)
    person_photo_compared:bool|None=None
    id_type:str|None=None
    id_number:str|None=None
    head_photo_evidence_id:UUID|None=None
    id_evidence_id:UUID|None=None
    field_evidence_id:UUID|None=None
    declared_barangay_id:UUID|None=None
    address:str|None=None
    zone:str|None=None
    members:list[Member]|None=None


class OpenIntake(StrictModel):
    disaster_id:UUID
    barangay_ids:list[UUID]=Field(min_length=1)
    response_hours:int=Field(gt=0,le=720)
    basis_evidence_id:UUID


class ReasonRevision(StrictModel):
    expected_revision:int=Field(ge=0)
    reason:str=Field(min_length=1,max_length=3000)


class Nomination(StrictModel):
    staff_role:Literal['barangay','disbursing']
    display_name:str=Field(min_length=1,max_length=200)
    email:str|None=None
    barangay_id:UUID|None=None
    position:str|None=None
    nominator_name:str|None=None
    nomination_evidence_id:UUID|None=None


class StaffDecision(ReasonRevision):status:Literal['active','deactivated']
class MemberLink(ReasonRevision):member_id:UUID


def command(c,name,key,body,handler,**ids):
    request=body.model_dump(exclude_none=True) if isinstance(body,Review) else body.model_dump()
    return result(execute_command(c.actor_id,name,key,{**request,**ids},lambda tx:handler(tx,request)))


@router.post('/registry')
def register(body:Registration,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    return command(c,'registry.register',idempotency_key,body,registry.register)


@router.post('/registry/{identity}/reviews')
def review(identity:UUID,body:Review,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    return command(c,'registry.review',idempotency_key,body,lambda tx,r:registry.review(tx,identity,r),household_id=identity)


@router.get('/registry')
def households(c=Depends(actor)):
    require_role(c,'dswd','auditor','barangay','beneficiary')
    with connection() as db:
        ids=db.execute('SELECT id FROM households WHERE run_id=%s ORDER BY display_id LIMIT 200',(c.run_id,)).fetchall()
        rows=[]
        for row in ids:
            try:rows.append(registry.project(db,c,row['id']))
            except DomainError:pass
    if c.role=='auditor':log_access(c,'browse','evaluation_run_id',c.run_id,['registry_names','registry_scoped_facts'])
    return result({'households':rows,'limit':200})


@router.get('/registry/{identity}')
def detail(identity:UUID,identity_open:bool=False,c=Depends(actor)):
    with connection() as db:view=registry.project(db,c,identity,identity_open=identity_open)
    log_access(c,'identity' if identity_open else 'open','household_id',identity,['id_number','identity_photo'] if identity_open else ['registry_facts','contact'])
    return result(view)


@router.post('/intake/open')
def open_intake(body:OpenIntake,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    return command(c,'intake.open',idempotency_key,body,registry.open_intake)


@router.post('/intake/{identity}/close')
def close_intake(identity:UUID,body:ReasonRevision,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    return command(c,'intake.close',idempotency_key,body,lambda tx,r:registry.close_intake(tx,identity,r),operation_id=identity)


@router.get('/intake')
def intake(c=Depends(actor)):
    with connection() as db:
        rows=db.execute('SELECT id,disaster_id,current_version_id,business_status,revision FROM claim_operations WHERE run_id=%s ORDER BY created_at,id',(c.run_id,)).fetchall()
        for row in rows:
            version=db.execute('SELECT response_hours FROM operation_versions WHERE id=%s',(row['current_version_id'],)).fetchone();row.update(version)
            row['barangay_ids']=[b['barangay_id'] for b in db.execute('SELECT barangay_id FROM operation_barangays WHERE operation_version_id=%s',(row['current_version_id'],)).fetchall()]
    return result(rows)


@router.post('/staff/nominations')
def nominate(body:Nomination,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    return command(c,'staff.nominate',idempotency_key,body,registry.nominate)


@router.post('/staff/{identity}/status')
def staff_status(identity:UUID,body:StaffDecision,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    return command(c,'staff.status',idempotency_key,body,lambda tx,r:registry.staff_decision(tx,identity,r),staff_id=identity)


@router.post('/staff/{identity}/member-link')
def member_link(identity:UUID,body:MemberLink,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    return command(c,'staff.member_link',idempotency_key,body,lambda tx,r:registry.member_link(tx,identity,r),staff_id=identity)


@router.get('/staff')
def staff(c=Depends(actor)):
    require_role(c,'dswd','auditor')
    with connection() as db:
        rows=db.execute("SELECT a.id,a.role,a.display_name,a.revision,a.current_member_link_id,v.id version_id,v.status,v.barangay_id,v.position,v.nomination_id,v.approved_by FROM actors a JOIN actor_versions v ON v.id=a.current_version_id WHERE a.run_id=%s AND a.role IN ('barangay','disbursing') ORDER BY a.display_name,a.id",(c.run_id,)).fetchall()
    log_access(c,'browse','evaluation_run_id',c.run_id,['staff_nomination_status'])
    return result(rows)
