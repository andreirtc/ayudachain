"""Isolated actual CSV API journeys; no production records or chain."""
import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import test_api as business
from fastapi.testclient import TestClient
from auth_support import HEADERS, TEST_PASSWORD
from app.database import SessionLocal
from app.models.entities import Beneficiary, Distribution, AuditEvent, ReliefBatch
from app.services.csv_onboarding import CsvImport
from app.seed_demo import seed_database
from app import auth

CSV = "beneficiary_id,household_name,barangay_id,barangay_name,dafac_id\nBEN-CSV-ONE,Synthetic Nima Solar,BRGY-001,San Isidro,DFC-CSV-ONE\nBEN-CSV-TWO,Juan Dela Cruz,BRGY-001,San Isidro,DFC-2026-0002\n"
class TestCsv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_accounts = business._accounts_path.read_text()
        cls.client = TestClient(business.app, base_url="http://127.0.0.1", headers=HEADERS)
        cls.client.__enter__()
    @classmethod
    def tearDownClass(cls):
        business._accounts_path.write_text(cls.original_accounts)
        cls.client.__exit__(None, None, None)
    def setUp(self):
        business._accounts_path.write_text(self.original_accounts)
        seed_database(); auth._attempts.clear(); self.client.cookies.clear()
        self.login()
    def login(self, identity="demo-officer-01"):
        response = self.client.post("/api/auth/login", json={"username": identity, "password": TEST_PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
    def preview(self, content=CSV, batch="RELIEF-2026-001"):
        return self.client.post("/api/beneficiaries/csv/preview", json={"batch_id": batch, "csv_content": content})
    def save(self, stage):
        return self.client.post("/api/beneficiaries/csv/" + stage + "/import")
    def test_preview_import_replay_preserves_history_and_requires_review(self):
        before = self.client.get("/api/distributions").json()
        result = self.preview(); self.assertEqual(result.status_code, 200, result.text)
        plan = result.json(); self.assertTrue(plan["valid"])
        self.assertEqual(plan["rows"][1]["matches"][0]["beneficiary_id"], "BEN-0002")
        self.assertEqual(len(self.client.get("/api/beneficiaries").json()), 24)
        saved = self.save(plan["import_id"]); self.assertEqual(saved.status_code, 201, saved.text)
        self.assertEqual(self.save(plan["import_id"]).json(), saved.json())
        self.assertEqual(self.save(plan["import_id"]).status_code, 200)
        for identity in saved.json()["beneficiary_ids"]:
            row = self.client.get("/api/beneficiaries/" + identity).json()
            self.assertEqual((row["review_status"], row["verification_status"]), ("PENDING", "FLAGGED_FOR_REVIEW"))
        self.assertEqual(self.client.get("/api/distributions").json(), before)
        with SessionLocal() as db: self.assertEqual(db.query(AuditEvent).filter_by(event_type="CSV_IMPORTED").count(), 1)
        repeated = self.preview().json(); self.assertFalse(repeated["valid"]); self.assertIsNone(repeated["import_id"])
    def test_invalid_rows_and_headers_never_import(self):
        for content in [CSV.replace("BEN-CSV-TWO", "BEN-CSV-ONE"), CSV.replace("San Isidro", "Wrong area"), CSV.replace("BEN-CSV-ONE", "BEN-0001"), CSV.replace("Synthetic Nima Solar", "x" * 129)]:
            plan = self.preview(content).json(); self.assertFalse(plan["valid"]); self.assertIsNone(plan["import_id"])
            self.assertTrue(any(row["errors"] for row in plan["rows"]))
        for content in ["wrong,columns\nx,y", "beneficiary_id,beneficiary_id,household_name,barangay_id,barangay_name\nx,x,y,z,w", CSV + '"unterminated']:
            self.assertEqual(self.preview(content).status_code, 422)
        self.assertEqual(len(self.client.get("/api/beneficiaries").json()), 24)
    def test_dafac_and_in_file_matches_are_review_suggestions(self):
        content = CSV.replace("BEN-CSV-TWO,Juan Dela Cruz", "BEN-CSV-TWO,Synthetic Nima Solar").replace("DFC-2026-0002", "DFC-CSV-ONE")
        plan = self.preview(content).json()
        self.assertTrue(plan["valid"])
        self.assertEqual(plan["rows"][0]["matches"][0]["record_status"], "IN_FILE")
        self.assertTrue(plan["rows"][0]["matches"][0]["same_dafac"])
    def test_retained_registry_matches_remain_visible(self):
        with SessionLocal() as db:
            db.query(Beneficiary).filter_by(beneficiary_id="BEN-0002").update({"record_status": "DUPLICATE", "canonical_beneficiary_id": "BEN-0004"}); db.commit()
        plan = self.preview().json()
        self.assertEqual(plan["rows"][1]["matches"][0]["record_status"], "DUPLICATE")
        self.assertEqual(self.save(plan["import_id"]).status_code, 201)
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0002").json()["record_status"], "DUPLICATE")
    def test_stale_expired_unknown_and_inactive_previews_are_refused(self):
        stage = self.preview().json()["import_id"]
        self.client.post("/api/beneficiaries/BEN-0007/verify", json={"status": "REJECTED", "review_notes": "Synthetic decision after preview"})
        self.assertEqual(self.save(stage).status_code, 409)
        stage = self.preview().json()["import_id"]
        with SessionLocal() as db: db.query(CsvImport).filter_by(import_id=stage).update({"expires_at": 0}); db.commit()
        self.assertEqual(self.save(stage).status_code, 409)
        self.assertEqual(self.save("missing").status_code, 404)
        self.assertEqual(self.preview(batch="missing").status_code, 409)
        with SessionLocal() as db: db.query(ReliefBatch).update({"status": "SUSPENDED"}); db.commit()
        self.assertEqual(self.preview().status_code, 409)
    def test_permissions_csrf_and_actor_bound_preview(self):
        stage = self.preview().json()["import_id"]
        accounts = json.loads(self.original_accounts)
        other = {**accounts["accounts"][0], "id": "synthetic-other-officer"}; accounts["accounts"].append(other)
        business._accounts_path.write_text(json.dumps(accounts)); self.login(other["id"])
        self.assertEqual(self.save(stage).status_code, 404)
        for identity in ["demo-auditor-01", "demo-barangay-01", "demo-beneficiary-01", "demo-disbursing-001"]:
            self.login(identity); self.assertEqual(self.preview().status_code, 403); self.assertEqual(self.save(stage).status_code, 403)
        self.login(); self.client.headers["X-CSRF-Token"] = "wrong"
        self.assertEqual(self.save(stage).status_code, 403)
    def test_parallel_import_replays_one_atomic_result(self):
        stage = self.preview().json()["import_id"]
        with ThreadPoolExecutor(max_workers=4) as pool: results = list(pool.map(lambda _: self.save(stage), range(4)))
        self.assertEqual(sorted(r.status_code for r in results), [200, 200, 200, 201])
        self.assertTrue(all(r.json() == results[0].json() for r in results))
        with SessionLocal() as db: self.assertEqual(db.query(Beneficiary).count(), 26)
    def test_failed_commit_rolls_back_registry_stage_and_audit(self):
        from sqlalchemy.orm import Session
        stage = self.preview().json()["import_id"]
        with patch.object(Session, "commit", side_effect=RuntimeError("Synthetic commit failure")):
            with self.assertRaises(RuntimeError): self.save(stage)
        with SessionLocal() as db:
            self.assertEqual(db.query(Beneficiary).count(), 24); self.assertIsNone(db.get(CsvImport, stage).result_json)
            self.assertEqual(db.query(AuditEvent).filter_by(event_type="CSV_IMPORTED").count(), 0)
        self.assertEqual(self.save(stage).status_code, 201)
    def test_row_limits_empty_and_utf8_bom(self):
        self.assertEqual(self.preview("beneficiary_id,household_name,barangay_id,barangay_name\n").status_code, 422)
        self.assertEqual(self.preview(CSV + "\n".join(f"BEN-LIM-{n},Synthetic Limit {n},BRGY-001,San Isidro," for n in range(200))).status_code, 413)
        self.assertTrue(self.preview("\ufeff" + CSV).json()["valid"])
        self.assertEqual(self.preview(CSV + "x" * 131072).status_code, 422)

if __name__ == "__main__": unittest.main(verbosity=2)
