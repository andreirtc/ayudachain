import importlib.util
import unittest
from uuid import UUID,uuid4
from concurrent.futures import ThreadPoolExecutor
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError


class PayoutTests(unittest.TestCase):
    def service(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.payouts'),'Recipient authorization/once-only handover service missing')
        from backend.app.services import payouts
        return payouts

    def session(self,h):
        from backend.tests.test_sessions import SessionTests
        from backend.app.services import sessions,registry,entitlements
        from backend.scripts.synthetic_evidence import synthetic_portrait
        req,entry=SessionTests().payable(h)
        with h.connection() as db:household=db.execute('SELECT household_id FROM entitlements WHERE id=%s',(entry['entitlement_id'],)).fetchone()['household_id']
        review={'expected_revision':0,'action':'field_check','reason':'Invented documented field check','id_type':'Synthetic photo ID','id_number':None,'head_photo_evidence_id':h.upload('identity_photo',synthetic_portrait(),actor='beneficiary',prepared_for=h.actors['beneficiary']),'id_evidence_id':h.upload('identity_document',actor='beneficiary',prepared_for=h.actors['beneficiary']),'field_evidence_id':h.upload('field_check'),'person_photo_compared':True,'accepted_id_type':'Synthetic photo ID'}
        execute_command(h.actors['dswd'],'registry.review','field',review,lambda tx:registry.review(tx,household,review))
        lr={'disaster_id':h.disasters[0],'barangay_id':h.barangays[2],'expected_revision':None}
        ack=execute_command(h.actors['dswd'],'list.request','updated-list',lr,lambda tx:entitlements.request_list(tx,lr));h.drain_anchors()
        with h.connection() as db:entry=db.execute('SELECT * FROM approved_list_entries WHERE list_version_id=%s',(UUID(ack['resources'][0]['id']),)).fetchone()
        req.update(list_version_id=entry['list_version_id'],list_entry_ids=[entry['id']])
        ack=execute_command(h.actors['dswd'],'session.schedule','session',req,lambda tx:sessions.schedule(tx,req));version=UUID(ack['resources'][0]['id'])
        change={'expected_revision':0,'action':'open','reason':'Invented opening'};execute_command(h.actors['dswd'],'session.change','open',change,lambda tx:sessions.change(tx,version,change))
        with h.connection() as db:
            session=db.execute('SELECT * FROM payout_sessions').fetchone();transaction=db.execute('SELECT * FROM payout_transactions').fetchone();entitlement=db.execute('SELECT * FROM entitlements').fetchone()
        return session,transaction,entitlement

    def test_two_clients_different_keys_save_one_receipt_and_replay_never_reveals_code(self):
        svc=self.service()
        with Harness() as h:
            h.register_chain();s,t,e=self.session(h)
            opening={'expected_revision':t['revision'],'path':'own_device','pin':None}
            ack=execute_command(h.actors['beneficiary'],'attempt.open','open-attempt',opening,lambda tx:svc.open_attempt(tx,e['id'],opening));code=ack['code']
            replay=execute_command(h.actors['beneficiary'],'attempt.open','open-attempt',opening,lambda tx:svc.open_attempt(tx,e['id'],opening));self.assertNotIn('code',replay)
            with h.connection() as db:attempt=db.execute('SELECT * FROM payout_attempts').fetchone()
            check={'household_id':e['household_id'],'result':'pass','accepted_id_type':'Synthetic photo ID','person_photo_compared':True,'reason':None,'attempt_id':attempt['id']}
            execute_command(h.actors['disbursing'],'id.check','present',check,lambda tx:svc.id_check(tx,s['id'],check))
            with h.connection() as db:t=db.execute('SELECT * FROM payout_transactions').fetchone()
            request={'expected_revision':t['revision'],'attempt_id':attempt['id'],'code':code,'checker_actor_id':None}
            def run(_):
                try:return execute_command(h.actors['disbursing'],'handover',str(uuid4()),request,lambda tx:svc.handover(tx,t['id'],request))
                except DomainError:return None
            with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,[0,1]))
            self.assertEqual(sum(r is not None for r in results),1)
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'],1)
                self.assertEqual(db.execute("SELECT count(*) n FROM attempt_events WHERE action='handover'").fetchone()['n'],1)
                self.assertEqual(db.execute("SELECT count(*) n FROM commitments WHERE kind='handover'").fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT amount_centavos FROM recorded_handovers').fetchone()['amount_centavos'],495000)
            with self.assertRaises(DomainError):execute_command(h.actors['beneficiary'],'attempt.open','again',dict(opening,expected_revision=t['revision']+1),lambda tx:svc.open_attempt(tx,e['id'],dict(opening,expected_revision=t['revision']+1)))
