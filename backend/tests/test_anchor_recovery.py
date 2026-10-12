import importlib.util
import json
import os
import subprocess
import unittest
from pathlib import Path
from uuid import uuid4
from backend.tests.support import Harness,fault_manifest_path
from backend.app.config import ROOT
from backend.app.commands import execute_command


class ActualAnchorTests(unittest.TestCase):
    def test_actual_submission_restart_reconcile_and_independent_read(self):
        self.assertTrue((ROOT/'contracts/scripts/anchor_worker.js').exists(),'Durable signed-byte worker missing')
        from backend.scripts.register_deployment import register
        from backend.app.services.commitments import freeze_commitment
        from backend.app.services.integrity import check_saved
        with Harness() as h:
            os.environ['MVP_RPC_URL']='http://127.0.0.1:8555'
            os.environ['MVP_DEPLOYMENT_MANIFEST']=str(fault_manifest_path())
            with h.connection() as db:
                from backend.app.actor import resolve_identity
                from backend.app.commands import Transaction
                tx=Transaction(db,resolve_identity(db,h.actors['system'],system=True),uuid4())
                register(tx,fault_manifest_path())
            captured={}
            def action(tx):
                # Actual byte-backed input document, not a ready-made business success.
                from backend.app.services.evidence import prepare_upload,save_upload
                from backend.scripts.synthetic_evidence import synthetic_portrait
                refs=save_upload(tx,prepare_upload(synthetic_portrait(),'image/png'),'wage')
                item=tx.get('evidence_versions',refs[0][1])
                from backend.app.services.commitments import document_commitment
                captured['commitment']=document_commitment(tx,item)['id']
                return refs
            execute_command(h.actors['dswd'],'upload-proof',str(uuid4()),{},action)
            env=os.environ.copy();env['MVP_WORKER_DATABASE_URL']=env['MVP_TEST_DATABASE_URL'];env['MVP_DEPLOYMENT_MANIFEST']=str(fault_manifest_path());env['MVP_RPC_URL']='http://127.0.0.1:8555'
            # Public local Hardhat development key stays in the subprocess environment.
            env['MVP_PRIVATE_KEY']='0x'+'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
            def worker(fault=None):
                e=env.copy()
                if fault: e['MVP_WORKER_FAULT']=fault
                return subprocess.run([env['MVP_NODE'],str(ROOT/'contracts/scripts/anchor_worker.js'),'--once'],env=e,capture_output=True,text=True,timeout=30)
            self.assertNotEqual(worker('after_prepare').returncode,0)
            import time
            time.sleep(2.1) # let the actual crashed worker lease expire
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) FROM anchor_submissions').fetchone()['count'],1)
                commitment=db.execute('SELECT * FROM commitments WHERE id=%s',(captured['commitment'],)).fetchone()
                self.assertEqual(check_saved(db,commitment)['result'],'required_anchor_absent')
            self.assertEqual(worker().returncode,0)
            self.assertEqual(worker().returncode,0)
            with h.connection() as db:
                commitment=db.execute('SELECT * FROM commitments WHERE id=%s',(captured['commitment'],)).fetchone()
                self.assertEqual(check_saved(db,commitment)['result'],'match')
                self.assertEqual(db.execute('SELECT count(*) FROM anchor_submissions').fetchone()['count'],1)
                events=db.execute("SELECT * FROM anchor_observations WHERE verdict='mined_match'").fetchall()
                self.assertGreaterEqual(len(events),1)
                self.assertTrue(events[0]['observed_tx_hash'])
                observation=events[0]['id']
            from backend.app.services.anchors import apply_observation
            self.assertTrue(apply_observation(observation))
            self.assertTrue(apply_observation(observation))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM anchor_applications').fetchone()['n'],1)
                self.assertEqual(db.execute("SELECT count(*) n FROM audit_events WHERE action='anchor.confirm'").fetchone()['n'],1)


if __name__=='__main__': unittest.main()
