import json
import hashlib
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from ..config import ROOT,load_local_environment
from .commitments import hex32
from .evidence_protocol import content_hash,parse_canonical,KINDS
from .evidence import original_bytes
from ..commands import DomainError


def read_public(manifest,public_id):
    load_local_environment()
    try:
        run=subprocess.run([os.environ.get('MVP_NODE','node'),str(ROOT/'contracts/scripts/read_chain.js')],input=json.dumps({'manifest':manifest,'public_id':hex32(public_id)}),text=True,capture_output=True,cwd=ROOT,timeout=12)
        return json.loads(run.stdout)
    except (OSError,subprocess.SubprocessError,ValueError): return {'status':'chain_unreachable'}


def manifest_for(deployment):
    try:
        path,expected=deployment['abi_reference'].rsplit('#sha256=',1)
        raw=Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('manifest changed')
        manifest=json.loads(raw)
        for key in ['address','deployment_uid','genesis_hash','deploy_block_hash','runtime_code_hash']:
            if key=='deployment_uid' and deployment[key] is None:
                if manifest.get(key) is not None:raise ValueError('manifest changed')
            elif bytes.fromhex(manifest[key][2:])!=deployment[key]: raise ValueError('manifest changed')
        if str(deployment['chain_id'])!=manifest['chain_id'] or str(deployment['deploy_block_number'])!=str(manifest['deploy_block_number']): raise ValueError('manifest changed')
        return manifest
    except (OSError,ValueError,KeyError): raise DomainError(503,'evidence_unavailable') from None


def check_saved(db,commitment):
    def result(value):
        value['checked_at']=datetime.now(timezone.utc)
        value['commitment_id']=str(commitment['id'])
        value['kind']=commitment['kind']
        if value['result']!='match':
            prior=db.execute("SELECT o.observed_tx_hash,o.receipt_json,o.checked_at FROM anchor_observations o JOIN anchor_job_items i ON i.job_id=o.job_id WHERE i.commitment_id=%s AND o.verdict='mined_match' ORDER BY o.checked_at DESC LIMIT 1",(commitment['id'],)).fetchone()
            if prior:
                value['last_confirmed_observation']={'historical':True,'checked_at':prior['checked_at'],'observed_tx_hash':hex32(prior['observed_tx_hash']) if prior['observed_tx_hash'] else None,'receipt':prior['receipt_json']}
        return value
    try:
        raw=bytes(commitment['canonical_bytes'])
        envelope=parse_canonical(raw)
        local=content_hash(raw)
        for descriptor in envelope['evidence']:
            item=db.execute('SELECT * FROM evidence_versions WHERE id=%s',(descriptor['id'],)).fetchone()
            if not item: raise DomainError(503,'evidence_unavailable')
            original_bytes(item)
            if descriptor['byte_sha256']!=hex32(item['byte_sha256']) or descriptor['byte_length']!=str(item['byte_length']) or descriptor['mime_type']!=item['mime_type']: raise DomainError(409,'evidence_mismatch')
        deployment=db.execute('SELECT * FROM deployments WHERE id=%s',(commitment['deployment_id'],)).fetchone()
        manifest=manifest_for(deployment)
    except DomainError as e:
        return result({'result':'mismatch' if e.code=='evidence_mismatch' else 'evidence_unavailable','components':['canonical_bytes','raw_originals'],'historical':False})
    except (ValueError,TypeError,KeyError): return result({'result':'evidence_unavailable','historical':False})
    read=read_public(manifest,commitment['public_id'])
    if read['status']!='read': return result({'result':'chain_unreachable','deployment_state':'lost' if read['status']=='deployment_lost' else 'unknown','historical':False})
    record=read['record']
    if record['content_hash']=='0x'+'00'*32: verdict='required_anchor_absent'
    else:
        match=(record['content_hash']==hex32(local)==hex32(commitment['content_hash']) and record['kind']==str(KINDS[commitment['kind']]) and record['context']==hex32(commitment['public_context']))
        previous=db.execute('SELECT public_id FROM commitments WHERE id=%s',(commitment['predecessor_commitment_id'],)).fetchone() if commitment['predecessor_commitment_id'] else None
        expected_previous=hex32(previous['public_id']) if previous else '0x'+'00'*32
        expected_related=hex32(commitment['public_related']) if commitment['public_related'] else '0x'+'00'*32
        if commitment['kind'] in {'fund_reversal','fund_replacement'}:expected_related=envelope['payload']['correction_public_id']
        match=match and record['predecessor']==expected_previous and record['related']==expected_related
        match=match and (envelope['predecessor'] or '0x'+'00'*32)==expected_previous and envelope['context']==hex32(commitment['public_context'])
        if commitment['kind'] not in {'fund_reversal','fund_replacement'}:match=match and (envelope['related'] or '0x'+'00'*32)==expected_related
        if record['fund']:
            root=db.execute('SELECT public_id FROM commitments WHERE fund_entry_id=%s',(envelope['payload']['source_root_id'],)).fetchone()
            match=match and root is not None and record['fund']['root']==hex32(root['public_id']) and record['fund']['disaster']==hex32(commitment['public_context']) and record['fund']['delta_centavos']==envelope['payload']['delta_centavos'] and record['fund']['correction_set']==(envelope['payload'].get('correction_public_id') or '0x'+'00'*32)
        verdict='match' if match else 'mismatch'
    return result({'result':verdict,'components':['canonical_bytes','raw_originals','chain_record'], 'local_hash':hex32(local),'onchain_hash':record['content_hash'],
            'deployment_id':str(deployment['id']),'chain_id':manifest['chain_id'],'contract_address':manifest['address'],
            'public_id':hex32(commitment['public_id']),'block_number':record['block_number'],'block_hash':record['block_hash'],'historical':False})
