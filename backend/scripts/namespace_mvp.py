"""Explicit retirement, never destructive reset; separately inspected old history."""
import argparse,json
from uuid import UUID,uuid4
from backend.app.database import connection
from backend.app.actor import resolve_identity,require_role
from backend.app.commands import Transaction,DomainError,wire
from backend.app.services.access import log_access


def retire(run,*,signer_guard_db=None):
    run=UUID(str(run))
    with connection(purpose='owner') as db:
        # Reset already holds this lock on its outer connection while deploying.
        # Reuse that guard; a second connection cannot reacquire its lock.
        guard=signer_guard_db if signer_guard_db is not None else db
        guard.execute("SELECT pg_advisory_xact_lock(hashtext('ayudachain-local-signer'))")
        if guard.execute("SELECT 1 FROM anchor_jobs WHERE state IN ('prepared','submitted','uncertain') LIMIT 1").fetchone():
            raise ValueError('Resolve durable uncertain submissions before retiring; records retained')
        row=db.execute('SELECT * FROM evaluation_runs WHERE id=%s FOR UPDATE',(run,)).fetchone()
        if not row:raise ValueError('Evaluation namespace unavailable')
        db.execute('SELECT id FROM field_offices WHERE id=%s FOR UPDATE',(row['office_id'],))
        if row['state']=='retired':return False
        system=db.execute("SELECT id FROM actors WHERE run_id=%s AND role='system'",(run,)).fetchone()
        tx=Transaction(db,resolve_identity(db,system['id'],system=True),uuid4())
        tx.audit('evaluation.retire',[('evaluation_run_id',run)],'Explicit local reset retires history; no business records, originals, uncertain submissions or manifests deleted')
        db.execute("UPDATE evaluation_runs SET state='retired' WHERE id=%s",(run,))
        return True


def history(actor,*,commitment=None,original=None):
    with connection() as db:
        c=resolve_identity(db,actor,historical=True);require_role(c,'auditor')
        if commitment:
            from backend.app.services.integrity import check_saved
            proof=db.execute('SELECT * FROM commitments WHERE id=%s AND run_id=%s',(commitment,c.run_id)).fetchone()
            if not proof:raise DomainError(404,'record_unavailable')
            checked=check_saved(db,proof)
            log_access(c,'integrity','commitment_id',proof['id'],['exact_retired_commitment_material'],checked['result'])
            return {'result':checked,'canonical_utf8':bytes(proof['canonical_bytes']).decode()}
        if original:
            from backend.app.services.evidence import original_bytes
            file=db.execute('SELECT * FROM evidence_versions WHERE id=%s AND run_id=%s',(original,c.run_id)).fetchone()
            if not file:raise DomainError(404,'record_unavailable')
            raw=original_bytes(file)
            log_access(c,'open','evidence_version_id',file['id'],['retired_original_bytes'])
            return raw
        run=db.execute('SELECT state FROM evaluation_runs WHERE id=%s',(c.run_id,)).fetchone()
        view={'run_id':c.run_id,'state':run['state'],'mode':'read_only_separate_history',
            'originals':db.execute('SELECT id,purpose,mime_type,created_at FROM evidence_versions WHERE run_id=%s ORDER BY created_at,id',(c.run_id,)).fetchall(),
            'proofs':db.execute('SELECT id,kind,created_at FROM commitments WHERE run_id=%s ORDER BY created_at,id',(c.run_id,)).fetchall(),
            'audit':db.execute('SELECT id,sequence,action,reason,safe_details,created_at FROM audit_events WHERE run_id=%s ORDER BY sequence',(c.run_id,)).fetchall()}
        log_access(c,'browse','evaluation_run_id',c.run_id,['separate_retired_history'])
        return view


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['retire','catalogue','history']);p.add_argument('--run',type=UUID);p.add_argument('--actor',type=UUID);p.add_argument('--commitment',type=UUID);p.add_argument('--original',type=UUID);p.add_argument('--output')
    a=p.parse_args()
    if a.action=='retire':print(json.dumps({'retired':retire(a.run)}))
    elif a.action=='catalogue':
        with connection() as db:rows=db.execute("SELECT r.id,r.state,a.id auditor_actor_id,a.display_name FROM evaluation_runs r JOIN actors a ON a.run_id=r.id WHERE a.role='auditor' ORDER BY r.created_at,a.id").fetchall()
        print(json.dumps(rows,default=wire))
    else:
        data=history(a.actor,commitment=a.commitment,original=a.original)
        if isinstance(data,bytes):
            if not a.output:raise ValueError('Original requires explicit output path')
            from pathlib import Path
            with Path(a.output).open('xb') as target:target.write(data)
            print('Original copied; inspection logged')
        else:print(json.dumps(data,default=wire,ensure_ascii=False))

if __name__=='__main__':main()
