const fs=require('node:fs');
const path=require('node:path');
const ROOT=path.resolve(__dirname,'../../..');
function localConfig() {
  const file=path.join(ROOT,'.env.mvp');
  if(fs.existsSync(file)) for(const line of fs.readFileSync(file,'utf8').split(/\r?\n/)) {
    const n=line.indexOf('='); if(n>0&&!line.startsWith('#')) process.env[line.slice(0,n)]??=line.slice(n+1);
  }
  const rpc=process.env.MVP_RPC_URL||'http://127.0.0.1:8545';
  const url=new URL(rpc);
  if(url.protocol!=='http:' || !['127.0.0.1','localhost','[::1]'].includes(url.hostname)||url.username||url.password) throw Error('loopback RPC required');
  if(![22,24].includes(Number(process.versions.node.split('.')[0]))) throw Error('supported Node 22/24 required');
  return {rpc,root:ROOT,manifest:process.env.MVP_DEPLOYMENT_MANIFEST||path.join(ROOT,'.runtime/deployment.json')};
}
module.exports={localConfig,ROOT};
