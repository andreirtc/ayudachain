// Independent read-only CLI: receives pinned manifest/ID on stdin, no signer.
const {localConfig}=require('./lib/local_config');
const {readRecord,DeploymentLost}=require('./lib/pinned_chain');
async function main() {
  let input='';for await(const c of process.stdin) input+=c;
  const cfg=localConfig(),req=JSON.parse(input);
  try {console.log(JSON.stringify({status:'read',record:await readRecord(cfg.rpc,req.manifest,req.public_id)}));}
  catch(e){console.log(JSON.stringify({status:e instanceof DeploymentLost?'deployment_lost':'chain_unreachable'}));}
}
main().catch(()=>{console.log(JSON.stringify({status:'chain_unreachable'}));process.exitCode=1;});
