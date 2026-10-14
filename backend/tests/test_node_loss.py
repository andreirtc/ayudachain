import os,json,socket,subprocess,time,unittest
from uuid import uuid4
import httpx
from backend.tests.support import Harness
from backend.app.config import ROOT

class NodeLossTests(unittest.TestCase):
    def test_same_address_reset_loses_old_deployment_without_replacement_signature(self):
        from backend.tests.test_worker_faults import WorkerFaultTests
        from backend.app.services.integrity import check_saved
        with Harness() as h:
            with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
            node=os.environ['MVP_NODE'];directory=ROOT/'.runtime/fault-nodes'/uuid4().hex;directory.mkdir(parents=True)
            log=(directory/'private-node.log').open('wb')
            process=subprocess.Popen([node,str(ROOT/'contracts/node_modules/hardhat/internal/cli/cli.js'),'node','--hostname','127.0.0.1','--port',str(port)],cwd=ROOT/'contracts',stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            os.environ['MVP_RPC_URL']=f'http://127.0.0.1:{port}';first=directory/'before.json';os.environ['MVP_DEPLOYMENT_MANIFEST']=str(first)
            try:
                for _ in range(100):
                    try:
                        if httpx.post(os.environ['MVP_RPC_URL'],json={'jsonrpc':'2.0','id':1,'method':'eth_chainId','params':[]}).json().get('result')=='0x7a69':break
                    except httpx.HTTPError:pass
                    time.sleep(.1)
                else:self.fail('Owned isolated fault node unavailable')
                def deploy():
                    run=subprocess.run([node,str(ROOT/'contracts/scripts/deploy_evidence.js')],capture_output=True,env=os.environ.copy(),timeout=30);self.assertEqual(run.returncode,0,'Actual owned deployment failed')
                deploy();h.register_chain();worker=WorkerFaultTests();worker.intent(h);h.drain_anchors()
                with h.connection() as db:old=db.execute('SELECT * FROM commitments WHERE id=%s',(worker.proof,)).fetchone()
                self.assertEqual(check_saved_for(h,old)['result'],'match')
                worker.intent(h);worker.worker('after_prepare')
                response=httpx.post(os.environ['MVP_RPC_URL'],json={'jsonrpc':'2.0','id':1,'method':'hardhat_reset','params':[]});self.assertNotIn('error',response.json())
                second=directory/'after.json';os.environ['MVP_DEPLOYMENT_MANIFEST']=str(second);deploy()
                self.assertEqual(json.loads(first.read_text())['address'],json.loads(second.read_text())['address'])
                self.assertNotEqual(json.loads(first.read_text())['deployment_uid'],json.loads(second.read_text())['deployment_uid'])
                os.environ['MVP_DEPLOYMENT_MANIFEST']=str(first);time.sleep(2.1);worker.worker()
                result=check_saved_for(h,old);self.assertEqual(result['result'],'chain_unreachable');self.assertEqual(result['deployment_state'],'lost')
                self.assertTrue(result['last_confirmed_observation']['historical'])
                with h.connection() as db:
                    self.assertEqual(db.execute("SELECT count(*) n FROM anchor_submissions").fetchone()['n'],2)
                    self.assertEqual(db.execute("SELECT state FROM anchor_jobs WHERE state!='confirmed'").fetchone()['state'],'deployment_lost')
                    self.assertEqual(db.execute('SELECT count(*) n FROM commitments').fetchone()['n'],2)
            finally:
                if process.poll() is None:process.terminate()
                process.wait(timeout=10);log.close()

def check_saved_for(h,proof):
    from backend.app.services.integrity import check_saved
    with h.connection() as db:return check_saved(db,proof)
