from uuid import uuid4
from datetime import timedelta
from fastapi import APIRouter,Depends,Header
from pydantic import Field
from .main import actor,result
from .schemas.mvp import StrictModel
from .actor import require_role
from .database import connection
from .commands import execute_command
from .services.access import log_access

router=APIRouter(prefix='/api/v1/evaluation')

@router.get('/status')
def status(c=Depends(actor)):
    with connection() as db:row=db.execute('SELECT id,state,clock_mode,clock_offset,clock_timestamp() actual_utc,clock_timestamp()+clock_offset business_utc FROM evaluation_runs WHERE id=%s AND office_id=%s',(c.run_id,c.office_id)).fetchone()
    row['offset_hours']=str(row.pop('clock_offset').total_seconds()/3600)
    log_access(c,'browse','evaluation_run_id',c.run_id,['evaluation_clock'])
    return result(row)

class Clock(StrictModel):advance_hours:int=Field(gt=0,le=720)

@router.post('/clock')
def advance(body:Clock,idempotency_key:str=Header(alias='Idempotency-Key'),c=Depends(actor)):
    require_role(c,'dswd')
    def action(tx):
        prior=tx.db.execute('SELECT clock_offset FROM evaluation_runs WHERE id=%s',(c.run_id,)).fetchone()['clock_offset']
        tx.db.execute("UPDATE evaluation_runs SET clock_mode='simulated',clock_offset=clock_offset+%s WHERE id=%s",(timedelta(hours=body.advance_hours),c.run_id))
        tx.audit('evaluation.clock_advanced',[('evaluation_run_id',c.run_id)],'Explicit synthetic business-time advance; chain time remains actual',details={'advance_hours':body.advance_hours,'prior_offset_seconds':str(prior.total_seconds()),'chain_time':'actual'})
        return [('evaluation_run_id',c.run_id)]
    return result(execute_command(c.actor_id,'evaluation.clock',idempotency_key,body.model_dump(),action))
