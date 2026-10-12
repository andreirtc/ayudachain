import importlib.util
import unittest
from uuid import UUID,uuid4
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError


class EntitlementTests(unittest.TestCase):
    def service(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.entitlements'),'Human decision/input/publication service missing')
        from backend.app.services import entitlements
        return entitlements

    def pending_claim(self,h):
        from backend.tests.test_claim_routing import ClaimsTests
        from backend.app.services import claims
        identity=ClaimsTests().register_and_open(h,barangay_index=2);req=ClaimsTests().request(h,identity)
        ack=execute_command(h.actors['beneficiary'],'claim.submit','submit',req,lambda tx:claims.submit(tx,req))
        return UUID(ack['resources'][0]['id'])

    def decision(self,h,identity,action='approve'):
        with h.connection() as db:
            claim=db.execute('SELECT * FROM claims WHERE id=%s',(identity,)).fetchone();check=db.execute('SELECT id FROM check_runs WHERE submission_id=%s ORDER BY created_at DESC,id DESC LIMIT 1',(claim['current_submission_id'],)).fetchone()
        return {'expected_revision':claim['revision'],'reviewed_check_id':check['id'],'action':action,'category_id':h.categories[0],'reason':'Invented human review','question':None,'response_hours':None}

    def inputs(self,h,wage='43500'):
        return {'disaster_id':h.disasters[0],'expected_revision':0,'mode':'wage_formula','wage_centavos':wage,'wage_evidence_id':h.upload('wage'),'rules':[{'category_id':h.categories[0],'day_count':15,'fixed_centavos':None,'evidence_id':h.upload('days')}],'reason':'Invented documentary basis'}

    def test_approval_without_basis_is_null_then_real_documented_formula(self):
        svc=self.service()
        with Harness() as h:
            h.register_chain();claim=self.pending_claim(h);req=self.decision(h,claim)
            execute_command(h.actors['dswd'],'claim.decide','approve',req,lambda tx:svc.decide(tx,claim,req))
            with h.connection() as db:
                row=db.execute('SELECT v.* FROM entitlements e JOIN entitlement_versions v ON v.id=e.current_version_id').fetchone();self.assertIsNone(row['amount_centavos']);self.assertIsNone(row['input_version_id'])
                self.assertEqual(db.execute('SELECT count(*) n FROM payout_transactions').fetchone()['n'],1)
            inputs=self.inputs(h);execute_command(h.actors['dswd'],'inputs.save','inputs',inputs,lambda tx:svc.save_inputs(tx,inputs))
            with h.connection() as db:
                row=db.execute('SELECT v.* FROM entitlements e JOIN entitlement_versions v ON v.id=e.current_version_id').fetchone();self.assertEqual(row['amount_centavos'],495000)
                self.assertEqual(db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'],0)
            self.assertEqual(svc.calculate('wage_formula',40000,1,None)[0],30000)
            self.assertEqual(svc.calculate('wage_formula',40001,1,None)[0],31000)
            self.assertEqual(svc.calculate('fixed_category',None,None,2000000)[0],2000000)
            with self.assertRaises(DomainError):svc.calculate('wage_formula',9000000000000000000,2147483647,None)

    def test_review_changed_data_refuses_and_persists_new_check_then_human_retries(self):
        svc=self.service()
        with Harness() as h:
            h.register_chain();claim=self.pending_claim(h);req=self.decision(h,claim)
            with h.connection() as db:db.execute('UPDATE field_offices SET check_data_revision=check_data_revision+1 WHERE id=%s',(h.office,))
            with self.assertRaises(DomainError):execute_command(h.actors['dswd'],'claim.decide','stale-review',req,lambda tx:svc.decide(tx,claim,req))
            with h.connection() as db:self.assertEqual(db.execute('SELECT count(*) n FROM entitlements').fetchone()['n'],0)
            req=self.decision(h,claim);execute_command(h.actors['dswd'],'claim.decide','fresh-review',req,lambda tx:svc.decide(tx,claim,req))
