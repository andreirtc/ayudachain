import unittest
from uuid import uuid4
from fastapi.testclient import TestClient
from backend.tests.support import Harness
from backend.app.main import app


class BarangayCountsTests(unittest.TestCase):
    def test_counts_only_scoped_read_has_no_business_side_effects(self):
        with Harness() as h, TestClient(app) as client:
            with h.connection() as db:
                before = db.execute('SELECT count(*) n FROM audit_events').fetchone()['n']
            headers = {'X-Demo-Actor-ID': str(h.actors['barangay'])}
            response = client.get('/api/v1/barangay/payout-counts', params={'disaster_id': str(h.disasters[0])}, headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['data'], {'approved': 0, 'recorded_handover': 0, 'remaining': 0})
            other = client.get('/api/v1/barangay/payout-counts', params={'disaster_id': str(uuid4())}, headers=headers)
            self.assertEqual(other.status_code, 404)
            override = client.get('/api/v1/barangay/payout-counts', params={'disaster_id': str(h.disasters[0]), 'barangay_id': str(h.barangays[1])}, headers=headers)
            self.assertEqual(override.json()['data'], response.json()['data'])
            with h.connection() as db:
                self.assertEqual(before, db.execute('SELECT count(*) n FROM audit_events').fetchone()['n'])

    def test_other_roles_cannot_use_barangay_counts(self):
        with Harness() as h, TestClient(app) as client:
            for role in ['beneficiary', 'dswd', 'disbursing', 'auditor']:
                response = client.get('/api/v1/barangay/payout-counts', params={'disaster_id': str(h.disasters[0])}, headers={'X-Demo-Actor-ID': str(h.actors[role])})
                self.assertEqual(response.status_code, 403, role)
