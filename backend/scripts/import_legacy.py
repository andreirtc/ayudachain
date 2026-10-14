"""Operator-invoked synthetic snapshot import; Auditor has no import action."""
import argparse
import json
import hashlib
import os
import subprocess
from pathlib import Path
from uuid import UUID
from backend.app.commands import execute_command,DomainError
from backend.app.config import ROOT,load_local_environment
from backend.app.services.legacy import import_snapshot


def register_legacy(tx,manifest_path):
    path=Path(manifest_path).resolve();raw=path.read_bytes();manifest=json.loads(raw)
    if manifest['protocol']!='legacy.receipt.v1' or manifest.get('deployment_uid') is not None:raise DomainError(422,'legacy_protocol_required')
    run=subprocess.run([os.environ.get('MVP_NODE','node'),str(ROOT/'contracts/scripts/read_legacy.js')],input=json.dumps({'manifest':manifest,'distribution_id':'DFC-2026-PROBE'}),capture_output=True,text=True,timeout=12,cwd=ROOT)
    if json.loads(run.stdout)['status']!='read':raise DomainError(503,'legacy_deployment_unavailable')
    prior=tx.db.execute("SELECT * FROM deployments WHERE run_id=%s AND protocol='legacy.receipt.v1' AND address=%s AND deploy_block_hash=%s",(tx.context.run_id,bytes.fromhex(manifest['address'][2:]),bytes.fromhex(manifest['deploy_block_hash'][2:]))).fetchone()
    if prior:return prior
    fields={k:bytes.fromhex(manifest[k][2:]) for k in ['address','genesis_hash','deploy_block_hash','runtime_code_hash']}
    row=tx.insert('deployments',dict(fields,protocol='legacy.receipt.v1',deployment_uid=None,chain_id=int(manifest['chain_id']),deploy_block_number=int(manifest['deploy_block_number']),abi_reference=str(path)+'#sha256='+hashlib.sha256(raw).hexdigest(),confirmation_policy=manifest['confirmation_policy'],state='active'))
    tx.audit('deployment.legacy_register',[('evaluation_run_id',tx.context.run_id)],'Original legacy protocol and deployment pinned')
    return row


def main():
    p=argparse.ArgumentParser();p.add_argument('--actor',type=UUID,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--manifest',type=Path);args=p.parse_args();load_local_environment()
    def action(tx):
        from backend.app.actor import require_role
        require_role(tx.context,'dswd')
        deployment=register_legacy(tx,args.manifest) if args.manifest else None
        return import_snapshot(tx,args.source,deployment_id=deployment['id'] if deployment else None)
    ack=execute_command(args.actor,'legacy.import',hashlib.sha256(args.source.read_bytes()).hexdigest(),{'source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'manifest':str(args.manifest)},action)
    print(json.dumps(ack))


if __name__=='__main__':main()
