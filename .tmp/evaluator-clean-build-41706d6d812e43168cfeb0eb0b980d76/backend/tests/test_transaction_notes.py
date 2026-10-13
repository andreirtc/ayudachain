import unittest
from fastapi.testclient import TestClient
from backend.tests.support import Harness
from backend.tests import test_outcomes
from backend.app.main import app
from backend.app.commands import execute_command
from backend.app.services import sessions


class TransactionNoteTests(unittest.TestCase):
    def test_dswd_and_assigned_officer_append_after_closure_without_private_leak_or_anchor(self):
        with Harness() as h,TestClient(app) as client:
            h.register_chain();session,transaction,entitlement=test_outcomes.OutcomeTests().handover(h)
            close={'expected_revision':1,'action':'close','reason':'Invented cash closure'}
            execute_command(h.actors['dswd'],'session.change','close',close,lambda tx:sessions.change(tx,session['id'],close))
            path='/api/v1/transactions/'+str(transaction['id'])+'/notes'
            def headers(role,key):return {'X-Demo-Actor-ID':str(h.actors[role]),'Idempotency-Key':key}
            with h.connection() as db:proof_count=db.execute('SELECT count(*) n FROM commitments').fetchone()['n']
            dswd=client.post(path,headers=headers('dswd','office-note'),json={'text':'Invented private office follow-up details','evidence_ids':[]})
            self.assertEqual(dswd.status_code,200,dswd.text)
            officer=client.post(path,headers=headers('disbursing','officer-note'),json={'text':'Invented cash site closed; continue follow-up','evidence_ids':[]})
            self.assertEqual(officer.status_code,200,officer.text)
            for role in ['auditor','beneficiary','barangay']:
                self.assertEqual(client.post(path,headers=headers(role,'denied-note'),json={'text':'Invented rejected note'}).status_code,403)
            self.assertEqual(client.post(path,headers=headers('dswd','blank-note'),json={'text':' \t '}).status_code,422)
            own=client.get(path,headers=headers('disbursing','read-own'))
            self.assertEqual(own.status_code,200,own.text);self.assertEqual(len(own.json()['data']),1)
            self.assertNotIn('private office follow-up',own.text)
            inspected=client.get(path,headers=headers('auditor','read-all'))
            self.assertEqual(inspected.status_code,200);self.assertEqual(len(inspected.json()['data']),2)
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM commitments').fetchone()['n'],proof_count)
                self.assertEqual(db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'],1)
                self.assertEqual(db.execute("SELECT count(*) n FROM audit_events WHERE action='transaction.note'").fetchone()['n'],2)
