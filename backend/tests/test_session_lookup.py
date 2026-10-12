import unittest
from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.tests.support import Harness
from backend.tests.test_sessions import SessionTests
from backend.app.commands import execute_command
from backend.app.services import sessions

class SessionLookupTests(unittest.TestCase):
    def test_role_and_input_boundaries(self):
        with Harness() as h, TestClient(app) as client:
            endpoint=f'/api/v1/sessions/{uuid4()}/lookup'
            for role in ['beneficiary','barangay','dswd','auditor']:
                response=client.post(endpoint,headers={'X-Demo-Actor-ID':str(h.actors[role])},json={'reference':str(uuid4())})
                self.assertEqual(response.status_code,403,role)
            headers={'X-Demo-Actor-ID':str(h.actors['disbursing'])}
            self.assertEqual(client.post(endpoint,headers=headers,json={'reference':'DFC-2026-0001'}).status_code,422)
            self.assertEqual(client.post(endpoint,headers=headers,json={'reference':str(uuid4()),'household_id':str(uuid4())}).status_code,422)
            self.assertEqual(client.post(endpoint,headers=headers,json={'reference':str(uuid4())}).status_code,404)
            self.assertEqual(client.post(endpoint,headers=headers,json={'reference':'AYUDACHAIN:TRANSACTION:'+str(uuid4()).upper()}).status_code,404)

    def test_actual_published_session_lookup_has_no_mutation_or_secret(self):
        with Harness() as h, TestClient(app) as client:
            h.register_chain();req,entry=SessionTests().payable(h)
            ack=execute_command(h.actors['dswd'],'session.schedule','lookup-session',req,lambda tx:sessions.schedule(tx,req))
            with h.connection() as db:
                session=db.execute('SELECT session_id FROM session_versions WHERE id=%s',(UUID(ack['resources'][0]['id']),)).fetchone()['session_id']
                transaction=db.execute('SELECT id FROM payout_transactions WHERE entitlement_id=%s',(entry['entitlement_id'],)).fetchone()['id']
                before=db.execute('SELECT count(*) n FROM audit_events').fetchone()['n']
            headers={'X-Demo-Actor-ID':str(h.actors['disbursing'])};endpoint=f'/api/v1/sessions/{session}/lookup'
            projected=client.get(f'/api/v1/transactions/{transaction}',headers=headers)
            self.assertEqual(projected.status_code,200)
            self.assertEqual(projected.json()['data']['disaster_id'],str(h.disasters[0]))
            for reference in [str(transaction),f'ayudachain:transaction:{transaction}',str(transaction)]:
                response=client.post(endpoint,headers=headers,json={'reference':reference})
                self.assertEqual(response.status_code,200,response.text)
                self.assertEqual(response.json()['data'],{'transaction_id':str(transaction)})
            unknown=client.post(endpoint,headers=headers,json={'reference':str(uuid4())})
            wrong=client.post(f'/api/v1/sessions/{uuid4()}/lookup',headers=headers,json={'reference':str(transaction)})
            self.assertEqual((unknown.status_code,unknown.json()),(wrong.status_code,wrong.json()))
            with h.connection() as db:
                self.assertEqual(before,db.execute('SELECT count(*) n FROM audit_events').fetchone()['n'])
                self.assertEqual(0,db.execute('SELECT count(*) n FROM payout_attempts').fetchone()['n'])
                self.assertEqual(0,db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'])
            change={'expected_revision':0,'action':'amend','reason':'Invented reassignment','cash_actor_ids':[h.actors['disbursing2']]}
            execute_command(h.actors['dswd'],'session.change','remove-payer',change,lambda tx:sessions.change(tx,session,change))
            self.assertEqual(client.post(endpoint,headers=headers,json={'reference':str(transaction)}).status_code,404)
