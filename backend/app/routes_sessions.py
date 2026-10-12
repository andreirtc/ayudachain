from uuid import UUID
from datetime import date as CalendarDate
from typing import Literal
from fastapi import APIRouter,Depends,Header
from pydantic import Field
from .main import actor,result
from .schemas.mvp import StrictModel
from .commands import execute_command,DomainError
from .database import connection
from .actor import require_role
from .services import sessions
from .services.access import log_access

router=APIRouter(prefix='/api/v1')


@router.get('/barangay/payout-counts')
def barangay_payout_counts(disaster_id:UUID,c=Depends(actor)):
    """Own-barangay aggregate progress; no household-level payout facts."""
    require_role(c,'barangay')
    with connection() as db:
        disaster=db.execute('SELECT id FROM disasters WHERE id=%s AND run_id=%s AND office_id=%s',(disaster_id,c.run_id,c.office_id)).fetchone()
        if not disaster:raise DomainError(404,'record_unavailable')
        counts=db.execute('''SELECT count(*) approved,
            count(r.id) recorded_handover,
            count(*) FILTER (WHERE r.id IS NULL) remaining
            FROM entitlements e JOIN entitlement_versions v ON v.id=e.current_version_id
            JOIN household_versions h ON h.id=v.registry_version_id
            LEFT JOIN recorded_handovers r ON r.entitlement_id=e.id
            WHERE e.run_id=%s AND e.office_id=%s AND e.disaster_id=%s
            AND h.declared_barangay_id=%s AND e.business_status!='cancelled' ''',
            (c.run_id,c.office_id,disaster_id,c.barangay_id)).fetchone()
    log_access(c,'browse','disaster_id',disaster_id,['own_barangay_aggregate_payout_counts'])
    return result(dict(counts))


class Schedule(StrictModel):
    disaster_id:UUID
    barangay_id:UUID
    list_version_id:UUID
    list_entry_ids:list[UUID]=Field(min_length=1,max_length=500)
    date:CalendarDate
    site:str=Field(min_length=1,max_length=1000)
    cash_actor_ids:list[UUID]=Field(min_length=1,max_length=50)
    followup_actor_ids:list[UUID]=Field(default=[],max_length=50)


class Change(StrictModel):
    expected_revision:int=Field(ge=0)
    action:Literal['open','close','cancel','amend','followup_assign']
    reason:str|None=Field(default=None,max_length=5000)
    date:CalendarDate|None=None
    site:str|None=Field(default=None,min_length=1,max_length=1000)
    list_version_id:UUID|None=None
    list_entry_ids:list[UUID]|None=None
    cash_actor_ids:list[UUID]|None=None
    followup_actor_ids:list[UUID]|None=None


@router.post('/sessions')
def schedule(body:Schedule,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump();return result(execute_command(c.actor_id,'session.schedule',idempotency_key,req,lambda tx:sessions.schedule(tx,req)))


@router.post('/sessions/{identity}/changes')
def change(identity:UUID,body:Change,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    req=body.model_dump(exclude_none=True);return result(execute_command(c.actor_id,'session.change',idempotency_key,dict(req,session_id=identity),lambda tx:sessions.change(tx,identity,req)))


@router.get('/sessions')
def list_sessions(disaster_id:UUID,c=Depends(actor)):
    require_role(c,'dswd','auditor','disbursing','beneficiary')
    with connection() as db:
        rows=db.execute('SELECT s.id,s.disaster_id,s.barangay_id,s.current_version_id,s.business_status,s.revision,v.date,v.site,v.original_list_version_id FROM payout_sessions s JOIN session_versions v ON v.id=s.current_version_id WHERE s.run_id=%s AND s.disaster_id=%s ORDER BY v.date,s.id',(c.run_id,disaster_id)).fetchall();views=[]
        for row in rows:
            assignments=db.execute('SELECT a.id,a.actor_id,a.assignment_kind,p.display_name FROM session_assignments a JOIN actors p ON p.id=a.actor_id WHERE a.session_version_id=%s ORDER BY a.assignment_kind,p.display_name',(row['current_version_id'],)).fetchall()
            entries=db.execute('''SELECT e.id,e.entitlement_id,e.entitlement_version_id,e.list_entry_id,l.frozen_name name,c.label category,v.amount_centavos,t.id transaction_id,h.household_id FROM session_entries e JOIN approved_list_entries l ON l.id=e.list_entry_id JOIN entitlement_versions v ON v.id=e.entitlement_version_id JOIN entitlements h ON h.id=e.entitlement_id JOIN damage_categories c ON c.id=v.category_id JOIN payout_transactions t ON t.entitlement_id=e.entitlement_id WHERE e.session_version_id=%s ORDER BY l.frozen_name,e.id''',(row['current_version_id'],)).fetchall()
            if c.role=='disbursing' and not any(a['actor_id']==c.actor_id for a in assignments):continue
            if c.role=='beneficiary':
                entries=[e for e in entries if e['household_id']==c.household_id]
                if not entries:continue
            for entry in entries:
                entry['amount_centavos']=str(entry['amount_centavos'])
                # No outcome/case selector or status reaches staff session views.
                entry.pop('household_id')
            row['assignments']=assignments;row['entries']=entries;views.append(row)
    log_access(c,'browse','disaster_id',disaster_id,['sessions','assignments','session_amounts'])
    return result(views)


@router.get('/notifications')
def notices(c=Depends(actor)):
    require_role(c,'dswd','auditor','beneficiary')
    with connection() as db:
        rows=db.execute('SELECT id,household_id,purpose,channel,content,simulated,state,created_at FROM notifications WHERE run_id=%s AND (%s OR household_id=%s) ORDER BY created_at DESC,id DESC LIMIT 200',(c.run_id,c.role in {'dswd','auditor'},c.household_id)).fetchall()
    log_access(c,'browse','evaluation_run_id',c.run_id,['notice_intents','simulated_delivery_results'])
    return result(rows)
