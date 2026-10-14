import unittest
from backend.tests.support import Harness


class ApiFoundationTests(unittest.TestCase):
    def client(self):
        try:
            from backend.app.main import app
        except ImportError as e:
            self.fail('Authoritative MVP API boundary missing: '+str(e))
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_selected_actor_uses_stored_role_and_honest_metadata(self):
        with Harness() as h:
            c=self.client()
            r=c.get('/api/v1/context',headers={'X-Demo-Actor-ID':str(h.actors['dswd']),'X-Role':'auditor'})
            self.assertEqual(r.status_code,200)
            self.assertEqual(r.json()['data']['role'],'dswd')
            self.assertEqual(r.json()['meta']['authentication'],'pending')
            self.assertEqual(r.headers['cache-control'],'no-store')

    def test_catalogue_has_multiple_claimed_actors_without_private_fields(self):
        with Harness() as h:
            r=self.client().get('/api/v1/actors/catalogue')
            self.assertEqual(r.status_code,200)
            rows=r.json()['data']
            for role in ['dswd','barangay','beneficiary','disbursing','auditor']:
                self.assertGreaterEqual(sum(x['role']==role and x['status']=='active' for x in rows),2)
            for x in rows:
                self.assertNotIn('email',x)
                self.assertNotIn('household_id',x)
                self.assertNotEqual(x['role'],'system')

    def test_unknown_or_inactive_selection_is_denied_without_details(self):
        with Harness() as h:
            for identity in ['not-a-uuid',str(h.actors['pending']),str(h.actors['system'])]:
                r=self.client().get('/api/v1/context',headers={'X-Demo-Actor-ID':identity})
                self.assertEqual(r.status_code,403)
                self.assertEqual(r.json()['error'],'actor_unavailable')
                self.assertNotIn('household',str(r.json()))
