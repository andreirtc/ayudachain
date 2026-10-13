"""Run owned demo web services for local Wi-Fi; preserve database and chain."""
import json, os, socket, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.scripts.local_mvp import environment
from backend.app.config import ROOT

node, python = environment()
for port in (8000, 3000):
    with socket.socket() as sock:
        sock.bind(('0.0.0.0', port))
owned = {}
api_code = "from backend.app.main import app; from fastapi.middleware.cors import CORSMiddleware; import uvicorn; app.add_middleware(CORSMiddleware,allow_origins=['http://192.168.1.103:3000','http://127.0.0.1:3000','http://localhost:3000'],allow_methods=['GET','POST'],allow_headers=['Content-Type','X-Demo-Actor-ID','Idempotency-Key']); uvicorn.run(app,host='0.0.0.0',port=8000)"
for name, args, cwd in (
    ('api', [python, '-c', api_code], ROOT),
    ('frontend', [node, str(ROOT/'frontend/node_modules/next/dist/bin/next'), 'dev', '-p', '3000', '--hostname', '0.0.0.0'], ROOT/'frontend'),
):
    with (ROOT/'.runtime'/('usability-'+name+'.log')).open('ab') as log:
        process = subprocess.Popen(args, cwd=cwd, stdout=log, stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    owned[name] = process.pid
(ROOT/'.runtime/usability-services.json').write_text(json.dumps(owned))
print('Started owned LAN frontend and API. Database and chain preserved.')
