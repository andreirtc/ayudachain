"""
AyudaChain Backend Unit Test Suite
Tests AI entity resolution, anomaly detection, hashing pipeline, and API models.
"""

import unittest
from unittest.mock import patch
from types import SimpleNamespace
import subprocess
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai.entity_resolution import EntityResolutionEngine, normalize_name, token_similarity
from app.ai.anomaly_detection import DistributionAnomalyDetector
from app.services.hasher import compute_receipt_hash, verify_receipt_integrity, canonical_json, compute_sha256_hex
from app.money import to_centavos, centavos_to_str, format_peso

class TestAyudaChainAI(unittest.TestCase):
    def setUp(self):
        self.engine = EntityResolutionEngine(confidence_threshold=0.78)

    def test_name_normalization(self):
        self.assertEqual(normalize_name("Juan Dela Cruz"), "juan dela cruz")
        self.assertEqual(normalize_name("Juan D. Cruz"), "juan dela cruz")
        self.assertEqual(normalize_name("Ma. Santos"), "maria santos")
        self.assertEqual(normalize_name("Cruz, Juan Dela"), "cruz juan dela")

    def test_duplicate_detection_juan_dela_cruz(self):
        existing = [
            {"beneficiary_id": "BEN-0002", "household_name": "Juan Dela Cruz", "barangay_id": "BRGY-001"}
        ]
        res = self.engine.evaluate_duplicate("Juan D. Cruz", "BRGY-001", existing)
        self.assertTrue(res["is_duplicate"])
        self.assertGreaterEqual(res["confidence"], 0.90)
        self.assertEqual(res["matched_id"], "BEN-0002")
        self.assertEqual(res["status"], "FLAGGED_FOR_HUMAN_REVIEW")

    def test_non_duplicate(self):
        existing = [
            {"beneficiary_id": "BEN-0002", "household_name": "Juan Dela Cruz", "barangay_id": "BRGY-001"}
        ]
        res = self.engine.evaluate_duplicate("Rodrigo Mendoza", "BRGY-001", existing)
        self.assertFalse(res["is_duplicate"])
        self.assertEqual(res["status"], "NORMAL")

class TestAnomalyDetector(unittest.TestCase):
    def setUp(self):
        self.detector = DistributionAnomalyDetector(standard_grant_amount=5000.0)

    def test_amount_deviation(self):
        res = self.detector.analyze_distribution(
            candidate_amount=15000.0,
            beneficiary_id="BEN-0022",
            barangay_id="BRGY-004",
            past_distributions=[]
        )
        self.assertTrue(res["is_anomaly"])
        self.assertEqual(res["status"], "FLAGGED_FOR_HUMAN_REVIEW")

    def test_standard_distribution_is_normal(self):
        res = self.detector.analyze_distribution(
            candidate_amount=5000.0,
            beneficiary_id="BEN-0001",
            barangay_id="BRGY-001",
            past_distributions=[]
        )
        self.assertFalse(res["is_anomaly"])
        self.assertEqual(res["status"], "NORMAL")

class TestHashingPipeline(unittest.TestCase):
    def test_canonical_json_determinism(self):
        d1 = {"b": 2, "a": 1}
        d2 = {"a": 1, "b": 2}
        self.assertEqual(canonical_json(d1), canonical_json(d2))

    def test_receipt_hash_reproducibility(self):
        h1 = compute_receipt_hash("DIST-0001", "BEN-0001", "RELIEF-2026-001", 500_000, "Sample OCR Text")
        h2 = compute_receipt_hash("DIST-0001", "BEN-0001", "RELIEF-2026-001", 500_000, "Sample OCR Text")
        self.assertEqual(h1, h2)
        self.assertTrue(h1.startswith("0x"))
        self.assertEqual(len(h1), 66)

    def test_hash_tamper_detection(self):
        h_orig = compute_receipt_hash("DIST-0001", "BEN-0001", "RELIEF-2026-001", 500_000, "Original Data")
        h_tampered = compute_receipt_hash("DIST-0001", "BEN-0001", "RELIEF-2026-001", 500_000, "Tampered Data")
        self.assertNotEqual(h_orig, h_tampered)

        valid, msg = verify_receipt_integrity(h_orig, h_tampered)
        self.assertFalse(valid)
        self.assertIn("mismatch", msg.lower())

    def test_receipt_hash_matches_peso_string_format(self):
        # Receipts anchored before the switch to centavos used f"{amount:.2f}"
        payload = {
            "amount": "5000.00",
            "batch_id": "RELIEF-2026-001",
            "beneficiary_id": "BEN-0001",
            "distribution_id": "DIST-0001",
            "ocr_content": "Sample OCR Text",
            "verification_method": "QR_VOUCHER_PHYSICAL_RECEIPT",
        }
        expected = compute_sha256_hex(canonical_json(payload))
        actual = compute_receipt_hash("DIST-0001", "BEN-0001", "RELIEF-2026-001", 500_000, "Sample OCR Text")
        self.assertEqual(actual, expected)


class TestMoney(unittest.TestCase):
    def test_to_centavos_is_exact(self):
        self.assertEqual(to_centavos("5000"), 500_000)
        self.assertEqual(to_centavos("0.10"), 10)
        self.assertEqual(to_centavos("1234567.89"), 123_456_789)

    def test_to_centavos_rejects_fractional_centavos(self):
        with self.assertRaises(ValueError):
            to_centavos("0.001")

    def test_formatting(self):
        self.assertEqual(centavos_to_str(500_000), "5000.00")
        self.assertEqual(centavos_to_str(5), "0.05")
        self.assertEqual(format_peso(1_000_000_000), "₱10,000,000.00")

class TestBlockchainEvidence(unittest.TestCase):
    def setUp(self):
        from app.services.blockchain import BlockchainService
        from contextlib import nullcontext
        # These pure CLI boundary units must never open the default/original DB.
        signer = patch("app.services.payout_anchors.legacy_signer", return_value=nullcontext(True))
        signer.start()
        self.addCleanup(signer.stop)
        self.service = BlockchainService()
        self.service.contract_address = "0x" + "1" * 40

    def test_failed_writes_preserve_failure_without_hash(self):
        failure = {"success": False, "error": "Chain unavailable"}
        with patch.object(self.service, "_execute_cli", return_value=failure):
            results = [
                self.service.release_fund("BATCH", 100, "Fictional flood", "Demo agency"),
                self.service.allocate_fund("BATCH", "ALLOC", "BRGY", 100),
                self.service.confirm_distribution("BATCH", "ALLOC", "DIST", "BEN", 100, "0x" + "1" * 64),
            ]
        for result in results:
            self.assertEqual(result, failure)
            self.assertNotIn("txHash", result)

    def test_missing_anchor_is_not_verified(self):
        observed = {"success": True, "exists": False, "matched": False, "onchainHash": "0x" + "0" * 64, "timestamp": 0}
        with patch.object(self.service, "_execute_cli", return_value=observed):
            result = self.service.verify_receipt("DIST", "0x" + "a" * 64)
        self.assertEqual(result, observed)
        self.assertFalse(result["matched"])
        self.assertFalse(result["exists"])

    def test_offline_receipt_lookup_never_claims_evidence(self):
        observed = {"success": False, "error": "Offline"}
        with patch.object(self.service, "_execute_cli", return_value=observed):
            result = self.service.verify_receipt("DIST", "0x" + "a" * 64)
        self.assertEqual(result, observed)
        self.assertNotIn("matched", result)
        self.assertNotIn("onchainHash", result)
        self.assertNotIn("timestamp", result)

    def test_cli_timeout_returns_explicit_failure(self):
        with patch("app.services.blockchain.subprocess.run", side_effect=subprocess.TimeoutExpired("node", 8)):
            result = self.service.verify_receipt("DIST", "0x" + "a" * 64)
        self.assertFalse(result["success"])
        self.assertIn("timed out", result["error"])
        self.assertNotIn("txHash", result)

    def test_nonzero_process_success_output_is_rejected(self):
        response = SimpleNamespace(returncode=1, stdout='{"success":true,"txHash":"0xpretend"}', stderr="Failed")
        with patch("app.services.blockchain.subprocess.run", return_value=response):
            result = self.service.get_status()
        self.assertFalse(result["success"])
        self.assertNotIn("txHash", result)

    def test_malformed_process_output_is_rejected(self):
        for stdout in ("no result", '{"success": "true"}', '{invalid JSON}', '{"matched":true}'):
            with self.subTest(stdout=stdout), patch("app.services.blockchain.subprocess.run", return_value=SimpleNamespace(returncode=0, stdout=stdout, stderr="")):
                self.assertFalse(self.service.verify_receipt("DIST", "0x" + "a" * 64)["success"])

    def test_missing_contract_configuration_does_not_spawn_guessing_client(self):
        self.service.contract_address = None
        with patch("app.services.blockchain.subprocess.run") as execute:
            result = self.service.get_status()
        self.assertFalse(result["success"])
        execute.assert_not_called()

    def test_transaction_hash_requires_success_and_valid_shape(self):
        from app.services.blockchain import confirmed_transaction_hash
        valid = "0x" + "a" * 64
        self.assertEqual(confirmed_transaction_hash({"success": True, "txHash": valid}), valid)
        for payload in ({"success": False, "txHash": valid}, {"success": "true", "txHash": valid}, {"success": 1, "txHash": valid}, {"success": True}, {"success": True, "txHash": "0xpretend"}):
            self.assertIsNone(confirmed_transaction_hash(payload))

    def test_successful_process_evidence_is_passed_through(self):
        from app import config
        observed = {"success": True, "exists": False, "matched": False, "chainId": config.CHAIN_ID}
        response = SimpleNamespace(returncode=0, stdout="log line\n" + canonical_json(observed), stderr="")
        with patch("app.services.blockchain.subprocess.run", return_value=response) as execute:
            result = self.service.verify_receipt("DIST", "0x" + "a" * 64)
        self.assertEqual(result, observed)
        self.assertEqual(execute.call_args.kwargs["env"]["CHAIN_ID"], str(config.CHAIN_ID))


if __name__ == "__main__":
    unittest.main()
