"""
AyudaChain API Test Suite
Exercises the FastAPI app against a temporary SQLite database and a fake
blockchain service, so no Hardhat node is needed.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_tmp_dir = tempfile.mkdtemp(prefix="ayudachain-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp_dir, 'test.db')}"

from fastapi.testclient import TestClient

from app.services.blockchain import blockchain_service


class FakeChain:
    """Stands in for the Node CLI bridge and remembers anchored receipt hashes."""

    def __init__(self):
        self.receipts = {}
        self.tx_count = 0

    def _tx(self):
        self.tx_count += 1
        return {"success": True, "txHash": "0x" + f"{self.tx_count:064x}"}

    def get_status(self):
        return {"success": True, "network": "Test Chain", "chainId": 31337, "contractAddress": "0xTEST"}

    def release_fund(self, *args, **kwargs):
        return self._tx()

    def allocate_fund(self, *args, **kwargs):
        return self._tx()

    def confirm_distribution(self, batch_id, allocation_id, distribution_id, beneficiary_id, amount_centavos, receipt_hash):
        self.receipts[distribution_id] = receipt_hash
        return self._tx()

    def verify_receipt(self, distribution_id, receipt_hash):
        onchain = self.receipts.get(distribution_id, "0x" + "0" * 64)
        return {"success": True, "matched": onchain == receipt_hash, "onchainHash": onchain, "timestamp": 1}


fake_chain = FakeChain()
for _name in ("get_status", "release_fund", "allocate_fund", "confirm_distribution", "verify_receipt"):
    setattr(blockchain_service, _name, getattr(fake_chain, _name))

from app.main import app


class TestAyudaChainAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def setUp(self):
        res = self.client.post("/api/demo/reset")
        self.assertEqual(res.status_code, 200)

    def test_startup_seeds_demo_batch(self):
        res = self.client.get("/api/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["batch_id"], "RELIEF-2026-001")
        self.assertEqual(data["total_beneficiaries"], 24)
        self.assertEqual(data["confirmed_distributions"], 5)
        self.assertEqual(data["total_distributed"], 25000.0)

    def test_beneficiaries_include_dafac_id(self):
        res = self.client.get("/api/beneficiaries/BEN-0001")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["dafac_id"], "DFC-2026-0001")

    def test_register_flags_likely_duplicate(self):
        res = self.client.post("/api/beneficiaries", json={
            "beneficiary_id": "BEN-0100",
            "household_name": "Juan Dela Cruz",
            "barangay_id": "BRGY-001",
            "barangay_name": "San Isidro",
            "batch_id": "RELIEF-2026-001",
        })
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.json()["duplicate_flag"])
        self.assertEqual(res.json()["verification_status"], "FLAGGED_FOR_REVIEW")

    def test_payout_then_verify_receipt(self):
        res = self.client.post("/api/distributions/confirm", json={
            "distribution_id": "DIST-0100",
            "beneficiary_id": "BEN-0004",
            "batch_id": "RELIEF-2026-001",
            "amount": 5000.0,
        })
        self.assertEqual(res.status_code, 201)

        res = self.client.post("/api/blockchain/verify", json={"distribution_id": "DIST-0100"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["is_verified"])
        self.assertEqual(data["beneficiary_id"], "BEN-0004")

    def test_second_payout_to_same_household_rejected(self):
        res = self.client.post("/api/distributions/confirm", json={
            "distribution_id": "DIST-0101",
            "beneficiary_id": "BEN-0001",
            "batch_id": "RELIEF-2026-001",
            "amount": 5000.0,
        })
        self.assertEqual(res.status_code, 400)

    def test_payout_above_demo_maximum_rejected(self):
        res = self.client.post("/api/distributions/confirm", json={
            "distribution_id": "DIST-0102",
            "beneficiary_id": "BEN-0004",
            "batch_id": "RELIEF-2026-001",
            "amount": 15000.0,
        })
        self.assertEqual(res.status_code, 400)

    def test_tampered_receipt_fails_verification(self):
        fake_chain.receipts["DIST-0001"] = "0x" + "f" * 64
        res = self.client.post("/api/blockchain/verify", json={"distribution_id": "DIST-0001"})
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["is_verified"])

    def test_csv_sample_and_upload(self):
        res = self.client.get("/api/beneficiaries/sample-csv")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.headers["content-type"].startswith("text/csv"))

        res = self.client.post("/api/beneficiaries/upload-csv", json={"csv_content": ""})
        self.assertEqual(res.status_code, 200)
        self.assertGreater(res.json()["total_records_processed"], 0)

    def test_amounts_are_exact_centavos(self):
        dist = self.client.get("/api/distributions").json()[0]
        self.assertEqual(dist["amount_centavos"], 500_000)
        self.assertEqual(dist["amount"], 5000.0)

        self._release("RELIEF-TEST-001", 1000)
        res = self._allocate("ALLOC-0100", "RELIEF-TEST-001", 0.1)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["amount_centavos"], 10)

    def _release(self, batch_id, amount):
        res = self.client.post("/api/funds/releases", json={
            "batch_id": batch_id,
            "calamity_name": "Test Flood",
            "amount": amount,
        })
        self.assertEqual(res.status_code, 201)

    def _allocate(self, allocation_id, batch_id, amount, barangay_id="BRGY-001", barangay_name="San Isidro"):
        return self.client.post("/api/allocations", json={
            "allocation_id": allocation_id,
            "batch_id": batch_id,
            "barangay_id": barangay_id,
            "barangay_name": barangay_name,
            "amount": amount,
        })

    def test_allocations_cannot_exceed_released_funds(self):
        self._release("RELIEF-TEST-002", 1000)
        self.assertEqual(self._allocate("ALLOC-0200", "RELIEF-TEST-002", 600).status_code, 201)

        res = self._allocate("ALLOC-0201", "RELIEF-TEST-002", 400.01, "BRGY-002", "Santa Elena")
        self.assertEqual(res.status_code, 400)
        self.assertIn("₱400.00", res.json()["detail"])

        self.assertEqual(self._allocate("ALLOC-0202", "RELIEF-TEST-002", 400, "BRGY-002", "Santa Elena").status_code, 201)
        dashboard_alloc = sum(a["amount_centavos"] for a in self.client.get("/api/batches/RELIEF-TEST-002").json()["allocations"])
        self.assertEqual(dashboard_alloc, 100_000)

    def test_fully_allocated_seed_batch_rejects_more(self):
        res = self._allocate("ALLOC-0300", "RELIEF-2026-001", 1)
        self.assertEqual(res.status_code, 400)

    def test_allocation_requires_known_batch_and_barangay(self):
        self.assertEqual(self._allocate("ALLOC-0400", "RELIEF-NOPE", 1).status_code, 404)

        self._release("RELIEF-TEST-003", 1000)
        res = self._allocate("ALLOC-0401", "RELIEF-TEST-003", 1, barangay_id="BRGY-999", barangay_name="Nowhere")
        self.assertEqual(res.status_code, 400)
        res = self._allocate("ALLOC-0402", "RELIEF-TEST-003", 1, barangay_id="BRGY-001", barangay_name="Maligaya")
        self.assertEqual(res.status_code, 400)

    def test_one_allocation_per_barangay_per_batch(self):
        self._release("RELIEF-TEST-006", 1000)
        self.assertEqual(self._allocate("ALLOC-0600", "RELIEF-TEST-006", 100).status_code, 201)
        res = self._allocate("ALLOC-0601", "RELIEF-TEST-006", 100)
        self.assertEqual(res.status_code, 400)
        self.assertIn("ALLOC-0600", res.json()["detail"])

    def _register(self, ben_id, name, batch_id, barangay_id="BRGY-003", barangay_name="San Roque"):
        res = self.client.post("/api/beneficiaries", json={
            "beneficiary_id": ben_id, "household_name": name,
            "barangay_id": barangay_id, "barangay_name": barangay_name, "batch_id": batch_id,
        })
        self.assertEqual(res.status_code, 201)

    def _pay(self, dist_id, ben_id, batch_id, amount):
        return self.client.post("/api/distributions/confirm", json={
            "distribution_id": dist_id, "beneficiary_id": ben_id, "batch_id": batch_id, "amount": amount,
        })

    def test_payouts_cannot_exceed_barangay_allocation(self):
        self._release("RELIEF-TEST-010", 10000)
        self.assertEqual(self._allocate("ALLOC-1000", "RELIEF-TEST-010", 6000, "BRGY-003", "San Roque").status_code, 201)
        self._register("BEN-1001", "Amelia Ferrer", "RELIEF-TEST-010")
        self._register("BEN-1002", "Benigno Lacson", "RELIEF-TEST-010")
        self._register("BEN-1003", "Clarita Umali", "RELIEF-TEST-010")

        res = self._pay("DIST-1001", "BEN-1001", "RELIEF-TEST-010", 5000)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["allocation_id"], "ALLOC-1000")

        res = self._pay("DIST-1002", "BEN-1002", "RELIEF-TEST-010", 5000)
        self.assertEqual(res.status_code, 400)
        self.assertIn("₱1,000.00", res.json()["detail"])

        self.assertEqual(self._pay("DIST-1003", "BEN-1003", "RELIEF-TEST-010", 1000).status_code, 201)

    def test_payout_requires_matching_batch_and_allocation(self):
        res = self._pay("DIST-1100", "BEN-0004", "RELIEF-OTHER", 5000)
        self.assertEqual(res.status_code, 400)

        self._release("RELIEF-TEST-011", 10000)
        self._register("BEN-1101", "Dionisio Salonga", "RELIEF-TEST-011")
        res = self._pay("DIST-1101", "BEN-1101", "RELIEF-TEST-011", 5000)
        self.assertEqual(res.status_code, 400)
        self.assertIn("no allocation", res.json()["detail"])

    def test_grant_policy_is_per_batch(self):
        res = self.client.post("/api/funds/releases", json={
            "batch_id": "RELIEF-TEST-020", "calamity_name": "Test Quake",
            "amount": 100000, "standard_grant": 3000, "max_grant": 4000,
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["standard_grant_centavos"], 300_000)
        self.assertEqual(res.json()["max_grant"], 4000.0)
        self._allocate("ALLOC-2000", "RELIEF-TEST-020", 50000, "BRGY-003", "San Roque")
        self._register("BEN-2001", "Esperanza Dizon", "RELIEF-TEST-020")
        self._register("BEN-2002", "Feliciano Arroyo", "RELIEF-TEST-020")

        res = self._pay("DIST-2001", "BEN-2001", "RELIEF-TEST-020", 4500)
        self.assertEqual(res.status_code, 400)
        self.assertIn("₱4,000.00", res.json()["detail"])

        self.assertEqual(self._pay("DIST-2001", "BEN-2001", "RELIEF-TEST-020", 3000).status_code, 201)
        self.assertFalse(self.client.get("/api/beneficiaries/BEN-2001").json()["anomaly_flag"])

        self.assertEqual(self._pay("DIST-2002", "BEN-2002", "RELIEF-TEST-020", 3500).status_code, 201)
        self.assertTrue(self.client.get("/api/beneficiaries/BEN-2002").json()["anomaly_flag"])

    def test_standard_grant_cannot_exceed_maximum(self):
        res = self.client.post("/api/funds/releases", json={
            "batch_id": "RELIEF-TEST-021", "calamity_name": "X",
            "amount": 100000, "standard_grant": 5000, "max_grant": 4000,
        })
        self.assertEqual(res.status_code, 400)

    def test_seed_batch_policy(self):
        batch = self.client.get("/api/batches/RELIEF-2026-001").json()["batch"]
        self.assertEqual(batch["standard_grant_centavos"], 500_000)
        self.assertEqual(batch["max_grant_centavos"], 1_000_000)

    def test_payout_requires_approved_beneficiary(self):
        # BEN-0007 is a seeded possible duplicate awaiting review
        res = self._pay("DIST-3001", "BEN-0007", "RELIEF-2026-001", 5000)
        self.assertEqual(res.status_code, 400)
        self.assertIn("not approved", res.json()["detail"])

        res = self.client.post("/api/beneficiaries/BEN-0007/verify", json={"status": "VERIFIED", "review_notes": "Different household", "reviewed_by": "demo-auditor-01"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self._pay("DIST-3001", "BEN-0007", "RELIEF-2026-001", 5000).status_code, 201)

    def test_payout_rejected_for_rejected_beneficiary(self):
        self.client.post("/api/beneficiaries/BEN-0014/verify", json={"status": "REJECTED", "review_notes": "Same as BEN-0013", "reviewed_by": "demo-auditor-01"})
        self.assertEqual(self._pay("DIST-3002", "BEN-0014", "RELIEF-2026-001", 5000).status_code, 400)

    def test_payout_requires_active_batch(self):
        from app.database import SessionLocal
        from app.models.entities import ReliefBatch
        db = SessionLocal()
        try:
            db.query(ReliefBatch).filter(ReliefBatch.batch_id == "RELIEF-2026-001").update({"status": "SUSPENDED"})
            db.commit()
        finally:
            db.close()
        res = self._pay("DIST-3003", "BEN-0004", "RELIEF-2026-001", 5000)
        self.assertEqual(res.status_code, 400)
        self.assertIn("SUSPENDED", res.json()["detail"])

    def test_database_rejects_second_payout_in_batch(self):
        from sqlalchemy.exc import IntegrityError
        from app.database import SessionLocal
        from app.models.entities import Distribution
        db = SessionLocal()
        try:
            db.add(Distribution(
                distribution_id="DIST-4001", beneficiary_id="BEN-0001", batch_id="RELIEF-2026-001",
                allocation_id="ALLOC-0001", amount_centavos=500_000, receipt_hash="0x" + "1" * 64,
            ))
            with self.assertRaises(IntegrityError):
                db.commit()
        finally:
            db.rollback()
            db.close()

    def test_concurrent_payouts_pay_once(self):
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=5) as pool:
            codes = list(pool.map(
                lambda i: self._pay(f"DIST-50{i:02d}", "BEN-0004", "RELIEF-2026-001", 5000).status_code,
                range(5),
            ))
        self.assertEqual(codes.count(201), 1, codes)
        paid = [d for d in self.client.get("/api/distributions").json() if d["beneficiary_id"] == "BEN-0004"]
        self.assertEqual(len(paid), 1)

    def _keyed_pay(self, key="payout-test", **overrides):
        return self.client.post("/api/distributions/confirm", headers={"Idempotency-Key": key}, json={
            "beneficiary_id": "BEN-0004", "batch_id": "RELIEF-2026-001", "amount": 5000,
            **overrides,
        })

    def test_idempotent_retry_returns_persisted_uuid_payout_once(self):
        from uuid import UUID
        from app.database import SessionLocal
        from app.models.entities import AuditEvent, ReliefBatch
        before = fake_chain.tx_count
        first = self._keyed_pay()
        self.assertEqual(first.status_code, 201, first.text)
        UUID(first.json()["distribution_id"].removeprefix("DIST-"))
        # A later eligibility change must not hide an already recorded result.
        with SessionLocal() as db:
            db.query(ReliefBatch).filter_by(batch_id="RELIEF-2026-001").update({"status": "SUSPENDED"})
            db.commit()
        # Use a new client/session to establish that replay is not an in-memory cache.
        retry = TestClient(app).post("/api/distributions/confirm", headers={"Idempotency-Key": "payout-test"}, json={
            "beneficiary_id": "BEN-0004", "batch_id": "RELIEF-2026-001", "amount": "5000.00",
        })
        self.assertEqual(retry.status_code, 200, retry.text)
        self.assertEqual(first.json(), retry.json())
        self.assertEqual(fake_chain.tx_count - before, 1)
        with SessionLocal() as db:
            self.assertEqual(db.query(AuditEvent).filter_by(entity_id=first.json()["distribution_id"]).count(), 1)

    def test_changed_request_with_same_key_conflicts(self):
        self.assertEqual(self._keyed_pay().status_code, 201)
        before = fake_chain.tx_count
        for changed in (
            {"amount": 4000}, {"beneficiary_id": "BEN-0005"}, {"batch_id": "RELIEF-OTHER"},
            {"receipt_filename": "other.svg"}, {"ocr_raw_text": "Changed receipt"},
            {"verification_method": "OTHER"}, {"distribution_id": "DIST-OTHER"},
        ):
            with self.subTest(changed=changed):
                self.assertEqual(self._keyed_pay(**changed).status_code, 409)
        self.assertEqual(fake_chain.tx_count, before)

    def test_legacy_stable_distribution_id_replays(self):
        first = self._pay("DIST-RETRY", "BEN-0004", "RELIEF-2026-001", 5000)
        retry = self._pay("DIST-RETRY", "BEN-0004", "RELIEF-2026-001", 5000)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(first.json(), retry.json())
        self.assertEqual(self._pay("DIST-RETRY", "BEN-0004", "RELIEF-2026-001", 4000).status_code, 409)

    def test_different_key_cannot_claim_existing_distribution_id(self):
        self.assertEqual(self._keyed_pay(distribution_id="DIST-KEYED").status_code, 201)
        self.assertEqual(self._keyed_pay(key="another-key", distribution_id="DIST-KEYED").status_code, 409)
        self.assertEqual(self._keyed_pay().status_code, 409)

    def test_retry_identity_validation(self):
        payload = {"beneficiary_id": "BEN-0004", "batch_id": "RELIEF-2026-001", "amount": 5000}
        self.assertEqual(self.client.post("/api/distributions/confirm", json=payload).status_code, 422)
        for key in ("", "x" * 129, "white space"):
            self.assertEqual(self._keyed_pay(key=key).status_code, 422)
        self.assertEqual(self._keyed_pay(distribution_id="x" * 65).status_code, 422)
        self.assertEqual(self._keyed_pay(distribution_id="").status_code, 422)

    def test_rejected_request_does_not_consume_key(self):
        self.assertEqual(self._keyed_pay(amount=15000).status_code, 400)
        self.assertEqual(self._keyed_pay().status_code, 201)

    def test_payout_survives_anchor_exception_and_retry_does_not_resubmit(self):
        from app.database import SessionLocal
        from app.models.entities import Distribution
        def fail_after_recording(**kwargs):
            with SessionLocal() as db:
                self.assertIsNotNone(db.query(Distribution).filter_by(distribution_id=kwargs["distribution_id"]).first())
            raise TimeoutError("Submission result unknown")
        with patch.object(blockchain_service, "confirm_distribution", side_effect=fail_after_recording) as submit:
            first = self._keyed_pay()
            retry = self._keyed_pay()
        self.assertEqual(first.status_code, 201, first.text)
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(first.json(), retry.json())
        self.assertIsNone(first.json()["blockchain_tx_hash"])
        self.assertEqual(submit.call_count, 1)

    def test_failed_anchor_does_not_store_fabricated_transaction_hash(self):
        with patch.object(blockchain_service, "confirm_distribution", return_value={"success": False, "txHash": "0xfabricated"}) as submit:
            first = self._keyed_pay()
            retry = self._keyed_pay()
        self.assertEqual(first.status_code, 201)
        self.assertEqual(retry.status_code, 200)
        self.assertIsNone(first.json()["blockchain_tx_hash"])
        self.assertEqual(submit.call_count, 1)

    def test_failed_database_commit_does_not_anchor(self):
        from sqlalchemy.orm import Session
        with patch.object(blockchain_service, "confirm_distribution", wraps=fake_chain.confirm_distribution) as submit:
            with patch.object(Session, "commit", side_effect=RuntimeError("Database failure")):
                with self.assertRaises(RuntimeError):
                    self._keyed_pay()
            self.assertEqual(submit.call_count, 0)
        # No payout was committed, so this key can be submitted normally.
        with patch.object(blockchain_service, "confirm_distribution", wraps=fake_chain.confirm_distribution) as submit:
            self.assertEqual(self._keyed_pay().status_code, 201)
        self.assertEqual(submit.call_count, 1)

    def test_lost_anchor_metadata_commit_replays_without_another_submission(self):
        from sqlalchemy.orm import Session
        original_commit = Session.commit
        commit_count = 0
        def fail_second_commit(db):
            nonlocal commit_count
            commit_count += 1
            if commit_count == 2:
                raise RuntimeError("Anchor metadata commit failed")
            return original_commit(db)
        with patch.object(blockchain_service, "confirm_distribution", wraps=fake_chain.confirm_distribution) as submit:
            with patch.object(Session, "commit", fail_second_commit):
                with self.assertRaises(RuntimeError):
                    self._keyed_pay()
            retry = self._keyed_pay()
        self.assertEqual(retry.status_code, 200)
        self.assertIsNone(retry.json()["blockchain_tx_hash"])
        self.assertEqual(submit.call_count, 1)
        # The receipt can exist on-chain despite lost local transaction metadata.
        self.assertIn(retry.json()["distribution_id"], fake_chain.receipts)

    def test_concurrent_same_key_replays_without_process_lock(self):
        from concurrent.futures import ThreadPoolExecutor
        from contextlib import nullcontext
        import threading
        import app.main as api
        barrier = threading.Barrier(4)
        thread_state = threading.local()
        original_replay = api._replayed_payout
        def simultaneous_initial_lookup(*args):
            existing = original_replay(*args)
            if not getattr(thread_state, "started", False):
                thread_state.started = True
                barrier.wait(timeout=10)
            return existing
        before = fake_chain.tx_count
        with patch.object(api, "_funds_lock", nullcontext()), patch.object(api, "_replayed_payout", side_effect=simultaneous_initial_lookup):
            with ThreadPoolExecutor(max_workers=4) as pool:
                results = list(pool.map(lambda _: self._keyed_pay(), range(4)))
        codes = [r.status_code for r in results]
        self.assertEqual(codes.count(201), 1, codes)
        self.assertEqual(codes.count(200), 3, codes)
        self.assertEqual(len({r.json()["distribution_id"] for r in results}), 1)
        self.assertEqual(fake_chain.tx_count - before, 1)

    def test_idempotency_key_has_database_uniqueness(self):
        from sqlalchemy.exc import IntegrityError
        from app.database import SessionLocal
        from app.models.entities import Distribution
        self.assertEqual(self._keyed_pay().status_code, 201)
        with SessionLocal() as db:
            db.add(Distribution(
                distribution_id="DIST-CONFLICT", beneficiary_id="BEN-0005", batch_id="RELIEF-2026-001",
                allocation_id="ALLOC-0001", amount_centavos=500_000, receipt_hash="0x" + "1" * 64,
                idempotency_key="payout-test",
            ))
            with self.assertRaises(IntegrityError):
                db.commit()

    def test_sqlite_retry_migration_preserves_previous_records(self):
        from sqlalchemy import create_engine, inspect, text
        import app.database as database
        migration_engine = create_engine(f"sqlite:///{os.path.join(_tmp_dir, 'migration.db')}")
        with migration_engine.begin() as conn:
            conn.execute(text("CREATE TABLE distributions (id INTEGER PRIMARY KEY, distribution_id VARCHAR(64))"))
            conn.execute(text("INSERT INTO distributions VALUES (1, 'DIST-HISTORY')"))
        with patch.object(database, "engine", migration_engine):
            database._migrate_payout_idempotency()
            # Recover an interrupted migration that added columns but lost its index.
            with migration_engine.begin() as conn:
                conn.execute(text("DROP INDEX ix_distributions_idempotency_key"))
            database._migrate_payout_idempotency()
        with migration_engine.connect() as conn:
            self.assertEqual(conn.execute(text("SELECT distribution_id FROM distributions")).scalar(), "DIST-HISTORY")
        self.assertIn("idempotency_key", {c["name"] for c in inspect(migration_engine).get_columns("distributions")})
        self.assertTrue(any(i["unique"] and i["column_names"] == ["idempotency_key"] for i in inspect(migration_engine).get_indexes("distributions")))
        migration_engine.dispose()

    def test_seeded_payouts_link_to_allocations(self):
        dists = {d["distribution_id"]: d["allocation_id"] for d in self.client.get("/api/distributions").json()}
        self.assertEqual(dists["DIST-0001"], "ALLOC-0001")
        self.assertEqual(dists["DIST-0005"], "ALLOC-0002")

    def test_zero_or_negative_amounts_rejected(self):
        res = self.client.post("/api/funds/releases", json={"batch_id": "RELIEF-TEST-004", "calamity_name": "X", "amount": 0})
        self.assertEqual(res.status_code, 422)
        self._release("RELIEF-TEST-005", 1000)
        self.assertEqual(self._allocate("ALLOC-0500", "RELIEF-TEST-005", -5).status_code, 422)

    def test_register_requires_known_batch_and_barangay(self):
        base = {"beneficiary_id": "BEN-0500", "household_name": "Test Household", "barangay_id": "BRGY-001", "barangay_name": "San Isidro"}
        self.assertEqual(self.client.post("/api/beneficiaries", json={**base, "batch_id": "RELIEF-NOPE"}).status_code, 404)
        res = self.client.post("/api/beneficiaries", json={**base, "batch_id": "RELIEF-2026-001", "barangay_id": "BRGY-999"})
        self.assertEqual(res.status_code, 400)

    def test_fractional_centavo_rejected(self):
        res = self.client.post("/api/distributions/confirm", json={
            "distribution_id": "DIST-0103",
            "beneficiary_id": "BEN-0004",
            "batch_id": "RELIEF-2026-001",
            "amount": 5000.001,
        })
        self.assertEqual(res.status_code, 422)

    def test_dashboard_reports_unavailable_chain(self):
        original = blockchain_service.get_status
        blockchain_service.get_status = lambda: {"success": False, "network": "Local EVM", "chainId": 31337}
        try:
            data = self.client.get("/api/dashboard").json()
        finally:
            blockchain_service.get_status = original
        self.assertEqual(data["blockchain_status"], "UNAVAILABLE")

    def test_contract_address_comes_from_deployment_file(self):
        from app import config
        deployment = config._load_deployment(config.DEPLOYMENT_FILE)
        if "CONTRACT_ADDRESS" not in os.environ:
            self.assertEqual(config.CONTRACT_ADDRESS, deployment.get("contractAddress"))
        self.assertEqual(config.CHAIN_ID, int(os.getenv("CHAIN_ID") or deployment.get("chainId") or 31337))

    def _review(self, ben_id="BEN-0007", status="VERIFIED", reason="Different fictional household", actor="demo-auditor-01"):
        return self.client.post(f"/api/beneficiaries/{ben_id}/verify", json={
            "status": status, "review_notes": reason, "reviewed_by": actor,
        })

    def _reviews(self, ben_id="BEN-0007"):
        response = self.client.get(f"/api/beneficiaries/{ben_id}/reviews")
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_approve_duplicate_records_actor_reason_timestamp_and_evidence(self):
        from datetime import datetime, timezone
        from uuid import UUID
        before = self.client.get("/api/beneficiaries/BEN-0007").json()
        started = datetime.now(timezone.utc)
        response = self._review(reason="  Different fictional household  ")
        self.assertEqual(response.status_code, 200, response.text)
        approved = response.json()
        self.assertEqual((approved["verification_status"], approved["review_status"]), ("VERIFIED", "APPROVED"))
        self.assertFalse(approved["duplicate_flag"])
        self.assertFalse(approved["anomaly_flag"])
        self.assertEqual(approved["duplicate_matched_id"], before["duplicate_matched_id"])
        self.assertEqual(approved["duplicate_confidence"], before["duplicate_confidence"])
        self.assertNotIn("BEN-0007", {b["beneficiary_id"] for b in self.client.get("/api/beneficiaries?flagged_only=true").json()})
        review = self._reviews()[0]
        UUID(review["review_id"].removeprefix("REVIEW-"))
        self.assertEqual(review["reason"], "Different fictional household")
        self.assertEqual(review["reviewed_by"], "demo-auditor-01")
        timestamp = datetime.fromisoformat(review["reviewed_at"].replace("Z", "+00:00"))
        self.assertGreaterEqual(timestamp, started)
        self.assertLessEqual(timestamp, datetime.now(timezone.utc))
        self.assertEqual(review["previous_review_notes"], before["review_notes"])
        self.assertTrue(review["duplicate_flag_before"])
        self.assertFalse(review["duplicate_flag_after"])
        self.assertEqual(review["matched_beneficiary_id"], "BEN-0002")
        events = self.client.get("/api/audit-trail/RELIEF-2026-001").json()
        audit = next(e for e in events if e["event_type"] == "BENEFICIARY_REVIEWED")
        self.assertIn(review["review_id"], audit["description"])
        self.assertIsNone(audit["blockchain_tx_hash"])

    def test_rejection_resolves_flags_but_blocks_payout(self):
        rejected = self._review(status="REJECTED", reason="Confirmed same fictional household").json()
        self.assertEqual((rejected["verification_status"], rejected["review_status"]), ("REJECTED", "REJECTED"))
        self.assertFalse(rejected["duplicate_flag"])
        self.assertNotIn("BEN-0007", {b["beneficiary_id"] for b in self.client.get("/api/beneficiaries?flagged_only=true").json()})
        self.assertEqual(self._pay("DIST-REJECTED", "BEN-0007", "RELIEF-2026-001", 5000).status_code, 400)
        self.assertEqual(self._reviews()[0]["decision"], "REJECTED")

    def test_keep_pending_never_sets_rejected_review_state(self):
        response = self._review(status="FLAGGED_FOR_REVIEW", reason="Need more evidence")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual((data["verification_status"], data["review_status"]), ("FLAGGED_FOR_REVIEW", "PENDING"))
        self.assertTrue(data["duplicate_flag"])
        self.assertEqual(self._pay("DIST-PENDING", "BEN-0007", "RELIEF-2026-001", 5000).status_code, 400)

    def test_reopened_review_restores_flags_and_preserves_prior_decisions(self):
        self.assertEqual(self._review().status_code, 200)
        first = self._reviews()[0]
        self.assertEqual(self._review(status="FLAGGED_FOR_REVIEW", reason="Recheck household evidence").status_code, 200)
        history = self._reviews()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[1], first)
        self.assertEqual(history[0]["previous_verification_status"], "VERIFIED")
        self.assertTrue(history[0]["duplicate_flag_after"])
        self.assertEqual(self._review(status="REJECTED", reason="Same household after review", actor="demo-officer-01").status_code, 200)
        self.assertEqual(len(self._reviews()), 3)
        self.assertEqual(self._reviews()[0]["reviewed_by"], "demo-officer-01")

    def test_anomaly_resolution_and_reopening_preserve_evidence(self):
        approved = self._review(ben_id="BEN-0022", reason="Reviewed fictional grant anomaly").json()
        self.assertFalse(approved["anomaly_flag"])
        history = self._reviews("BEN-0022")
        self.assertTrue(history[0]["anomaly_flag_before"])
        reopened = self._review(ben_id="BEN-0022", status="FLAGGED_FOR_REVIEW", reason="Reassess anomaly evidence").json()
        self.assertTrue(reopened["anomaly_flag"])
        self.assertFalse(reopened["duplicate_flag"])
        self.assertEqual(reopened["review_status"], "PENDING")

    def test_invalid_review_input_cannot_change_state_or_create_history(self):
        before = self.client.get("/api/beneficiaries/BEN-0007").json()
        payload = {"status": "VERIFIED", "review_notes": "Different household", "reviewed_by": "demo-auditor-01"}
        for changed in ({"status": "APPROVED"}, {"status": "UNKNOWN"}, {"review_notes": "   "}, {"review_notes": None}, {"review_notes": "x" * 2001}, {"reviewed_by": ""}, {"reviewed_by": "unknown-person"}):
            with self.subTest(changed=changed):
                self.assertEqual(self.client.post("/api/beneficiaries/BEN-0007/verify", json={**payload, **changed}).status_code, 422)
        for missing in ("review_notes", "reviewed_by"):
            partial = {key: value for key, value in payload.items() if key != missing}
            self.assertEqual(self.client.post("/api/beneficiaries/BEN-0007/verify", json=partial).status_code, 422)
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0007").json(), before)
        self.assertEqual(self._reviews(), [])

    def test_review_history_empty_and_unknown_beneficiary(self):
        self.assertEqual(self._reviews(), [])
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-NOPE/reviews").status_code, 404)
        self.assertEqual(self._review(ben_id="BEN-NOPE").status_code, 404)

    def test_failed_review_commit_leaves_all_state_unchanged(self):
        from sqlalchemy.orm import Session
        before = self.client.get("/api/beneficiaries/BEN-0007").json()
        with patch.object(Session, "commit", side_effect=RuntimeError("Review database failure")):
            with self.assertRaises(RuntimeError):
                self._review()
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0007").json(), before)
        self.assertEqual(self._reviews(), [])
        self.assertFalse(any(e["event_type"] == "BENEFICIARY_REVIEWED" for e in self.client.get("/api/audit-trail/RELIEF-2026-001").json()))

    def test_reviews_never_modify_existing_payouts_or_receipts(self):
        before = self.client.get("/api/distributions").json()
        tx_before = fake_chain.tx_count
        self.assertEqual(self._review(ben_id="BEN-0001", status="REJECTED", reason="Investigate paid household").status_code, 200)
        self.assertEqual(self.client.get("/api/distributions").json(), before)
        self.assertEqual(fake_chain.tx_count, tx_before)

    def test_concurrent_reviews_record_serial_prior_states_without_process_lock(self):
        from concurrent.futures import ThreadPoolExecutor
        from contextlib import nullcontext
        import threading
        import app.main as api
        barrier = threading.Barrier(4)
        decisions = ["VERIFIED", "REJECTED", "FLAGGED_FOR_REVIEW", "VERIFIED"]
        def review_together(index):
            barrier.wait(timeout=10)
            return self._review(status=decisions[index], reason=f"Fictional reviewer decision {index}")
        with patch.object(api, "_funds_lock", nullcontext()):
            with ThreadPoolExecutor(max_workers=4) as pool:
                responses = list(pool.map(review_together, range(4)))
        self.assertEqual([r.status_code for r in responses], [200] * 4)
        history = list(reversed(self._reviews()))
        self.assertEqual(len(history), 4)
        previous_status = "FLAGGED_FOR_REVIEW"
        for review in history:
            self.assertEqual(review["previous_verification_status"], previous_status)
            previous_status = review["decision"]
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0007").json()["verification_status"], previous_status)

    def test_review_table_upgrade_preserves_existing_payouts(self):
        from sqlalchemy import inspect
        from app.database import engine, init_db
        from app.models.entities import BeneficiaryReview
        before = self.client.get("/api/distributions").json()
        BeneficiaryReview.__table__.drop(engine)
        init_db()
        self.assertIn("beneficiary_reviews", inspect(engine).get_table_names())
        self.assertEqual(self.client.get("/api/distributions").json(), before)
        self.assertEqual(self._reviews(), [])

    def test_delete_beneficiary(self):
        res = self.client.delete("/api/beneficiaries/BEN-0007")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0007").status_code, 404)

        res = self.client.post("/api/beneficiaries/BEN-0014/delete")
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
