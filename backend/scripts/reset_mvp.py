"""Explicit new local registry/namespace; retain every retired record and file."""
import os,json,subprocess
from uuid import uuid4
from backend.app.config import ROOT,load_local_environment,validate_environment
from backend.app.database import connection
from backend.scripts.namespace_mvp import retire
from backend.scripts.seed_mvp import seed

def reset(*,persist_configuration=False):
    load_local_environment();validate_environment()
    with connection(purpose='owner') as db:
        db.execute("SELECT pg_advisory_xact_lock(hashtext('ayudachain-local-signer'))")
        # An uncertain retired signature also owns its nonce. Never discard it.
        if db.execute("SELECT 1 FROM anchor_jobs WHERE state IN ('prepared','submitted','uncertain') LIMIT 1").fetchone():raise ValueError('Resolve durable uncertain submissions before resetting; records retained')
        runs=[r['id'] for r in db.execute("SELECT id FROM evaluation_runs WHERE state='active'").fetchall()]
        manifest=ROOT/'.runtime'/('evaluation-'+uuid4().hex+'.json')
        env=os.environ.copy();env['MVP_DEPLOYMENT_MANIFEST']=str(manifest)
        result=subprocess.run([env['MVP_NODE'],str(ROOT/'contracts/scripts/deploy_evidence.js')],env=env,capture_output=True,timeout=30)
        if result.returncode:raise ValueError('Actual new local deployment failed; current namespace preserved')
        os.environ['MVP_DEPLOYMENT_MANIFEST']=str(manifest)
        for identity in runs:retire(identity,signer_guard_db=db)
        if not seed():raise ValueError('New namespace could not be seeded; history retained')
        if persist_configuration:
            file=ROOT/'.env.mvp'
            lines=[line for line in file.read_text().splitlines() if not line.startswith('MVP_DEPLOYMENT_MANIFEST=')]
            lines.append('MVP_DEPLOYMENT_MANIFEST='+str(manifest));file.write_text('\n'.join(lines)+'\n')
    return {'status':'new_reference_only_namespace','retired_count':len(runs),'manifest':str(manifest),'old_history':'retained_read_only','blockchain_simulated':False}

if __name__=='__main__':print(json.dumps(reset(persist_configuration=True)))
