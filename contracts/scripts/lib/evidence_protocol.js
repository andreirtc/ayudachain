const { createHash } = require('node:crypto');
const forbidden=new Set(['pin','code','payout_code','salt','digest','credential_digest','raw_signed_tx','signing_key','private_key']);
function normalize(value) {
  if (value===null || typeof value==='boolean') return value;
  if (typeof value==='string') {
    for(let i=0;i<value.length;i++) {
      const c=value.charCodeAt(i);
      if(c>=0xd800 && c<=0xdbff) { const next=value.charCodeAt(++i); if(!(next>=0xdc00&&next<=0xdfff)) throw Error('surrogate'); }
      else if(c>=0xdc00 && c<=0xdfff) throw Error('surrogate');
    }
    return value.normalize('NFC');
  }
  if(Array.isArray(value)) return value.map(normalize);
  if(typeof value==='object' && Object.getPrototypeOf(value)===Object.prototype) {
    const result={};
    for(const key of Object.keys(value).sort()) {
      if(!/^[a-z][a-z0-9_]*$/.test(key) || forbidden.has(key)) throw Error('protocol key');
      result[key]=normalize(value[key]);
    }
    return result;
  }
  throw Error('numeric/non-JSON protocol value');
}
function canonicalBytes(value) {return Buffer.from(JSON.stringify(normalize(value)),'utf8');}
function contentHash(bytes) {return '0x'+createHash('sha256').update('AYUDACHAIN-EVIDENCE-v1\n','ascii').update(bytes).digest('hex');}
module.exports={canonicalBytes,contentHash};
