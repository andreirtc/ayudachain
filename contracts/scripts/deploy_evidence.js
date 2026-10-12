// Explicit local-only deployment and generated-artifact provenance.
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {ethers}=require('ethers');
const {localConfig}=require('./lib/local_config');
async function main() {
  const cfg=localConfig();
  if(fs.existsSync(cfg.manifest)) throw Error('manifest exists: deliberate new namespace/path required; never overwrite history');
  const provider=new ethers.JsonRpcProvider(cfg.rpc,undefined,{cacheTimeout:-1});
  if((await provider.getNetwork()).chainId!==31337n) throw Error('local chain ID 31337 required');
  const artifact=JSON.parse(fs.readFileSync(path.join(__dirname,'../artifacts/contracts/AyudaChainEvidenceRegistry.sol/AyudaChainEvidenceRegistry.json')));
  const uid=ethers.hexlify(crypto.randomBytes(32));
  const signer=await provider.getSigner(0);
  const contract=await new ethers.ContractFactory(artifact.abi,artifact.bytecode,signer).deploy(uid);
  const receipt=await contract.deploymentTransaction().wait(1);
  const address=await contract.getAddress();
  const block=await provider.getBlock(receipt.blockNumber),genesis=await provider.getBlock(0);
  const abiText=JSON.stringify(artifact.abi);
  const manifest={protocol:'ayudachain.evidence.v1',chain_id:'31337',address,deployment_uid:uid,genesis_hash:genesis.hash,
    deploy_block_number:receipt.blockNumber.toString(),deploy_block_hash:block.hash,runtime_code_hash:ethers.keccak256(await provider.getCode(address)),
    abi:artifact.abi,abi_sha256:crypto.createHash('sha256').update(abiText).digest('hex'),confirmation_policy:'one_mined_block_local',
    observed_deploy_tx_hash:receipt.hash,operator:await signer.getAddress(),created_at:new Date().toISOString(),blockchain_simulated:false};
  fs.mkdirSync(path.dirname(cfg.manifest),{recursive:true});
  fs.writeFileSync(cfg.manifest,JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
  const generated=path.join(cfg.root,'shared/contracts/AyudaChainEvidenceRegistry.json');
  fs.mkdirSync(path.dirname(generated),{recursive:true});
  fs.writeFileSync(generated,JSON.stringify({contractName:artifact.contractName,abi:artifact.abi,protocol:manifest.protocol,generatedBy:'contracts/scripts/deploy_evidence.js'},null,2)+'\n');
  console.log('Generated actual local deployment manifest; gas units '+receipt.gasUsed.toString());
}
main().catch(()=>{console.error('Local deployment failed; inspect owned node/configuration. No synthetic success.');process.exitCode=1;});
