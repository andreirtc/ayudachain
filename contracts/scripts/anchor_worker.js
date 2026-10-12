// Durable, real local submissions. No business locks, publication or cash writes.
const fs=require('node:fs');
const crypto=require('node:crypto');
const {Client}=require('pg');
const {ethers}=require('ethers');
const {localConfig}=require('./lib/local_config');
const {pinnedChain,readRecord,DeploymentLost}=require('./lib/pinned_chain');
const {contentHash}=require('./lib/evidence_protocol');
const ZERO=ethers.ZeroHash;
const hex=(b)=>b?'0x'+Buffer.from(b).toString('hex'):ZERO;
let db,scope,cfg;
async function insert(table,data) {
  const row={id:crypto.randomUUID(),run_id:scope.run_id,office_id:scope.office_id,created_by:scope.actor_id,identity_assurance:'system',...data};
  const keys=Object.keys(row);
  await db.query(`INSERT INTO ${table}(${keys.join(',')}) VALUES(${keys.map((_,i)=>'$'+(i+1)).join(',')})`,Object.values(row));
  return row;
}
async function event(job,submission,action,details={}) {
  return insert('anchor_submission_events',{job_id:job.id,submission_id:submission?.id||null,action,safe_details:{},observed_at:new Date(),...details});
}
async function observe(job,submission,verdict,receipt,records) {
  const observed=receipt?.hash?Buffer.from(receipt.hash.slice(2),'hex'):null;
  await insert('anchor_observations',{job_id:job.id,submission_id:submission?.id||null,verdict,observed_tx_hash:observed,
    receipt_json:receipt?{status:receipt.status,hash:receipt.hash,block_number:receipt.blockNumber.toString(),block_hash:receipt.blockHash,gas_used:receipt.gasUsed.toString(),to:receipt.to}:null,
    chain_record_json:records?JSON.stringify(records):null,checked_at:new Date()});
  await db.query('UPDATE anchor_jobs SET state=$1,lease_owner=NULL,lease_until=NULL WHERE id=$2',[verdict==='mined_match'?'mined_unapplied':verdict==='deployment_lost'?'deployment_lost':verdict==='conflict'?'conflict':'retry_wait',job.id]);
}
function matches(item,record) {
  const e=JSON.parse(item.canonical_bytes.toString());
  if(record.content_hash!==hex(item.content_hash)||record.kind!==String({document:1,amount_input:2,barangay_submission:3,system_fallback:4,approved_list:5,handover:6,outcome:7,fund_release:8,fund_reversal:9,fund_replacement:10}[item.kind])||record.context!==hex(item.public_context)) return false;
  if(record.predecessor!==(e.predecessor||ZERO)||record.related!==(e.payload.correction_public_id||hex(item.public_related)))return false;
  if(record.fund) return record.fund.root===item.expectedFundRoot&&record.fund.delta_centavos===e.payload.delta_centavos&&record.fund.disaster===e.context&&record.fund.correction_set===(e.payload.correction_public_id||ZERO);
  return true;
}
async function processJob(job) {
  scope=null;
  scope={run_id:job.run_id,office_id:job.office_id,actor_id:(await db.query("SELECT id FROM actors WHERE run_id=$1 AND role='system'",[job.run_id])).rows[0].id};
  const dep=(await db.query('SELECT * FROM deployments WHERE id=$1',[job.deployment_id])).rows[0];
  const [manifestPath,manifestHash]=dep.abi_reference.split('#sha256=');
  const manifestBytes=fs.readFileSync(manifestPath);
  if(!manifestHash||crypto.createHash('sha256').update(manifestBytes).digest('hex')!==manifestHash)throw new DeploymentLost('manifest changed');
  const manifest=JSON.parse(manifestBytes);
  for(const k of ['address','deployment_uid','genesis_hash','deploy_block_hash','runtime_code_hash']) if(manifest[k].toLowerCase()!==hex(dep[k]).toLowerCase()) throw new DeploymentLost('manifest changed');
  const {provider,contract}=await pinnedChain(cfg.rpc,manifest);
  const items=(await db.query('SELECT c.* FROM commitments c JOIN anchor_job_items i ON i.commitment_id=c.id WHERE i.job_id=$1 ORDER BY i.ordinal',[job.id])).rows;
  for(const item of items)if(item.kind.startsWith('fund_')){
    const root=(await db.query('SELECT public_id FROM commitments WHERE fund_entry_id=$1',[JSON.parse(item.canonical_bytes.toString()).payload.source_root_id])).rows[0];
    item.expectedFundRoot=hex(root?.public_id);
  }
  if(items.length!==(job.operation==='fund_correction'?2:1)) throw Error('invalid inventory');
  for(const item of items) if(contentHash(item.canonical_bytes)!==hex(item.content_hash)) {await observe(job,null,'conflict');return;}
  let submission=(await db.query('SELECT * FROM anchor_submissions WHERE job_id=$1 ORDER BY attempt_number DESC LIMIT 1',[job.id])).rows[0];
  let receipt=submission?await provider.getTransactionReceipt(hex(submission.candidate_tx_hash)):null;
  let records=await Promise.all(items.map(i=>readRecord(cfg.rpc,manifest,hex(i.public_id))));
  const present=records.map(r=>r.content_hash!==ZERO);
  if(present.some(Boolean)) {
    if(!present.every(Boolean)||!items.every((i,n)=>matches(i,records[n]))) {await observe(job,submission,'conflict');return;}
    if(!receipt) {
      const logs=await contract.queryFilter(contract.filters.RecordAnchored(hex(items[0].public_id)),Number(manifest.deploy_block_number));
      if(logs.length!==1) {await observe(job,submission,'conflict');return;}
      receipt=await provider.getTransactionReceipt(logs[0].transactionHash);
    }
    if(!receipt||receipt.status!==1||receipt.to.toLowerCase()!==manifest.address.toLowerCase()) {await observe(job,submission,'conflict');return;}
    await observe(job,submission,'mined_match',receipt,records);return;
  }
  if(receipt&&receipt.status===0) {
    await event(job,submission,'reverted',{receipt_status:0,observed_tx_hash:Buffer.from(receipt.hash.slice(2),'hex'),block_number:String(receipt.blockNumber),block_hash:Buffer.from(receipt.blockHash.slice(2),'hex')});
    await observe(job,submission,'reverted',receipt);submission=null;
  } else if(receipt) {await observe(job,submission,'conflict',receipt);return;}
  const privateKey=process.env.MVP_PRIVATE_KEY;
  if(!privateKey) throw Error('local signer not configured');
  const signer=new ethers.Wallet(privateKey,provider);
  if(signer.address.toLowerCase()!==manifest.operator.toLowerCase()) throw Error('operator mismatch');
  if(!submission) {
    const unresolved=(await db.query(`SELECT s.id FROM anchor_submissions s JOIN anchor_jobs j ON j.id=s.job_id
      WHERE s.signer_address=$1 AND j.id!=$2 AND j.state IN ('prepared','submitted','uncertain') LIMIT 1`,[Buffer.from(signer.address.slice(2),'hex'),job.id])).rows;
    if(unresolved.length) throw Error('unresolved signer nonce');
    let request;
    const envelope=JSON.parse(items[0].canonical_bytes.toString());
    if(job.operation==='anchor_record') request=await contract.anchorRecord.populateTransaction(hex(items[0].public_id),hex(items[0].content_hash),Number({document:1,amount_input:2,barangay_submission:3,system_fallback:4,approved_list:5,handover:6,outcome:7}[items[0].kind]),hex(items[0].public_context),envelope.predecessor||ZERO,hex(items[0].public_related));
    else if(job.operation==='fund_release') request=await contract.recordFundRelease.populateTransaction(hex(items[0].public_id),hex(items[0].public_context),BigInt(envelope.payload.delta_centavos),hex(items[0].content_hash));
    else request=await contract.recordFundCorrection.populateTransaction(envelope.payload.correction_public_id,envelope.predecessor,hex(items[0].public_id),hex(items[0].content_hash),hex(items[1].public_id),hex(items[1].content_hash),BigInt(JSON.parse(items[1].canonical_bytes.toString()).payload.delta_centavos));
    request.from=signer.address;request.chainId=31337n;request.nonce=await provider.getTransactionCount(signer.address,'pending');
    request.gasLimit=await provider.estimateGas(request);
    if(process.env.MVP_WORKER_FAULT==='under_gas'){
      if(new URL(cfg.rpc).port!=='8555'||!/^test_mvp_[a-f0-9]{32}$/.test(process.env.MVP_SCHEMA||''))throw Error('isolated fault evaluation only');
      request.gasLimit-=1000n; // actual EVM out-of-gas receipt; never a mocked result
    }
    const fees=await provider.getFeeData();request.maxFeePerGas=fees.maxFeePerGas;request.maxPriorityFeePerGas=fees.maxPriorityFeePerGas;request.type=2;
    const raw=await signer.signTransaction(request),candidate=ethers.keccak256(raw);
    const attempt=(await db.query('SELECT COALESCE(MAX(attempt_number),0)+1 n FROM anchor_submissions WHERE job_id=$1',[job.id])).rows[0].n;
    await db.query('BEGIN');
    submission=await insert('anchor_submissions',{job_id:job.id,attempt_number:attempt,signer_address:Buffer.from(signer.address.slice(2),'hex'),nonce:String(request.nonce),raw_signed_tx:Buffer.from(raw.slice(2),'hex'),candidate_tx_hash:Buffer.from(candidate.slice(2),'hex'),prepared_at:new Date()});
    await event(job,submission,'prepared');
    await db.query("UPDATE anchor_jobs SET state='prepared' WHERE id=$1",[job.id]);await db.query('COMMIT');
    if(process.env.MVP_WORKER_FAULT==='after_prepare') process.exit(86);
  }
  // Unknown nonce consumption is never answered with a new nonce/ID.
  const parsed=ethers.Transaction.from(hex(submission.raw_signed_tx));
  const minedNonce=await provider.getTransactionCount(parsed.from,'latest');
  if(minedNonce>Number(submission.nonce)) {
    await db.query("UPDATE anchor_jobs SET state='uncertain',last_error_code='unknown_nonce_consumption' WHERE id=$1",[job.id]);return;
  }
  let observed;
  try {observed=await provider.broadcastTransaction(hex(submission.raw_signed_tx));}
  catch(e) {
    receipt=await provider.getTransactionReceipt(hex(submission.candidate_tx_hash));
    if(!receipt) {await db.query("UPDATE anchor_jobs SET state='uncertain',last_error_code='broadcast_unacknowledged' WHERE id=$1",[job.id]);return;}
  }
  if(observed) {
    await event(job,submission,'broadcast',{observed_tx_hash:Buffer.from(observed.hash.slice(2),'hex')});
    await db.query("UPDATE anchor_jobs SET state='submitted' WHERE id=$1",[job.id]);
  }
  if(process.env.MVP_WORKER_FAULT==='after_broadcast') process.exit(87);
  if(!receipt){
    try{receipt=await observed.wait(1,12000);}
    catch(e){if(e.receipt?.status===0)receipt=e.receipt;else throw e;}
  }
  if(!receipt||receipt.status!==1) {await observe(job,submission,'reverted',receipt);return;}
  records=await Promise.all(items.map(i=>readRecord(cfg.rpc,manifest,hex(i.public_id))));
  if(!items.every((i,n)=>matches(i,records[n]))) {await observe(job,submission,'conflict',receipt,records);return;}
  if(process.env.MVP_WORKER_FAULT==='after_mining') process.exit(88);
  await observe(job,submission,'mined_match',receipt,records);
}
async function once() {
  const lock=(await db.query("SELECT pg_try_advisory_lock(hashtext('ayudachain-local-signer')) locked")).rows[0].locked;
  if(!lock) return false;
  let job;
  try {
    await db.query('BEGIN');
    job=(await db.query(`SELECT j.* FROM anchor_jobs j WHERE j.state IN ('pending','prepared','submitted','uncertain','retry_wait')
      AND EXISTS(SELECT 1 FROM evaluation_runs r WHERE r.id=j.run_id AND r.state='active')
      AND j.next_attempt_at<=clock_timestamp() AND (j.lease_until IS NULL OR j.lease_until<clock_timestamp())
      AND NOT EXISTS(SELECT 1 FROM anchor_dependencies d JOIN anchor_jobs p ON p.id=d.prerequisite_job_id WHERE d.job_id=j.id AND p.state!='confirmed')
      ORDER BY j.next_attempt_at,j.created_at,j.id FOR UPDATE SKIP LOCKED LIMIT 1`)).rows[0];
    if(job) await db.query("UPDATE anchor_jobs SET lease_owner=$1,lease_until=clock_timestamp()+interval '2 seconds' WHERE id=$2",[String(process.pid),job.id]);
    await db.query('COMMIT');
    if(!job) return false;
    try {await processJob(job);}
    catch(e) {
      try {await db.query('ROLLBACK');} catch {}
      if(e instanceof DeploymentLost) await observe(job,null,'deployment_lost');
      else {
        if(scope) await event(job,null,'retry',{error_code:/^[A-Z0-9_]{1,30}$/.test(e.code||'')?e.code:'rpc_or_worker_failure'});
        const retries=(await db.query("SELECT count(*) n FROM anchor_submission_events WHERE job_id=$1 AND action='retry'",[job.id])).rows[0].n;
        const delay=Math.min(60,2**Math.min(6,Number(retries)));
        await db.query("UPDATE anchor_jobs SET state=CASE WHEN state IN ('prepared','submitted','uncertain') THEN 'uncertain' ELSE 'retry_wait' END,last_error_code='rpc_or_worker_failure',next_attempt_at=clock_timestamp()+($2*interval '1 second') WHERE id=$1",[job.id,delay]);
      }
      console.error('Anchor work retained for recovery');
    }
    finally {await db.query('UPDATE anchor_jobs SET lease_owner=NULL,lease_until=NULL WHERE id=$1',[job.id]);}
    return true;
  } finally {await db.query("SELECT pg_advisory_unlock(hashtext('ayudachain-local-signer'))");}
}
async function main() {
  cfg=localConfig();
  const dsn=process.env.MVP_WORKER_DATABASE_URL;
  const url=new URL(dsn);
  if(!['127.0.0.1','localhost'].includes(url.hostname)||!['postgres:','postgresql:'].includes(url.protocol)) throw Error('local PostgreSQL required');
  db=new Client({connectionString:dsn});await db.connect();
  const schema=process.env.MVP_SCHEMA||'public';if(!/^[a-z][a-z0-9_]*$/.test(schema)) throw Error('invalid schema');
  await db.query(`SET search_path TO "${schema}",public`);await db.query('SET ROLE mvp_worker');
  if(process.argv.includes('--once')) {await once();await db.end();return;}
  while(true){await once();await new Promise(r=>setTimeout(r,2000));}
}
main().catch(async()=>{console.error('Worker unavailable; no business or chain success asserted');if(db) await db.end().catch(()=>{});process.exitCode=1;});
