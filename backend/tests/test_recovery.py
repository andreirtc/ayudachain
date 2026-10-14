import importlib.util
import unittest
from pathlib import Path
from uuid import uuid4
from backend.tests.support import Harness


class RecoveryTests(unittest.TestCase):
    def test_restored_prepared_signature_reconciles_same_candidate_once(self):
        import json,os
        from backend.scripts.backup_mvp import backup,restore
        from backend.tests.test_worker_faults import WorkerFaultTests
        from backend.app.config import ROOT
        with Harness() as h:
            h.register_chain();worker=WorkerFaultTests();worker.intent(h);worker.worker('after_prepare')
            with h.connection() as db:original=db.execute('SELECT candidate_tx_hash,raw_signed_tx,nonce FROM anchor_submissions').fetchone()
            bundle=backup(ROOT/'.runtime/backups'/uuid4().hex)
            restored=restore(Path(bundle['directory']),'ayudachain_mvp_restore_'+uuid4().hex[:12]);config=json.loads(Path(restored['configuration']).read_text());saved={k:os.environ.get(k) for k in config}
            try:
                os.environ.update(config);h.drain_anchors()
                with h.connection() as db:
                    submissions=db.execute('SELECT candidate_tx_hash,raw_signed_tx,nonce FROM anchor_submissions').fetchall()
                    self.assertEqual(submissions,[original])
                    self.assertEqual(db.execute('SELECT state FROM anchor_jobs').fetchone()['state'],'confirmed')
                    self.assertEqual(db.execute('SELECT count(*) n FROM anchor_applications').fetchone()['n'],1)
            finally:
                for k,v in saved.items():
                    if v is None:os.environ.pop(k,None)
                    else:os.environ[k]=v
    def test_checked_database_originals_manifests_and_replay_key_restore_against_surviving_chain(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.scripts.backup_mvp'))
        from backend.scripts.backup_mvp import backup,restore
        from backend.app.config import ROOT
        from backend.app.services.evidence import storage_root
        from backend.app.commands import execute_command
        from backend.app.services.commitments import document_commitment
        with Harness() as h:
            h.register_chain();identity=h.upload('wage')
            def intent(tx):document_commitment(tx,tx.get('evidence_versions',identity));return [('evidence_version_id',identity)]
            execute_command(h.actors['dswd'],'document.intent','proof',{},intent);h.drain_anchors()
            bundle=backup(ROOT/'.runtime/backups'/uuid4().hex)
            self.assertEqual(bundle['status'],'complete')
            restored=restore(Path(bundle['directory']),'ayudachain_mvp_restore_'+uuid4().hex[:12])
            self.assertTrue(restored['checked']);self.assertEqual(restored['evidence_count'],1)
            import json,os
            from backend.tests.api_process import ActualAPI
            config=json.loads(Path(restored['configuration']).read_text())
            saved={k:os.environ.get(k) for k in config}
            try:
                os.environ.update(config)
                with ActualAPI() as api:
                    headers={'X-Demo-Actor-ID':str(h.actors['auditor'])}
                    response=api.client.get('/audit/proofs',headers=headers)
                    self.assertEqual(response.status_code,200,response.text)
                    proof=response.json()['data'][0]['id']
                    checked=api.client.post('/integrity/check',headers=headers,json={'commitment_id':proof})
                    self.assertEqual(checked.json()['data']['result'],'match')
                    self.assertEqual(api.client.get('/evidence/'+str(identity)+'/content',headers=headers).status_code,200)
                with h.connection() as db:
                    self.assertGreaterEqual(db.execute('SELECT count(*) n FROM command_results').fetchone()['n'],2)
                replay=execute_command(h.actors['dswd'],'document.intent','proof',{},lambda tx:self.fail('Restored replay executed the business handler'))
                self.assertTrue(replay['replayed'])
            finally:
                for k,v in saved.items():
                    if v is None:os.environ.pop(k,None)
                    else:os.environ[k]=v
            # Writes unknown to this coherent snapshot are refused at restoration.
            newer=h.upload('wage')
            def later(tx):document_commitment(tx,tx.get('evidence_versions',newer));return [('evidence_version_id',newer)]
            execute_command(h.actors['dswd'],'document.intent','new-after-backup',{},later);h.drain_anchors()
            with self.assertRaises(ValueError):restore(Path(bundle['directory']),'ayudachain_mvp_restore_'+uuid4().hex[:12])
            # A backup is never accepted after any byte is silently modified.
            file=Path(bundle['directory'])/'database.dump';raw=file.read_bytes()
            try:
                file.write_bytes(raw+b'changed')
                with self.assertRaises(ValueError):restore(Path(bundle['directory']),'ayudachain_mvp_restore_'+uuid4().hex[:12])
            finally:file.write_bytes(raw)
