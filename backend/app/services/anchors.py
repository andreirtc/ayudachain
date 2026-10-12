from uuid import uuid4
from ..commands import execute_command,DomainError
from ..database import connection
from .integrity import check_saved


def apply_observation(identity):
    with connection() as db:
        observation=db.execute("SELECT o.* FROM anchor_observations o JOIN evaluation_runs r ON r.id=o.run_id WHERE o.id=%s AND o.verdict='mined_match' AND r.state='active'",(identity,)).fetchone()
        if not observation: return False
        items=db.execute('SELECT c.* FROM commitments c JOIN anchor_job_items i ON i.commitment_id=c.id WHERE i.job_id=%s ORDER BY i.ordinal',(observation['job_id'],)).fetchall()
        if not items or any(check_saved(db,c)['result']!='match' for c in items): return False
        system=db.execute("SELECT id FROM actors WHERE run_id=%s AND role='system'",(observation['run_id'],)).fetchone()['id']
    def apply(tx):
        if tx.db.execute('SELECT 1 FROM anchor_applications WHERE observation_id=%s',(identity,)).fetchone(): return [('anchor_job_id',observation['job_id'])]
        job=tx.get('anchor_jobs',observation['job_id'])
        if job['state'] in {'conflict','deployment_lost'}: raise DomainError(409,'anchor_requires_investigation')
        tx.update('anchor_jobs',job['id'],{'state':'confirmed','lease_owner':None,'lease_until':None,'last_error_code':None})
        from .entitlements import publish_confirmed
        for item in items:
            if item['list_version_id']:publish_confirmed(tx,item['list_version_id'])
        event=tx.audit('anchor.confirm',[('anchor_job_id',job['id'])])
        tx.insert('anchor_applications',{'observation_id':identity,'audit_event_id':event,'applied_at':tx.now})
        return [('anchor_job_id',job['id'])]
    try:execute_command(system,'anchor.apply',str(identity),{'observation_id':str(identity)},apply,system=True)
    except DomainError as error:
        if error.code=='actor_unavailable':
            with connection() as db:
                if db.execute("SELECT 1 FROM evaluation_runs WHERE id=%s AND state='retired'",(observation['run_id'],)).fetchone():return False
        raise
    return True


def apply_due_observations():
    with connection() as db:
        rows=db.execute("SELECT o.id FROM anchor_observations o JOIN evaluation_runs r ON r.id=o.run_id LEFT JOIN anchor_applications a ON a.observation_id=o.id WHERE r.state='active' AND o.verdict='mined_match' AND a.observation_id IS NULL ORDER BY o.checked_at,o.id LIMIT 100").fetchall()
    return sum(apply_observation(row['id']) for row in rows)
