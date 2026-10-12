"""ayudachain.evidence.v1 restricted JSON; legacy receipt protocol is separate."""
import hashlib
import json
import re
import unicodedata

PROTOCOL='ayudachain.evidence.v1'
DOMAIN=b'AYUDACHAIN-EVIDENCE-v1\n'
KINDS={'document':1,'amount_input':2,'barangay_submission':3,'system_fallback':4,'approved_list':5,'handover':6,'outcome':7,'fund_release':8,'fund_reversal':9,'fund_replacement':10}
FORBIDDEN={'pin','code','payout_code','salt','digest','credential_digest','raw_signed_tx','signing_key','private_key'}


def normalize(value):
    if value is None or isinstance(value,bool): return value
    if isinstance(value,str):
        if any(0xd800<=ord(c)<=0xdfff for c in value): raise ValueError('Surrogate in protocol text')
        return unicodedata.normalize('NFC',value)
    if isinstance(value,list): return [normalize(v) for v in value]
    if isinstance(value,dict):
        result={}
        for k,v in value.items():
            if not isinstance(k,str) or not re.fullmatch('[a-z][a-z0-9_]*',k): raise ValueError('ASCII snake_case key required')
            if k in FORBIDDEN: raise ValueError('Secret material excluded from evidence')
            result[k]=normalize(v)
        return result
    raise ValueError('Numeric and non-JSON values excluded from protocol')


def canonical_bytes(value):
    return json.dumps(normalize(value),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')


def parse_canonical(raw):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result: raise ValueError('Duplicate protocol key')
            result[k]=v
        return result
    result=json.loads(raw,object_pairs_hook=pairs)
    if canonical_bytes(result)!=raw: raise ValueError('Noncanonical saved material')
    return result


def content_hash(raw):
    parse_canonical(raw)
    return hashlib.sha256(DOMAIN+raw).digest()
