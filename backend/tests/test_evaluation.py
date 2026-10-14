import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.tests.support import Harness


class EvaluationTests(unittest.TestCase):
    def test_clock_is_explicitly_simulated_audited_and_never_changes_chain_time(self):
        with Harness() as h,TestClient(app) as client:
            dswd={'X-Demo-Actor-ID':str(h.actors['dswd']),'Idempotency-Key':'advance'}
            before=client.get('/api/v1/evaluation/status',headers=dswd)
            self.assertEqual(before.status_code,200)
            self.assertEqual(before.json()['data']['clock_mode'],'wall_clock')
            denied=client.post('/api/v1/evaluation/clock',headers={**dswd,'X-Demo-Actor-ID':str(h.actors['auditor'])},json={'advance_hours':72})
            self.assertEqual(denied.status_code,403)
            ack=client.post('/api/v1/evaluation/clock',headers=dswd,json={'advance_hours':72})
            self.assertEqual(ack.status_code,200,ack.text)
            after=client.get('/api/v1/evaluation/status',headers=dswd).json()
            self.assertEqual(after['data']['clock_mode'],'simulated')
            self.assertEqual(after['meta']['business_clock'],'simulated')
            self.assertEqual(client.get('/api/v1/actors/catalogue').status_code,200)
            self.assertEqual(client.get('/api/v1/context',headers=dswd).json()['meta']['chain_time'],'actual')
            with h.connection() as db:
                self.assertEqual(db.execute("SELECT count(*) n FROM audit_events WHERE action='evaluation.clock_advanced'").fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT count(*) n FROM commitments').fetchone()['n'],0)
