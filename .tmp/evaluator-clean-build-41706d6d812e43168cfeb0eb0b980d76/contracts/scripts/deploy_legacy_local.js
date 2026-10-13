// Explicit compatibility evaluation. Does not overwrite legacy generated artifacts.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {ethers}=require('ethers');
const {localConfig}=require('./lib/local_config');
async function main(){
  const cfg=localConfig(),target=path.resolve(process.argv[2]||'');
  if(!target.startsWith(path.join(cfg.root,'.runtime')+path.sep)||fs.existsSync(target))throw Error('new owned manifest path required');
  const provider=new ethers.JsonRpcProvider(cfg.rpc),network=await provider.getNetwork();
  if(network.chainId!==31337n)throw Error('local chain only');
  const artifact=JSON.parse(fs.readFileSync(path.join(cfg.root,'contracts/artifacts/contracts/AyudaChainRegistry.sol/AyudaChainRegistry.json')));
  const signer=await provider.getSigner(0),contract=await new ethers.ContractFactory(artifact.abi,artifact.bytecode,signer).deploy();
  const receipt=await contract.deploymentTransaction().wait(),address=await contract.getAddress(),genesis=await provider.getBlock(0);
  const manifest={protocol:'legacy.receipt.v1',chain_id:'31337',address,deployment_uid:null,genesis_hash:genesis.hash,deploy_block_number:String(receipt.blockNumber),deploy_block_hash:receipt.blockHash,runtime_code_hash:ethers.keccak256(await provider.getCode(address)),abi:artifact.abi,abi_sha256:crypto.createHash('sha256').update(JSON.stringify(artifact.abi)).digest('hex'),confirmation_policy:'one actual successful local receipt and pinned getter read'};
  fs.writeFileSync(target,JSON.stringify(manifest,null,2),{flag:'wx'});
  console.log(JSON.stringify({status:'deployed',address,block_number:manifest.deploy_block_number,manifest:target}));
}
main().catch(()=>{console.log(JSON.stringify({status:'local_deployment_failed'}));process.exitCode=1;});
