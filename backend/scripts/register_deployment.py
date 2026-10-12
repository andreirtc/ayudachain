"""Explicit pinned registration, idempotent; never silently remaps old history."""
import json
import os
import hashlib
from pathlib import Path
from backend.app.services.evidence_protocol import PROTOCOL
from backend.app.commands import Transaction,DomainError


def register(tx,manifest_path):
    from backend.app.services.integrity import read_public
    path=Path(manifest_path).resolve()
    manifest=json.loads(path.read_text(encoding='utf-8'))
    if manifest['protocol']!=PROTOCOL: raise DomainError(422,'protocol_invalid')
    observed=read_public(manifest,b'\x01'*32)
    if observed['status']!='read': raise DomainError(503,observed['status'])
    existing=tx.db.execute('SELECT * FROM deployments WHERE run_id=%s AND deployment_uid=%s',(tx.context.run_id,bytes.fromhex(manifest['deployment_uid'][2:]))).fetchone()
    if existing: return existing
    active=tx.db.execute("SELECT 1 FROM deployments WHERE run_id=%s AND protocol=%s AND state='active'",(tx.context.run_id,PROTOCOL)).fetchone()
    if active: raise DomainError(409,'retire_namespace_before_new_deployment')
    data={'protocol':PROTOCOL,'chain_id':int(manifest['chain_id']),'deploy_block_number':int(manifest['deploy_block_number']),
          'abi_reference':str(path)+'#sha256='+hashlib.sha256(path.read_bytes()).hexdigest(),'confirmation_policy':manifest['confirmation_policy'],'state':'active'}
    for key in ['address','deployment_uid','genesis_hash','deploy_block_hash','runtime_code_hash']: data[key]=bytes.fromhex(manifest[key][2:])
    row=tx.insert('deployments',data)
    tx.audit('deployment.register',[('evaluation_run_id',tx.context.run_id)])
    return row
