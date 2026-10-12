import importlib.util
import unittest
from backend.tests.support import Harness
from backend.app.actor import resolve_identity
from backend.app.commands import DomainError


class AuditTests(unittest.TestCase):
    def test_read_only_overview_and_timeline_log_private_inspection_only(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.audit_views'))
        from backend.app.services.audit_views import overview,timeline,inspection_history
        with Harness() as h:
            with h.connection() as db:
                auditor=resolve_identity(db,h.actors['auditor'])
                officer=resolve_identity(db,h.actors['dswd'])
                before=db.execute('SELECT count(*) n FROM audit_events').fetchone()['n']
            view=overview(auditor,h.disasters[0]);self.assertEqual(view['population']['claims'],0)
            self.assertIn('denominators',view);self.assertIn('not a fraud finding',view['interpretation'])
            events=timeline(auditor,'evaluation_run_id',h.run)
            self.assertTrue(events)
            private=inspection_history(auditor);self.assertGreaterEqual(len(private),2)
            with self.assertRaises(DomainError):inspection_history(officer)
            with h.connection() as db:
                self.assertEqual(before,db.execute('SELECT count(*) n FROM audit_events').fetchone()['n'])
                with self.assertRaises(Exception):db.execute('SELECT * FROM auditor_access_events')

    def test_all_roles_binary_material_history_errors_and_private_answer_noninterference(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        from backend.tests.test_outcomes import OutcomeTests
        from backend.app.commands import execute_command
        from backend.app.services import outcomes
        with Harness() as h,TestClient(app) as client:
            h.register_chain();s,t,e=OutcomeTests().handover(h)
            with h.connection() as db:
                photo=db.execute('SELECT head_photo_evidence_id,id_evidence_id FROM household_versions WHERE id=(SELECT registry_version_id FROM entitlement_versions WHERE id=%s)',(e['current_version_id'],)).fetchone()
                proof=db.execute("SELECT id FROM commitments WHERE kind='handover'").fetchone()['id']
            def get(path,role):return client.get('/api/v1'+path,headers={'X-Demo-Actor-ID':str(h.actors[role])})
            before=get('/transactions/'+str(t['id']),'disbursing').json()['data']
            req={'answer':'received_less','expected_latest_id':None};execute_command(h.actors['beneficiary'],'outcome.record','private',req,lambda tx:outcomes.answer(tx,t['id'],req))
            after=get('/transactions/'+str(t['id']),'disbursing').json()['data'];self.assertEqual(before,after)
            for role in ['dswd','auditor','beneficiary','barangay','disbursing','beneficiary2']:
                allowed=role in {'dswd','auditor','beneficiary'}
                response=get('/transactions/'+str(t['id'])+'/private-outcomes',role)
                self.assertEqual(response.status_code,200 if allowed else 404)
                full=get('/commitments/'+str(proof)+'/material',role)
                self.assertEqual(full.status_code,200 if role in {'dswd','auditor','beneficiary','disbursing'} else 404)
                for field in ['head_photo_evidence_id','id_evidence_id']:
                    binary=get('/evidence/'+str(photo[field])+'/content',role)
                    file_allowed=allowed or (role=='disbursing' and field=='head_photo_evidence_id')
                    self.assertEqual(binary.status_code,200 if file_allowed else 404,(role,field))
                history=get('/audit/timeline/evaluation_run_id/'+str(h.run),role)
                self.assertEqual(history.status_code,200 if role in {'dswd','auditor'} else 403)
                inspection=get('/audit/own-inspections',role)
                self.assertEqual(inspection.status_code,200 if role=='auditor' else 403)
            invalid=client.post('/api/v1/transactions/'+str(t['id'])+'/handover',headers={'X-Demo-Actor-ID':str(h.actors['disbursing']),'Idempotency-Key':'invalid'},json={'amount_centavos':'42','code':'private-test-secret'})
            self.assertEqual(invalid.status_code,422);self.assertNotIn('private-test-secret',invalid.text)
