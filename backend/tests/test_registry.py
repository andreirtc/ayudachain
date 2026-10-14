import importlib.util
import unittest
from uuid import UUID,uuid4
from backend.tests.support import Harness
from backend.app.commands import execute_command,DomainError


class RegistryTests(unittest.TestCase):
    def test_partial_fact_correction_keeps_other_facts_and_member_identity(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        registry=self.service()
        with Harness() as h,TestClient(app) as client:
            req=self.request(h)
            ack=execute_command(h.actors['beneficiary'],'registry.register','self',req,lambda tx:registry.register(tx,req));identity=UUID(ack['resources'][0]['id'])
            with h.connection() as db:member=db.execute('SELECT member_id FROM member_versions').fetchone()['member_id']
            response=client.post('/api/v1/registry/'+str(identity)+'/reviews',headers={'X-Demo-Actor-ID':str(h.actors['dswd']),'Idempotency-Key':'correct'},json={'expected_revision':0,'action':'facts_correct','reason':'Invented corrected street','address':'Invented corrected address 91'})
            self.assertEqual(response.status_code,200,response.text)
            with h.connection() as db:
                current=db.execute('SELECT v.* FROM households h JOIN household_versions v ON v.id=h.current_version_id WHERE h.id=%s',(identity,)).fetchone()
                self.assertEqual(current['zone'],req['zone']);self.assertEqual(current['address'],'Invented corrected address 91')
                self.assertEqual({m['member_id'] for m in db.execute('SELECT member_id FROM member_versions').fetchall()},{member})
    def service(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.registry'),'Registry/intake service missing')
        from backend.app.services import registry
        return registry

    def request(self,h,**kw):
        return {'beneficiary_actor_id':h.actors['beneficiary'],'phone':None,'declared_barangay_id':h.barangays[0],'address':'Invented address 12','zone':'7','id_type':None,'id_number':None,'head_photo_evidence_id':None,'id_evidence_id':None,'members':[{'name':'Invented Bituin Salonga','birth_date':None,'relationship':'head','is_head':True}],**kw}

    def test_registration_has_stable_identity_separate_contact_and_no_id_state(self):
        registry=self.service()
        with Harness() as h:
            req=self.request(h)
            ack=execute_command(h.actors['beneficiary'],'registry.register','self',req,lambda tx:registry.register(tx,req));household=UUID(ack['resources'][0]['id'])
            with h.connection() as db:
                row=db.execute('SELECT * FROM households WHERE id=%s',(household,)).fetchone();version=db.execute('SELECT * FROM household_versions WHERE id=%s',(row['current_version_id'],)).fetchone()
                self.assertTrue(row['registered_without_id']);self.assertEqual(version['identity_state'],'pending_field_check');self.assertEqual(version['residence_state'],'unconfirmed')
            relink={'expected_revision':0,'action':'contact_relink','reason':'Invented checked contact change','beneficiary_actor_id':h.actors['beneficiary2'],'phone':'09990000001','accepted_id_type':'Synthetic photo ID','person_photo_compared':True}
            execute_command(h.actors['dswd'],'registry.review','relink',relink,lambda tx:registry.review(tx,household,relink))
            with h.connection() as db:
                self.assertEqual(db.execute('SELECT count(*) n FROM households').fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT count(*) n FROM household_link_versions').fetchone()['n'],2)
                self.assertEqual(db.execute('SELECT beneficiary_actor_id FROM household_links WHERE household_id=%s',(household,)).fetchone()['beneficiary_actor_id'],h.actors['beneficiary2'])

    def test_assister_recusal_and_private_projection(self):
        registry=self.service()
        with Harness() as h:
            req=self.request(h,phone='09990000003')
            ack=execute_command(h.actors['barangay'],'registry.register','help',req,lambda tx:registry.register(tx,req));identity=UUID(ack['resources'][0]['id'])
            with h.connection() as db:
                from backend.app.actor import resolve_identity
                view=registry.project(db,resolve_identity(db,h.actors['barangay']),identity)
                self.assertNotIn('phone',str(view));self.assertNotIn('09990000003',str(view));self.assertNotIn('id_number',str(view))
                with self.assertRaises(DomainError):registry.require_endorser(db,resolve_identity(db,h.actors['barangay']),identity)

    def test_barangay_officer_confirms_residence_once_for_an_independent_own_barangay_household(self):
        registry=self.service()
        with Harness() as h:
            req=self.request(h)
            identity=UUID(execute_command(h.actors['beneficiary'],'registry.register','self',req,lambda tx:registry.register(tx,req))['resources'][0]['id'])
            confirm={'expected_revision':0,'action':'residence_confirm','reason':'Invented neighbours know this household'}
            execute_command(h.actors['barangay'],'registry.review','confirm',confirm,lambda tx:registry.review(tx,identity,confirm))
            with h.connection() as db:
                row=db.execute('SELECT h.revision,v.residence_state,v.predecessor_id FROM households h JOIN household_versions v ON v.id=h.current_version_id WHERE h.id=%s',(identity,)).fetchone()
                self.assertEqual(row['residence_state'],'confirmed');self.assertEqual(row['revision'],1);self.assertIsNotNone(row['predecessor_id'])
                self.assertEqual(db.execute("SELECT count(*) n FROM audit_events WHERE action='registry.residence_confirm'").fetchone()['n'],1)
                self.assertEqual(db.execute('SELECT count(*) n FROM household_versions').fetchone()['n'],2)
            again=confirm|{'expected_revision':1}
            with self.assertRaises(DomainError) as refused:execute_command(h.actors['barangay2'],'registry.review','again',again,lambda tx:registry.review(tx,identity,again))
            self.assertEqual(refused.exception.code,'residence_not_awaiting_confirmation')

    def test_barangay_officer_cannot_confirm_assisted_other_barangay_or_other_actions(self):
        registry=self.service()
        with Harness() as h:
            assisted=self.request(h,beneficiary_actor_id=None)
            identity=UUID(execute_command(h.actors['barangay'],'registry.register','help',assisted,lambda tx:registry.register(tx,assisted))['resources'][0]['id'])
            confirm={'expected_revision':0,'action':'residence_confirm','reason':'Invented neighbours know this household'}
            with self.assertRaises(DomainError) as own:execute_command(h.actors['barangay'],'registry.review','own',confirm,lambda tx:registry.review(tx,identity,confirm))
            self.assertEqual(own.exception.code,'independent_endorser_required')
            other=confirm|{'action':'facts_correct','address':'Invented elsewhere 5'}
            with self.assertRaises(DomainError) as scope:execute_command(h.actors['barangay2'],'registry.review','scope',other,lambda tx:registry.review(tx,identity,other))
            self.assertEqual(scope.exception.code,'barangay_residence_confirm_only')
            elsewhere=self.request(h,declared_barangay_id=h.barangays[1])
            far=UUID(execute_command(h.actors['beneficiary'],'registry.register','far',elsewhere,lambda tx:registry.register(tx,elsewhere))['resources'][0]['id'])
            with self.assertRaises(DomainError) as outside:execute_command(h.actors['barangay'],'registry.review','far',confirm,lambda tx:registry.review(tx,far,confirm))
            self.assertEqual(outside.exception.code,'independent_endorser_required')
            execute_command(h.actors['barangay2'],'registry.review','ok',confirm,lambda tx:registry.review(tx,identity,confirm))
            with h.connection() as db:self.assertEqual(db.execute('SELECT v.residence_state FROM households h JOIN household_versions v ON v.id=h.current_version_id WHERE h.id=%s',(identity,)).fetchone()['residence_state'],'confirmed')

    def test_documentary_intake_opens_and_closes_without_reopening(self):
        registry=self.service()
        with Harness() as h:
            req={'disaster_id':h.disasters[0],'barangay_ids':[h.barangays[0]],'response_hours':12,'basis_evidence_id':h.upload('operation_basis')}
            ack=execute_command(h.actors['dswd'],'intake.open','open',req,lambda tx:registry.open_intake(tx,req));operation=UUID(ack['resources'][0]['id'])
            close={'expected_revision':0,'reason':'Invented intake cutoff'}
            execute_command(h.actors['dswd'],'intake.close','close',close,lambda tx:registry.close_intake(tx,operation,close))
            with self.assertRaises(DomainError):execute_command(h.actors['dswd'],'intake.open','again',req,lambda tx:registry.open_intake(tx,req))
            with h.connection() as db:self.assertEqual(db.execute('SELECT count(*) n FROM operation_versions').fetchone()['n'],2)
