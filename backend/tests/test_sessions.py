import importlib.util
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from uuid import UUID
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError


class SessionTests(unittest.TestCase):
    def service(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.sessions'),'Session/notification service missing')
        from backend.app.services import sessions
        return sessions

    def payable(self,h):
        from backend.tests.test_entitlements import EntitlementTests
        from backend.app.services import entitlements
        helper=EntitlementTests();claim=helper.pending_claim(h);decision=helper.decision(h,claim)
        execute_command(h.actors['dswd'],'claim.decide','approve',decision,lambda tx:entitlements.decide(tx,claim,decision))
        inputs=helper.inputs(h);execute_command(h.actors['dswd'],'inputs.save','inputs',inputs,lambda tx:entitlements.save_inputs(tx,inputs))
        req={'disaster_id':h.disasters[0],'barangay_id':h.barangays[2],'expected_revision':None}
        ack=execute_command(h.actors['dswd'],'list.request','list',req,lambda tx:entitlements.request_list(tx,req));h.drain_anchors()
        with h.connection() as db:
            entry=db.execute('SELECT * FROM approved_list_entries WHERE list_version_id=%s',(UUID(ack['resources'][0]['id']),)).fetchone()
        return {'disaster_id':h.disasters[0],'barangay_id':h.barangays[2],'list_version_id':entry['list_version_id'],'list_entry_ids':[entry['id']],'date':datetime.now(ZoneInfo('Asia/Manila')).date(),'site':'Invented school hall','cash_actor_ids':[h.actors['disbursing'],h.actors['disbursing2']],'followup_actor_ids':[]},entry

    def test_real_publication_session_lifecycle_and_secret_free_notices(self):
        svc=self.service()
        with Harness() as h:
            h.register_chain();req,entry=self.payable(h)
            ack=execute_command(h.actors['dswd'],'session.schedule','schedule',req,lambda tx:svc.schedule(tx,req));identity=UUID(ack['resources'][0]['id'])
            opened={'expected_revision':0,'action':'open','reason':'Invented local cash opening'}
            execute_command(h.actors['dswd'],'session.open','open',opened,lambda tx:svc.change(tx,identity,opened))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT business_status FROM payout_sessions').fetchone()['business_status'],'open')
                notices=db.execute('SELECT * FROM notifications WHERE purpose=%s',('session_scheduled',)).fetchall();self.assertEqual(len(notices),2)
                self.assertTrue(next(n for n in notices if n['channel']=='simulated_notice_sms')['simulated'])
                self.assertEqual(next(n for n in notices if n['channel']=='simulated_notice_sms')['state'],'no_contact')
                self.assertNotIn('code',str([n['content'] for n in notices]).lower())
            closed={'expected_revision':1,'action':'close','reason':'Invented closing'}
            execute_command(h.actors['dswd'],'session.close','close',closed,lambda tx:svc.change(tx,identity,closed))
            with self.assertRaises(DomainError):execute_command(h.actors['dswd'],'session.reopen','reopen',dict(opened,expected_revision=2),lambda tx:svc.change(tx,identity,dict(opened,expected_revision=2)))
