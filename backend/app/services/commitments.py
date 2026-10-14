import os
import json
import secrets
from datetime import datetime
from uuid import UUID
from pathlib import Path
from ..commands import DomainError
from .evidence_protocol import canonical_bytes,content_hash,PROTOCOL,KINDS
from .evidence import original_bytes


def hex32(value): return '0x'+bytes(value).hex()


def freeze_value(value):
    if value is None or isinstance(value,bool): return value
    if isinstance(value,(int,UUID)): return str(value)
    if isinstance(value,bytes): return hex32(value)
    if isinstance(value,datetime): return value.isoformat(timespec='milliseconds').replace('+00:00','Z')
    if hasattr(value,'isoformat'): return value.isoformat()
    if isinstance(value,list): return [freeze_value(v) for v in value]
    if isinstance(value,dict): return {k:freeze_value(v) for k,v in value.items()}
    if isinstance(value,str): return value
    raise ValueError('Exact protocol scalar required')


def freeze_commitment(tx,slot,owner_id,kind,payload,*,context=None,predecessor=None,related=None,evidence=(),job_id=None,ordinal=0):
    from ..models.mvp import PROOF_OWNERS
    if slot not in PROOF_OWNERS or kind not in KINDS: raise ValueError('Typed proof owner/kind required')
    deployment=tx.db.execute("SELECT * FROM deployments WHERE run_id=%s AND office_id=%s AND protocol=%s AND state='active' ORDER BY created_at DESC LIMIT 1",(tx.context.run_id,tx.context.office_id,PROTOCOL)).fetchone()
    if not deployment: raise DomainError(503,'registry_registration_required')
    public_id,nonce=secrets.token_bytes(32),secrets.token_bytes(32)
    context=context or secrets.token_bytes(32)
    previous=tx.get('commitments',predecessor) if predecessor else None
    related_record=tx.get('commitments',related) if related else None
    descriptors=[]
    for item in evidence:
        original_bytes(item)
        descriptors.append({k:item[k] for k in ['id','mime_type','byte_sha256','byte_length']})
    envelope={'protocol':PROTOCOL,'kind':kind,'public_id':public_id,'owner':owner_id,'context':context,
        'predecessor':previous['public_id'] if previous else None,'related':related_record['public_id'] if related_record else None,
        'effective_at':tx.now,'actor':{'actor_id':tx.context.actor_id,'display_name':tx.context.display_name,'position':tx.context.position,'identity_assurance':tx.context.identity_assurance},
        'evidence':descriptors,'payload':payload,'private_nonce':nonce}
    raw=canonical_bytes(freeze_value(envelope))
    row=tx.insert('commitments',{slot:owner_id,'public_id':public_id,'protocol':PROTOCOL,'kind':kind,'predecessor_commitment_id':predecessor,
        'public_context':context,'public_related':related_record['public_id'] if related_record else None,'canonical_bytes':raw,'content_hash':content_hash(raw),'private_nonce':nonce,'deployment_id':deployment['id']})
    if job_id is None:
        job=tx.insert('anchor_jobs',{'deployment_id':deployment['id'],'operation':'fund_release' if kind=='fund_release' else 'anchor_record',
            'state':'pending','next_attempt_at':tx.wall_now,'lease_owner':None,'lease_until':None,'last_error_code':None})
        job_id=job['id']
        tx.audit('anchor.intent',[('anchor_job_id',job_id)])
    tx.insert('anchor_job_items',{'commitment_id':row['id'],'job_id':job_id,'ordinal':ordinal})
    for dependency in [previous,related_record]:
        if dependency:
            prior_job=tx.db.execute('SELECT job_id FROM anchor_job_items WHERE commitment_id=%s',(dependency['id'],)).fetchone()['job_id']
            if prior_job!=job_id and not tx.db.execute('SELECT 1 FROM anchor_dependencies WHERE job_id=%s AND prerequisite_job_id=%s',(job_id,prior_job)).fetchone():
                tx.insert('anchor_dependencies',{'job_id':job_id,'prerequisite_job_id':prior_job})
    return row


def document_commitment(tx,item):
    prior=tx.db.execute('SELECT * FROM commitments WHERE evidence_version_id=%s',(item['id'],)).fetchone()
    if prior: return prior
    return freeze_commitment(tx,'evidence_version_id',item['id'],'document',{'purpose':item['purpose'],'extraction_state':item['extraction_state'],'extraction_version':item['extraction_version'],'extracted_fields':item['extracted_fields'],'signature_state':'not_validated'},evidence=[item])
