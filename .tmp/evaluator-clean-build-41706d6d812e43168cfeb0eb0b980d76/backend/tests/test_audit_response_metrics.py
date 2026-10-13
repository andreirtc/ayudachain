"""Officer response metrics follow saved business time and count responses once."""
import unittest
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.commands import execute_command
from backend.app.services import claims
from backend.tests import test_claim_routing
from backend.tests.support import Harness


class AuditResponseMetricTests(unittest.TestCase):
    def test_business_clock_late_reply_and_on_time_endorsement_keep_exact_officer_counts(self):
        with Harness() as h, TestClient(app) as client:
            # Registration validates the actual pinned local deployment by read;
            # fallback creates a pending intent, with no signer/worker invocation.
            h.register_chain()
            helper = test_claim_routing.ClaimsTests()
            household = helper.register_and_open(h)
            request = helper.request(h, household)
            ack = execute_command(h.actors['beneficiary'], 'claim.submit', str(uuid4()), request,
                                  lambda tx: claims.submit(tx, request))
            claim_id = UUID(ack['resources'][0]['id'])
            with h.connection() as db:
                round_row = db.execute('SELECT * FROM claim_rounds').fetchone()
            endorsement = {'kind': 'endorse', 'residence_attested': True, 'affected_attested': True,
                           'category_opinion_id': h.categories[0], 'category_disputed': False,
                           'related_declared': False, 'reason': None, 'parent_response_id': None,
                           'evidence_ids': []}
            ack = execute_command(h.actors['barangay'], 'claim.respond', str(uuid4()), endorsement,
                                  lambda tx: claims.respond(tx, round_row['id'], endorsement))
            first_response = UUID(ack['resources'][0]['id'])
            with h.connection() as db:
                # The real endorsement also emits registry.attested with this
                # target. A general audit join must not count it a second time.
                targets = db.execute('SELECT count(*) n FROM audit_targets WHERE response_id=%s',
                                     (first_response,)).fetchone()['n']
                self.assertGreaterEqual(targets, 2)

            advanced = client.post('/api/v1/evaluation/clock',
                                   headers={'X-Demo-Actor-ID': str(h.actors['dswd']),
                                            'Idempotency-Key': str(uuid4())},
                                   json={'advance_hours': 2})
            self.assertEqual(advanced.status_code, 200, advanced.text)
            clock = client.get('/api/v1/evaluation/status',
                               headers={'X-Demo-Actor-ID': str(h.actors['dswd'])})
            self.assertEqual(clock.json()['data']['clock_mode'], 'simulated')
            self.assertEqual(clock.json()['data']['offset_hours'], '2.0')
            execute_command(h.actors['system'], 'claim.route', str(uuid4()),
                            {'round_id': round_row['id']},
                            lambda tx: claims.fallback(tx, round_row['id']), system=True)
            late_reply = endorsement | {'kind': 'not_endorse', 'residence_attested': False,
                                        'affected_attested': False, 'category_opinion_id': h.categories[1],
                                        'category_disputed': True, 'related_declared': True,
                                        'reason': 'Invented late field information before final review'}
            ack = execute_command(h.actors['barangay2'], 'claim.respond', str(uuid4()), late_reply,
                                  lambda tx: claims.respond(tx, round_row['id'], late_reply))
            late_response = UUID(ack['resources'][0]['id'])
            with h.connection() as db:
                late = db.execute("""SELECT r.created_at,a.effective_at FROM claim_responses r
                    JOIN audit_targets t ON t.response_id=r.id JOIN audit_events a ON a.id=t.audit_event_id
                    WHERE r.id=%s AND a.action='claim.respond'""", (late_response,)).fetchone()
                self.assertLess(late['created_at'], round_row['deadline_at'])
                self.assertGreater(late['effective_at'], round_row['deadline_at'])
                self.assertEqual(db.execute('SELECT business_status FROM claims WHERE id=%s',
                                            (claim_id,)).fetchone()['business_status'], 'awaiting_dswd')
                routed = db.execute('SELECT * FROM claim_rounds WHERE id=%s', (round_row['id'],)).fetchone()
                self.assertEqual(routed['route_kind'], 'system_fallback')
                snapshot = db.execute('SELECT fallback_reason FROM submission_snapshots WHERE id=%s',
                                      (routed['primary_snapshot_id'],)).fetchone()
                self.assertEqual(snapshot['fallback_reason'], 'no_barangay_submission')
                before = db.execute('SELECT count(*) n FROM audit_events').fetchone()['n']

            overview = client.get('/api/v1/audit/overview', params={'disaster_id': str(h.disasters[0])},
                                  headers={'X-Demo-Actor-ID': str(h.actors['auditor'])})
            self.assertEqual(overview.status_code, 200, overview.text)
            view = overview.json()['data']
            self.assertEqual(view['population']['responses'], 2)
            by_actor = {officer['id']: officer for officer in view['officers']}
            first = by_actor[str(h.actors['barangay'])]
            self.assertEqual((first['response_count'], first['endorsements'], first['category_differences'],
                              first['relative_declarations'], first['after_deadline']), (1, 1, 0, 0, 0))
            late = by_actor[str(h.actors['barangay2'])]
            self.assertEqual((late['response_count'], late['endorsements'], late['category_differences'],
                              late['relative_declarations'], late['after_deadline']), (1, 0, 1, 1, 1))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM audit_events').fetchone()['n'], before)
                self.assertEqual(db.execute('SELECT count(*) n FROM anchor_submissions').fetchone()['n'], 0)
