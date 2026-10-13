import unittest
from uuid import uuid4
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError


class PaidChangesTests(unittest.TestCase):
    def test_pending_paid_list_cannot_publish_before_new_display_decision(self):
        from uuid import UUID
        from backend.tests.test_outcomes import OutcomeTests
        from backend.tests.test_entitlements import EntitlementTests
        from backend.app.services import entitlements
        with Harness() as h:
            h.register_chain();session,transaction,root=OutcomeTests().handover(h)
            req={'disaster_id':h.disasters[0],'barangay_id':h.barangays[2],'expected_revision':None}
            candidate=UUID(execute_command(h.actors['dswd'],'list.request','old-paid-display',req,lambda tx:entitlements.request_list(tx,req))['resources'][0]['id'])
            decision=EntitlementTests().decision(h,root['claim_id'])|{'action':'category_change','category_id':h.categories[1],'reason':'Invented corrected paid display category'}
            try:execute_command(h.actors['dswd'],'claim.decide','review-changed',decision,lambda tx:entitlements.decide(tx,root['claim_id'],decision))
            except DomainError as error:
                self.assertEqual(error.code,'review_changed_refresh_and_review_new_flags')
                decision=EntitlementTests().decision(h,root['claim_id'])|{'action':'category_change','category_id':h.categories[1],'reason':'Invented corrected paid display category'}
                execute_command(h.actors['dswd'],'claim.decide','review-current',decision,lambda tx:entitlements.decide(tx,root['claim_id'],decision))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT business_status FROM approved_list_versions WHERE id=%s',(candidate,)).fetchone()['business_status'],'stale')
                self.assertEqual(db.execute('SELECT current_version_id FROM entitlements').fetchone()['current_version_id'],root['current_version_id'])
            h.drain_anchors()
            with h.connection() as db:self.assertNotEqual(db.execute('SELECT current_published_id FROM list_heads').fetchone()['current_published_id'],candidate)

    def test_post_paid_category_change_is_informational_and_keeps_locked_version(self):
        from backend.tests.test_outcomes import OutcomeTests
        from backend.tests.test_entitlements import EntitlementTests
        from backend.app.services import entitlements
        with Harness() as h:
            h.register_chain();s,t,e=OutcomeTests().handover(h)
            with h.connection() as db:old=db.execute('SELECT * FROM recorded_handovers').fetchone()
            import psycopg
            with self.assertRaises(psycopg.errors.CheckViolation),h.connection() as db:
                db.execute("UPDATE entitlements SET business_status='available'")
            d=EntitlementTests().decision(h,e['claim_id']);d.update(action='category_change',category_id=h.categories[1],reason='Invented post-paid category correction')
            try:execute_command(h.actors['dswd'],'claim.decide','review-changed-data',d,lambda tx:entitlements.decide(tx,e['claim_id'],d))
            except DomainError as err:
                self.assertEqual(err.code,'review_changed_refresh_and_review_new_flags')
                d=EntitlementTests().decision(h,e['claim_id']);d.update(action='category_change',category_id=h.categories[1],reason='Invented post-paid category correction')
                execute_command(h.actors['dswd'],'claim.decide','fresh-human',d,lambda tx:entitlements.decide(tx,e['claim_id'],d))
            with h.connection() as db:
                locked=db.execute('SELECT * FROM recorded_handovers').fetchone();self.assertEqual(old,locked)
                self.assertEqual(db.execute('SELECT current_version_id FROM entitlements').fetchone()['current_version_id'],old['entitlement_version_id'])
                self.assertEqual(db.execute('SELECT count(*) n FROM paid_difference_events').fetchone()['n'],0)
            inputs=EntitlementTests().inputs(h);inputs.update(expected_revision=1,reason='Invented documented second category days')
            inputs['rules'].append({'category_id':h.categories[1],'day_count':20,'fixed_centavos':None,'evidence_id':h.upload('days')})
            execute_command(h.actors['dswd'],'inputs.save','new-rule',inputs,lambda tx:entitlements.save_inputs(tx,inputs))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM paid_difference_events').fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT current_version_id FROM entitlements').fetchone()['current_version_id'],old['entitlement_version_id'])
            from fastapi.testclient import TestClient
            from backend.app.main import app
            with TestClient(app) as client:
                view=client.get('/api/v1/audit/overview',params={'disaster_id':str(h.disasters[0])},headers={'X-Demo-Actor-ID':str(h.actors['auditor'])})
                self.assertEqual(view.status_code,200,view.text)
                diff=view.json()['data']['exceptions']['paid_differences'][0]
                self.assertIsInstance(diff['hypothetical_centavos'],str,'Money must cross JSON as exact decimal strings')
