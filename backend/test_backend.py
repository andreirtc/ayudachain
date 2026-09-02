"""
AyudaChain Backend Unit Test Suite
Tests AI entity resolution, anomaly detection, hashing pipeline, and API models.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai.entity_resolution import EntityResolutionEngine, normalize_name, token_similarity
from app.ai.anomaly_detection import DistributionAnomalyDetector
from app.services.hasher import compute_receipt_hash, verify_receipt_integrity, canonical_json

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
        h1 = compute_receipt_hash("DIST-0001", "BEN-0001", "RELIEF-2026-001", 5000.0, "Sample OCR Text")
        h2 = compute_receipt_hash("DIST-0001", "BEN-0001", "RELIEF-2026-001", 5000.0, "Sample OCR Text")
        self.assertEqual(h1, h2)
        self.assertTrue(h1.startswith("0x"))
        self.assertEqual(len(h1), 66)

    def test_hash_tamper_detection(self):
        h_orig = compute_receipt_hash("DIST-0001", "BEN-0001", "RELIEF-2026-001", 5000.0, "Original Data")
        h_tampered = compute_receipt_hash("DIST-0001", "BEN-0001", "RELIEF-2026-001", 5000.0, "Tampered Data")
        self.assertNotEqual(h_orig, h_tampered)

        valid, msg = verify_receipt_integrity(h_orig, h_tampered)
        self.assertFalse(valid)
        self.assertIn("mismatch", msg.lower())

if __name__ == "__main__":
    unittest.main()
