const fs=require('node:fs');
const crypto=require('node:crypto');
const {ethers}=require('ethers');
class DeploymentLost extends Error {}
async function pinnedChain(rpc,manifest) {
  const provider=new ethers.JsonRpcProvider(rpc,undefined,{cacheTimeout:-1});
  const block=await provider.getBlock(Number(manifest.deploy_block_number));
  const genesis=await provider.getBlock(0);
  const code=await provider.getCode(manifest.address);
  const abiHash=crypto.createHash('sha256').update(JSON.stringify(manifest.abi)).digest('hex');
  if((await provider.getNetwork()).chainId.toString()!==manifest.chain_id || !block||block.hash!==manifest.deploy_block_hash||genesis.hash!==manifest.genesis_hash||code==='0x'||ethers.keccak256(code)!==manifest.runtime_code_hash||abiHash!==manifest.abi_sha256) throw new DeploymentLost('pinned deployment lost');
  const contract=new ethers.Contract(manifest.address,manifest.abi,provider);
  if(manifest.protocol!=='legacy.receipt.v1' && await contract.deploymentUid()!==manifest.deployment_uid) throw new DeploymentLost('UID changed');
  return {provider,contract};
}
async function readRecord(rpc,manifest,id) {
  const {provider,contract}=await pinnedChain(rpc,manifest);
  const blockNumber=await provider.getBlockNumber();
  const block=await provider.getBlock(blockNumber);
  const record=await contract.records(id,{blockTag:blockNumber});
  const fund=record.kind>=8n ? await contract.funds(id,{blockTag:blockNumber}):null;
  return {content_hash:record.contentHash,kind:record.kind.toString(),context:record.context,predecessor:record.predecessor,related:record.related,timestamp:record.timestamp.toString(),block_number:blockNumber.toString(),block_hash:block.hash,
    fund:fund?{delta_centavos:fund.deltaCentavos.toString(),disaster:fund.disaster,root:fund.root,correction_set:fund.correctionSet}:null};
}
module.exports={pinnedChain,readRecord,DeploymentLost};
