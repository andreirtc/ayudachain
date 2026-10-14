import unittest
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError
from backend.app.services.evidence import prepare_upload,save_upload


class EvidencePrivacyTests(unittest.TestCase):
    def test_helper_upload_ack_does_not_grant_original_read(self):
        with Harness() as h:
            from fastapi.testclient import TestClient
            from backend.app.main import app
            c=TestClient(app)
            r=c.post('/api/v1/evidence',headers={'X-Demo-Actor-ID':str(h.actors['barangay']),'Idempotency-Key':'private-upload'},
                     data={'purpose':'identity_photo','prepared_for_actor_id':str(h.actors['beneficiary'])},files={'file':('synthetic.png',b'\x89PNG\r\n\x1a\nInvented photo','image/png')})
            self.assertEqual(r.status_code,200)
            self.assertNotIn('byte_sha256',str(r.json()))
            identity=r.json()['data']['resources'][0]['id']
            self.assertEqual(c.get('/api/v1/evidence/'+identity+'/content',headers={'X-Demo-Actor-ID':str(h.actors['barangay'])}).status_code,404)
            self.assertEqual(c.get('/api/v1/evidence/'+identity+'/content',headers={'X-Demo-Actor-ID':str(h.actors['beneficiary'])}).status_code,200)

    def test_auditor_file_read_is_private_and_logging_failure_blocks_disclosure(self):
        with Harness() as h:
            from fastapi.testclient import TestClient
            from backend.app.main import app
            c=TestClient(app)
            r=c.post('/api/v1/evidence',headers={'X-Demo-Actor-ID':str(h.actors['dswd']),'Idempotency-Key':'source'},data={'purpose':'release_source'},files={'file':('synthetic.png',b'\x89PNG\r\n\x1a\nInvented release','image/png')})
            self.assertEqual(r.status_code,200)
            identity=r.json()['data']['resources'][0]['id']
            with h.connection() as db: before=db.execute('SELECT count(*) n FROM audit_events').fetchone()['n']
            from unittest.mock import patch
            import psycopg
            with patch('backend.app.services.access.connection',side_effect=psycopg.OperationalError('isolated log outage')):
                denied=c.get('/api/v1/evidence/'+identity+'/content',headers={'X-Demo-Actor-ID':str(h.actors['auditor'])})
            self.assertEqual(denied.status_code,503)
            self.assertNotIn('Invented release',denied.text)
            r=c.get('/api/v1/evidence/'+identity+'/content',headers={'X-Demo-Actor-ID':str(h.actors['auditor'])})
            self.assertEqual(r.status_code,200)
            with h.connection() as db:
                self.assertEqual(before,db.execute('SELECT count(*) n FROM audit_events').fetchone()['n'])
                import psycopg
                with self.assertRaises(psycopg.errors.InsufficientPrivilege): db.execute('SELECT * FROM auditor_access_events')
