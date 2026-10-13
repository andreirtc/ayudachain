"""Frozen legacy snapshots; they never create MVP eligibility or cash records."""
import hashlib
import json
import os
import sqlite3
import subprocess
from contextlib import closing
from pathlib import Path
from datetime import datetime,timezone
from ..config import ROOT
from ..commands import DomainError
from ..actor import require_role
from .hasher import compute_receipt_hash
from .integrity import manifest_for

TABLES=('relief_batches','allocations','beneficiaries','distributions','audit_events')


def import_snapshot(tx,source,*,deployment_id=None):
    require_role(tx.context,'dswd')
    path=Path(source).resolve()
    if not path.is_file():raise DomainError(404,'legacy_source_unavailable')
    snapshots=ROOT/'.runtime/legacy_snapshots';snapshots.mkdir(parents=True,exist_ok=True)
    temporary=snapshots/(os.urandom(16).hex()+'.sqlite')
    # SQLite backup reads a coherent snapshot, including a surviving WAL.
    with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as old,closing(sqlite3.connect(temporary)) as frozen:old.backup(frozen)
    raw=temporary.read_bytes();digest=hashlib.sha256(raw).digest()
    target=snapshots/(digest.hex()+'.sqlite')
    if not target.exists():temporary.rename(target)
    # Temporary copies are kept inside the ignored snapshot directory; no source reset.
    if deployment_id:
        deployment=tx.get('deployments',deployment_id)
        if deployment['protocol']!='legacy.receipt.v1':raise DomainError(422,'legacy_protocol_required')
    counts={}
    with closing(sqlite3.connect(target.as_uri()+'?mode=ro&immutable=1',uri=True)) as frozen:
        frozen.row_factory=sqlite3.Row
        existing={r[0] for r in frozen.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for name in TABLES:
            counts[name]=0
            if name not in existing:continue
            for ordinal,row in enumerate(frozen.execute('SELECT * FROM '+name)):
                fields=dict(row);key=str(fields.get('id',ordinal))
                if tx.db.execute('SELECT 1 FROM legacy_records WHERE run_id=%s AND source_db_sha256=%s AND source_table=%s AND source_key=%s',(tx.context.run_id,digest,name,key)).fetchone():continue
                original=fields.get('receipt_hash');hashed=None
                if isinstance(original,str) and original.startswith('0x') and len(original)==66:
                    try:hashed=bytes.fromhex(original[2:])
                    except ValueError:pass
                tx.insert('legacy_records',{'source_db_sha256':digest,'source_table':name,'source_key':key,'original_fields':fields,'original_receipt_hash':hashed,'deployment_id':deployment_id,'imported_at':datetime.now(timezone.utc)})
                counts[name]+=1
    if any(counts.values()):tx.audit('legacy.import',[('evaluation_run_id',tx.context.run_id)],'Exact frozen synthetic legacy snapshot',details={'source_db_sha256':digest.hex(),'counts':counts})
    return [('evaluation_run_id',tx.context.run_id)]


def check(record,deployment):
    base={'protocol':'legacy.receipt.v1','coverage':'Original normalized receipt text and distribution fields only; raw receipt files and MVP business records are outside this legacy protocol.','historical_transaction_reference':'untrusted stored string; never an observed transaction'}
    fields=record['original_fields']
    needed={'distribution_id','beneficiary_id','batch_id','amount','ocr_text','verification_method'}
    if record['source_table']!='distributions' or not needed.issubset(fields) or not deployment:return dict(base,result='evidence_unavailable',historical=False)
    try:
        local=compute_receipt_hash(*(fields[k] for k in ['distribution_id','beneficiary_id','batch_id','amount','ocr_text','verification_method']))
        manifest=manifest_for(deployment)
        req={'manifest':manifest,'distribution_id':fields['distribution_id']}
        run=subprocess.run([os.environ.get('MVP_NODE','node'),str(ROOT/'contracts/scripts/read_legacy.js')],input=json.dumps(req),capture_output=True,text=True,timeout=12,cwd=ROOT)
        read=json.loads(run.stdout)
    except DomainError:return dict(base,result='evidence_unavailable',historical=False)
    except (ValueError,TypeError,KeyError,OSError,subprocess.SubprocessError):return dict(base,result='chain_unreachable',historical=False)
    if read['status']!='read':return dict(base,result='chain_unreachable',deployment_state='lost' if read['status']=='deployment_lost' else 'unknown',historical=False)
    chain=read['record']
    verdict='required_anchor_absent' if not chain['exists'] else 'match' if chain['receipt_hash']==local else 'mismatch'
    return dict(base,result=verdict,local_hash=local,onchain_hash=chain['receipt_hash'],block_number=chain['block_number'],block_hash=chain['block_hash'],historical=False)
