import unittest
from uuid import UUID,uuid4
import psycopg
from backend.tests.support import Harness
from backend.app.actor import resolve_identity
from backend.app.commands import Transaction,execute_command


class RelationalTests(unittest.TestCase):
    def test_database_rejects_headless_version_and_missing_wage_even_with_audit(self):
        from backend.tests.test_registry import RegistryTests
        from backend.app.services import registry
        with Harness() as h:
            req=RegistryTests().request(h)
            ack=execute_command(h.actors['beneficiary'],'registry.register','register',req,lambda tx:registry.register(tx,req));identity=UUID(ack['resources'][0]['id'])
            with self.assertRaises(psycopg.IntegrityError):
                with h.connection() as db:
                    tx=Transaction(db,resolve_identity(db,h.actors['dswd']),uuid4());root=tx.get('households',identity);old=tx.get('household_versions',root['current_version_id'])
                    fields={k:old[k] for k in ['household_id','declared_barangay_id','address','zone','residence_state','identity_state','id_type','id_number','head_photo_evidence_id','id_evidence_id','assister_id','registry_review_id']}
                    v=tx.insert('household_versions',dict(fields,predecessor_id=old['id']));tx.update('households',identity,{'current_version_id':v['id']});tx.audit('bad.version',[('household_version_id',v['id'])]);db.execute('SET CONSTRAINTS ALL IMMEDIATE')
            with self.assertRaises(psycopg.IntegrityError):
                with h.connection() as db:
                    tx=Transaction(db,resolve_identity(db,h.actors['dswd']),uuid4());v=tx.insert('amount_input_versions',{'disaster_id':h.disasters[0],'predecessor_id':None,'mode':'wage_formula','wage_centavos':None,'reason':None});tx.audit('bad.input',[('input_version_id',v['id'])]);db.execute('SET CONSTRAINTS ALL IMMEDIATE')

