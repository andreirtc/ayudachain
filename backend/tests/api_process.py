"""Owned actual API subprocess; never stops an existing development service."""
import os
import socket
import subprocess
import sys
import time
from uuid import uuid4
import httpx
from backend.app.config import ROOT


class ActualAPI:
    def __enter__(self):
        with socket.socket() as socket_:socket_.bind(('127.0.0.1',0));self.port=socket_.getsockname()[1]
        self.log=(ROOT/'.runtime'/('api-evaluation-'+uuid4().hex+'.log')).open('wb')
        self.client=httpx.Client(base_url=f'http://127.0.0.1:{self.port}/api/v1',timeout=30)
        try:self.start();return self
        except Exception:
            if self.process.poll() is None:self.process.terminate();self.process.wait(timeout=10)
            self.client.close();self.log.close();raise

    def start(self):
        env=os.environ.copy()
        executable=sys.executable
        if os.name=='nt':
            # Windows venv python is a redirector; launch its real interpreter
            # with the SAME locked environment to keep ownership of the API PID.
            executable=sys._base_executable
            env['PYTHONPATH']=os.pathsep.join([str(ROOT/'.venv/Lib/site-packages'),str(ROOT)])
        self.process=subprocess.Popen([executable,'-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port',str(self.port)],cwd=ROOT,env=env,stdout=self.log,stderr=self.log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            if self.process.poll() is not None:raise RuntimeError('Owned evaluation API failed to start; inspect its private runtime log')
            try:
                if self.client.get('/health').status_code==200:return
            except httpx.TransportError:pass
            time.sleep(.2)
        raise RuntimeError('Owned evaluation API startup timed out')

    def restart(self):
        self.process.terminate();self.process.wait(timeout=10);self.start()

    def __exit__(self,*args):
        self.process.terminate();self.process.wait(timeout=10);self.client.close();self.log.close()
