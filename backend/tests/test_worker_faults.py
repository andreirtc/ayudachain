import os,json,subprocess,time,unittest
from uuid import uuid4
from backend.tests.support import Harness,fault_manifest_path
from backend.app.config import ROOT
from backend.app.commands import execute_command


class WorkerFaultTests(unittest.TestCase):
    def chain(self,source,request):
        run=subprocess.run([os.environ['MVP_NODE'],'-e',source],input=json.dumps(request),capture_output=True,text=True,cwd=ROOT/'contracts',timeout=30)
        self.assertEqual(run.returncode,0,'Actual isolated chain fault operation failed')
    def intent(self,h):
        from backend.app.services.commitments import document_commitment
        identity=h.upload('wage')
        def save(tx):
            proof=document_commitment(tx,tx.get('evidence_versions',identity));self.proof=proof['id'];return [('evidence_version_id',identity)]
        execute_command(h.actors['dswd'],'document.intent',str(uuid4()),{},save)

    def worker(self,fault=None):
        env=os.environ.copy();env['MVP_PRIVATE_KEY']='0x'+'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
        if fault:env['MVP_WORKER_FAULT']=fault
        return subprocess.run([env['MVP_NODE'],str(ROOT/'contracts/scripts/anchor_worker.js'),'--once'],env=env,capture_output=True,text=True,timeout=30)

    def test_real_out_of_gas_revert_is_retained_then_same_job_can_use_proven_next_nonce(self):
        with Harness() as h:
            h.register_chain();self.intent(h);self.worker('under_gas')
            with h.connection() as db:
                self.assertEqual(db.execute("SELECT count(*) n FROM anchor_observations WHERE verdict='mined_match'").fetchone()['n'],0)
            time.sleep(2.1);h.drain_anchors()
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM anchor_submissions').fetchone()['n'],2)
                self.assertGreaterEqual(db.execute("SELECT count(*) n FROM anchor_observations WHERE verdict='reverted'").fetchone()['n'],1)

    def test_kills_after_broadcast_and_after_mining_reconcile_same_signed_bytes(self):
        from backend.app.services.integrity import check_saved
        for fault in ['after_broadcast','after_mining']:
            with self.subTest(fault=fault),Harness() as h:
                h.register_chain();self.intent(h);self.assertNotEqual(self.worker(fault).returncode,0)
                time.sleep(2.1);h.drain_anchors()
                with h.connection() as db:
                    self.assertEqual(db.execute('SELECT count(*) n FROM anchor_submissions').fetchone()['n'],1)
                    proof=db.execute('SELECT * FROM commitments WHERE id=%s',(self.proof,)).fetchone();self.assertEqual(check_saved(db,proof)['result'],'match')

    def test_retired_namespace_never_broadcasts_pending_intent(self):
        with Harness() as h:
            h.register_chain();self.intent(h)
            def retire(tx):tx.db.execute("UPDATE evaluation_runs SET state='retired' WHERE id=%s",(h.run,));tx.audit('evaluation.retire',[('evaluation_run_id',h.run)]);return [('evaluation_run_id',h.run)]
            execute_command(h.actors['dswd'],'evaluation.retire','retire',{},retire)
            self.worker()
            with h.connection() as db:self.assertEqual(db.execute('SELECT count(*) n FROM anchor_submissions').fetchone()['n'],0)

    def test_unknown_nonce_consumption_never_signs_a_replacement(self):
        with Harness() as h:
            h.register_chain();self.intent(h);self.worker('after_prepare')
            with h.connection() as db:nonce=db.execute('SELECT nonce FROM anchor_submissions').fetchone()['nonce']
            script="const fs=require('fs'),{ethers}=require('ethers');(async()=>{const r=JSON.parse(fs.readFileSync(0,'utf8')),p=new ethers.JsonRpcProvider(process.env.MVP_RPC_URL),s=await p.getSigner(0);await(await s.sendTransaction({to:await s.getAddress(),value:0n,nonce:Number(r.nonce)})).wait();p.destroy();})().catch(()=>process.exit(1));"
            self.chain(script,{'nonce':str(nonce)});time.sleep(2.1);self.worker();time.sleep(2.1);self.worker()
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM anchor_submissions').fetchone()['n'],1)
                job=db.execute('SELECT state,last_error_code FROM anchor_jobs').fetchone();self.assertEqual(job['state'],'uncertain');self.assertEqual(job['last_error_code'],'unknown_nonce_consumption')

    def test_actual_conflicting_content_stops_without_a_signature(self):
        from backend.app.services.integrity import check_saved
        with Harness() as h:
            h.register_chain();self.intent(h)
            with h.connection() as db:proof=db.execute('SELECT * FROM commitments WHERE id=%s',(self.proof,)).fetchone()
            manifest=json.loads((fault_manifest_path()).read_text())
            script="const fs=require('fs'),{ethers}=require('ethers');(async()=>{const r=JSON.parse(fs.readFileSync(0,'utf8')),p=new ethers.JsonRpcProvider(process.env.MVP_RPC_URL),c=new ethers.Contract(r.m.address,r.m.abi,await p.getSigner(0));await(await c.anchorRecord(r.id,ethers.sha256(ethers.toUtf8Bytes('Invented conflicting source')),1,r.context,ethers.ZeroHash,ethers.ZeroHash)).wait();p.destroy();})().catch(()=>process.exit(1));"
            self.chain(script,{'m':manifest,'id':'0x'+proof['public_id'].hex(),'context':'0x'+proof['public_context'].hex()});self.worker()
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT state FROM anchor_jobs').fetchone()['state'],'conflict')
                self.assertEqual(db.execute('SELECT count(*) n FROM anchor_submissions').fetchone()['n'],0)
                self.assertEqual(check_saved(db,proof)['result'],'mismatch')
