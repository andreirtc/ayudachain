"""Start only API/frontend for scoped UI checks; never deploy, migrate or reset."""
import json,os,socket,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.scripts.local_mvp import environment
from backend.app.config import ROOT
node,python=environment()
for port in [8000,3000]:
    with socket.socket() as sock:
        try:sock.bind(('127.0.0.1',port))
        except OSError:raise RuntimeError('Occupied service preserved')
owned={}
for name,args,cwd in [('api',[python,'-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000'],ROOT),
    ('frontend',[node,str(ROOT/'frontend/node_modules/next/dist/bin/next'),'dev','-p','3000','--hostname','127.0.0.1'],ROOT/'frontend')]:
    log=(ROOT/'.runtime'/('usability-'+name+'.log')).open('ab')
    process=subprocess.Popen(args,cwd=cwd,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    owned[name]=process.pid
(ROOT/'.runtime/usability-services.json').write_text(json.dumps(owned))
print('Started owned API/frontend only. No chain, migrations, resets or worker changes.')
