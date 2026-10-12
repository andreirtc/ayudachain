const fs=require('node:fs');
const {localConfig}=require('./lib/local_config');
const {pinnedChain}=require('./lib/pinned_chain');
(async()=>{const cfg=localConfig(),manifest=JSON.parse(fs.readFileSync(cfg.manifest));
 const {provider}=await pinnedChain(cfg.rpc,manifest);provider.destroy();
 console.log(JSON.stringify({status:'pinned_deployment_present',blockchain_simulated:false}));
})().catch(()=>{console.error('Pinned deployment unavailable. Preserve history and use an explicit new namespace after deployment loss.');process.exit(1);});
