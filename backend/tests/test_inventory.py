import unittest
from uuid import UUID
from backend.tests.support import Harness
from backend.app.commands import execute_command


class InventoryTests(unittest.TestCase):
    def test_complete_real_fund_pair_and_retained_original_byte_coverage(self):
        from backend.tests.test_funds import FundsTests
        from backend.app.services import funds
        from backend.app.services.integrity import check_saved
        with Harness() as h:
            h.register_chain();req=FundsTests().request(h,h.upload('release_source'))
            ack=execute_command(h.actors['dswd'],'fund.release','release',req,lambda tx:funds.release(tx,req));original=UUID(ack['resources'][0]['id'])
            correction=dict(req,expected_revision=0,reason='Invented transcription correction',correction_kind='transcription',amount_centavos='12000000')
            execute_command(h.actors['dswd'],'fund.correct','correct',correction,lambda tx:funds.correct(tx,original,correction));h.drain_anchors()
            with h.connection() as db:
                proofs=db.execute('SELECT * FROM commitments ORDER BY created_at,id').fetchall()
                self.assertEqual({p['kind'] for p in proofs},{'document','fund_release','fund_reversal','fund_replacement'})
                import os,json,subprocess
                from backend.app.config import ROOT
                from backend.app.services.integrity import manifest_for
                from backend.app.services.evidence import storage_root
                for proof in proofs:
                    self.assertEqual(check_saved(db,proof)['result'],'match',proof['kind'])
                    e=json.loads(bytes(proof['canonical_bytes']))
                    originals=[]
                    for d in e['evidence']:
                        item=db.execute('SELECT storage_key FROM evidence_versions WHERE id=%s',(d['id'],)).fetchone()
                        originals.append({'id':d['id'],'path':str(storage_root()/item['storage_key'])})
                    deployment=db.execute('SELECT * FROM deployments WHERE id=%s',(proof['deployment_id'],)).fetchone()
                    material={'canonical_utf8':bytes(proof['canonical_bytes']).decode(),'content_hash':'0x'+proof['content_hash'].hex(),'deployment':manifest_for(deployment),'originals':originals}
                    env=os.environ.copy();env.pop('MVP_PRIVATE_KEY',None)
                    read=subprocess.run([env['MVP_NODE'],str(ROOT/'contracts/scripts/verify_evidence.js')],input=json.dumps(material),env=env,capture_output=True,text=True,timeout=20)
                    self.assertEqual(json.loads(read.stdout)['result'],'match',proof['kind'])
                self.assertEqual(funds.totals(db,h.run,h.disasters[0])['received_centavos'],'12000000')
