import unittest
from uuid import UUID,uuid4
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError
from backend.app.services import outcomes

class CaseRaceTests(unittest.TestCase):
    def test_timeout_and_answer_serialize_then_late_answer_preserves_one_receipt(self):
        from backend.tests.test_outcomes import OutcomeTests
        with Harness() as h:
            h.register_chain();s,t,e=OutcomeTests().handover(h)
            with h.connection() as db:db.execute("UPDATE evaluation_runs SET clock_mode='simulated',clock_offset=interval '73 hours'")
            request={'answer':'received_full','expected_latest_id':None}
            def run(human):
                try:
                    return execute_command(h.actors['beneficiary' if human else 'system'],'outcome.record' if human else 'outcome.timeout',str(uuid4()),request if human else {},lambda tx:outcomes.answer(tx,t['id'],request) if human else outcomes.timeout(tx,t['id']),system=not human)
                except DomainError:return None
            with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,[True,False]))
            with h.connection() as db:
                rows=db.execute('SELECT * FROM outcome_versions ORDER BY created_at').fetchall();self.assertEqual(len(rows),1)
                self.assertEqual(db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'],1)
            if rows[0]['answer']=='unconfirmed':
                request['expected_latest_id']=rows[0]['id'];execute_command(h.actors['beneficiary'],'outcome.record','late',request,lambda tx:outcomes.answer(tx,t['id'],request))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT o.answer FROM payout_transactions t JOIN outcome_versions o ON o.id=t.current_outcome_id').fetchone()['answer'],'received_full')
                self.assertEqual(db.execute('SELECT business_status FROM entitlements').fetchone()['business_status'],'handed_over')

    def test_human_challenge_resolution_and_cash_race_cancel_or_retain_paid_evidence(self):
        from backend.tests.test_authorization_changes import AuthorizationChangesTests
        from backend.app.services import registry,payouts
        with Harness() as h:
            h.register_chain();s,t,e,a,cash=AuthorizationChangesTests().prepare(h)
            with h.connection() as db:hh=db.execute('SELECT * FROM households').fetchone();le=db.execute('SELECT * FROM approved_list_entries ORDER BY created_at DESC LIMIT 1').fetchone()
            # Independent DSWD residence confirmation grants the declared resident view.
            review={'expected_revision':hh['revision'],'action':'residence_confirm','reason':'Invented residence checked'}
            execute_command(h.actors['dswd'],'registry.review','resident',review,lambda tx:registry.review(tx,hh['id'],review))
            report={'text':'Invented documented concern before cash','evidence_ids':[]}
            ack=execute_command(h.actors['beneficiary'],'challenge.report','report',report,lambda tx:outcomes.challenge(tx,le['id'],report))
            with h.connection() as db:case=db.execute('SELECT * FROM list_challenges').fetchone()
            review={'expected_revision':0,'action':'review','text':'Invented human investigation'}
            execute_command(h.actors['dswd'],'challenge.review','review',review,lambda tx:outcomes.challenge_action(tx,case['id'],review))
            resolution={'expected_revision':1,'action':'substantiate','text':'Invented substantiated review'}
            def run(hand):
                try:return execute_command(h.actors['disbursing' if hand else 'dswd'],'handover' if hand else 'challenge.resolve',str(uuid4()),cash if hand else resolution,lambda tx:payouts.handover(tx,t['id'],cash) if hand else outcomes.challenge_action(tx,case['id'],resolution))
                except DomainError:return None
            with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,[True,False]))
            with h.connection() as db:
                count=db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'];status=db.execute('SELECT business_status FROM entitlements').fetchone()['business_status']
                self.assertEqual(status,'handed_over' if count else 'cancelled')
                self.assertEqual(db.execute('SELECT business_status FROM list_challenges').fetchone()['business_status'],'closed')
                self.assertEqual(db.execute("SELECT count(*) n FROM claim_decisions WHERE action='reverse_approval'").fetchone()['n'],0 if count else 1)
                self.assertEqual(db.execute('SELECT count(*) n FROM payout_transactions').fetchone()['n'],1)
            with self.assertRaises(DomainError):execute_command(h.actors['disbursing'],'handover','repeat',cash,lambda tx:payouts.handover(tx,t['id'],cash))
