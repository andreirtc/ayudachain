// Authorized independent verification: exact private material + original paths on stdin.
// No database, wallet, signing key, replay, retry or business-write dependency.
const fs=require('node:fs');
const crypto=require('node:crypto');
const {canonicalBytes,contentHash}=require('./lib/evidence_protocol');
const {readRecord,DeploymentLost}=require('./lib/pinned_chain');
const {localConfig}=require('./lib/local_config');
const ZERO='0x'+'00'.repeat(32);
const kinds={document:1,amount_input:2,barangay_submission:3,system_fallback:4,approved_list:5,handover:6,outcome:7,fund_release:8,fund_reversal:9,fund_replacement:10};
async function verify(input){
  let e,local;
  try{
    const bytes=Buffer.from(input.canonical_utf8,'utf8');e=JSON.parse(input.canonical_utf8);
    if(!canonicalBytes(e).equals(bytes)||e.protocol!=='ayudachain.evidence.v1')return {result:'evidence_unavailable'};
    local=contentHash(bytes);
    for(const d of e.evidence){
      const file=(input.originals||[]).find(f=>f.id===d.id);if(!file)return {result:'evidence_unavailable'};
      const raw=fs.readFileSync(file.path);
      if(String(raw.length)!==d.byte_length||'0x'+crypto.createHash('sha256').update(raw).digest('hex')!==d.byte_sha256)return {result:'mismatch'};
    }
  }catch{return {result:'evidence_unavailable'};}
  try{
    const cfg=localConfig(),r=await readRecord(cfg.rpc,input.deployment,e.public_id);
    if(r.content_hash===ZERO)return {result:'required_anchor_absent'};
    let match=r.content_hash===local&&local===input.content_hash&&r.kind===String(kinds[e.kind])&&r.context===e.context&&r.predecessor===(e.predecessor||ZERO)&&r.related===(e.payload.correction_public_id||e.related||ZERO);
    if(r.fund){
      let root=e.public_id;
      if(e.predecessor){const prior=await readRecord(cfg.rpc,input.deployment,e.predecessor);root=prior.fund?.root;}
      match=match&&r.fund.root===root&&r.fund.delta_centavos===e.payload.delta_centavos&&r.fund.disaster===e.context&&r.fund.correction_set===(e.payload.correction_public_id||ZERO);
    }
    return {result:match?'match':'mismatch',local_hash:local,onchain_hash:r.content_hash,block_number:r.block_number,block_hash:r.block_hash,historical:false};
  }catch(e){return {result:'chain_unreachable',deployment_state:e instanceof DeploymentLost?'lost':'unknown',historical:false};}
}
async function main(){let input='';for await(const c of process.stdin)input+=c;console.log(JSON.stringify(await verify(JSON.parse(input))));}
if(require.main===module)main().catch(()=>{console.log(JSON.stringify({result:'evidence_unavailable'}));process.exitCode=1;});
module.exports={verify};
