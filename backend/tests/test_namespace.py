import unittest
from uuid import uuid4
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError

class NamespaceTests(unittest.TestCase):
    def test_explicit_retirement_refuses_prepared_signature_then_allows_reconciled_history(self):
        from backend.scripts.namespace_mvp import retire
        from backend.tests.test_worker_faults import WorkerFaultTests
        with Harness() as h:
            h.register_chain()
            faults=WorkerFaultTests();faults.intent(h)
            self.assertNotEqual(faults.worker('after_prepare').returncode,0)
            with self.assertRaises(ValueError):retire(h.run)
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT state FROM evaluation_runs WHERE id=%s',(h.run,)).fetchone()['state'],'active')
                self.assertEqual(db.execute('SELECT count(*) n FROM anchor_submissions').fetchone()['n'],1)
            h.drain_anchors()
            self.assertTrue(retire(h.run))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT state FROM evaluation_runs WHERE id=%s',(h.run,)).fetchone()['state'],'retired')
                self.assertEqual(db.execute('SELECT count(*) n FROM anchor_submissions').fetchone()['n'],1)

    def test_retired_mined_observation_cannot_starve_current_application(self):
        import os,subprocess
        from backend.app.config import ROOT
        from backend.scripts.reset_mvp import reset
        from backend.app.services.commitments import document_commitment
        from backend.app.services.anchors import apply_due_observations
        with Harness() as h:
            h.register_chain()
            def intent(tx,file):
                proof=document_commitment(tx,tx.get('evidence_versions',file));return [('commitment_id',proof['id'])]
            old=h.upload('wage')
            execute_command(h.actors['dswd'],'document.intent','old-unapplied',{},lambda tx:intent(tx,old))
            def mine():
                env=os.environ.copy();env['MVP_PRIVATE_KEY']='0x'+'ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
                result=subprocess.run([env['MVP_NODE'],str(ROOT/'contracts/scripts/anchor_worker.js'),'--once'],env=env,capture_output=True,timeout=30)
                self.assertEqual(result.returncode,0)
            mine();reset()
            with h.connection() as db:h.actors['dswd']=db.execute("SELECT a.id FROM actors a JOIN evaluation_runs r ON r.id=a.run_id WHERE r.state='active' AND a.role='dswd' LIMIT 1").fetchone()['id']
            current=h.upload('wage')
            execute_command(h.actors['dswd'],'document.intent','new-unapplied',{},lambda tx:intent(tx,current))
            mine();self.assertEqual(apply_due_observations(),1)
            with h.connection() as db:
                self.assertEqual(db.execute("SELECT j.state FROM anchor_jobs j JOIN evaluation_runs r ON r.id=j.run_id WHERE r.state='active'").fetchone()['state'],'confirmed')
                self.assertEqual(db.execute("SELECT j.state FROM anchor_jobs j JOIN evaluation_runs r ON r.id=j.run_id WHERE r.state='retired'").fetchone()['state'],'mined_unapplied')
                self.assertEqual(db.execute('SELECT count(*) n FROM anchor_applications').fetchone()['n'],1)

    def test_release_document_deduplication_is_scoped_to_retained_namespace(self):
        from backend.tests.test_funds import FundsTests
        from backend.tests.support import synthetic_pdf
        from backend.scripts.reset_mvp import reset
        from backend.app.services import funds
        with Harness() as h:
            h.register_chain();raw=synthetic_pdf('Invented repeatable release\nAmount: PHP 100,000.00')
            original=h.upload('release_source',raw);req=FundsTests().request(h,original)
            execute_command(h.actors['dswd'],'fund.release','old',req,lambda tx:funds.release(tx,req))
            reset()
            with h.connection() as db:
                h.actors['dswd']=db.execute("SELECT a.id FROM actors a JOIN evaluation_runs r ON r.id=a.run_id WHERE r.state='active' AND a.role='dswd' LIMIT 1").fetchone()['id']
                h.disasters[0]=db.execute("SELECT d.id FROM disasters d JOIN evaluation_runs r ON r.id=d.run_id WHERE r.state='active' LIMIT 1").fetchone()['id']
            original=h.upload('release_source',raw);req=FundsTests().request(h,original)
            execute_command(h.actors['dswd'],'fund.release','new',req,lambda tx:funds.release(tx,req))
            with h.connection() as db:self.assertEqual(db.execute('SELECT count(*) n FROM release_document_uses').fetchone()['n'],2)
    def test_retirement_keeps_originals_and_history_readable_but_forbids_commands(self):
        from backend.scripts.namespace_mvp import retire,history
        with Harness() as h:
            h.register_chain();original=h.upload('wage')
            from backend.app.services.commitments import document_commitment
            def intent(tx):
                proof=document_commitment(tx,tx.get('evidence_versions',original));return [('commitment_id',proof['id'])]
            proof=execute_command(h.actors['dswd'],'document.intent','old-proof',{},intent)['resources'][0]['id'];h.drain_anchors()
            with h.connection() as db:before=db.execute('SELECT count(*) n FROM audit_events').fetchone()['n']
            retire(h.run)
            with self.assertRaises(DomainError):execute_command(h.actors['dswd'],'anything',str(uuid4()),{},lambda tx:[])
            view=history(h.actors['auditor'])
            self.assertEqual(history(h.actors['auditor'],commitment=proof)['result']['result'],'match')
            self.assertTrue(history(h.actors['auditor'],original=original).startswith(b'%PDF-'))
            self.assertEqual(view['state'],'retired');self.assertIn(str(original),str(view['originals']))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM evidence_versions').fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT count(*) n FROM audit_events').fetchone()['n'],before+1)
            with self.assertRaises(DomainError):history(h.actors['dswd'])
            from backend.scripts.seed_mvp import seed
            from backend.scripts.reset_mvp import reset
            reset();self.assertFalse(seed())
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM evaluation_runs').fetchone()['n'],2)
                self.assertEqual(db.execute('SELECT count(*) n FROM claims').fetchone()['n'],0)
                roles=db.execute("SELECT role,count(*) n FROM actors WHERE run_id!=%s AND role!='system' GROUP BY role",(h.run,)).fetchall()
                self.assertEqual(len(roles),5);self.assertTrue(all(r['n']>=2 for r in roles))
