"""Durable due work. Business services use persisted deadlines and office locks."""
import time
from .services.anchors import apply_due_observations
from .database import connection
from .commands import execute_command,DomainError


def route_overdue():
    from .services.claims import fallback
    with connection() as db:
        rows=db.execute("""SELECT r.id,a.id actor_id FROM claim_rounds r JOIN evaluation_runs e ON e.id=r.run_id JOIN actors a ON a.run_id=r.run_id AND a.role='system' WHERE r.state='waiting' AND e.state='active' AND r.deadline_at<=clock_timestamp()+e.clock_offset ORDER BY r.deadline_at,r.id LIMIT 100""").fetchall()
    routed=0
    for row in rows:
        try:
            execute_command(row['actor_id'],'claim.deadline',str(row['id']),{'round_id':row['id']},lambda tx:fallback(tx,row['id']),system=True);routed+=1
        except DomainError as error:
            if error.code not in {'round_already_routed','deadline_not_due'}:raise
    return routed


def process_due():
    from .services.notifications import due
    with connection() as db:runs=db.execute("SELECT a.id FROM actors a JOIN evaluation_runs r ON r.id=a.run_id WHERE r.state='active' AND a.role='system' AND EXISTS(SELECT 1 FROM notifications n WHERE n.run_id=r.id AND n.state='pending')").fetchall()
    for actor in runs:
        # Each tick gets a new request key; already delivered rows are excluded.
        from uuid import uuid4
        execute_command(actor['id'],'notice.deliver',str(uuid4()),{},lambda tx:(due(tx),[('evaluation_run_id',tx.context.run_id)])[1],system=True)
    from .services.payouts import expire_due
    with connection() as db:
        expired=db.execute("SELECT DISTINCT a.id FROM actors a JOIN evaluation_runs r ON r.id=a.run_id JOIN payout_attempts p ON p.run_id=r.id WHERE r.state='active' AND a.role='system' AND p.business_status IN ('open','presented') AND p.expires_at<=clock_timestamp()+r.clock_offset").fetchall()
    for actor in expired:execute_command(actor['id'],'attempt.expiry',str(uuid4()),{},lambda tx:(expire_due(tx),[('evaluation_run_id',tx.context.run_id)])[1],system=True)
    from .services.outcomes import timeout
    with connection() as db:
        rows=db.execute("SELECT r.transaction_id,a.id actor_id FROM recorded_handovers r JOIN payout_transactions t ON t.id=r.transaction_id JOIN evaluation_runs e ON e.id=r.run_id JOIN actors a ON a.run_id=r.run_id AND a.role='system' WHERE e.state='active' AND t.current_outcome_id IS NULL AND r.handed_at+interval '72 hours'<=clock_timestamp()+e.clock_offset ORDER BY r.handed_at,r.id LIMIT 100").fetchall()
    for row in rows:
        try:execute_command(row['actor_id'],'outcome.timeout',str(row['transaction_id']),{'transaction_id':row['transaction_id']},lambda tx:timeout(tx,row['transaction_id']),system=True)
        except DomainError as error:
            if error.code not in {'answer_already_recorded','outcome_deadline_not_due'}:raise
    return {'anchor_applications':apply_due_observations(),'claim_deadlines':route_overdue()}


if __name__=='__main__':
    while True:
        try: process_due()
        except Exception: print('Due work unavailable; persisted work retained',flush=True)
        time.sleep(2)
