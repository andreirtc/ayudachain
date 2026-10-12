import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.tests.support import Harness
from backend.tests import test_registry
from backend.app.commands import execute_command
from backend.app.services import registry


class QueueTests(unittest.TestCase):
    def test_search_counts_pages_and_scope_without_private_fields(self):
        with Harness() as h, TestClient(app) as client:
            for i, barangay in enumerate(h.barangays[:2]):
                req=test_registry.RegistryTests().request(h,beneficiary_actor_id=None,declared_barangay_id=barangay,
                    members=[{'name':f'Invented Queue {i}', 'birth_date':None,'relationship':'head','is_head':True}])
                execute_command(h.actors['dswd'],'registry.register',f'queue-{i}',req,lambda tx:registry.register(tx,req))
            def search(role,**kw):
                return client.post('/api/v1/queues/search',headers={'X-Demo-Actor-ID':str(h.actors[role])},
                    json={'kind':'registry','disaster_id':str(h.disasters[0]),**kw})
            response=search('dswd',query='Invented Queue',limit=1)
            self.assertEqual(response.status_code,200,response.text)
            data=response.json()['data'];self.assertEqual(data['total'],2);self.assertEqual(len(data['rows']),1)
            self.assertNotIn('phone',str(data));self.assertNotIn('id_number',str(data))
            scoped=search('barangay').json()['data'];self.assertEqual(scoped['total'],1)
            self.assertEqual(search('beneficiary').json()['data']['total'],0)
            self.assertEqual(search('disbursing').status_code,403)
            self.assertEqual(search('barangay',state='received_less').status_code,422)
            empty=search('dswd',query='absent').json()['data'];self.assertEqual(empty['total'],0)
            other=search('barangay',barangay_id=str(h.barangays[1])).json()['data'];self.assertEqual(other['total'],0)

    def test_operations_barangay_allowlist_and_office_denominators(self):
        with Harness() as h,TestClient(app) as client:
            for role in ['barangay','dswd','auditor']:
                response=client.get('/api/v1/operations',params={'disaster_id':str(h.disasters[0])},headers={'X-Demo-Actor-ID':str(h.actors[role])})
                self.assertEqual(response.status_code,200,response.text)
                rows=response.json()['data']['rows'];self.assertEqual(len(rows),1 if role=='barangay' else 3)
                if role=='barangay':
                    self.assertEqual(set(rows[0]),{'barangay_id','name','approved','recorded_handover','remaining'})
                else:
                    self.assertEqual(rows[0]['known_approved_centavos'],'0');self.assertEqual(rows[0]['awaiting_amount'],0)
