"""Durability, authorization and recovery faults in an isolated synthetic API."""
import json
import time
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

import test_api as business
from auth_support import HEADERS, TEST_PASSWORD
from app.database import SessionLocal, init_db
from app.models.entities import Distribution, PayoutAnchorJob, AnchorSignerLease, AnchorObservation, AuditEvent
from app.services.blockchain import blockchain_service, BlockchainService
from app.services import payout_anchors as anchors
from app.seed_demo import seed_database


class TestPayoutAnchors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(business.app, base_url="http://127.0.0.1", headers=HEADERS)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def setUp(self):
        seed_database()
        self.client.cookies.clear()
        self.login("demo-disbursing-001")

    def login(self, identity):
        result = self.client.post("/api/auth/login", json={"username": identity, "password": TEST_PASSWORD})
        self.assertEqual(result.status_code, 200)
        self.client.headers["X-CSRF-Token"] = result.json()["csrf_token"]

    def pay(self, key="anchor-test", ben="BEN-0004"):
        return self.client.post("/api/distributions/confirm", headers={"Idempotency-Key": key}, json={"beneficiary_id": ben, "batch_id": "RELIEF-2026-001", "amount": 5000})

    def retry(self, identity):
        return self.client.post("/api/distributions/" + identity + "/anchor/retry")

    def test_unavailable_prepare_records_failed_job_and_business_retry_never_resubmits(self):
        with patch.object(blockchain_service, "payout_anchor", return_value={"success": False, "error_code": "RPC_UNAVAILABLE"}) as cli:
            first = self.pay()
            self.assertEqual(first.status_code, 201, first.text)
            second = self.pay()
            self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json(), second.json())
        self.assertEqual(cli.call_count, 1)
        self.assertEqual(first.json()["anchor_job"]["state"], "FAILED")
        self.assertIsNone(first.json()["blockchain_tx_hash"])
        recovered = self.retry(first.json()["distribution_id"])
        self.assertEqual(recovered.status_code, 200, recovered.text)
        self.assertEqual(recovered.json()["anchor_job"]["state"], "CONFIRMED")
        with SessionLocal() as db:
            self.assertEqual(db.query(Distribution).count(), 6)
            self.assertEqual(db.query(AuditEvent).filter_by(event_type="DISTRIBUTION_CONFIRMED").count(), 6)

    def test_envelope_is_durable_before_send_and_reused_after_interruption(self):
        captured = []
        def interrupted(action, payload, raw=None, pin=None, candidate=None):
            if action == "prepare":
                return business.fake_chain.payout_anchor(action, payload)
            with SessionLocal() as db:
                job = db.get(PayoutAnchorJob, payload["distribution_id"])
                self.assertEqual((job.raw_transaction, job.candidate_tx_hash), (raw, candidate))
            captured.append(raw)
            return {"success": False, "error_code": "RPC_UNAVAILABLE"}
        with patch.object(blockchain_service, "payout_anchor", side_effect=interrupted):
            first = self.pay().json()
        self.assertEqual(first["anchor_job"]["state"], "SUBMITTED")
        with patch.object(blockchain_service, "payout_anchor", wraps=business.fake_chain.payout_anchor) as cli:
            result = self.retry(first["distribution_id"])
        self.assertEqual(result.json()["anchor_job"]["state"], "CONFIRMED")
        self.assertEqual([call.args[0] for call in cli.call_args_list], ["recover"])
        self.assertEqual(cli.call_args.args[2], captured[0])
        self.assertNotIn("raw_transaction", result.text)
        self.assertNotIn("snapshot_json", result.text)

    def test_lost_mined_metadata_recovers_without_second_chain_write_or_audit(self):
        before = business.fake_chain.tx_count
        with patch.object(anchors, "finish", side_effect=RuntimeError("Lost DB commit after mining")):
            with self.assertRaises(RuntimeError): self.pay()
        first = self.pay().json()
        self.assertEqual(first["anchor_job"]["state"], "SUBMITTED")
        self.assertIsNone(first["blockchain_tx_hash"])
        self.assertEqual(self.retry(first["distribution_id"]).status_code, 200)
        self.assertEqual(self.retry(first["distribution_id"]).status_code, 200)
        self.assertEqual(business.fake_chain.tx_count - before, 1)
        with SessionLocal() as db:
            self.assertEqual(db.query(AuditEvent).filter_by(event_type="PAYOUT_ANCHOR_CONFIRMED").count(), 1)
            self.assertGreaterEqual(db.query(AnchorObservation).count(), 3)

    def test_changed_record_refuses_recovery_without_calling_chain(self):
        with patch.object(blockchain_service, "payout_anchor", return_value={"success": False, "error_code": "RPC_UNAVAILABLE"}):
            first = self.pay().json()
        with SessionLocal() as db:
            db.query(Distribution).filter_by(distribution_id=first["distribution_id"]).update({"amount_centavos": 400000})
            db.commit()
        with patch.object(blockchain_service, "payout_anchor") as cli:
            result = self.retry(first["distribution_id"])
        self.assertEqual(result.json()["anchor_job"]["error_code"], "RECORD_CHANGED")
        cli.assert_not_called()

    def test_false_confirmation_never_sets_transaction_metadata(self):
        def malformed(action, payload, *args):
            if action == "prepare": return business.fake_chain.payout_anchor(action, payload)
            return {"success": True, "state": "CONFIRMED", "tx_hash": args[-1], "block_number": 2, "block_hash": "0x" + "1" * 64, "receipt_timestamp": 1, "chain_id": 1, "contract_address": payload["contract_address"]}
        with patch.object(blockchain_service, "payout_anchor", side_effect=malformed):
            first = self.pay().json()
        self.assertEqual(first["anchor_job"]["state"], "FAILED")
        self.assertIsNone(first["blockchain_tx_hash"])

    def test_record_changed_during_send_does_not_receive_confirmation_metadata(self):
        def changed(action, payload, *args):
            result = business.fake_chain.payout_anchor(action, payload, *args)
            if action == "recover":
                with SessionLocal() as db:
                    db.query(Distribution).filter_by(distribution_id=payload["distribution_id"]).update({"amount_centavos": 400000})
                    db.commit()
            return result
        with patch.object(blockchain_service, "payout_anchor", side_effect=changed):
            first = self.pay().json()
        self.assertEqual(first["anchor_job"]["error_code"], "RECORD_CHANGED")
        self.assertIsNone(first["blockchain_tx_hash"])

    def test_authorized_recovery_scope_csrf_and_historical_records(self):
        with patch.object(blockchain_service, "payout_anchor", return_value={"success": False, "error_code": "RPC_UNAVAILABLE"}):
            first = self.pay().json()
        path = first["distribution_id"]
        self.assertEqual(self.retry("DIST-0001").status_code, 409)
        self.assertEqual(self.client.post("/api/distributions/" + path + "/anchor/retry", headers={"X-CSRF-Token": "wrong"}).status_code, 403)
        for account in ("demo-auditor-01", "demo-beneficiary-01", "demo-barangay-01", "demo-officer-01"):
            self.login(account)
            self.assertEqual(self.retry(path).status_code, 403)
        self.login("demo-disbursing-002")
        self.assertEqual(self.retry(path).status_code, 404)
        self.client.cookies.clear()
        self.assertEqual(self.retry(path).status_code, 401)

    def test_one_lease_across_workers_and_expired_lease_can_recover(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: anchors.claim(), range(4)))
        owners = [owner for owner in results if owner]
        self.assertEqual(len(owners), 1)
        with SessionLocal() as db:
            db.get(AnchorSignerLease, 1).expires_at = int(time.time()) - 1
            db.commit()
        new = anchors.claim()
        self.assertIsNotNone(new)
        anchors.release(owners[0])
        self.assertIsNone(anchors.claim())  # stale owner cannot release a newer lease
        anchors.release(new)

    def test_unresolved_envelope_blocks_other_jobs_and_legacy_signer(self):
        def pending(action, payload, *args):
            if action == "prepare": return business.fake_chain.payout_anchor(action, payload)
            return {"success": False, "error_code": "RPC_UNAVAILABLE"}
        with patch.object(blockchain_service, "payout_anchor", side_effect=pending):
            first = self.pay().json()
        other = self.pay(key="another-job", ben="BEN-0006").json()
        self.assertEqual(other["anchor_job"]["state"], "PENDING")
        self.assertEqual(self.retry(other["distribution_id"]).status_code, 409)
        with patch.object(BlockchainService, "_execute_cli") as cli:
            result = BlockchainService().release_fund("DEMO", 100, "Synthetic", "Demo")
        self.assertEqual(result["error_code"], "SIGNER_BUSY")
        cli.assert_not_called()
        self.assertEqual(self.retry(first["distribution_id"]).status_code, 200)
        self.assertEqual(self.retry(other["distribution_id"]).status_code, 200)

    def test_additive_startup_preserves_existing_payout_and_proof(self):
        first = self.pay().json()
        with SessionLocal() as db:
            before = [(d.distribution_id, d.receipt_hash, d.amount_centavos) for d in db.query(Distribution)]
        init_db(); init_db()
        with SessionLocal() as db:
            self.assertEqual(before, [(d.distribution_id, d.receipt_hash, d.amount_centavos) for d in db.query(Distribution)])
            self.assertIsNotNone(db.get(PayoutAnchorJob, first["distribution_id"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
