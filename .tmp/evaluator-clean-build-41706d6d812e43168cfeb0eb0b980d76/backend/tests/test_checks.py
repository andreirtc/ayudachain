import unittest
from datetime import date
from uuid import UUID,uuid4
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError


class ChecksTests(unittest.TestCase):
    def test_all_five_flags_near_matches_phone_three_vs_four_and_simulated_id(self):
        from backend.app.services import registry,claims,checks,entitlements
        from backend.tests.test_registry import RegistryTests
        from backend.tests.test_entitlements import EntitlementTests
        with Harness() as h:
            h.register_chain()
            opening={'disaster_id':h.disasters[0],'barangay_ids':h.barangays[:2],'response_hours':48,'basis_evidence_id':h.upload('operation_basis')}
            execute_command(h.actors['dswd'],'intake.open','intake',opening,lambda tx:registry.open_intake(tx,opening))
            def register(index,phone,role=None):
                target=h.actors[role] if role else None
                req=RegistryTests().request(h,beneficiary_actor_id=target,phone=phone,declared_barangay_id=h.barangays[1 if index==1 else 0],address='Invented street 12 zone 3',members=[{'name':'Invented Tala Salunga' if index==1 else 'Invented Tala Salonga' if index==0 else 'Invented Una '+str(index),'birth_date':date(1980,1,2) if index<2 else None,'relationship':'head','is_head':True}])
                if role:req.update(id_type='Synthetic photo ID',id_number='DFC-2026-SHARED',id_evidence_id=h.upload('identity_document',actor=role,prepared_for=target))
                ack=execute_command(h.actors[role or 'dswd'],'registry.register',str(uuid4()),req,lambda tx:registry.register(tx,req));return UUID(ack['resources'][0]['id'])
            households=[register(0,'09990000001','beneficiary'),register(1,'0999 000 0001','beneficiary2'),register(2,'+639990000001')]
            def submit(household,role,key):
                req={'household_id':household,'disaster_id':h.disasters[0],'stated_category_id':h.categories[0],'damage_description':'Invented damaged roof','evidence_ids':[],'new_information':None}
                execute_command(h.actors[role],'claim.submit',key,req,lambda tx:claims.submit(tx,req))
                with h.connection() as db:return db.execute('SELECT * FROM claims WHERE household_id=%s',(household,)).fetchone()
            other=submit(households[1],'beneficiary2','other')
            d=EntitlementTests().decision(h,other['id']);execute_command(h.actors['dswd'],'claim.decide','approve-other',d,lambda tx:entitlements.decide(tx,other['id'],d))
            own=submit(households[0],'beneficiary','own')
            def flags():
                with h.connection() as db:
                    check=db.execute('SELECT * FROM check_runs WHERE submission_id=%s ORDER BY created_at DESC LIMIT 1',(own['current_submission_id'],)).fetchone()
                    self.assertFalse(check['simulation_result']['identity_verified']);self.assertTrue(check['simulated'])
                    return {r['code'] for r in db.execute('SELECT code FROM check_flags WHERE check_run_id=%s',(check['id'],)).fetchall()}
            first=flags();self.assertTrue({'person_in_two_households','reused_id','aid_in_other_barangay'}<=first);self.assertNotIn('phone_shared_over_three',first)
            register(3,'09990000001')
            def recheck(tx):
                submission=tx.get('claim_submissions',own['current_submission_id']);round_=claims.latest_round(tx,tx.get('claims',own['id']));check=checks.run(tx,submission,round_['id'],'recheck');return [('check_run_id',check['id'])]
            execute_command(h.actors['dswd'],'claim.recheck','recheck',{},recheck)
            self.assertIn('phone_shared_over_three',flags())
            # Human review is still required; flags never mutate the decision.
            with h.connection() as db:self.assertEqual(db.execute('SELECT business_status FROM claims WHERE id=%s',(own['id'],)).fetchone()['business_status'],'waiting_barangay')
            with h.connection() as db:round_id=db.execute('SELECT id FROM claim_rounds WHERE submission_id=%s',(own['current_submission_id'],)).fetchone()['id']
            response={'kind':'endorse','parent_response_id':None,'residence_attested':True,'affected_attested':True,'category_opinion_id':h.categories[0],'category_disputed':False,'related_declared':False,'reason':None,'evidence_ids':[]}
            for role in ['barangay','barangay2']:execute_command(h.actors[role],'claim.respond',str(uuid4()),response,lambda tx:claims.respond(tx,round_id,response))
            signed={'disaster_id':h.disasters[0],'barangay_id':h.barangays[0],'round_ids':[round_id],'resolution_evidence_id':h.upload('council_resolution',actor='barangay')}
            execute_command(h.actors['barangay'],'claim.send','signed',signed,lambda tx:claims.send(tx,signed))
            d=EntitlementTests().decision(h,own['id'])
            with self.assertRaises(DomainError):execute_command(h.actors['dswd'],'claim.bulk','bulk',{'claims':[dict(d,claim_id=own['id'])]},lambda tx:entitlements.bulk_approve(tx,{'claims':[dict(d,claim_id=own['id'])]}))
            execute_command(h.actors['dswd'],'claim.decide','human-reviewed-flags',d,lambda tx:entitlements.decide(tx,own['id'],d))
            with self.assertRaises(DomainError):submit(households[0],'beneficiary','duplicate')
            self.assertIn('already_approved_or_handed_over',flags())

    def test_absent_person_birthdate_id_phone_do_not_collide(self):
        from backend.app.services import registry,claims
        from backend.tests.test_claim_routing import ClaimsTests
        from backend.tests.test_registry import RegistryTests
        with Harness() as h:
            h.register_chain();own=ClaimsTests().register_and_open(h,barangay_index=2)
            other=RegistryTests().request(h,beneficiary_actor_id=None)
            execute_command(h.actors['dswd'],'registry.register','unlinked',other,lambda tx:registry.register(tx,other))
            req={'household_id':own,'disaster_id':h.disasters[0],'stated_category_id':h.categories[0],'damage_description':'Invented damage','evidence_ids':[],'new_information':None}
            execute_command(h.actors['beneficiary'],'claim.submit','claim',req,lambda tx:claims.submit(tx,req))
            with h.connection() as db:
                codes={r['code'] for r in db.execute('SELECT code FROM check_flags').fetchall()}
                self.assertFalse({'reused_id','person_in_two_households','phone_shared_over_three'}&codes)
