"""Original-use scope cannot be widened by attaching or replacing evidence.

These cases use PostgreSQL and original files without registering/draining chain
jobs. Private reports start from an explicit awaiting-amount transaction fixture;
the fixture supplies no publication, handover or blockchain success.
"""
import unittest
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from backend.app.actor import resolve_identity
from backend.app.commands import DomainError, Transaction, execute_command
from backend.app.main import app
from backend.app.services import claims, entitlements, outcomes, registry
from backend.app.services.evidence import prepare_upload, save_upload
from backend.tests.support import Harness
from backend.tests import test_registry


class EvidenceMutationScopeTests(unittest.TestCase):
    raw = b'\x89PNG\r\n\x1a\nInvented original evidence'

    def register(self, h, actor='beneficiary', **changes):
        req = test_registry.RegistryTests().request(h, beneficiary_actor_id=h.actors[actor], **changes)
        ack = execute_command(h.actors[actor], 'registry.register', str(uuid4()), req,
                              lambda tx: registry.register(tx, req))
        return UUID(ack['resources'][0]['id'])

    def open_intake(self, h):
        req = {'disaster_id': h.disasters[0], 'barangay_ids': h.barangays,
               'response_hours': 24, 'basis_evidence_id': h.upload('operation_basis', self.raw)}
        execute_command(h.actors['dswd'], 'intake.open', str(uuid4()), req,
                        lambda tx: registry.open_intake(tx, req))

    def claim(self, h, household, actor='beneficiary', evidence=()):
        req = {'household_id': household, 'disaster_id': h.disasters[0],
               'stated_category_id': h.categories[0], 'damage_description': 'Invented damaged roof',
               'new_information': None, 'evidence_ids': list(evidence)}
        return execute_command(h.actors[actor], 'claim.submit', str(uuid4()), req,
                               lambda tx: claims.submit(tx, req))

    def transaction_fixture(self, h, claim_id):
        # The report boundary does not depend on the route to approval. Construct
        # only its persisted precondition, with actual FKs/audit and no chain refs.
        with h.connection() as db:
            tx = Transaction(db, resolve_identity(db, h.actors['dswd']), uuid4())
            claim = tx.get('claims', claim_id)
            submission = tx.get('claim_submissions', claim['current_submission_id'])
            round_row = claims.latest_round(tx, claim)
            check = db.execute('SELECT id FROM check_runs WHERE submission_id=%s',
                               (submission['id'],)).fetchone()
            decision = tx.insert('claim_decisions', {
                'claim_id': claim_id, 'submission_id': submission['id'], 'round_id': round_row['id'],
                'predecessor_id': None, 'check_run_id': check['id'], 'action': 'approve',
                'category_id': h.categories[0], 'reason': 'Synthetic report precondition',
                'question': None, 'confirmed_by': None, 'bulk_group_id': None, 'challenge_event_id': None})
            tx.update('claims', claim_id, {'business_status': 'approved', 'current_decision_id': decision['id']})
            tx.audit('fixture.report_precondition', [('decision_id', decision['id'])])
            root = tx.insert('entitlements', {
                'claim_id': claim_id, 'household_id': claim['household_id'], 'disaster_id': claim['disaster_id'],
                'current_version_id': uuid4(), 'business_status': 'awaiting_amount', 'hold_reasons': [], 'revision': 0})
            entitlements.version_entitlement(tx, root, decision, initial=True)
            return tx.insert('payout_transactions', {
                'entitlement_id': root['id'], 'current_attempt_id': None, 'current_outcome_id': None, 'revision': 0})['id']

    def counts(self, h):
        with h.connection() as db:
            return tuple(db.execute('SELECT count(*) n FROM ' + table).fetchone()['n']
                         for table in ['evidence_links', 'evidence_versions', 'claims', 'grievance_events', 'audit_events'])

    def read(self, client, h, identity, actor):
        return client.get('/api/v1/evidence/' + str(identity) + '/content',
                          headers={'X-Demo-Actor-ID': str(h.actors[actor])})

    def replacement(self, client, h, identity, actor='beneficiary', purpose='damage', recipient=None):
        data = {'purpose': purpose, 'predecessor_id': str(identity)}
        if recipient is not None:
            data['prepared_for_actor_id'] = str(recipient)
        return client.post('/api/v1/evidence',
                           headers={'X-Demo-Actor-ID': str(h.actors[actor]), 'Idempotency-Key': str(uuid4())},
                           data=data, files={'file': ('synthetic.png', self.raw + b' replacement', 'image/png')})

    def test_claim_attachment_cannot_make_another_households_damage_readable(self):
        with Harness() as h, TestClient(app) as client:
            own, other = self.register(h), self.register(h, 'beneficiary2')
            self.open_intake(h)
            foreign = h.upload('damage', self.raw, actor='beneficiary2')
            self.claim(h, other, 'beneficiary2', [foreign])
            self.assertEqual(self.read(client, h, foreign, 'beneficiary').status_code, 404)
            before = self.counts(h)
            with self.assertRaises(DomainError) as refused:
                self.claim(h, own, evidence=[foreign])
            self.assertEqual(refused.exception.status, 404)
            self.assertEqual(self.counts(h), before)
            self.assertEqual(self.read(client, h, foreign, 'beneficiary').status_code, 404)
            self.assertEqual(self.read(client, h, foreign, 'beneficiary2').content, self.raw)

    def test_private_report_attachment_cannot_disclose_another_households_original(self):
        with Harness() as h, TestClient(app) as client:
            own, other = self.register(h), self.register(h, 'beneficiary2')
            self.open_intake(h)
            own_claim = UUID(self.claim(h, own)['resources'][0]['id'])
            other_claim = UUID(self.claim(h, other, 'beneficiary2')['resources'][0]['id'])
            own_transaction = self.transaction_fixture(h, own_claim)
            other_transaction = self.transaction_fixture(h, other_claim)
            foreign = h.upload('private_report', self.raw, actor='beneficiary2')
            report = {'text': 'Invented private concern', 'evidence_ids': [foreign]}
            execute_command(h.actors['beneficiary2'], 'report', str(uuid4()), report,
                            lambda tx: outcomes.report(tx, other_transaction, report))
            self.assertEqual(self.read(client, h, foreign, 'beneficiary').status_code, 404)
            before = self.counts(h)
            response = client.post('/api/v1/transactions/' + str(own_transaction) + '/reports',
                                   headers={'X-Demo-Actor-ID': str(h.actors['beneficiary']), 'Idempotency-Key': str(uuid4())},
                                   json=report | {'evidence_ids': [str(foreign)]})
            self.assertEqual(response.status_code, 404, response.text)
            self.assertEqual(self.counts(h), before)
            self.assertEqual(self.read(client, h, foreign, 'beneficiary').status_code, 404)
            self.assertEqual(self.read(client, h, foreign, 'beneficiary2').content, self.raw)

    def test_foreign_unlinked_original_cannot_be_used_as_upload_predecessor(self):
        with Harness() as h, TestClient(app) as client:
            foreign = h.upload('damage', self.raw, actor='beneficiary2')
            before = self.counts(h)
            response = self.replacement(client, h, foreign)
            self.assertEqual(response.status_code, 404, response.text)
            self.assertEqual(self.counts(h), before)
            self.assertEqual(self.read(client, h, foreign, 'beneficiary').status_code, 404)

    def test_predecessor_cannot_change_evidence_purpose(self):
        with Harness() as h, TestClient(app) as client:
            own = h.upload('damage', self.raw, actor='beneficiary')
            before = self.counts(h)
            response = self.replacement(client, h, own, purpose='private_report')
            self.assertEqual(response.status_code, 422, response.text)
            self.assertEqual(self.counts(h), before)
            self.assertEqual(self.read(client, h, own, 'beneficiary').content, self.raw)

    def test_identity_predecessor_cannot_change_private_recipient(self):
        with Harness() as h, TestClient(app) as client:
            identity = h.upload('identity_photo', self.raw, prepared_for=h.actors['beneficiary'])
            before = self.counts(h)
            response = self.replacement(client, h, identity, actor='dswd', purpose='identity_photo',
                                        recipient=h.actors['beneficiary2'])
            self.assertEqual(response.status_code, 422, response.text)
            self.assertEqual(self.counts(h), before)
            self.assertEqual(self.read(client, h, identity, 'beneficiary2').status_code, 404)

    def test_beneficiary_cannot_prepare_private_evidence_for_another_recipient(self):
        with Harness() as h:
            item = prepare_upload(self.raw, 'image/png')
            before = self.counts(h)
            with self.assertRaises(DomainError) as refused:
                execute_command(h.actors['beneficiary'], 'evidence.upload', str(uuid4()), {},
                                lambda tx: save_upload(tx, item, 'identity_photo', h.actors['beneficiary2']))
            self.assertEqual(refused.exception.status, 403)
            self.assertEqual(self.counts(h), before)

    def test_own_original_replacement_retains_predecessor_and_original_bytes(self):
        with Harness() as h, TestClient(app) as client:
            original = h.upload('damage', self.raw, actor='beneficiary')
            response = self.replacement(client, h, original)
            self.assertEqual(response.status_code, 200, response.text)
            successor = UUID(response.json()['data']['resources'][0]['id'])
            with h.connection() as db:
                row = db.execute('SELECT * FROM evidence_versions WHERE id=%s', (successor,)).fetchone()
                prior = db.execute('SELECT * FROM evidence_versions WHERE id=%s', (original,)).fetchone()
                self.assertEqual(row['predecessor_id'], original)
                self.assertNotEqual(row['storage_key'], prior['storage_key'])
            self.assertEqual(self.read(client, h, original, 'beneficiary').content, self.raw)
            self.assertEqual(self.read(client, h, successor, 'beneficiary').content, self.raw + b' replacement')

    def test_helper_can_attach_private_panel_evidence_without_original_read(self):
        with Harness() as h, TestClient(app) as client:
            identity = h.upload('identity_photo', self.raw, actor='beneficiary')
            req = test_registry.RegistryTests().request(h, head_photo_evidence_id=identity)
            self.assertEqual(self.read(client, h, identity, 'barangay').status_code, 404)
            execute_command(h.actors['barangay'], 'registry.register', str(uuid4()), req,
                            lambda tx: registry.register(tx, req))
            self.assertEqual(self.read(client, h, identity, 'barangay').status_code, 404)
            self.assertEqual(self.read(client, h, identity, 'beneficiary').content, self.raw)

    def test_helper_can_replace_their_private_panel_upload_for_the_same_recipient(self):
        with Harness() as h, TestClient(app) as client:
            identity = h.upload('identity_photo', self.raw, actor='barangay',
                                prepared_for=h.actors['beneficiary'])
            response = self.replacement(client, h, identity, actor='barangay', purpose='identity_photo',
                                        recipient=h.actors['beneficiary'])
            self.assertEqual(response.status_code, 200, response.text)
            successor = response.json()['data']['resources'][0]['id']
            self.assertEqual(self.read(client, h, successor, 'barangay').status_code, 404)
            self.assertEqual(self.read(client, h, successor, 'beneficiary').content, self.raw + b' replacement')

    def test_dswd_can_reuse_another_officers_field_original(self):
        with Harness() as h:
            household = self.register(h)
            original = h.upload('field_check', self.raw, actor='dswd2')
            for revision in [0, 1]:
                req = {'expected_revision': revision, 'action': 'residence_confirm',
                       'reason': 'Invented field residence confirmation', 'field_evidence_id': original}
                execute_command(h.actors['dswd'], 'registry.review', str(uuid4()), req,
                                lambda tx: registry.review(tx, household, req))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM evidence_links WHERE evidence_version_id=%s',
                                            (original,)).fetchone()['n'], 2)
