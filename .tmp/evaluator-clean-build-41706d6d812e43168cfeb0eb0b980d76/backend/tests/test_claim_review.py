"""Final threads, fresh closed-intake referrals and one substantive resubmission."""
import unittest
from uuid import UUID, uuid4
from datetime import timedelta
from backend.tests.support import Harness
from backend.tests import test_claim_routing, test_entitlements
from backend.app.commands import execute_command, DomainError
from backend.app.services import claims, entitlements, registry


class ClaimReviewTests(unittest.TestCase):
    def decision(self,h,claim,action,**changes):
        req=test_entitlements.EntitlementTests().decision(h,claim,action)|changes
        return execute_command(h.actors['dswd'],'claim.decide',str(uuid4()),req,lambda tx:entitlements.decide(tx,claim,req))

    def test_fresh_referral_after_intake_closure_and_final_reply_refusal(self):
        with Harness() as h:
            h.register_chain();helper=test_claim_routing.ClaimsTests();household=helper.register_and_open(h)
            req=helper.request(h,household)
            claim=UUID(execute_command(h.actors['beneficiary'],'claim.submit','first',req,lambda tx:claims.submit(tx,req))['resources'][0]['id'])
            with h.connection() as db:
                initial=db.execute('SELECT * FROM claim_rounds').fetchone();operation=db.execute('SELECT * FROM claim_operations').fetchone()
            response={'kind':'not_endorse','reason':'Invented residence question','residence_attested':False,'affected_attested':False,'category_opinion_id':None,'category_disputed':False,'related_declared':False,'parent_response_id':None,'evidence_ids':[]}
            execute_command(h.actors['barangay2'],'claim.respond','negative',response,lambda tx:claims.respond(tx,initial['id'],response))
            batch={'disaster_id':h.disasters[0],'barangay_id':h.barangays[0],'round_ids':[initial['id']],'resolution_evidence_id':h.upload('council_resolution',actor='barangay')}
            execute_command(h.actors['barangay'],'claim.send','send',batch,lambda tx:claims.send(tx,batch))
            close={'expected_revision':operation['revision'],'reason':'Invented intake cutoff'}
            execute_command(h.actors['dswd'],'intake.close','close',close,lambda tx:registry.close_intake(tx,operation['id'],close))
            with h.connection() as db:db.execute("UPDATE evaluation_runs SET clock_mode='simulated',clock_offset=interval '2 hours' WHERE id=%s",(h.run,))
            self.decision(h,claim,'refer',question='Invented field details required',response_hours=4)
            with h.connection() as db:
                referral=db.execute('SELECT * FROM claim_rounds WHERE referral_decision_id IS NOT NULL').fetchone()
                self.assertGreater(referral['deadline_at'],initial['deadline_at']+timedelta(hours=4))
                self.assertEqual(db.execute('SELECT business_status FROM claim_operations').fetchone()['business_status'],'closed')
            reply=response|{'kind':'referral_answer','reason':'Invented checked field details'}
            execute_command(h.actors['barangay2'],'claim.respond','reply',reply,lambda tx:claims.respond(tx,referral['id'],reply))
            with h.connection() as db:self.assertEqual(db.execute('SELECT business_status FROM claims').fetchone()['business_status'],'awaiting_dswd')
            self.decision(h,claim,'approve')
            with self.assertRaises(DomainError):execute_command(h.actors['barangay2'],'claim.respond','final-late',reply,lambda tx:claims.respond(tx,referral['id'],reply))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM claim_decisions').fetchone()['n'],2)
                self.assertEqual(db.execute('SELECT count(*) n FROM submission_snapshots').fetchone()['n'],1)

    def test_only_one_substantive_declined_resubmission_preserves_prior_versions(self):
        with Harness() as h:
            h.register_chain();helper=test_claim_routing.ClaimsTests();household=helper.register_and_open(h,barangay_index=2)
            first=helper.request(h,household)
            claim=UUID(execute_command(h.actors['beneficiary'],'claim.submit','first',first,lambda tx:claims.submit(tx,first))['resources'][0]['id'])
            self.decision(h,claim,'decline')
            for value in [None,'',' \t\n ']:
                request=first|{'new_information':value}
                with self.assertRaises(DomainError):execute_command(h.actors['beneficiary'],'claim.submit',str(uuid4()),request,lambda tx:claims.submit(tx,request))
            request=first|{'new_information':'Invented fresh field evidence changes the recorded damage','damage_description':'Invented newly documented roof damage','evidence_ids':[h.upload('damage',actor='beneficiary')]}
            ack=execute_command(h.actors['beneficiary'],'claim.submit','second',request,lambda tx:claims.submit(tx,request))
            self.assertEqual(ack['resources'][0]['id'],str(claim));self.decision(h,claim,'decline')
            with self.assertRaises(DomainError):execute_command(h.actors['beneficiary'],'claim.submit','third',request|{'new_information':'Invented further information'},lambda tx:claims.submit(tx,request|{'new_information':'Invented further information'}))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM claims').fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT count(*) n FROM claim_submissions').fetchone()['n'],2)
                self.assertEqual(db.execute('SELECT count(*) n FROM claim_decisions').fetchone()['n'],2)
                self.assertEqual(db.execute('SELECT resubmissions FROM claims').fetchone()['resubmissions'],1)
