"""Focused authenticated concern journeys with disposable synthetic records."""
import unittest
from uuid import uuid4
import test_api as business
from fastapi.testclient import TestClient
from auth_support import HEADERS, TEST_PASSWORD
from app import auth
from app.database import SessionLocal
from app.models.entities import HouseholdConcern, ConcernRevision, Beneficiary
from app.seed_demo import seed_database

class TestConcerns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(business.app,base_url="http://127.0.0.1",headers=HEADERS);cls.client.__enter__()
    @classmethod
    def tearDownClass(cls):cls.client.__exit__(None,None,None)
    def setUp(self):seed_database();auth._attempts.clear();self.login()
    def login(self,id="demo-beneficiary-01"):
        self.client.cookies.clear();r=self.client.post("/api/auth/login",json={"username":id,"password":TEST_PASSWORD});self.assertEqual(r.status_code,200,r.text);self.client.headers["X-CSRF-Token"]=r.json()["csrf_token"]
    def create(self,**extra):
        data={"request_id":str(uuid4()),"batch_id":"RELIEF-2026-001","category":"PAYOUT","message":"Please review the synthetic recorded amount."};data.update(extra);return self.client.post("/api/concerns",json=data)
    def reply(self,id,**extra):
        data={"request_id":str(uuid4()),"expected_revision":1,"status":"IN_REVIEW","household_message":"We will review your recorded receipt.","staff_reason":"Private synthetic staff reason"};data.update(extra);return self.client.post("/api/concerns/"+id+"/revisions",json=data)
    def test_own_intake_replay_and_unchanged_business_records(self):
        before=[self.client.get(p).json() for p in ("/api/beneficiaries","/api/distributions","/api/batches")]
        key=str(uuid4());first=self.create(request_id=key);self.assertEqual(first.status_code,201,first.text)
        body=first.json();self.assertEqual(body["beneficiary_id"],"BEN-0004");self.assertEqual(body["source"],"HOUSEHOLD")
        self.assertEqual(self.create(request_id=key).status_code,200);self.assertEqual(self.create(request_id=key,message="Different concern").status_code,409)
        self.assertEqual(self.create(beneficiary_id="BEN-0001").status_code,404);self.assertEqual(self.create(distribution_id="DIST-0001").status_code,404)
        self.assertEqual([self.client.get(p).json() for p in ("/api/beneficiaries","/api/distributions","/api/batches")],before)
        with SessionLocal() as db:self.assertEqual(db.query(HouseholdConcern).count(),1)
        del self.client.headers["X-CSRF-Token"];self.assertEqual(self.create().status_code,403)
    def test_staff_reply_retains_history_and_private_reason(self):
        id=self.create().json()["concern_id"];self.login("demo-officer-01");key=str(uuid4())
        reply=self.reply(id,request_id=key);self.assertEqual(reply.status_code,201,reply.text);self.assertEqual(len(reply.json()["history"]),2)
        self.assertEqual(self.reply(id,request_id=key).status_code,200);self.assertEqual(self.reply(id).status_code,409)
        self.assertEqual(self.reply(id,expected_revision=2,staff_reason=" ").status_code,422)
        self.assertEqual(self.reply(id,expected_revision=2,status="RESOLVED",household_message="The recorded amount matches your receipt.").status_code,201)
        self.login();mine=self.client.get("/api/concerns/"+id);self.assertEqual(mine.status_code,200)
        self.assertNotIn("Private synthetic staff reason",mine.text);self.assertNotIn('"staff_reason"',mine.text);self.assertEqual(mine.json()["current"]["status"],"RESOLVED")
        self.assertEqual(self.reply(id,expected_revision=3).status_code,403)
    def test_staff_assistance_and_scope_without_impersonation(self):
        self.login("demo-barangay-01");r=self.create(beneficiary_id="BEN-0004");self.assertEqual(r.status_code,201,r.text);id=r.json()["concern_id"]
        self.assertEqual(r.json()["source"],"STAFF_ASSISTED");self.assertEqual(r.json()["created_by"],"demo-barangay-01")
        self.assertEqual(self.create(beneficiary_id="BEN-0008").status_code,404)
        self.login("demo-disbursing-002");self.assertEqual(self.client.get("/api/concerns/"+id).status_code,404);self.assertEqual(self.client.get("/api/concerns").json(),[])
        self.login("demo-auditor-01");self.assertEqual(self.client.get("/api/concerns/"+id).status_code,200);self.assertEqual(self.create(beneficiary_id="BEN-0004").status_code,403);self.assertEqual(self.reply(id).status_code,403)
        self.login();self.assertEqual(self.client.get("/api/concerns/"+id).json()["source"],"STAFF_ASSISTED")
        self.client.cookies.clear();self.assertEqual(self.client.get("/api/concerns").status_code,401)
    def test_retention_and_missing_own_record(self):
        from sqlalchemy import text
        from sqlalchemy.exc import DatabaseError
        id=self.create().json()["concern_id"]
        with SessionLocal() as db:
            for statement in ("DELETE FROM household_concerns", "UPDATE concern_revisions SET status='OPEN'"):
                with self.assertRaises(DatabaseError):db.execute(text(statement));db.commit()
                db.rollback()
            db.query(Beneficiary).filter_by(beneficiary_id="BEN-0004").delete();db.commit()
        self.assertEqual(self.create(category="DETAILS").status_code,201)
        self.assertEqual(self.client.get("/api/concerns/"+id).status_code,200)
        self.assertEqual(self.create(message="  ").status_code,422)
        self.assertEqual(self.create(source="STAFF_ASSISTED").status_code,422)

if __name__=="__main__":unittest.main(verbosity=2)
