import unittest
from uuid import UUID
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError


class PublicationTests(unittest.TestCase):
    def test_registry_move_invalidates_old_barangay_candidate_and_publishes_both_successors(self):
        from backend.tests.test_entitlements import EntitlementTests
        from backend.app.services import entitlements,registry
        with Harness() as h:
            h.register_chain();helper=EntitlementTests();claim=helper.pending_claim(h)
            decision=helper.decision(h,claim)
            execute_command(h.actors['dswd'],'claim.decide','move-approve',decision,lambda tx:entitlements.decide(tx,claim,decision))
            inputs=helper.inputs(h)
            execute_command(h.actors['dswd'],'inputs.save','move-inputs',inputs,lambda tx:entitlements.save_inputs(tx,inputs))
            old_req={'disaster_id':h.disasters[0],'barangay_id':h.barangays[2],'expected_revision':None}
            execute_command(h.actors['dswd'],'list.request','old-published',old_req,lambda tx:entitlements.request_list(tx,old_req))
            h.drain_anchors()
            pending=UUID(execute_command(h.actors['dswd'],'list.request','old-pending',old_req,lambda tx:entitlements.request_list(tx,old_req))['resources'][0]['id'])
            with h.connection() as db:
                household=db.execute('SELECT * FROM households').fetchone()
                profile=db.execute('SELECT * FROM household_versions WHERE id=%s',(household['current_version_id'],)).fetchone()
                old_version=db.execute('SELECT current_version_id FROM entitlements').fetchone()['current_version_id']
            review={'expected_revision':household['revision'],'action':'facts_correct','reason':'Invented documented residence correction',
                    'declared_barangay_id':h.barangays[0],'address':profile['address'],'zone':'Invented corrected zone'}
            execute_command(h.actors['dswd'],'registry.review','move',review,lambda tx:registry.review(tx,household['id'],review))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT business_status FROM approved_list_versions WHERE id=%s',(pending,)).fetchone()['business_status'],'stale')
                self.assertNotEqual(db.execute('SELECT current_version_id FROM entitlements').fetchone()['current_version_id'],old_version)
            removed=UUID(execute_command(h.actors['dswd'],'list.request','old-removal',old_req,lambda tx:entitlements.request_list(tx,old_req))['resources'][0]['id'])
            new_req=dict(old_req,barangay_id=h.barangays[0])
            included=UUID(execute_command(h.actors['dswd'],'list.request','new-inclusion',new_req,lambda tx:entitlements.request_list(tx,new_req))['resources'][0]['id'])
            h.drain_anchors()
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT current_published_id FROM list_heads WHERE barangay_id=%s',(h.barangays[2],)).fetchone()['current_published_id'],removed)
                self.assertEqual(db.execute('SELECT count(*) n FROM approved_list_entries WHERE list_version_id=%s',(removed,)).fetchone()['n'],0)
                self.assertEqual(db.execute('SELECT current_published_id FROM list_heads WHERE barangay_id=%s',(h.barangays[0],)).fetchone()['current_published_id'],included)
                self.assertEqual(db.execute('SELECT count(*) n FROM approved_list_entries WHERE list_version_id=%s',(included,)).fetchone()['n'],1)

    def test_actual_list_anchor_publishes_only_current_candidate_and_no_notice(self):
        from backend.tests.test_entitlements import EntitlementTests
        from backend.app.services import entitlements
        with Harness() as h:
            h.register_chain();helper=EntitlementTests();claim=helper.pending_claim(h);decision=helper.decision(h,claim)
            execute_command(h.actors['dswd'],'claim.decide','decide',decision,lambda tx:entitlements.decide(tx,claim,decision))
            inputs=helper.inputs(h);execute_command(h.actors['dswd'],'inputs.save','input',inputs,lambda tx:entitlements.save_inputs(tx,inputs))
            req={'disaster_id':h.disasters[0],'barangay_id':h.barangays[2],'expected_revision':None}
            first=execute_command(h.actors['dswd'],'list.request','first',req,lambda tx:entitlements.request_list(tx,req));old=UUID(first['resources'][0]['id'])
            second=execute_command(h.actors['dswd'],'list.request','second',req,lambda tx:entitlements.request_list(tx,req));new=UUID(second['resources'][0]['id'])
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT business_status FROM approved_list_versions WHERE id=%s',(new,)).fetchone()['business_status'],'pending_publication')
                self.assertIsNone(db.execute('SELECT current_published_id FROM list_heads').fetchone()['current_published_id'])
            h.drain_anchors()
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT current_published_id FROM list_heads').fetchone()['current_published_id'],new)
                self.assertEqual(db.execute('SELECT business_status FROM approved_list_versions WHERE id=%s',(old,)).fetchone()['business_status'],'stale')
                self.assertEqual(db.execute('SELECT count(*) n FROM notifications WHERE purpose=%s',('session_scheduled',)).fetchone()['n'],0)
                from backend.app.services.integrity import check_saved
                for proof in db.execute('SELECT * FROM commitments').fetchall():self.assertEqual(check_saved(db,proof)['result'],'match')
