"""Own and supervise local evaluation processes; never take over occupied ports."""
import argparse,os,json,socket,subprocess,sys,time,signal
from uuid import uuid4
from pathlib import Path
from backend.app.config import ROOT,load_local_environment,validate_environment

def command(args,cwd=ROOT):
    r=subprocess.run(args,cwd=cwd,env=os.environ.copy(),capture_output=True,timeout=180)
    if r.returncode:raise RuntimeError('Local preparation failed; no successful deployment or migration inferred')

def environment():
    load_local_environment();validate_environment()
    node=Path(os.environ['MVP_NODE']);os.environ['PATH']=str(node.parent)+os.pathsep+os.environ['PATH']
    if os.name=='nt':os.environ['PYTHONPATH']=os.pathsep.join([str(ROOT/'.venv/Lib/site-packages'),str(ROOT)])
    return str(node),sys._base_executable if os.name=='nt' else sys.executable

def available(port):
    with socket.socket() as s:
        try:s.bind(('127.0.0.1',port));return True
        except OSError:return False

def stop_owned(owned):
    """Terminate only Popen-owned trees, including Next's Windows descendants."""
    for _,p,*_ in reversed(owned):
        if p.poll() is not None:continue
        if os.name=='nt':
            result=subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True,timeout=15)
            if result.returncode and p.poll() is None:raise RuntimeError('Owned process tree could not be stopped')
        else:
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
    for _,p,*_ in owned:
        try:p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            if os.name=='nt':p.kill()
            else:
                try:os.killpg(p.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            p.wait(timeout=5)

def prepare():
    node,python=environment()
    command([node,str(ROOT/'contracts/scripts/check_deployment.js')])
    command([python,'-m','backend.scripts.setup_mvp'])
    command([python,'-m','backend.scripts.seed_mvp'])
    print('Migrated PostgreSQL and preserved/idempotently seeded reference records; pinned local deployment checked',flush=True)

def serve(with_chain=False):
    node,python=environment();owned=[];logs=[]
    token=uuid4().hex
    for port in [3000,8000]+([8545] if with_chain else []):
        if not available(port):raise RuntimeError('Required local port occupied; existing process preserved')
    private=ROOT/'.runtime/supervised';private.mkdir(parents=True,exist_ok=True)
    def record(state):
        (private/'owner.json').write_text(json.dumps({'state':state,'owner_token':token,'supervisor':os.getpid(),'root':str(ROOT),'children':{n:p.pid for n,p,*_ in owned}}))
    def start(name,args,cwd=ROOT,env=None):
        log=(private/(name+'.log')).open('ab');logs.append(log)
        p=subprocess.Popen(args,cwd=cwd,env=env or os.environ.copy(),stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0,start_new_session=os.name!='nt')
        owned.append((name,p,args,cwd,env));return p
    try:
        if with_chain:
            start('chain',[node,str(ROOT/'contracts/node_modules/hardhat/internal/cli/cli.js'),'node','--hostname','127.0.0.1'],ROOT/'contracts')
            import httpx
            for _ in range(100):
                try:
                    if httpx.post('http://127.0.0.1:8545',json={'jsonrpc':'2.0','id':1,'method':'eth_chainId','params':[]}).json()['result']=='0x7a69':break
                except (httpx.HTTPError,ValueError,KeyError):pass
                time.sleep(.2)
            else:raise RuntimeError('Owned local node did not become available')
        manifest=Path(os.environ.get('MVP_DEPLOYMENT_MANIFEST',str(ROOT/'.runtime/deployment.json')))
        if not manifest.exists():
            command([node,str(ROOT/'contracts/node_modules/hardhat/internal/cli/cli.js'),'compile'],ROOT/'contracts')
            command([node,str(ROOT/'contracts/scripts/deploy_evidence.js')])
        prepare()
        env=os.environ.copy()
        # Public Hardhat development key is permitted only with loopback chain ID
        # and an operator-pinned deployment. Never send it to a public network.
        env.setdefault('MVP_PRIVATE_KEY','0x'+'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')
        start('api',[python,'-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000'])
        start('scheduler',[python,'-m','backend.app.scheduler'])
        start('worker',[node,str(ROOT/'contracts/scripts/anchor_worker.js')],env=env)
        start('frontend',[node,str(ROOT/'frontend/node_modules/next/dist/bin/next'),'dev','--hostname','127.0.0.1','--port','3000'],ROOT/'frontend')
        record('running')
        print('Local synthetic MVP: http://127.0.0.1:3000/mvp ; stop with Ctrl+C. Worker and scheduler recover durable work.',flush=True)
        while True:
            time.sleep(2)
            try:
                if json.loads((private/'stop-request.json').read_text()).get('owner_token')==token:break
            except (OSError,ValueError):pass
            for index,(name,p,args,cwd,child_env) in enumerate(list(owned)):
                if p.poll() is not None:
                    if name=='chain':raise RuntimeError('Owned chain stopped; preserve deployment history and restart explicitly')
                    log=(private/(name+'.log')).open('ab');logs.append(log)
                    replacement=subprocess.Popen(args,cwd=cwd,env=child_env or os.environ.copy(),stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0,start_new_session=os.name!='nt')
                    owned[index]=(name,replacement,args,cwd,child_env)
                    record('running')
                    print(name+' restarted; persisted records retained',flush=True)
    except KeyboardInterrupt:print('Stopping owned local evaluation processes',flush=True)
    finally:
        stop_owned(owned)
        for log in logs:log.close()
        record('stopped')

def stop():
    private=ROOT/'.runtime/supervised';owner=json.loads((private/'owner.json').read_text())
    if Path(owner['root']).resolve()!=ROOT or not owner.get('owner_token'):raise ValueError('Owned supervisor handshake unavailable; existing processes preserved')
    if owner.get('state')=='stopped':print('Owned supervisor is stopped');return
    (private/'stop-request.json').write_text(json.dumps({'owner_token':owner['owner_token']}))
    for _ in range(100):
        state=json.loads((private/'owner.json').read_text())
        if state.get('owner_token')==owner['owner_token'] and state.get('state')=='stopped':print('Owned evaluation processes stopped; records retained');return
        time.sleep(.2)
    raise ValueError('Owned supervisor stop could not be confirmed; no unrelated process was terminated')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','serve','stop']);parser.add_argument('--with-chain',action='store_true');args=parser.parse_args()
    try:
        if args.action=='prepare':prepare()
        elif args.action=='stop':stop()
        else:serve(args.with_chain)
    except (ValueError,RuntimeError,subprocess.SubprocessError):print('Local setup/service unavailable. Inspect ignored runtime logs and keep existing history.',file=sys.stderr);sys.exit(1)
