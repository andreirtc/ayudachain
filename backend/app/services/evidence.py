"""Private original-byte storage; immutable uploads precede business linking."""
import hashlib
import os
import subprocess
import json
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timezone
from ..config import ROOT
from ..commands import DomainError
from .access import authorize_evidence


def storage_root():
    return Path(os.environ.get('MVP_EVIDENCE_ROOT',str(ROOT/'.runtime/originals'))).resolve()


def original_bytes(item,*,root=None):
    root=storage_root() if root is None else Path(root).resolve()
    path=(root/item['storage_key']).resolve()
    if not path.is_relative_to(root): raise DomainError(404,'evidence_unavailable')
    try: raw=path.read_bytes()
    except OSError: raise DomainError(503,'evidence_unavailable') from None
    if len(raw)!=item['byte_length'] or hashlib.sha256(raw).digest()!=item['byte_sha256']:
        raise DomainError(409,'evidence_mismatch')
    return raw


def prepare_upload(raw,mime,*,root=None):
    if not raw or len(raw)>10485760: raise DomainError(422,'file_size_invalid')
    signatures={'application/pdf':b'%PDF-','image/png':b'\x89PNG\r\n\x1a\n','image/jpeg':b'\xff\xd8\xff'}
    if mime not in signatures or not raw.startswith(signatures[mime]): raise DomainError(422,'file_type_invalid')
    root=storage_root() if root is None else Path(root).resolve()
    root.mkdir(parents=True,exist_ok=True)
    key=uuid4().hex+'.original'
    path=root/key
    with path.open('xb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    state,fields='manual_required',None
    if mime=='application/pdf':
        try:
            run=subprocess.run([sys.executable,'-m','backend.app.services.extraction',str(path)],capture_output=True,timeout=8,cwd=ROOT)
            if run.returncode==0:
                fields=json.loads(run.stdout)
                state='extracted' if fields.get('text') else 'manual_required'
            else: state='failed'
        except (subprocess.SubprocessError,ValueError,OSError): state='failed'
    return {'mime_type':mime,'byte_length':len(raw),'byte_sha256':hashlib.sha256(raw).digest(),'storage_key':key,
            'storage_version':None,'uploaded_at':datetime.now(timezone.utc),'extraction_state':state,
            'extraction_version':'pypdf.text.v1' if mime=='application/pdf' else None,'extracted_fields':fields,'signature_state':'not_validated'}


def save_upload(tx,item,purpose,prepared_for=None,predecessor=None):
    from ..actor import require_role
    require_role(tx.context,'dswd','barangay','beneficiary')
    if purpose in {'identity_photo','identity_document'}:
        if prepared_for is None:
            if tx.context.role!='beneficiary': raise DomainError(422,'private_recipient_required')
            prepared_for=tx.context.actor_id
        if tx.context.role=='beneficiary' and prepared_for!=tx.context.actor_id:
            raise DomainError(403,'private_evidence_scope_mismatch')
        recipient=tx.get('actors',prepared_for)
        if recipient['role']!='beneficiary': raise DomainError(422,'private_recipient_required')
    elif prepared_for is not None: raise DomainError(422,'preparation_scope_invalid')
    if predecessor:
        prior=tx.get('evidence_versions',predecessor)
        # A helper may replace their own private-panel upload without gaining
        # stored-original access. Other predecessors require current file scope.
        helper_preparation=(tx.context.role=='barangay' and prior['uploaded_by']==tx.context.actor_id
                            and prior['purpose'] in {'identity_photo','identity_document'})
        if not helper_preparation: authorize_evidence(tx.db,tx.context,predecessor)
        if prior['purpose']!=purpose: raise DomainError(422,'evidence_purpose_invalid')
        if prior['prepared_for_actor_id']!=prepared_for: raise DomainError(422,'preparation_scope_invalid')
    row=tx.insert('evidence_versions',dict(item,predecessor_id=predecessor,uploaded_by=tx.context.actor_id,prepared_for_actor_id=prepared_for,purpose=purpose))
    tx.audit('evidence.upload',[('evidence_version_id',row['id'])])
    return [('evidence_version_id',row['id'])]


def link_evidence(tx,identity,owner_slot,owner_id,role,input_field=None):
    item=tx.get('evidence_versions',identity)
    # registry.identity_evidence checks the private recipient before calling us.
    # The assisting officer can attach that panel's identity original but cannot
    # read it; all ordinary attachments must be accessible before adding a link.
    helper_preparation=(tx.context.role=='barangay' and owner_slot=='household_version_id'
                        and role in {'identity_photo','identity_document'})
    if helper_preparation:
        owner=tx.get('household_versions',owner_id)
        if owner['assister_id']!=tx.context.actor_id or owner['declared_barangay_id']!=tx.context.barangay_id:
            raise DomainError(403,'private_evidence_scope_mismatch')
    else: authorize_evidence(tx.db,tx.context,identity)
    if item['purpose']!=role and not (role=='amended_source' and item['purpose']=='release_source'):
        raise DomainError(422,'evidence_purpose_invalid')
    original_bytes(item)
    tx.insert('evidence_links',{'evidence_version_id':identity,owner_slot:owner_id,'attachment_role':role,'input_field':input_field})
    return item
