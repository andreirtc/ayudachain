"""
AyudaChain API Test Suite
Exercises the FastAPI app against a temporary SQLite database and a fake
blockchain service, so no Hardhat node is needed.
"""

import os
import sys
import tempfile
import unittest

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

    def confirm_distribution(self, batch_id, distribution_id, beneficiary_id, amount_centavos, receipt_hash):
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

        res = self._allocate("ALLOC-0201", "RELIEF-TEST-002", 400.01)
        self.assertEqual(res.status_code, 400)
        self.assertIn("₱400.00", res.json()["detail"])

        self.assertEqual(self._allocate("ALLOC-0202", "RELIEF-TEST-002", 400).status_code, 201)
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

    def test_delete_beneficiary(self):
        res = self.client.delete("/api/beneficiaries/BEN-0007")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0007").status_code, 404)

        res = self.client.post("/api/beneficiaries/BEN-0014/delete")
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
