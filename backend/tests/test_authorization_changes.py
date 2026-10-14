import unittest
from uuid import UUID,uuid4
from datetime import timedelta
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError
from backend.app.services import payouts,registry,sessions,entitlements


class AuthorizationChangesTests(unittest.TestCase):
    def test_secret_failure_replays_count_once_and_cooldowns_do_not_create_outcomes(self):
        with Harness() as h:
            h.register_chain();s,t,e,a,req=self.prepare(h,True)
            wrong=dict(req,code='000000' if req['code']!='000000' else '111111')
            for index in range(5):
                for _ in range(2):
                    with self.assertRaises(DomainError):execute_command(h.actors['disbursing'],'handover','bad-code-'+str(index),wrong,lambda tx:payouts.handover(tx,t['id'],wrong))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT bad_code_count FROM payout_attempts').fetchone()['bad_code_count'],5)
                self.assertEqual(db.execute('SELECT count(*) n FROM outcome_versions').fetchone()['n'],0)
                revision=db.execute('SELECT revision FROM payout_transactions').fetchone()['revision']
            opening={'expected_revision':revision,'path':'assisted','pin':'837261'}
            with self.assertRaises(DomainError) as blocked:execute_command(h.actors['beneficiary'],'attempt.open','cooldown',opening,lambda tx:payouts.open_attempt(tx,e['id'],opening))
            self.assertEqual(blocked.exception.status,429)
            with h.connection() as db:db.execute("UPDATE evaluation_runs SET clock_mode='simulated',clock_offset=interval '11 minutes'")
            wrong_pin=dict(opening,pin='000001')
            for index in range(5):
                for _ in range(2):
                    with self.assertRaises(DomainError):execute_command(h.actors['beneficiary'],'attempt.open','bad-pin-'+str(index),wrong_pin,lambda tx:payouts.open_attempt(tx,e['id'],wrong_pin))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT failed_count FROM credential_counters').fetchone()['failed_count'],5)
                self.assertNotIn('000001',str(db.execute('SELECT safe_details FROM audit_events').fetchall()))
            with self.assertRaises(DomainError) as blocked:execute_command(h.actors['beneficiary'],'attempt.open','pin-cooldown',opening,lambda tx:payouts.open_attempt(tx,e['id'],opening))
            self.assertEqual(blocked.exception.status,429)
            with h.connection() as db:db.execute("UPDATE evaluation_runs SET clock_offset=interval '27 minutes'")
            execute_command(h.actors['beneficiary'],'attempt.open','valid-after-expiry',opening,lambda tx:payouts.open_attempt(tx,e['id'],opening))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM payout_transactions').fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT count(*) n FROM payout_attempts').fetchone()['n'],2)
                self.assertEqual(db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'],0)

    def prepare(self,h,assisted=False):
        from backend.tests.test_payouts import PayoutTests
        s,t,e=PayoutTests().session(h)
        if assisted:
            check={'household_id':e['household_id'],'result':'pass','accepted_id_type':'Synthetic ID','person_photo_compared':True,'reason':None,'attempt_id':None}
            execute_command(h.actors['disbursing'],'id.check','prior',check,lambda tx:payouts.id_check(tx,s['id'],check))
            with h.connection() as db:i=db.execute('SELECT id FROM identity_checks').fetchone()['id']
            pin={'identity_check_id':i,'pin':'837261'}
            execute_command(h.actors['beneficiary'],'pin.set','pin',pin,lambda tx:payouts.establish_pin(tx,e['household_id'],pin))
        opening={'expected_revision':t['revision'],'path':'assisted' if assisted else 'own_device','pin':'837261' if assisted else None}
        ack=execute_command(h.actors['beneficiary'],'attempt.open','authorize',opening,lambda tx:payouts.open_attempt(tx,e['id'],opening))
        with h.connection() as db:a=db.execute('SELECT * FROM payout_attempts').fetchone()
        check={'household_id':e['household_id'],'result':'pass','accepted_id_type':'Synthetic ID','person_photo_compared':True,'reason':None,'attempt_id':a['id']}
        execute_command(h.actors['disbursing'],'id.check','present',check,lambda tx:payouts.id_check(tx,s['id'],check))
        with h.connection() as db:t=db.execute('SELECT * FROM payout_transactions').fetchone()
        return s,t,e,a,{'expected_revision':t['revision'],'attempt_id':a['id'],'code':ack['code'],'checker_actor_id':h.actors['disbursing2'] if assisted else None}

    def test_absent_checker_records_hold_and_replay_does_not_duplicate_it(self):
        with Harness() as h:
            h.register_chain();s,t,e,a,req=self.prepare(h,True);req['checker_actor_id']=None
            for _ in range(2):
                with self.assertRaises(DomainError):execute_command(h.actors['disbursing'],'handover','absent',req,lambda tx:payouts.handover(tx,t['id'],req))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT business_status FROM entitlements').fetchone()['business_status'],'held')
                self.assertEqual(db.execute("SELECT count(*) n FROM audit_events WHERE action='entitlement.checker_unavailable'").fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'],0)
                self.assertIsNone(db.execute('SELECT consumed_at FROM payout_codes').fetchone()['consumed_at'])
            req['checker_actor_id']=h.actors['disbursing2']
            with self.assertRaises(DomainError):execute_command(h.actors['disbursing'],'handover','still-held',req,lambda tx:payouts.handover(tx,t['id'],req))
            amend={'expected_revision':1,'action':'amend','reason':'Invented independent checker now available'}
            execute_command(h.actors['dswd'],'session.change','checker-resolved',amend,lambda tx:sessions.change(tx,s['id'],amend))
            execute_command(h.actors['disbursing'],'handover','cash',req,lambda tx:payouts.handover(tx,t['id'],req))

    def test_staff_deactivation_invalidates_presented_code_without_cash(self):
        with Harness() as h:
            h.register_chain();s,t,e,a,req=self.prepare(h)
            decision={'expected_revision':0,'status':'deactivated','reason':'Invented officer unavailable'}
            execute_command(h.actors['dswd'],'staff.decision','deactivate',decision,lambda tx:registry.staff_decision(tx,h.actors['disbursing'],decision))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT business_status FROM payout_attempts').fetchone()['business_status'],'expired')
                self.assertEqual(db.execute('SELECT count(*) n FROM recorded_handovers').fetchone()['n'],0)
            with self.assertRaises(DomainError):execute_command(h.actors['disbursing'],'handover','cash',req,lambda tx:payouts.handover(tx,t['id'],req))

    def test_stopped_clearance_requires_distinct_later_session_even_on_same_day(self):
        with Harness() as h:
            h.register_chain();s,t,e,a,req=self.prepare(h)
            fail={'household_id':e['household_id'],'result':'fail','accepted_id_type':None,'person_photo_compared':False,'reason':'Invented comparison failed','attempt_id':a['id']}
            execute_command(h.actors['disbursing'],'id.check','stop',fail,lambda tx:payouts.id_check(tx,s['id'],fail))
            with h.connection() as db:t=db.execute('SELECT * FROM payout_transactions').fetchone();sv=db.execute('SELECT * FROM session_versions WHERE id=%s',(s['current_version_id'],)).fetchone();le=db.execute('SELECT * FROM approved_list_entries ORDER BY created_at DESC LIMIT 1').fetchone()
            clear={'expected_revision':t['revision'],'reason':'Invented reviewed stop','evidence_id':h.upload('clearance')}
            execute_command(h.actors['dswd'],'attempt.clearance','clear',clear,lambda tx:payouts.clearance(tx,t['id'],clear))
            with h.connection() as db:revision=db.execute('SELECT revision FROM payout_transactions').fetchone()['revision']
            opening={'expected_revision':revision,'path':'own_device','pin':None}
            with self.assertRaises(DomainError):execute_command(h.actors['beneficiary'],'attempt.open','same-session',opening,lambda tx:payouts.open_attempt(tx,e['id'],opening))
            schedule={'disaster_id':s['disaster_id'],'barangay_id':s['barangay_id'],'list_version_id':le['list_version_id'],'list_entry_ids':[le['id']],'date':sv['date'],'site':'Invented later same-day hall','cash_actor_ids':[h.actors['disbursing'],h.actors['disbursing2']],'followup_actor_ids':[]}
            ack=execute_command(h.actors['dswd'],'session.schedule','later',schedule,lambda tx:sessions.schedule(tx,schedule));v=UUID(ack['resources'][0]['id'])
            change={'expected_revision':0,'action':'open','reason':'Invented later opening'}
            execute_command(h.actors['dswd'],'session.change','later-open',change,lambda tx:sessions.change(tx,v,change))
            execute_command(h.actors['beneficiary'],'attempt.open','retry',opening,lambda tx:payouts.open_attempt(tx,e['id'],opening))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM payout_transactions').fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT count(*) n FROM payout_attempts').fetchone()['n'],2)
                self.assertEqual(db.execute('SELECT business_status FROM payout_attempts WHERE id=%s',(a['id'],)).fetchone()['business_status'],'stopped')

    def test_unrelated_list_publication_preserves_code_but_new_basis_expires_it(self):
        with Harness() as h:
            h.register_chain();s,t,e,a,req=self.prepare(h)
            with h.connection() as db:head=db.execute('SELECT * FROM list_heads').fetchone()
            lr={'disaster_id':s['disaster_id'],'barangay_id':s['barangay_id'],'expected_revision':None}
            execute_command(h.actors['dswd'],'list.request','same-payability',lr,lambda tx:entitlements.request_list(tx,lr));h.drain_anchors()
            with h.connection() as db:self.assertEqual(db.execute('SELECT business_status FROM payout_attempts').fetchone()['business_status'],'presented')
            from backend.tests.test_entitlements import EntitlementTests
            inputs=EntitlementTests().inputs(h);inputs.update(expected_revision=1,wage_centavos='50000',reason='Invented new documentary wage')
            execute_command(h.actors['dswd'],'inputs.save','change',inputs,lambda tx:entitlements.save_inputs(tx,inputs))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT business_status FROM payout_attempts').fetchone()['business_status'],'expired')
                self.assertEqual(db.execute('SELECT business_status FROM entitlements').fetchone()['business_status'],'held')
            with self.assertRaises(DomainError):execute_command(h.actors['disbursing'],'handover','stale-cash',req,lambda tx:payouts.handover(tx,t['id'],req))
