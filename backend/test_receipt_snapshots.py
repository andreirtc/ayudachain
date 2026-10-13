"""Versioned snapshots, captured bytes, compatibility and tamper checks on owned data."""
import json
import hashlib
import unittest
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError
import test_api as business
from fastapi.testclient import TestClient
from auth_support import HEADERS, TEST_PASSWORD
from app import config
from app.database import SessionLocal, init_db
from app.models.entities import Distribution, Beneficiary, ReliefBatch, ReceiptSnapshot
from app.services.hasher import compute_receipt_hash, canonical_json, compute_sha256_hex
from app.services.receipt_snapshots import current_receipt_hash
from app.seed_demo import seed_database
from app.services.receipt_generator import DEMO_OCR_TEXT

class TestSnapshots(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.client=TestClient(business.app,base_url="http://127.0.0.1",headers=HEADERS);cls.client.__enter__()
    @classmethod
    def tearDownClass(cls): cls.client.__exit__(None,None,None)
    def login(self,identity="demo-disbursing-001"):
        r=self.client.post("/api/auth/login",json={"username":identity,"password":TEST_PASSWORD});self.assertEqual(r.status_code,200);self.client.headers["X-CSRF-Token"]=r.json()["csrf_token"]
    def setUp(self): seed_database();self.client.cookies.clear();self.login()
    def pay(self,**extra): return self.client.post("/api/distributions/confirm",headers={"Idempotency-Key":"snapshot-fixture"},json={"beneficiary_id":"BEN-0004","batch_id":"RELIEF-2026-001","amount":"100.25",**extra})
    def verify(self,id): return self.client.post("/api/blockchain/verify",json={"distribution_id":id}).json()
    def test_v2_exact_snapshot_hash_and_replay(self):
        result=self.pay();self.assertEqual(result.status_code,201,result.text);row=result.json();self.assertEqual(row["receipt_version"],2);self.assertEqual(row["receipt_snapshot"]["payout"]["amount_centavos"],10025)
        self.assertEqual(row["receipt_hash"],compute_sha256_hex(canonical_json({**row["receipt_snapshot"],"payout":{**row["receipt_snapshot"]["payout"],"receipt_file_path":"/receipts/snapshot-"+row["distribution_id"]},"receipt":{**row["receipt_snapshot"]["receipt"],"ocr_text":DEMO_OCR_TEXT}})))
        self.assertEqual(self.verify(row["distribution_id"])["verification_status"],"VERIFIED")
        self.assertEqual(self.pay().json(),row)
        with SessionLocal() as db: self.assertEqual(db.query(ReceiptSnapshot).count(),1)
    def test_snapshot_only_tamper_cannot_be_hidden_by_unchanged_live_values(self):
        row=self.pay().json()
        with SessionLocal() as db:
            db.execute(text("DROP TRIGGER receipt_snapshot_no_update"))
            saved=db.get(ReceiptSnapshot,row["distribution_id"]);data=json.loads(saved.snapshot_json);data["payout"]["amount_centavos"]+=1;saved.snapshot_json=canonical_json(data);db.commit()
        self.assertEqual(self.verify(row["distribution_id"])["verification_status"],"MISMATCH")
    def test_source_file_and_registry_changes_do_not_rewrite_original(self):
        source=Path(config.RECEIPTS_DIR,"captured.svg");content=b'<svg xmlns="http://www.w3.org/2000/svg"><text>Synthetic original evidence</text></svg>';source.write_bytes(content)
        row=self.pay(receipt_filename="captured.svg",ocr_raw_text="Synthetic captured receipt").json()
        self.assertEqual(row["receipt_snapshot"]["receipt"]["document"]["sha256"],"0x"+hashlib.sha256(content).hexdigest())
        source.write_bytes(b"changed source file")
        with SessionLocal() as db:
            db.query(Beneficiary).filter_by(beneficiary_id="BEN-0004").update({"household_name":"Synthetic changed registry label"});db.query(ReliefBatch).update({"calamity_name":"Changed current batch label"});db.commit()
        self.assertEqual(self.client.get(row["receipt_file_path"]).content,content)
        self.assertEqual(self.verify(row["distribution_id"])["verification_status"],"VERIFIED")
        current=next(r for r in self.client.get("/api/distributions").json() if r["distribution_id"]==row["distribution_id"])
        self.assertEqual(current["receipt_snapshot"]["household"]["household_name"],"Danilo Soriano");self.assertEqual(current["receipt_hash"],row["receipt_hash"])
    def test_snapshot_updates_and_deletes_are_blocked_on_sqlite(self):
        row=self.pay().json();init_db()
        for statement in ["UPDATE receipt_snapshots SET snapshot_json='{}'", "DELETE FROM receipt_snapshots"]:
            with SessionLocal() as db:
                with self.assertRaises(DatabaseError): db.execute(text(statement));db.commit()
        self.assertEqual(self.verify(row["distribution_id"])["verification_status"],"VERIFIED")
    def test_payout_and_ocr_tamper_mismatch_and_restore(self):
        row=self.pay().json()
        with SessionLocal() as db: db.query(Distribution).filter_by(distribution_id=row["distribution_id"]).update({"amount_centavos":10026});db.commit()
        self.assertEqual(self.verify(row["distribution_id"])["verification_status"],"MISMATCH")
        with SessionLocal() as db: db.query(Distribution).filter_by(distribution_id=row["distribution_id"]).update({"amount_centavos":10025});db.commit()
        self.assertEqual(self.verify(row["distribution_id"])["verification_status"],"VERIFIED")
        with SessionLocal() as db: db.query(Distribution).filter_by(distribution_id=row["distribution_id"]).update({"ocr_text":"Altered local OCR"});db.commit()
        self.assertEqual(self.verify(row["distribution_id"])["verification_status"],"MISMATCH")
    def test_legacy_hashes_and_records_are_not_backfilled(self):
        self.login("demo-auditor-01");before=self.client.get("/api/distributions").json();init_db();after=self.client.get("/api/distributions").json();self.assertEqual(before,after)
        self.assertTrue(all(r["receipt_version"]==1 and r["receipt_snapshot"] is None for r in after))
        with SessionLocal() as db:
            dist=db.query(Distribution).filter_by(distribution_id="DIST-0001").one();self.assertEqual(current_receipt_hash(dist),compute_receipt_hash(distribution_id=dist.distribution_id,beneficiary_id=dist.beneficiary_id,batch_id=dist.batch_id,amount_centavos=dist.amount_centavos,ocr_text=dist.ocr_text,verification_method=dist.verification_method))
    def test_shared_template_redaction_and_office_capture_are_preserved(self):
        row=self.pay().json();self.assertIsNone(row["receipt_file_path"]);self.assertIsNone(row["receipt_snapshot"]["receipt"]["ocr_text"]);self.assertEqual(row["receipt_snapshot"]["receipt"]["document"]["kind"],"SHARED_TEMPLATE")
        self.login("demo-auditor-01");office=next(r for r in self.client.get("/api/distributions").json() if r["distribution_id"]==row["distribution_id"]);self.assertTrue(office["receipt_snapshot"]["receipt"]["ocr_text"]);self.assertEqual(self.client.get(office["receipt_file_path"]).status_code,200)
        self.login("demo-beneficiary-01");self.assertEqual(self.client.get(office["receipt_file_path"]).status_code,404)
        self.client.cookies.clear();self.assertEqual(self.client.get(office["receipt_file_path"]).status_code,401);proof=self.verify(row["distribution_id"]);self.assertNotIn("receipt_snapshot",proof);self.assertIsNone(proof["beneficiary_id"])
    def test_missing_evidence_is_explicit_and_not_silently_backfilled(self):
        missing=Path(config.RECEIPTS_DIR,"not-yet-present.svg");missing.unlink(missing_ok=True)
        row=self.pay(receipt_filename=missing.name).json();self.assertEqual(row["receipt_snapshot"]["receipt"]["document"]["kind"],"MISSING");self.assertIsNone(row["receipt_file_path"])
        missing.write_bytes(b"later file");self.assertEqual(self.pay(receipt_filename=missing.name).json(),row)
    def test_unsafe_file_references_and_large_evidence_never_record_payout(self):
        self.assertEqual(self.pay(receipt_filename="../outside.svg").status_code,422)
        Path(config.RECEIPTS_DIR,"oversized.svg").write_bytes(b"x"*(2*1024*1024+1));self.assertEqual(self.pay(receipt_filename="oversized.svg").status_code,413)
        self.assertEqual(self.pay().status_code,201)
    def test_source_evidence_cannot_be_captured_from_another_scope(self):
        Path(config.RECEIPTS_DIR,"other-scope.svg").write_bytes(b"Synthetic private evidence")
        with SessionLocal() as db: db.query(Distribution).filter_by(distribution_id="DIST-0004").update({"receipt_file_path":"/receipts/other-scope.svg"});db.commit()
        self.assertEqual(self.pay(receipt_filename="other-scope.svg").status_code,404)

    def test_canonical_serialization_is_order_independent(self):
        self.assertEqual(compute_sha256_hex(canonical_json({"version":2,"amount_centavos":10025,"name":"Synthetic Ñ"})),compute_sha256_hex(canonical_json({"name":"Synthetic Ñ","amount_centavos":10025,"version":2})))

if __name__=="__main__":unittest.main(verbosity=2)
