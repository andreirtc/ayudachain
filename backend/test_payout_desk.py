"""Small authenticated desk regression suite using the disposable business fixture."""
import unittest
import test_api as business
from fastapi.testclient import TestClient
from auth_support import HEADERS, TEST_PASSWORD
from app import auth
from app.database import SessionLocal
from app.models.entities import Allocation, Beneficiary, Distribution
from app.seed_demo import seed_database

class TestDesk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(business.app, base_url="http://127.0.0.1", headers=HEADERS)
        cls.client.__enter__()
    @classmethod
    def tearDownClass(cls): cls.client.__exit__(None, None, None)
    def setUp(self):
        seed_database(); auth._attempts.clear(); self.login("demo-officer-01")
        self.assertEqual(self.client.post("/api/beneficiaries/BEN-0004/verify", json={"status":"VERIFIED", "review_notes":"Inspected synthetic household"}).status_code,200)
        self.login()
    def login(self, identity="demo-disbursing-001"):
        self.client.cookies.clear()
        r=self.client.post("/api/auth/login",json={"username":identity,"password":TEST_PASSWORD})
        self.assertEqual(r.status_code,200,r.text)
        self.client.headers["X-CSRF-Token"]=r.json()["csrf_token"]
    def test_ready_budget_and_once_only_replay(self):
        r=self.client.get("/api/payout-desk/BEN-0004?amount=5000")
        self.assertEqual(r.status_code,200,r.text); self.assertTrue(r.json()["can_record"])
        payload={"beneficiary_id":"BEN-0004","batch_id":"RELIEF-2026-001","amount":5000}
        first=self.client.post("/api/distributions/confirm",json=payload,headers={"Idempotency-Key":"desk-demo-retry"})
        self.assertEqual(first.status_code,201,first.text)
        self.assertEqual(self.client.post("/api/distributions/confirm",json=payload,headers={"Idempotency-Key":"desk-demo-retry"}).status_code,200)
        checks=self.client.get("/api/payout-desk/BEN-0004").json()
        self.assertFalse(checks["can_record"]); self.assertEqual(checks["existing_distribution_id"],first.json()["distribution_id"])
        with SessionLocal() as db: self.assertEqual(db.query(Distribution).filter_by(beneficiary_id="BEN-0004").count(),1)
    def test_budget_alias_and_invalid_amount(self):
        with SessionLocal() as db:
            allocation=db.query(Allocation).filter_by(batch_id="RELIEF-2026-001",barangay_id="BRGY-001").one()
            allocation.amount_centavos=1; db.commit()
        body=self.client.get("/api/payout-desk/BEN-0004?amount=5000").json()
        self.assertFalse(body["can_record"]); self.assertFalse(next(c for c in body["checks"] if c["code"]=="BUDGET")["passed"])
        for amount in ("0","-1","5000.001","NaN","Infinity"):
            self.assertEqual(self.client.get("/api/payout-desk/BEN-0004?amount="+amount).status_code,422)
        with SessionLocal() as db:
            db.query(Beneficiary).filter_by(beneficiary_id="BEN-0001").update({"record_status":"DUPLICATE","canonical_beneficiary_id":"BEN-0004"}); db.commit()
        body=self.client.get("/api/payout-desk/BEN-0004").json()
        self.assertIsNotNone(body["existing_distribution_id"]); self.assertFalse(next(c for c in body["checks"] if c["code"]=="PRIOR_PAYOUT")["passed"])
    def test_roles_and_area_scope(self):
        self.login("demo-disbursing-002"); self.assertEqual(self.client.get("/api/payout-desk/BEN-0004").status_code,404)
        for identity in ("demo-beneficiary-01","demo-barangay-01"):
            self.login(identity); self.assertEqual(self.client.get("/api/payout-desk/BEN-0004").status_code,403)
        self.login("demo-auditor-01"); self.assertFalse(self.client.get("/api/payout-desk/BEN-0004").json()["can_record"])
        self.client.cookies.clear(); self.assertEqual(self.client.get("/api/payout-desk/BEN-0004").status_code,401)

if __name__=="__main__": unittest.main(verbosity=2)
