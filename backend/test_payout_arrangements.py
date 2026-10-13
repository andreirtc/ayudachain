"""Authenticated arrangement journeys in business test's disposable SQLite fixture."""
import unittest
from datetime import date, timedelta
from uuid import uuid4
import test_api as business
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
from auth_support import HEADERS, TEST_PASSWORD
from app import auth
from app.database import SessionLocal
from app.models.entities import PayoutArrangement, ArrangementRevision, Beneficiary, AuditEvent
from app.seed_demo import seed_database

SOON = (date.today() + timedelta(days=7)).isoformat()
DETAILS = {"collection_date": SOON, "time_window": "8:00 AM - 12:00 NN", "site": "San Isidro covered court", "requirements": ["Any government ID", "Household reference"], "responsible_staff": "Synthetic payout team lead"}

class TestArrangements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(business.app,base_url="http://127.0.0.1",headers=HEADERS);cls.client.__enter__()
    @classmethod
    def tearDownClass(cls):cls.client.__exit__(None,None,None)
    def setUp(self):seed_database();auth._attempts.clear();self.client.cookies.clear();self.login()
    def login(self,identity="demo-officer-01"):
        self.client.cookies.clear()
        result=self.client.post("/api/auth/login",json={"username":identity,"password":TEST_PASSWORD});self.assertEqual(result.status_code,200)
        self.client.headers["X-CSRF-Token"]=result.json()["csrf_token"]
    def approve(self,id="BEN-0004"):
        r=self.client.post(f"/api/beneficiaries/{id}/verify",json={"status":"VERIFIED","review_notes":"Inspected distinct synthetic household"});self.assertEqual(r.status_code,200,r.text)
    def finalized_list(self,exclusions=None,finalize=True):
        id=self.client.post("/api/validated-lists/prepare",json={"batch_id":"RELIEF-2026-001","barangay_id":"BRGY-001","request_id":str(uuid4()),"exclusions":exclusions or {}}).json()["list_id"]
        if finalize:self.assertEqual(self.client.post(f"/api/validated-lists/{id}/finalize",json={"reason":"Inspected","confirm":True}).status_code,201)
        return id
    def create(self,list_id,**extra):
        payload={"list_id":list_id,"request_id":str(uuid4()),**DETAILS};payload.update(extra)
        return self.client.post("/api/arrangements",json=payload)
    def revise(self,id,expected,action="EDIT",**extra):
        payload={"request_id":str(uuid4()),"expected_revision":expected,"action":action,"reason":"Venue moved after inspection","details":{**DETAILS,"site":"Barangay hall"} if action=="EDIT" else None};payload.update(extra)
        return self.client.post(f"/api/arrangements/{id}/revisions",json=payload)
    def test_only_finalized_current_lists_receive_one_arrangement_with_replay(self):
        self.approve();draft=self.finalized_list(finalize=False)
        self.assertEqual(self.create(draft).status_code,409)
        list_id=self.finalized_list();key=str(uuid4())
        first=self.create(list_id,request_id=key);self.assertEqual(first.status_code,201,first.text)
        replay=self.create(list_id,request_id=key);self.assertEqual(replay.status_code,200);self.assertEqual(replay.json(),first.json())
        self.assertEqual(self.create(list_id,request_id=key,site="Different site").status_code,409)
        self.assertEqual(self.create(list_id).status_code,409)
        self.assertEqual(first.json()["current"]["state"],"SCHEDULED");self.assertEqual(first.json()["included_households"],1)
        with SessionLocal() as db:self.assertEqual(db.query(AuditEvent).filter_by(event_type="ARRANGEMENT_PUBLISHED").count(),1)
    def test_changed_records_and_invalid_details_are_refused(self):
        self.approve();list_id=self.finalized_list()
        self.assertEqual(self.create(list_id,collection_date=(date.today()-timedelta(days=1)).isoformat()).status_code,422)
        self.assertEqual(self.create(list_id,requirements=[]).status_code,422)
        self.assertEqual(self.create(list_id,site="  ").status_code,422)
        self.assertEqual(self.create(list_id,site="Hall\x07").status_code,422)
        with SessionLocal() as db:db.query(Beneficiary).filter_by(beneficiary_id="BEN-0004").update({"household_name":"Later synthetic name"});db.commit()
        self.assertEqual(self.create(list_id).status_code,409)
        with SessionLocal() as db:self.assertEqual(db.query(PayoutArrangement).count(),0)
    def test_edits_and_cancellation_retain_history_and_refuse_stale_changes(self):
        self.approve();arr=self.create(self.finalized_list()).json();id=arr["arrangement_id"]
        edited=self.revise(id,1);self.assertEqual(edited.status_code,201,edited.text)
        body=edited.json();self.assertEqual(body["current"]["site"],"Barangay hall");self.assertEqual([h["revision"] for h in body["history"]],[2,1])
        self.assertEqual(body["history"][1]["site"],"San Isidro covered court");self.assertEqual(body["current"]["reason"],"Venue moved after inspection")
        self.assertEqual(self.revise(id,1).status_code,409)
        self.assertEqual(self.revise(id,2,details=None).status_code,422)
        self.assertEqual(self.revise(id,2,reason=" ",action="CANCEL").status_code,422)
        cancelled=self.revise(id,2,action="CANCEL",reason="Typhoon signal raised");self.assertEqual(cancelled.status_code,201)
        self.assertEqual(cancelled.json()["current"]["state"],"CANCELLED");self.assertEqual(cancelled.json()["current"]["site"],"Barangay hall")
        self.assertEqual(self.revise(id,3).status_code,409)
        with SessionLocal() as db:
            self.assertEqual(db.query(ArrangementRevision).count(),3)
            self.assertEqual(db.query(AuditEvent).filter_by(event_type="ARRANGEMENT_CANCELLED").count(),1)
    def test_revision_retry_replays_and_conflicting_identity(self):
        self.approve();id=self.create(self.finalized_list()).json()["arrangement_id"];key=str(uuid4())
        first=self.revise(id,1,request_id=key);self.assertEqual(first.status_code,201)
        self.assertEqual(self.revise(id,1,request_id=key).json(),first.json())
        self.assertEqual(self.revise(id,1,request_id=key,reason="Other change").status_code,409)
        with SessionLocal() as db:self.assertEqual(db.query(ArrangementRevision).count(),2)
    def test_household_sees_only_own_current_instructions_without_staff_notes(self):
        self.approve();id=self.create(self.finalized_list()).json()["arrangement_id"];self.revise(id,1)
        self.login("demo-beneficiary-01")
        mine=self.client.get("/api/arrangements/mine");self.assertEqual(mine.status_code,200)
        [item]=mine.json();self.assertEqual(item["current"]["site"],"Barangay hall");self.assertTrue(item["updated"])
        self.assertNotIn("Venue moved",mine.text);self.assertNotIn("demo-officer-01",mine.text)
        self.assertEqual(self.client.get("/api/arrangements").status_code,403)
        self.assertEqual(self.client.get("/api/arrangements/"+id).status_code,403)
        self.assertEqual(self.create("LIST-x").status_code,403)
    def test_excluded_and_superseded_households_see_no_stale_instructions(self):
        self.approve()
        self.client.post("/api/beneficiaries",json={"beneficiary_id":"BEN-ARR-NEW","household_name":"Synthetic arrangement household","barangay_id":"BRGY-001","barangay_name":"San Isidro","batch_id":"RELIEF-2026-001"})
        self.approve("BEN-ARR-NEW");self.create(self.finalized_list())
        newer=self.finalized_list(exclusions={"BEN-0004":"Moved to another evacuation centre"})
        self.login("demo-beneficiary-01");self.assertEqual(self.client.get("/api/arrangements/mine").json(),[])
        self.login();self.assertTrue(self.client.get("/api/arrangements").json()[0]["superseded"])
        self.assertEqual(self.create(newer).status_code,201)
        self.login("demo-beneficiary-01");self.assertEqual(self.client.get("/api/arrangements/mine").json(),[])
    def test_roles_and_area_scope(self):
        self.approve();list_id=self.finalized_list();id=self.create(list_id).json()["arrangement_id"]
        for actor in ("demo-auditor-01","demo-disbursing-001"):
            self.login(actor);self.assertEqual(self.client.get("/api/arrangements/"+id).status_code,200)
            self.assertEqual(self.revise(id,1).status_code,403)
        self.login("demo-barangay-01");self.assertEqual(self.revise(id,1).status_code,201)
        self.login("demo-disbursing-002");self.assertEqual(self.client.get("/api/arrangements/"+id).status_code,404);self.assertEqual(self.client.get("/api/arrangements").json(),[])
        self.client.cookies.clear();self.assertEqual(self.client.get("/api/arrangements").status_code,401)
    def test_arrangement_never_authorizes_or_changes_payout(self):
        self.approve();list_id=self.finalized_list()
        before=[self.client.get(path).json() for path in ("/api/beneficiaries?include_historical=true","/api/distributions","/api/batches")]
        self.create(list_id)
        self.assertEqual([self.client.get(path).json() for path in ("/api/beneficiaries?include_historical=true","/api/distributions","/api/batches")],before)
    def test_database_guards_and_csrf(self):
        self.approve();id=self.create(self.finalized_list()).json()["arrangement_id"]
        for table in ("payout_arrangements","arrangement_revisions"):
            for operation in (f"DELETE FROM {table}",f"UPDATE {table} SET arrangement_id='rewrite'"):
                with SessionLocal() as db:
                    with self.assertRaises(DatabaseError):db.execute(text(operation));db.commit()
                    db.rollback()
        del self.client.headers["X-CSRF-Token"];self.assertEqual(self.revise(id,1).status_code,403)

if __name__=="__main__":unittest.main(verbosity=2)
