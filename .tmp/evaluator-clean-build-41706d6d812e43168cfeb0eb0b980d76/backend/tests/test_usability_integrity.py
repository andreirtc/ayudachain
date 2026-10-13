import unittest
from uuid import uuid4
from backend.app.services.integrity import check_saved

class UnavailableDB:
    def execute(self,*args):return self
    def fetchone(self):return None

class IntegrityContextTests(unittest.TestCase):
    def test_missing_material_has_actual_check_time_and_context_without_chain_success(self):
        identity=uuid4()
        result=check_saved(UnavailableDB(),{'id':identity,'kind':'handover','canonical_bytes':b'not-canonical'})
        self.assertEqual(result['result'],'evidence_unavailable')
        self.assertEqual(result['commitment_id'],str(identity));self.assertEqual(result['kind'],'handover')
        self.assertIsNotNone(result['checked_at'].tzinfo)
        self.assertNotIn('onchain_hash',result);self.assertNotIn('block_number',result)
