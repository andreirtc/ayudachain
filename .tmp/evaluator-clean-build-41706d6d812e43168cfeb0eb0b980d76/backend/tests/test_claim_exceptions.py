import unittest
from uuid import UUID,uuid4
from backend.tests.support import Harness
from backend.tests import test_claim_routing,test_registry
from backend.app.commands import execute_command,DomainError
from backend.app.services import claims,registry


class ClaimExceptionTests(unittest.TestCase):
    def test_one_active_or_all_recused_officers_routes_an_unsigned_staffing_exception(self):
        for all_recused in [False,True]:
            with self.subTest(all_recused=all_recused),Harness() as h:
                h.register_chain()
                registration=test_registry.RegistryTests().request(h)
                ack=execute_command(h.actors['barangay' if all_recused else 'beneficiary'],'registry.register','reg',registration,lambda tx:registry.register(tx,registration))
                household=UUID(ack['resources'][0]['id'])
                if all_recused:
                    with h.connection() as db:member=db.execute('SELECT id FROM household_members').fetchone()['id']
                    link={'expected_revision':0,'member_id':member,'reason':'Invented same-household recusal'}
                    execute_command(h.actors['dswd'],'staff.member_link','recusal',link,lambda tx:registry.member_link(tx,h.actors['barangay2'],link))
                else:
                    execute_command(h.actors['dswd'],'staff.deactivate','fewer',{},lambda tx:h.deactivate(tx,h.actors['barangay2']))
                operation={'disaster_id':h.disasters[0],'barangay_ids':[h.barangays[0]],'response_hours':1,'basis_evidence_id':h.upload('operation_basis')}
                execute_command(h.actors['dswd'],'intake.open','open',operation,lambda tx:registry.open_intake(tx,operation))
                req=test_claim_routing.ClaimsTests().request(h,household)
                execute_command(h.actors['beneficiary'],'claim.submit','claim',req,lambda tx:claims.submit(tx,req))
                with h.connection() as db:
                    snap=db.execute('SELECT * FROM submission_snapshots').fetchone()
                    self.assertEqual(snap['kind'],'system_fallback');self.assertEqual(snap['fallback_reason'],'no_eligible_endorser')
                    self.assertIsNone(snap['sender_id']);self.assertIsNone(snap['resolution_evidence_id'])
                    round_id=db.execute('SELECT id FROM claim_rounds').fetchone()['id']
                    self.assertEqual(db.execute('SELECT count(*) n FROM claim_responses').fetchone()['n'],0)
                response={'kind':'endorse','reason':None,'residence_attested':True,'affected_attested':True,'category_opinion_id':None,'category_disputed':False,'related_declared':False,'parent_response_id':None,'evidence_ids':[]}
                with self.assertRaises(DomainError):execute_command(h.actors['barangay'],'claim.respond','barred',response,lambda tx:claims.respond(tx,round_id,response))

    def test_withdrawn_responded_unsent_deadline_retains_exact_response_history(self):
        with Harness() as h:
            h.register_chain();helper=test_claim_routing.ClaimsTests();household=helper.register_and_open(h)
            req=helper.request(h,household)
            execute_command(h.actors['beneficiary'],'claim.submit','claim',req,lambda tx:claims.submit(tx,req))
            with h.connection() as db:round_id=db.execute('SELECT id FROM claim_rounds').fetchone()['id']
            endorsed={'kind':'endorse','reason':None,'residence_attested':True,'affected_attested':True,'category_opinion_id':h.categories[0],'category_disputed':False,'related_declared':False,'parent_response_id':None,'evidence_ids':[]}
            parent=UUID(execute_command(h.actors['barangay2'],'claim.respond','endorse',endorsed,lambda tx:claims.respond(tx,round_id,endorsed))['resources'][0]['id'])
            withdrawn=endorsed|{'kind':'withdraw','reason':'Invented withdrawn opinion after new evidence','parent_response_id':parent}
            execute_command(h.actors['barangay2'],'claim.respond','withdraw',withdrawn,lambda tx:claims.respond(tx,round_id,withdrawn))
            with h.connection() as db:db.execute("UPDATE evaluation_runs SET clock_mode='simulated',clock_offset=interval '2 hours' WHERE id=%s",(h.run,))
            execute_command(h.actors['system'],'claim.deadline','due',{},lambda tx:claims.fallback(tx,round_id),system=True)
            with h.connection() as db:
                snap=db.execute('SELECT * FROM submission_snapshots').fetchone()
                self.assertEqual(snap['fallback_reason'],'no_barangay_submission')
                self.assertEqual(db.execute('SELECT count(*) n FROM snapshot_response_refs').fetchone()['n'],2)
                self.assertIsNone(snap['sender_id']);self.assertIsNone(snap['resolution_evidence_id'])
                self.assertEqual(db.execute('SELECT business_status FROM claims').fetchone()['business_status'],'awaiting_dswd')
