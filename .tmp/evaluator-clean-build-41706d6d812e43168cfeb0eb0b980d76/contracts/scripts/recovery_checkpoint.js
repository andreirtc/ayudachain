// Read-only recovery guard. Lost chains and post-backup UNKNOWN records block restore.
const {localConfig}=require('./lib/local_config');
const {pinnedChain}=require('./lib/pinned_chain');
async function main(){
  let raw='';for await(const c of process.stdin)raw+=c;
  const req=JSON.parse(raw),cfg=localConfig(),out=[];
  for(const item of req.deployments){
    const {provider,contract}=await pinnedChain(cfg.rpc,item.manifest);
    const number=await provider.getBlockNumber(),block=await provider.getBlock(number);
    if(req.action==='check'){
      const saved=await provider.getBlock(Number(item.checkpoint.block_number));
      if(!saved||saved.hash!==item.checkpoint.block_hash)throw Error('chain checkpoint lost');
      const logs=await provider.getLogs({address:item.manifest.address,fromBlock:Number(item.checkpoint.block_number)+1,toBlock:number});
      const known=new Map((item.known||[]).map(r=>[r.public_id,r.content_hash]));
      for(const log of logs){
        const event=contract.interface.parseLog(log);
        if(event?.name==='RecordAnchored'){
          if(known.get(event.args.id)!==event.args.contentHash)throw Error('post-backup unknown record');
        }else if(item.manifest.protocol==='legacy.receipt.v1')throw Error('post-backup legacy write');
      }
    }
    out.push({deployment_id:item.deployment_id,block_number:String(number),block_hash:block.hash});
    provider.destroy();
  }
  console.log(JSON.stringify({checked:true,checkpoints:out}));
}
main().catch(()=>{console.log(JSON.stringify({checked:false,error:'deployment_lost_or_chain_progress_outside_backup'}));process.exitCode=1;});
