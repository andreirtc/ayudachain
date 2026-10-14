import importlib.util
import unittest
from uuid import UUID,uuid4
from concurrent.futures import ThreadPoolExecutor
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError


class ClaimsTests(unittest.TestCase):
    def service(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.claims'),'Claim/thread/check routing missing')
        from backend.app.services import claims
        return claims

    def register_and_open(self,h,*,barangay_index=0):
        from backend.app.services import registry
        from backend.tests.test_registry import RegistryTests
        registration=RegistryTests().request(h,declared_barangay_id=h.barangays[barangay_index])
        ack=execute_command(h.actors['beneficiary'],'registry.register','reg',registration,lambda tx:registry.register(tx,registration));identity=UUID(ack['resources'][0]['id'])
        operation={'disaster_id':h.disasters[0],'barangay_ids':h.barangays,'response_hours':1,'basis_evidence_id':h.upload('operation_basis')}
        execute_command(h.actors['dswd'],'intake.open','open',operation,lambda tx:registry.open_intake(tx,operation))
        return identity

    def request(self,h,identity):return {'household_id':identity,'disaster_id':h.disasters[0],'stated_category_id':h.categories[0],'damage_description':'Invented damaged synthetic roof','evidence_ids':[],'new_information':None}

    def test_barangay_officer_cannot_submit_a_claim(self):
        claims=self.service()
        with Harness() as h:
            h.register_chain();identity=self.register_and_open(h);req=self.request(h,identity)
            with self.assertRaises(DomainError) as refused:execute_command(h.actors['barangay'],'claim.submit','officer-claim',req,lambda tx:claims.submit(tx,req))
            self.assertEqual(refused.exception.status,403)
            with h.connection() as db:self.assertEqual(db.execute('SELECT count(*) n FROM claims').fetchone()['n'],0)

    def test_staffless_immediate_fallback_is_fixed_real_snapshot_not_signed(self):
        claims=self.service()
        with Harness() as h:
            h.register_chain();identity=self.register_and_open(h,barangay_index=2);req=self.request(h,identity)
            ack=execute_command(h.actors['beneficiary'],'claim.submit','claim',req,lambda tx:claims.submit(tx,req))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT business_status FROM claims').fetchone()['business_status'],'awaiting_dswd')
                snap=db.execute('SELECT * FROM submission_snapshots').fetchone();self.assertEqual(snap['fallback_reason'],'no_eligible_endorser');self.assertIsNone(snap['sender_id']);self.assertIsNone(snap['resolution_evidence_id'])
                checks=db.execute('SELECT * FROM check_runs').fetchone();self.assertFalse(checks['simulation_result']['identity_verified']);self.assertTrue(checks['simulated'])
                self.assertEqual(db.execute('SELECT count(*) n FROM commitments WHERE kind=%s',('system_fallback',)).fetchone()['n'],1)

    def test_negative_thread_late_response_and_signed_timeout_race_route_once(self):
        claims=self.service()
        with Harness() as h:
            h.register_chain();identity=self.register_and_open(h);req=self.request(h,identity)
            execute_command(h.actors['beneficiary'],'claim.submit','claim',req,lambda tx:claims.submit(tx,req))
            with h.connection() as db:round_id=db.execute('SELECT id FROM claim_rounds').fetchone()['id']
            response={'kind':'not_endorse','reason':'Invented residence concern','residence_attested':False,'affected_attested':False,'category_opinion_id':h.categories[1],'category_disputed':True,'related_declared':False,'parent_response_id':None,'evidence_ids':[]}
            execute_command(h.actors['barangay2'],'claim.respond','no',response,lambda tx:claims.respond(tx,round_id,response))
            resolution=h.upload('council_resolution',actor='barangay')
            batch={'disaster_id':h.disasters[0],'barangay_id':h.barangays[0],'round_ids':[round_id],'resolution_evidence_id':resolution}
            with h.connection() as db:db.execute("UPDATE evaluation_runs SET clock_mode='simulated',clock_offset=interval '2 hours' WHERE id=%s",(h.run,))
            def run(kind):
                try:
                    if kind=='send':execute_command(h.actors['barangay'],'claim.send','send',batch,lambda tx:claims.send(tx,batch))
                    else:execute_command(h.actors['system'],'claim.route','timer',{'round_id':round_id},lambda tx:claims.fallback(tx,round_id),system=True)
                    return 'saved'
                except DomainError:return 'already_routed'
            with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,['send','timer']))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM submission_snapshots').fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT count(*) n FROM snapshot_response_refs').fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT business_status FROM claims').fetchone()['business_status'],'awaiting_dswd')
            late=dict(response,kind='endorse',residence_attested=True,affected_attested=True,category_disputed=False,reason=None)
            execute_command(h.actors['barangay2'],'claim.respond','late',late,lambda tx:claims.respond(tx,round_id,late))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM snapshot_response_refs').fetchone()['n'],1)
                self.assertGreaterEqual(db.execute('SELECT count(*) n FROM check_runs').fetchone()['n'],2)
