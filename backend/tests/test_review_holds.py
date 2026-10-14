import unittest
from uuid import uuid4
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError

class ReviewHoldTests(unittest.TestCase):
    def test_no_independent_dswd_actor_is_an_explicit_review_hold(self):
        from backend.tests.test_entitlements import EntitlementTests
        from backend.app.services import checks,registry,entitlements,claims
        with Harness() as h:
            h.register_chain();claim=EntitlementTests().pending_claim(h)
            with h.connection() as db:member=db.execute('SELECT member_id FROM member_versions').fetchone()['member_id']
            for actor in ['dswd','dswd2']:
                req={'expected_revision':0,'member_id':member,'reason':'Invented own-household recusal'}
                execute_command(h.actors['dswd'],'staff.member_link',str(uuid4()),req,lambda tx,actor=actor:registry.member_link(tx,h.actors[actor],req))
            def refresh(tx):
                c=tx.get('claims',claim);r=claims.latest_round(tx,c);s=tx.get('claim_submissions',c['current_submission_id']);check=checks.run(tx,s,r['id'],'recheck');return [('check_run_id',check['id'])]
            ack=execute_command(h.actors['system'],'check.refresh','review-hold',{},refresh,system=True)
            with h.connection() as db:
                flags=db.execute('SELECT code FROM check_flags WHERE check_run_id=%s',(ack['resources'][0]['id'],)).fetchall()
                self.assertIn('independent_dswd_reviewer_unavailable',{f['code'] for f in flags})
                self.assertEqual(db.execute('SELECT business_status FROM claims').fetchone()['business_status'],'awaiting_dswd')
            req=EntitlementTests().decision(h,claim)
            with self.assertRaises(DomainError):execute_command(h.actors['dswd'],'claim.decide','own-household',req,lambda tx:entitlements.decide(tx,claim,req))
