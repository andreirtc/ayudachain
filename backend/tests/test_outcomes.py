import importlib.util
import unittest
from uuid import UUID,uuid4
from concurrent.futures import ThreadPoolExecutor
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError


class OutcomeTests(unittest.TestCase):
    def service(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.outcomes'),'Private outcomes/cases/challenges service missing')
        from backend.app.services import outcomes
        return outcomes

    def handover(self,h,assisted=False):
        from backend.tests.test_payouts import PayoutTests
        from backend.app.services import payouts
        s,t,e=PayoutTests().session(h)
        if assisted:
            req={'household_id':e['household_id'],'result':'pass','accepted_id_type':'Synthetic photo ID','person_photo_compared':True,'reason':None,'attempt_id':None}
            execute_command(h.actors['disbursing'],'id.check','pre-pin',req,lambda tx:payouts.id_check(tx,s['id'],req))
            with h.connection() as db:check=db.execute('SELECT id FROM identity_checks ORDER BY created_at DESC LIMIT 1').fetchone()['id']
            pin={'identity_check_id':check,'pin':'837261'};execute_command(h.actors['beneficiary'],'pin.set','pin',pin,lambda tx:payouts.establish_pin(tx,e['household_id'],pin))
        req={'expected_revision':t['revision'],'path':'assisted' if assisted else 'own_device','pin':'837261' if assisted else None}
        ack=execute_command(h.actors['beneficiary'],'attempt.open','open',req,lambda tx:payouts.open_attempt(tx,e['id'],req))
        with h.connection() as db:attempt=db.execute('SELECT * FROM payout_attempts').fetchone()
        check={'household_id':e['household_id'],'result':'pass','accepted_id_type':'Synthetic photo ID','person_photo_compared':True,'reason':None,'attempt_id':attempt['id']}
        execute_command(h.actors['disbursing'],'id.check','present',check,lambda tx:payouts.id_check(tx,s['id'],check))
        with h.connection() as db:t=db.execute('SELECT * FROM payout_transactions').fetchone()
        req={'expected_revision':t['revision'],'attempt_id':attempt['id'],'code':ack['code'],'checker_actor_id':h.actors['disbursing2'] if assisted else None}
        execute_command(h.actors['disbursing'],'handover','cash',req,lambda tx:payouts.handover(tx,t['id'],req))
        return s,t,e

    def test_adverse_resolution_full_then_adverse_reopens_one_case_without_repayment(self):
        svc=self.service()
        with Harness() as h:
            h.register_chain();s,t,e=self.handover(h)
            req={'answer':'received_less','expected_latest_id':None}
            ack=execute_command(h.actors['beneficiary'],'outcome.record','less',req,lambda tx:svc.answer(tx,t['id'],req))
            with h.connection() as db:case=db.execute('SELECT * FROM grievances').fetchone();first=db.execute('SELECT current_outcome_id FROM payout_transactions').fetchone()['current_outcome_id']
            review={'expected_revision':0,'action':'review','text':'Invented private review'};execute_command(h.actors['dswd'],'case.review','review',review,lambda tx:svc.case_action(tx,case['id'],review))
            resolve={'expected_revision':1,'action':'resolve','text':'Invented resolution without another payout'};execute_command(h.actors['dswd'],'case.resolve','resolve',resolve,lambda tx:svc.case_action(tx,case['id'],resolve))
            req={'answer':'received_full','expected_latest_id':first};execute_command(h.actors['beneficiary'],'outcome.record','full',req,lambda tx:svc.answer(tx,t['id'],req))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT business_status FROM grievances').fetchone()['business_status'],'closed');latest=db.execute('SELECT current_outcome_id FROM payout_transactions').fetchone()['current_outcome_id']
            req={'answer':'not_received','expected_latest_id':latest};execute_command(h.actors['beneficiary'],'outcome.record','adverse',req,lambda tx:svc.answer(tx,t['id'],req))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM grievances').fetchone()['n'],1);self.assertEqual(db.execute('SELECT business_status FROM grievances').fetchone()['business_status'],'open')
                self.assertEqual(db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'],1);self.assertEqual(db.execute('SELECT business_status FROM entitlements').fetchone()['business_status'],'handed_over')
                self.assertEqual(db.execute("SELECT count(*) n FROM grievance_events WHERE kind='resolve'").fetchone()['n'],1)
                from backend.app.actor import resolve_identity
                from backend.app.services.payouts import project
                payer=project(db,resolve_identity(db,h.actors['disbursing']),t['id']);self.assertNotIn('outcome',str(payer));self.assertNotIn('grievance',str(payer));self.assertNotIn('revision',payer)

    def test_assisted_actual_payer_is_barred_from_exit_answer_and_checker_can_answer_after_close(self):
        svc=self.service()
        with Harness() as h:
            h.register_chain();s,t,e=self.handover(h,assisted=True)
            from backend.app.services import sessions
            req={'expected_revision':1,'action':'close','reason':'Invented closing'};execute_command(h.actors['dswd'],'session.close','close',req,lambda tx:sessions.change(tx,s['id'],req))
            req={'answer':'received_full','expected_latest_id':None}
            with self.assertRaises(DomainError):execute_command(h.actors['disbursing'],'outcome.record','payer',req,lambda tx:svc.answer(tx,t['id'],req))
            execute_command(h.actors['disbursing2'],'outcome.record','checker',req,lambda tx:svc.answer(tx,t['id'],req))
            with h.connection() as db:self.assertEqual(db.execute('SELECT answer FROM outcome_versions').fetchone()['answer'],'received_full')
