"""Real role-scoped API journeys on an isolated synthetic database."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import test_api as business
from fastapi.testclient import TestClient
from auth_support import HEADERS, TEST_PASSWORD
from app.database import SessionLocal
from app.models.entities import Distribution, Beneficiary, AuditEvent, RecipientAcknowledgement
from app.seed_demo import seed_database

class TestAcknowledgement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(business.app,base_url="http://127.0.0.1",headers=HEADERS); cls.client.__enter__()
    @classmethod
    def tearDownClass(cls): cls.client.__exit__(None,None,None)
    def login(self,identity):
        r=self.client.post("/api/auth/login",json={"username":identity,"password":TEST_PASSWORD}); self.assertEqual(r.status_code,200); self.client.headers["X-CSRF-Token"]=r.json()["csrf_token"]
    def setUp(self):
        seed_database(); self.client.cookies.clear(); self.login("demo-disbursing-001")
        r=self.client.post("/api/distributions/confirm",headers={"Idempotency-Key":"acknowledgement-fixture"},json={"beneficiary_id":"BEN-0004","batch_id":"RELIEF-2026-001","amount":"100.25"}); self.assertEqual(r.status_code,201,r.text); self.payout=r.json(); self.path="/api/distributions/"+self.payout["distribution_id"]+"/acknowledgement"; self.login("demo-beneficiary-01")
    def save(self): return self.client.post(self.path,json={"acknowledge":True})
    def test_acknowledgement_is_exact_attributed_durable_and_idempotent(self):
        before=self.client.get("/api/distributions").json()
        saved=self.save(); self.assertEqual(saved.status_code,201,saved.text)
        row=saved.json(); self.assertEqual(row["account_id"],"demo-beneficiary-01"); self.assertEqual(row["amount_centavos"],10025); self.assertEqual(row["receipt_hash"],self.payout["receipt_hash"]); self.assertTrue(row["acknowledged_at"].endswith("+00:00")); self.assertEqual(row["distribution_id"],self.payout["distribution_id"])
        self.assertEqual(self.save().status_code,200); self.assertEqual(self.save().json(),row)
        other=TestClient(business.app,base_url="http://127.0.0.1",headers=HEADERS); other.cookies.update(self.client.cookies)
        self.assertEqual(other.get(self.path).json(),row)
        after=self.client.get("/api/distributions").json(); self.assertEqual(after[0]["recipient_acknowledgement"],row)
        after[0]["recipient_acknowledgement"]=None; self.assertEqual(after,before)
        with SessionLocal() as db: self.assertEqual(db.query(RecipientAcknowledgement).count(),1); self.assertEqual(db.query(AuditEvent).filter_by(event_type="RECIPIENT_ACKNOWLEDGED").count(),1)
    def test_other_roles_are_readers_not_acknowledgers(self):
        self.save()
        for identity in ["demo-officer-01","demo-auditor-01","demo-disbursing-001"]:
            self.login(identity); self.assertEqual(self.client.get(self.path).status_code,200); self.assertEqual(self.save().status_code,403)
        self.login("demo-disbursing-002"); self.assertEqual(self.client.get(self.path).status_code,404)
        self.login("demo-barangay-01"); self.assertEqual(self.client.get(self.path).status_code,403); self.assertEqual(self.save().status_code,403)
    def test_own_household_unknown_and_forged_identity_controls(self):
        self.assertEqual(self.client.post("/api/distributions/DIST-0001/acknowledgement",json={"acknowledge":True}).status_code,404)
        self.assertEqual(self.client.post(self.path,json={"acknowledge":False}).status_code,422)
        self.assertEqual(self.client.post(self.path,json={"acknowledge":True,"account_id":"demo-officer-01"}).status_code,422)
        self.assertEqual(self.client.post("/api/distributions/missing/acknowledgement",json={"acknowledge":True}).status_code,404)
        self.client.headers["X-CSRF-Token"]="wrong"; self.assertEqual(self.save().status_code,403)
        self.client.cookies.clear(); self.assertEqual(self.save().status_code,401)
    def test_parallel_retries_create_one_ack_and_audit(self):
        with ThreadPoolExecutor(max_workers=4) as pool: responses=list(pool.map(lambda _:self.save(),range(4)))
        self.assertEqual(sorted(r.status_code for r in responses),[200,200,200,201]); self.assertTrue(all(r.json()==responses[0].json() for r in responses))
        with SessionLocal() as db: self.assertEqual(db.query(RecipientAcknowledgement).count(),1)
    def test_reversed_records_refuse_new_ack_but_retain_existing_history(self):
        with SessionLocal() as db: db.query(Distribution).filter_by(distribution_id=self.payout["distribution_id"]).update({"status":"REVERSED"}); db.commit()
        self.assertEqual(self.save().status_code,409)
        with SessionLocal() as db: db.query(Distribution).filter_by(distribution_id=self.payout["distribution_id"]).update({"status":"CONFIRMED"}); db.commit()
        saved=self.save().json()
        with SessionLocal() as db:
            db.query(Distribution).filter_by(distribution_id=self.payout["distribution_id"]).update({"status":"REVERSED"}); db.query(Beneficiary).filter_by(beneficiary_id="BEN-0004").update({"record_status":"DUPLICATE","canonical_beneficiary_id":"BEN-0002"}); db.commit()
        self.assertEqual(self.save().json(),saved); self.assertEqual(self.client.get(self.path).json(),saved)
    def test_failed_commit_does_not_partially_record_ack_or_audit(self):
        from sqlalchemy.orm import Session
        with patch.object(Session,"commit",side_effect=RuntimeError("Synthetic ack commit failure")):
            with self.assertRaises(RuntimeError): self.save()
        self.assertIsNone(self.client.get(self.path).json())
        with SessionLocal() as db: self.assertEqual(db.query(AuditEvent).filter_by(event_type="RECIPIENT_ACKNOWLEDGED").count(),0)
        self.assertEqual(self.save().status_code,201)
    def test_public_references_and_hash_checks_do_not_disclose_acknowledgement(self):
        self.save(); self.client.cookies.clear()
        rows=self.client.get("/api/public/receipts").json(); self.assertTrue(all(set(row)=={"distribution_id","batch_id"} for row in rows))
        result=self.client.post("/api/blockchain/verify",json={"distribution_id":self.payout["distribution_id"]}).json(); self.assertNotIn("recipient_acknowledgement",result); self.assertIsNone(result["beneficiary_id"])

if __name__=="__main__": unittest.main(verbosity=2)
