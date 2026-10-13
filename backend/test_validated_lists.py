"""Actual authenticated journeys in business test's disposable SQLite fixture."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import test_api as business
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from auth_support import HEADERS, TEST_PASSWORD
from app import auth
from app.database import SessionLocal
from app.models.entities import ValidatedList, ListFinalization, Beneficiary, AuditEvent, ReliefBatch
from app.seed_demo import seed_database

class TestLists(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(business.app,base_url="http://127.0.0.1",headers=HEADERS);cls.client.__enter__()
    @classmethod
    def tearDownClass(cls):cls.client.__exit__(None,None,None)
    def setUp(self):seed_database();auth._attempts.clear();self.client.cookies.clear();self.login()
    def login(self,identity="demo-officer-01",client=None):
        client=client or self.client
        result=client.post("/api/auth/login",json={"username":identity,"password":TEST_PASSWORD});self.assertEqual(result.status_code,200)
        client.headers["X-CSRF-Token"]=result.json()["csrf_token"];return client
    def approve(self,id="BEN-0004"):
        r=self.client.post(f"/api/beneficiaries/{id}/verify",json={"status":"VERIFIED","review_notes":"Inspected distinct synthetic household"});self.assertEqual(r.status_code,200,r.text)
    def prepare(self,**extra):
        payload={"batch_id":"RELIEF-2026-001","barangay_id":"BRGY-001","request_id":str(uuid4()),"exclusions":{}};payload.update(extra)
        return self.client.post("/api/validated-lists/prepare",json=payload)
    def finalize(self,id,**extra):
        payload={"reason":"Inspected included records and exclusions","confirm":True};payload.update(extra)
        return self.client.post(f"/api/validated-lists/{id}/finalize",json=payload)
    def test_preparation_requires_retained_decisions_and_never_changes_eligibility(self):
        before=self.client.get("/api/beneficiaries?include_historical=true").json()
        baseline=self.prepare().json();self.assertFalse(any(r["included"] for r in baseline["snapshot"]["rows"]))
        self.assertEqual(self.finalize(baseline["list_id"]).status_code,409)
        self.assertEqual(self.client.get("/api/beneficiaries?include_historical=true").json(),before)
        self.approve();plan=self.prepare().json();row=next(r for r in plan["snapshot"]["rows"] if r["beneficiary_id"]=="BEN-0004")
        self.assertTrue(row["included"]);self.assertEqual(row["decision"]["actor"],"demo-officer-01")
        self.assertTrue(row["decision"]["review_id"])
    def test_preparation_retry_and_conflicting_identity(self):
        key=str(uuid4());first=self.prepare(request_id=key);self.assertEqual(first.status_code,201,first.text)
        replay=self.prepare(request_id=key);self.assertEqual(replay.status_code,200);self.assertEqual(first.json(),replay.json())
        self.assertEqual(self.prepare(request_id=key,barangay_id="BRGY-002").status_code,409)
        with SessionLocal() as db:self.assertEqual(db.query(ValidatedList).count(),1);self.assertEqual(db.query(AuditEvent).filter_by(event_type="LIST_PREPARED").count(),1)
    def test_finalization_is_attributed_replayed_and_frozen_after_registry_changes(self):
        self.approve();plan=self.prepare().json();saved=self.finalize(plan["list_id"]);self.assertEqual(saved.status_code,201,saved.text)
        self.assertEqual(saved.json()["finalization"]["actor"],"demo-officer-01")
        self.assertEqual(self.finalize(plan["list_id"]).json(),saved.json());self.assertEqual(self.finalize(plan["list_id"]).status_code,200)
        with SessionLocal() as db:db.query(Beneficiary).filter_by(beneficiary_id="BEN-0004").update({"household_name":"Later synthetic name"});db.commit()
        retained=self.client.get("/api/validated-lists/"+plan["list_id"]).json();self.assertTrue(retained["stale"])
        self.assertEqual(retained["snapshot"],plan["snapshot"])
        with SessionLocal() as db:self.assertEqual(db.query(ListFinalization).count(),1);self.assertEqual(db.query(AuditEvent).filter_by(event_type="LIST_FINALIZED").count(),1)
    def test_changed_review_and_new_record_refuse_stale_finalization(self):
        self.approve();plan=self.prepare().json()
        self.client.post("/api/beneficiaries/BEN-0004/verify",json={"status":"REJECTED","review_notes":"Changed synthetic evidence"})
        self.assertEqual(self.finalize(plan["list_id"]).status_code,409)
        self.approve();plan=self.prepare().json()
        self.client.post("/api/beneficiaries",json={"beneficiary_id":"BEN-LIST-NEW","household_name":"Synthetic new list case","barangay_id":"BRGY-001","barangay_name":"San Isidro","batch_id":"RELIEF-2026-001"})
        self.assertEqual(self.finalize(plan["list_id"]).status_code,409)
        with SessionLocal() as db:self.assertEqual(db.query(ListFinalization).count(),0)
    def test_human_exclusions_and_flags_are_retained(self):
        self.approve();plan=self.prepare(exclusions={"BEN-0004":"Private synthetic exception note"}).json()
        row=next(r for r in plan["snapshot"]["rows"] if r["beneficiary_id"]=="BEN-0004");self.assertFalse(row["included"])
        self.assertIn("Staff exclusion: Private synthetic exception note",row["exclusion_reasons"])
        self.assertEqual(self.prepare(exclusions={"BEN-0010":"Outside assigned area"}).status_code,422)
        self.assertEqual(self.prepare(exclusions={"BEN-0004":" "}).status_code,422)
        self.assertEqual(self.prepare(prepared_by="another-officer").status_code,422)
        with SessionLocal() as db:db.query(Beneficiary).filter_by(beneficiary_id="BEN-0004").update({"duplicate_flag":True});db.commit()
        plan=self.prepare().json();row=next(r for r in plan["snapshot"]["rows"] if r["beneficiary_id"]=="BEN-0004");self.assertIn("Unresolved review flag",row["exclusion_reasons"])
    def test_scopes_roles_and_private_reason_projection(self):
        self.approve();plan=self.prepare(exclusions={"BEN-0004":"Private synthetic exception"}).json();id=plan["list_id"]
        for actor in ("demo-auditor-01","demo-disbursing-001","demo-beneficiary-01"):
            self.login(actor);self.assertEqual(self.prepare().status_code,403);self.assertEqual(self.finalize(id).status_code,403)
        self.assertEqual(self.client.get("/api/validated-lists").status_code,403)
        self.login("demo-barangay-01");self.assertEqual(self.prepare(barangay_id="BRGY-002").status_code,404)
        self.assertEqual(self.finalize(id).status_code,403)
        scoped=self.client.get("/api/validated-lists/"+id);self.assertEqual(scoped.status_code,200);self.assertNotIn("Private synthetic exception",scoped.text)
        self.assertNotIn('"actor":"demo-officer-01"',scoped.text)
        self.login("demo-disbursing-002");self.assertEqual(self.client.get("/api/validated-lists/"+id).status_code,404)
        self.client.cookies.clear();self.assertEqual(self.client.get("/api/validated-lists").status_code,401)
    def test_database_guards_prevent_mutating_or_deleting_frozen_history(self):
        self.approve();id=self.prepare().json()["list_id"];self.finalize(id)
        for table in ("validated_lists","list_finalizations"):
            for operation in (f"DELETE FROM {table}",f"UPDATE {table} SET list_id='rewrite'"):
                with SessionLocal() as db:
                    with self.assertRaises(DatabaseError):db.execute(text(operation));db.commit()
                    db.rollback()
        self.assertEqual(self.client.get("/api/validated-lists/"+id).json()["state"],"FINALIZED")
    def test_concurrent_prepare_and_finalization_create_once(self):
        self.approve();key=str(uuid4());clients=[self.login(client=TestClient(business.app,base_url="http://127.0.0.1",headers=HEADERS)) for _ in range(3)]
        def prepare(c):return c.post("/api/validated-lists/prepare",json={"batch_id":"RELIEF-2026-001","barangay_id":"BRGY-001","request_id":key})
        with ThreadPoolExecutor(3) as pool:results=list(pool.map(prepare,clients))
        self.assertEqual(sorted(r.status_code for r in results),[200,200,201]);id=results[0].json()["list_id"]
        self.assertEqual({r.json()["list_id"] for r in results},{id})
        with ThreadPoolExecutor(3) as pool:results=list(pool.map(lambda c:c.post(f"/api/validated-lists/{id}/finalize",json={"confirm":True,"reason":"Concurrent inspected version"}),clients))
        self.assertEqual(sorted(r.status_code for r in results),[200,200,201])
        with SessionLocal() as db:self.assertEqual(db.query(ListFinalization).count(),1)
    def test_no_budget_is_not_ineligibility_and_inactive_batches_cannot_finalize(self):
        self.approve()
        with SessionLocal() as db:db.query(ReliefBatch).update({"amount_centavos":0});db.commit()
        plan=self.prepare().json();self.assertTrue(next(r for r in plan["snapshot"]["rows"] if r["beneficiary_id"]=="BEN-0004")["included"])
        with SessionLocal() as db:db.query(ReliefBatch).update({"status":"SUSPENDED"});db.commit()
        self.assertEqual(self.finalize(plan["list_id"]).status_code,409);self.assertEqual(self.prepare().status_code,409)
    def test_csv_rows_remain_excluded_until_explicit_review(self):
        self.approve();old=self.prepare().json()
        csv="beneficiary_id,household_name,barangay_id,barangay_name,dafac_id\nBEN-LIST-CSV,Synthetic CSV list household,BRGY-001,San Isidro,DFC-LIST-CSV\n"
        preview=self.client.post("/api/beneficiaries/csv/preview",json={"batch_id":"RELIEF-2026-001","csv_content":csv}).json()
        self.assertEqual(self.client.post("/api/beneficiaries/csv/"+preview["import_id"]+"/import").status_code,201)
        self.assertEqual(self.finalize(old["list_id"]).status_code,409)
        draft=self.prepare().json();row=next(r for r in draft["snapshot"]["rows"] if r["beneficiary_id"]=="BEN-LIST-CSV")
        self.assertFalse(row["included"]);self.assertEqual(row["review_status"],"PENDING")
        self.approve("BEN-LIST-CSV");draft=self.prepare().json();self.assertTrue(next(r for r in draft["snapshot"]["rows"] if r["beneficiary_id"]=="BEN-LIST-CSV")["included"])
    def test_linked_prior_payouts_are_retained_and_not_eligible_for_another_payout_list(self):
        before=self.client.get("/api/distributions").json();self.approve()
        linked=self.client.post("/api/beneficiaries/BEN-0001/resolve-duplicate",json={"canonical_beneficiary_id":"BEN-0004","review_notes":"Retain original synthetic alias"});self.assertEqual(linked.status_code,200,linked.text)
        draft=self.prepare().json();row=next(r for r in draft["snapshot"]["rows"] if r["beneficiary_id"]=="BEN-0004")
        self.assertFalse(row["included"]);self.assertTrue(row["recorded_payout_references"])
        self.assertEqual(self.client.get("/api/distributions").json(),before)
        self.login("demo-barangay-01");scoped=self.client.get("/api/validated-lists/"+draft["list_id"]).json();self.assertFalse(any("recorded_payout_references" in r for r in scoped["snapshot"]["rows"]))
    def test_mutations_require_csrf_and_finalization_consent(self):
        self.approve();id=self.prepare().json()["list_id"]
        self.assertEqual(self.finalize(id,confirm=False).status_code,422);self.assertEqual(self.finalize(id,reason=" ").status_code,422)
        del self.client.headers["X-CSRF-Token"]
        self.assertEqual(self.prepare().status_code,403);self.assertEqual(self.finalize(id).status_code,403)

if __name__=="__main__":unittest.main(verbosity=2)
