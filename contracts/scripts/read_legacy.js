// Signer-free reader for an explicitly pinned ORIGINAL legacy deployment.
const {ethers}=require('ethers');
const {localConfig}=require('./lib/local_config');
const {pinnedChain,DeploymentLost}=require('./lib/pinned_chain');
async function main(){
  let input='';for await(const chunk of process.stdin)input+=chunk;
  const req=JSON.parse(input),cfg=localConfig();
  if(req.manifest.protocol!=='legacy.receipt.v1')throw new Error('legacy protocol required');
  try{
    const {provider,contract}=await pinnedChain(cfg.rpc,req.manifest);
    const number=await provider.getBlockNumber(),block=await provider.getBlock(number);
    const id=/^0x[0-9a-fA-F]{64}$/.test(req.distribution_id)?req.distribution_id:ethers.encodeBytes32String(req.distribution_id.slice(0,31));
    const r=await contract.distributions(id,{blockTag:number});
    console.log(JSON.stringify({status:'read',record:{receipt_hash:r.receiptHash,exists:r.exists,block_number:String(number),block_hash:block.hash}}));
  }catch(e){console.log(JSON.stringify({status:e instanceof DeploymentLost?'deployment_lost':'chain_unreachable'}));}
}
main().catch(()=>{console.log(JSON.stringify({status:'chain_unreachable'}));process.exitCode=1;});
