"""Compute vectors once; independent Node implementation checks every saved byte."""
import json
from backend.app.services.evidence_protocol import canonical_bytes,content_hash,KINDS
from backend.app.config import ROOT


def vectors():
    results=[]
    for kind in KINDS:
        envelope={'protocol':'ayudachain.evidence.v1','kind':kind,'public_id':'0x'+'11'*32,
            'owner':'00000000-0000-4000-8000-000000000001','context':'0x'+'22'*32,'predecessor':None,'related':None,
            'effective_at':'2026-10-10T00:00:00.000Z','actor':{'display_name':'Invented José\nSilong','position':None,'identity_assurance':'claimed_unverified'},
            'evidence':[{'byte_sha256':'0x'+'33'*32,'byte_length':'123','mime_type':'application/pdf'}],
            'payload':{'amount_centavos':'9000000000000000000','answer':'received_less' if kind=='outcome' else None},'private_nonce':'0x'+'44'*32}
        raw=canonical_bytes(envelope)
        results.append({'name':kind,'input':envelope,'canonical_utf8':raw.decode(),'sha256':'0x'+content_hash(raw).hex()})
    return results


if __name__=='__main__':
    path=ROOT/'shared/protocol/evidence-v1-vectors.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(vectors(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
