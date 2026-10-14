import os
import unittest
from pathlib import Path
from backend.tests.support import Harness
from backend.app.commands import execute_command


class IntegrityTests(unittest.TestCase):
    def test_actual_five_results_and_every_public_link_is_compared(self):
        from backend.tests.test_funds import FundsTests
        from backend.app.services import funds
        from backend.app.services.integrity import check_saved
        from backend.app.services.evidence import storage_root
        with Harness() as h:
            h.register_chain();req=FundsTests().request(h,h.upload('release_source'))
            execute_command(h.actors['dswd'],'fund.release','release',req,lambda tx:funds.release(tx,req))
            with h.connection() as db:
                proof=db.execute("SELECT * FROM commitments WHERE kind='document'").fetchone()
                self.assertEqual(check_saved(db,proof)['result'],'required_anchor_absent')
            h.drain_anchors()
            with h.connection() as db:
                self.assertEqual(check_saved(db,proof)['result'],'match')
                changed=dict(proof,public_related=b'\x12'*32)
                self.assertEqual(check_saved(db,changed)['result'],'mismatch')
                evidence=db.execute('SELECT * FROM evidence_versions WHERE id=%s',(req['source_evidence_id'],)).fetchone()
                file=storage_root()/evidence['storage_key'];raw=file.read_bytes()
                try:
                    file.write_bytes(raw+b'changed')
                    self.assertEqual(check_saved(db,proof)['result'],'mismatch')
                    moved=file.with_suffix('.held');file.rename(moved)
                    self.assertEqual(check_saved(db,proof)['result'],'evidence_unavailable')
                    moved.rename(file)
                finally:file.write_bytes(raw)
                rpc=os.environ['MVP_RPC_URL'];os.environ['MVP_RPC_URL']='http://127.0.0.1:8599'
                try:
                    failed=check_saved(db,proof);self.assertEqual(failed['result'],'chain_unreachable')
                    self.assertTrue(failed['last_confirmed_observation']['historical'])
                finally:os.environ['MVP_RPC_URL']=rpc

