"""Focused audit facts and role protection against disposable synthetic data."""
import unittest
from uuid import uuid4
import test_api as business
from fastapi.testclient import TestClient
from auth_support import HEADERS, TEST_PASSWORD
from app import auth
from app.seed_demo import seed_database

class TestAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(business.app,base_url="http://127.0.0.1",headers=HEADERS);cls.client.__enter__()
    @classmethod
    def tearDownClass(cls):cls.client.__exit__(None,None,None)
    def setUp(self):seed_database();auth._attempts.clear();self.login()
    def login(self,id="demo-officer-01"):
        self.client.cookies.clear();r=self.client.post("/api/auth/login",json={"username":id,"password":TEST_PASSWORD});self.assertEqual(r.status_code,200,r.text);self.client.headers["X-CSRF-Token"]=r.json()["csrf_token"]
    def workspace(self):return self.client.get("/api/audit-workspace?batch_id=RELIEF-2026-001")
    def test_exact_budgets_concerns_and_proof_states(self):
        baseline=self.workspace();self.assertEqual(baseline.status_code,200,baseline.text);body=baseline.json()
        self.assertEqual(body["recorded_centavos"],2500000);self.assertEqual(sum(a["recorded_centavos"] for a in body["allocations"]),body["recorded_centavos"])
        self.assertEqual(body["audit_protection"],"LOCAL_HISTORY");self.assertTrue(all(p["current_proof"]=="NOT_CHECKED" for p in body["payouts"]))
        r=self.client.post("/api/concerns",json={"request_id":str(uuid4()),"beneficiary_id":"BEN-0004","batch_id":"RELIEF-2026-001","category":"PAYOUT","message":"Check the synthetic payout desk."});self.assertEqual(r.status_code,201,r.text)
        self.client.post("/api/beneficiaries/BEN-0004/verify",json={"status":"VERIFIED","review_notes":"Inspected synthetic record"})
        self.login("demo-disbursing-001");payout=self.client.post("/api/distributions/confirm",headers={"Idempotency-Key":"audit-facts-payout"},json={"beneficiary_id":"BEN-0004","batch_id":"RELIEF-2026-001","amount":5000});self.assertEqual(payout.status_code,201,payout.text)
        self.login("demo-auditor-01");data=self.workspace().json()
        self.assertEqual(data["recorded_centavos"],3000000);self.assertEqual(data["open_concerns"],1);self.assertEqual(data["anchor_counts"]["CONFIRMED"],1)
        saved=next(p for p in data["payouts"] if p["distribution_id"]==payout.json()["distribution_id"])
        self.assertEqual(saved["current_proof"],"NOT_CHECKED");self.assertEqual(saved["receipt_version"],2);self.assertIsNotNone(saved["recorded_by"]);self.assertIsNone(saved["recipient_acknowledged_at"])
        self.assertNotIn("raw_transaction",str(data));self.assertNotIn("pin_json",str(data))
    def test_read_only_office_scope(self):
        for identity in ("demo-barangay-01","demo-disbursing-001","demo-beneficiary-01"):
            self.login(identity);self.assertEqual(self.workspace().status_code,403)
        self.login("demo-auditor-01");self.assertEqual(self.workspace().status_code,200)
        self.assertEqual(self.client.post("/api/concerns",json={}).status_code,403)
        self.assertEqual(self.client.get("/api/audit-workspace?batch_id=MISSING").status_code,404)
        self.client.cookies.clear();self.assertEqual(self.workspace().status_code,401)

if __name__=="__main__":unittest.main(verbosity=2)
