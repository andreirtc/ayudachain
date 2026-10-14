import unittest
from uuid import UUID
from backend.tests.support import Harness
from backend.app.commands import execute_command, DomainError
from backend.app.services import payouts, sessions


class IdentityStopTests(unittest.TestCase):
    def test_failed_comparison_before_pin_can_be_cleared_without_authorization_or_code(self):
        from backend.tests.test_payouts import PayoutTests
        with Harness() as h:
            h.register_chain()
            session, transaction, entitlement = PayoutTests().session(h)
            failure = {'household_id': entitlement['household_id'], 'result': 'fail',
                       'accepted_id_type': None, 'person_photo_compared': False,
                       'reason': 'Invented photo comparison failed before private PIN', 'attempt_id': None}
            execute_command(h.actors['disbursing'], 'id.check', 'before-pin-fail', failure,
                            lambda tx: payouts.id_check(tx, session['id'], failure))
            with h.connection() as db:
                stopped = db.execute('SELECT * FROM payout_attempts').fetchone()
                self.assertIsNotNone(stopped, 'Failed pre-authorization comparison needs a recoverable stop')
                self.assertEqual(stopped['business_status'], 'stopped')
                self.assertEqual(db.execute('SELECT count(*) n FROM payout_codes').fetchone()['n'], 0)
                self.assertEqual(db.execute("SELECT count(*) n FROM attempt_events WHERE action='open'").fetchone()['n'], 0)
                transaction = db.execute('SELECT * FROM payout_transactions').fetchone()
                version = db.execute('SELECT * FROM session_versions WHERE id=%s', (session['current_version_id'],)).fetchone()
                entry = db.execute('SELECT * FROM approved_list_entries ORDER BY created_at DESC LIMIT 1').fetchone()
            clearance = {'expected_revision': transaction['revision'], 'reason': 'Invented DSWD comparison review', 'evidence_id': h.upload('clearance')}
            execute_command(h.actors['dswd'], 'attempt.clearance', 'review-pre-pin-stop', clearance,
                            lambda tx: payouts.clearance(tx, transaction['id'], clearance))
            passing = dict(failure, result='pass', accepted_id_type='Synthetic photo ID', person_photo_compared=True, reason=None)
            with self.assertRaises(DomainError):
                execute_command(h.actors['disbursing'], 'id.check', 'same-session-pass', passing,
                                lambda tx: payouts.id_check(tx, session['id'], passing))
            schedule = {'disaster_id': session['disaster_id'], 'barangay_id': session['barangay_id'],
                        'list_version_id': entry['list_version_id'], 'list_entry_ids': [entry['id']],
                        'date': version['date'], 'site': 'Invented later assisted comparison site',
                        'cash_actor_ids': [h.actors['disbursing'], h.actors['disbursing2']], 'followup_actor_ids': []}
            ack = execute_command(h.actors['dswd'], 'session.schedule', 'after-pre-pin-clearance', schedule,
                                  lambda tx: sessions.schedule(tx, schedule))
            version_id = UUID(ack['resources'][0]['id'])
            change = {'expected_revision': 0, 'action': 'open', 'reason': 'Invented later opening'}
            execute_command(h.actors['dswd'], 'session.change', 'later-pre-pin-open', change,
                            lambda tx: sessions.change(tx, version_id, change))
            with h.connection() as db:
                later = db.execute('SELECT session_id FROM session_versions WHERE id=%s', (version_id,)).fetchone()['session_id']
            execute_command(h.actors['disbursing'], 'id.check', 'later-pre-pin-pass', passing,
                            lambda tx: payouts.id_check(tx, later, passing))
            with h.connection() as db:
                check = db.execute("SELECT id FROM identity_checks WHERE result='pass'").fetchone()['id']
                revision = db.execute('SELECT revision FROM payout_transactions').fetchone()['revision']
            pin = {'identity_check_id': check, 'pin': '837261'}
            execute_command(h.actors['beneficiary'], 'pin.set', 'after-recovered-comparison', pin,
                            lambda tx: payouts.establish_pin(tx, entitlement['household_id'], pin))
            opening = {'expected_revision': revision, 'path': 'assisted', 'pin': '837261'}
            authorization = execute_command(h.actors['beneficiary'], 'attempt.open', 'recovered-assisted', opening,
                                            lambda tx: payouts.open_attempt(tx, entitlement['id'], opening))
            with h.connection() as db:
                transaction = db.execute('SELECT * FROM payout_transactions').fetchone()
                attempt = db.execute('SELECT * FROM payout_attempts WHERE id=%s', (transaction['current_attempt_id'],)).fetchone()
            passing['attempt_id'] = attempt['id']
            execute_command(h.actors['disbursing'], 'id.check', 'present-recovered-assisted', passing,
                            lambda tx: payouts.id_check(tx, later, passing))
            with h.connection() as db:
                revision = db.execute('SELECT revision FROM payout_transactions').fetchone()['revision']
            handover = {'expected_revision': revision, 'attempt_id': attempt['id'],
                        'code': authorization['code'], 'checker_actor_id': h.actors['disbursing2']}
            execute_command(h.actors['disbursing'], 'handover', 'recovered-assisted-cash', handover,
                            lambda tx: payouts.handover(tx, transaction['id'], handover))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'], 1)
                self.assertEqual(db.execute('SELECT count(*) n FROM payout_transactions').fetchone()['n'], 1)
                self.assertEqual(db.execute('SELECT count(*) n FROM payout_codes').fetchone()['n'], 1)
                self.assertEqual(db.execute('SELECT business_status FROM payout_attempts WHERE id=%s', (stopped['id'],)).fetchone()['business_status'], 'stopped')
