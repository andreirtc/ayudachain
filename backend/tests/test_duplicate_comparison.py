import json
import unittest
from datetime import date
from uuid import UUID,uuid4
from unittest.mock import Mock
from backend.tests.support import Harness
from backend.app.commands import execute_command


class DuplicateComparisonTests(unittest.TestCase):
    def test_historical_missing_evidence_is_unavailable_and_raw_fields_are_not_projected(self):
        from backend.app.routes_claims import project_flag
        db=Mock()
        result=project_flag(db,{'code':'reused_id','matched_household_id':uuid4(),'scores':{'id_number':'DFC-2026-PRIVATE','phone':'09990000001','name_similarity':'0.9000'}})
        self.assertFalse(result['comparison_available'])
        self.assertIn('historical',result['comparison_unavailable_reason'])
        self.assertEqual(result['scores'],{'name_similarity':'0.9000'})
        db.execute.assert_not_called()

    def test_frozen_member_evidence_survives_candidate_correction_and_is_role_scoped(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        from backend.app.services import registry,claims
        from backend.tests.test_registry import RegistryTests
        with Harness() as h,TestClient(app) as client:
            def register(role,barangay):
                req=RegistryTests().request(h,beneficiary_actor_id=h.actors[role],declared_barangay_id=barangay,members=[{'name':'Invented Tala Salonga','birth_date':date(1980,1,2),'relationship':'head','is_head':True}])
                ack=execute_command(h.actors[role],'registry.register',role,req,lambda tx:registry.register(tx,req))
                return UUID(ack['resources'][0]['id'])
            own=register('beneficiary',h.barangays[0]);candidate=register('beneficiary2',h.barangays[1])
            operation={'disaster_id':h.disasters[0],'barangay_ids':h.barangays,'response_hours':48,'basis_evidence_id':h.upload('operation_basis')}
            execute_command(h.actors['dswd'],'intake.open','open',operation,lambda tx:registry.open_intake(tx,operation))
            req={'household_id':own,'disaster_id':h.disasters[0],'stated_category_id':h.categories[0],'damage_description':'Invented damage','evidence_ids':[],'new_information':None}
            ack=execute_command(h.actors['beneficiary'],'claim.submit','submit',req,lambda tx:claims.submit(tx,req));claim=ack['resources'][0]['id']
            def detail(role):
                response=client.get('/api/v1/claims/'+claim,headers={'X-Demo-Actor-ID':str(h.actors[role])})
                self.assertEqual(response.status_code,200,response.text)
                return response.json()['data']
            before=detail('dswd')['latest_check']
            flag=next(f for f in before['flags'] if f['code']=='person_in_two_households')
            compared=flag['comparison']['candidate']
            self.assertEqual(compared['members'][0]['name'],'Invented Tala Salonga')
            self.assertEqual(compared['members'][0]['birth_date'],'1980-01-02')
            self.assertIn('registry_version_id',compared)
            self.assertNotIn('latest_check',detail('barangay'))
            self.assertNotIn('latest_check',detail('beneficiary'))
            denied=client.get('/api/v1/claims/'+claim,headers={'X-Demo-Actor-ID':str(h.actors['beneficiary2'])})
            self.assertEqual(denied.status_code,404)
            correction={'expected_revision':0,'action':'facts_correct','reason':'Invented correction','address':'Invented corrected street 91'}
            execute_command(h.actors['dswd'],'registry.review','correct',correction,lambda tx:registry.review(tx,candidate,correction))
            after=detail('auditor')['latest_check']
            self.assertTrue(after['stale'])
            frozen=next(f for f in after['flags'] if f['code']=='person_in_two_households')['comparison']['candidate']
            self.assertEqual(frozen['address'],compared['address'])
            self.assertEqual(frozen['registry_version_id'],compared['registry_version_id'])
            self.assertTrue(frozen['version_changed'])
            serialized=json.dumps(after)
            self.assertNotIn('"id_number":',serialized);self.assertNotIn('"phone":',serialized)
            headers={'X-Demo-Actor-ID':str(h.actors['auditor']),'Idempotency-Key':'auditor-recheck'}
            response=client.post('/api/v1/claims/'+claim+'/recheck',headers=headers,json={'expected_revision':0})
            self.assertEqual(response.status_code,403)
            headers={'X-Demo-Actor-ID':str(h.actors['dswd']),'Idempotency-Key':'refresh-comparison'}
            revision=detail('dswd')['revision']
            response=client.post('/api/v1/claims/'+claim+'/recheck',headers=headers,json={'expected_revision':revision})
            self.assertEqual(response.status_code,200,response.text)
            refreshed=detail('dswd')['latest_check']
            self.assertNotEqual(refreshed['id'],before['id']);self.assertFalse(refreshed['stale'])
            replay=client.post('/api/v1/claims/'+claim+'/recheck',headers=headers,json={'expected_revision':revision})
            self.assertEqual(replay.status_code,200,replay.text)
            self.assertEqual(detail('dswd')['latest_check']['id'],refreshed['id'])
            with h.connection() as db:
                saved=db.execute('SELECT scores FROM check_flags WHERE check_run_id=%s AND code=%s',(UUID(before['id']),'person_in_two_households')).fetchone()['scores']
                self.assertEqual(saved['comparison']['candidate']['registry_version_id'],compared['registry_version_id'])
                self.assertGreater(db.execute("SELECT count(*) n FROM audit_events WHERE action='claim.check'").fetchone()['n'],1)
