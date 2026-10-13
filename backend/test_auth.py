"""Actual session/permission regression tests, isolated from all existing data."""
import json
import unittest
from unittest.mock import patch

import test_api as business
from auth_support import HEADERS, TEST_PASSWORD
from fastapi.testclient import TestClient
from app import config, auth
from app.database import SessionLocal
from app.models.entities import Beneficiary, BeneficiaryReview, Distribution
from app.seed_demo import seed_database


class TestSessions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(business._accounts_path.read_text())
        cls.client = TestClient(business.app, base_url="http://127.0.0.1", headers=HEADERS)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def setUp(self):
        business._accounts_path.write_text(json.dumps(self.original))
        seed_database()
        auth._attempts.clear()
        self.client.cookies.clear()
        self.client.headers.pop("X-CSRF-Token", None)

    def login(self, identity="demo-officer-01", **extras):
        response = self.client.post("/api/auth/login", json={"username": identity, "password": TEST_PASSWORD, **extras})
        self.assertEqual(response.status_code, 200, response.text)
        self.client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
        return response

    def test_anonymous_private_routes_and_mutations_are_denied(self):
        for path in ("/api/beneficiaries", "/api/beneficiaries/BEN-0001", "/api/distributions", "/api/audit-trail/RELIEF-2026-001", "/receipts/DIST-0001.svg"):
            self.assertEqual(self.client.get(path).status_code, 401, path)
        for path in ("/api/funds/releases", "/api/allocations", "/api/beneficiaries", "/api/distributions/confirm", "/api/beneficiaries/BEN-0007/verify"):
            self.assertEqual(self.client.post(path, json={}).status_code, 401, path)

    def test_cookie_is_opaque_http_only_and_session_is_durable(self):
        response = self.login()
        cookie = response.headers["set-cookie"]
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=strict", cookie)
        self.assertIn("Max-Age=3600", cookie)
        raw = self.client.cookies.get(auth.COOKIE)
        with SessionLocal() as db:
            saved = db.query(auth.DemoSession).one()
            self.assertNotEqual(saved.token_hash, raw)
        other = TestClient(business.app, base_url="http://127.0.0.1", headers=HEADERS)
        other.cookies.set(auth.COOKIE, raw)
        self.assertEqual(other.get("/api/auth/session").json()["account"]["role"], "DSWD")
        self.assertNotIn("password", response.text)

    def test_role_headers_and_login_role_claims_cannot_grant_privileges(self):
        self.client.cookies.set(auth.COOKIE, "forged-token")
        self.assertEqual(self.client.get("/api/beneficiaries", headers={"X-Demo-Actor-ID": "demo-officer-01", "Authorization": "Bearer DSWD"}).status_code, 401)
        response = self.login("demo-auditor-01", role="DSWD")
        self.assertEqual(response.json()["account"]["role"], "AUDITOR")
        self.assertEqual(self.client.post("/api/beneficiaries/BEN-0007/verify", json={"status": "VERIFIED", "review_notes": "Synthetic review"}).status_code, 403)

    def test_csrf_and_origin_reject_before_business_mutation(self):
        self.login()
        self.client.headers.pop("X-CSRF-Token")
        payload = {"status": "VERIFIED", "review_notes": "Synthetic review"}
        self.assertEqual(self.client.post("/api/beneficiaries/BEN-0007/verify", json=payload).status_code, 403)
        self.client.headers["X-CSRF-Token"] = "wrong"
        self.assertEqual(self.client.post("/api/beneficiaries/BEN-0007/verify", json=payload).status_code, 403)
        self.login()
        self.assertEqual(self.client.post("/api/beneficiaries/BEN-0007/verify", json=payload, headers={"Origin": "https://outside.invalid"}).status_code, 403)
        with SessionLocal() as db:
            self.assertEqual(db.query(BeneficiaryReview).count(), 0)
            self.assertTrue(db.query(Beneficiary).filter_by(beneficiary_id="BEN-0007").one().duplicate_flag)

    def test_review_identity_is_derived_and_forgery_is_denied(self):
        self.login()
        payload = {"status": "VERIFIED", "review_notes": "Distinct fictional household"}
        self.assertEqual(self.client.post("/api/beneficiaries/BEN-0007/verify", json={**payload, "reviewed_by": "demo-auditor-01"}).status_code, 403)
        self.assertEqual(self.client.post("/api/beneficiaries/BEN-0007/verify", json=payload).status_code, 200)
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0007/reviews").json()[0]["reviewed_by"], "demo-officer-01")

    def test_auditor_has_no_business_write_route(self):
        self.login("demo-auditor-01")
        for path in ("/api/funds/releases", "/api/allocations", "/api/beneficiaries", "/api/beneficiaries/upload-csv", "/api/beneficiaries/BEN-0007/verify", "/api/beneficiaries/BEN-0007/resolve-duplicate", "/api/distributions/confirm"):
            self.assertEqual(self.client.post(path, json={}).status_code, 403, path)
        self.assertEqual(self.client.get("/api/audit-trail/RELIEF-2026-001").status_code, 200)

    def test_decisions_and_payout_roles_are_separate(self):
        self.login()
        self.assertEqual(self.client.post("/api/distributions/confirm", json={}).status_code, 403)
        self.login("demo-barangay-01")
        self.assertEqual(self.client.post("/api/beneficiaries/BEN-0007/verify", json={}).status_code, 403)
        self.login("demo-disbursing-001")
        self.assertEqual(self.client.post("/api/funds/releases", json={}).status_code, 403)

    def test_barangay_queries_and_registration_cannot_escape_scope(self):
        self.login("demo-barangay-01")
        rows = self.client.get("/api/beneficiaries?barangay_id=BRGY-004&role=DSWD").json()
        self.assertTrue(rows)
        self.assertTrue(all(row["barangay_id"] == "BRGY-001" and row["contact_number"] is None and row["review_notes"] is None for row in rows))
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0009").status_code, 404)
        self.assertEqual(self.client.get("/api/distributions").status_code, 403)
        response = self.client.post("/api/beneficiaries", json={"beneficiary_id": "BEN-SCOPE", "household_name": "Fictional scope test", "barangay_id": "BRGY-004", "barangay_name": "Maligaya", "batch_id": "RELIEF-2026-001"})
        self.assertEqual(response.status_code, 403)
        response = self.client.post("/api/beneficiaries", json={"beneficiary_id": "BEN-SCOPE", "household_name": "Synthetic Amara Bayani", "barangay_id": "BRGY-001", "barangay_name": "San Isidro", "batch_id": "RELIEF-2026-001"})
        self.assertEqual(response.status_code, 201, response.text)
        row = response.json()
        self.assertEqual((row["verification_status"], row["review_status"]), ("FLAGGED_FOR_REVIEW", "PENDING"))
        self.assertIsNone(row["review_notes"])
        self.assertIsNone(row["duplicate_matched_id"])

    def test_disbursing_cannot_pay_another_barangay(self):
        self.login("demo-disbursing-001")
        response = self.client.post("/api/distributions/confirm", headers={"Idempotency-Key": "scoped-attempt"}, json={"beneficiary_id": "BEN-0009", "batch_id": "RELIEF-2026-001", "amount": 5000})
        self.assertEqual(response.status_code, 404)
        with SessionLocal() as db:
            self.assertEqual(db.query(Distribution).count(), 5)

    def test_beneficiary_reads_only_own_household(self):
        from pathlib import Path
        self.login("demo-disbursing-001")
        Path(config.RECEIPTS_DIR, "own-household.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'><text>Fictional BEN-0004</text></svg>")
        payout = self.client.post("/api/distributions/confirm", headers={"Idempotency-Key": "own-file-scope"}, json={"beneficiary_id": "BEN-0004", "batch_id": "RELIEF-2026-001", "amount": 5000, "receipt_filename": "own-household.svg", "ocr_raw_text": "Fictional BEN-0004 receipt"})
        self.assertEqual(payout.status_code, 201, payout.text)
        Path(config.RECEIPTS_DIR, "own-household.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'><text>Fictional BEN-0004</text></svg>")
        Path(config.RECEIPTS_DIR, "other-household.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'><text>Fictional BEN-0001</text></svg>")
        with SessionLocal() as db:
            db.query(Distribution).filter_by(distribution_id="DIST-0001").update({"receipt_file_path": "/receipts/other-household.svg"})
            db.commit()
        self.login("demo-beneficiary-01")
        self.assertEqual([row["beneficiary_id"] for row in self.client.get("/api/beneficiaries?include_historical=true").json()], ["BEN-0004"])
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0001").status_code, 404)
        self.assertEqual(self.client.get("/api/beneficiaries/BEN-0001/reviews").status_code, 404)
        self.assertEqual(self.client.get("/receipts/DIST-0001.svg").status_code, 404)
        self.assertEqual(self.client.get(payout.json()["receipt_file_path"]).status_code, 200)
        self.assertEqual(self.client.get("/receipts/other-household.svg").status_code, 404)
        self.assertTrue(all(row["beneficiary_id"] == "BEN-0004" for row in self.client.get("/api/distributions").json()))

    def test_logout_and_login_rotation_revoke_old_tokens(self):
        self.login()
        old = self.client.cookies.get(auth.COOKIE)
        self.login()
        self.assertNotEqual(old, self.client.cookies.get(auth.COOKIE))
        other = TestClient(business.app, base_url="http://127.0.0.1", headers=HEADERS)
        other.cookies.set(auth.COOKIE, old)
        self.assertEqual(other.get("/api/auth/session").status_code, 401)
        token = self.client.cookies.get(auth.COOKIE)
        self.assertEqual(self.client.post("/api/auth/logout").status_code, 200)
        other.cookies.set(auth.COOKIE, token)
        self.assertEqual(other.get("/api/auth/session").status_code, 401)

    def test_expiry_disable_and_account_change_revoke_access(self):
        self.login()
        with patch("app.auth.time.time", return_value=auth.time.time() + 4000):
            self.assertEqual(self.client.get("/api/beneficiaries").status_code, 401)
        for change in ({"enabled": False}, {"role": "AUDITOR"}, {"password_hash": "00" * 32}):
            business._accounts_path.write_text(json.dumps(self.original))
            self.login()
            changed = json.loads(json.dumps(self.original))
            changed["accounts"][0].update(change)
            business._accounts_path.write_text(json.dumps(changed))
            self.assertEqual(self.client.get("/api/beneficiaries").status_code, 401)

    def test_public_receipt_and_funding_responses_omit_private_context(self):
        rows = self.client.get("/api/public/receipts").json()
        self.assertTrue(rows)
        self.assertTrue(all(set(row) == {"distribution_id", "batch_id"} for row in rows))
        verification = self.client.post("/api/blockchain/verify", json={"distribution_id": "DIST-0001"}).json()
        self.assertIsNone(verification["beneficiary_id"])
        self.assertNotIn("ocr_text", verification)
        for endpoint, key in (("/api/dashboard", "recent_transactions"), ("/api/batches/RELIEF-2026-001", "timeline")):
            result = self.client.get(endpoint)
            self.assertEqual(result.status_code, 200, result.text)
            self.assertTrue(result.json()[key])
            self.assertTrue(all(row["event_type"] in {"FUND_RELEASE", "ALLOCATION"} for row in result.json()[key]))

    def test_public_responses_report_ended_sessions_without_restricting_verification(self):
        self.login("demo-auditor-01")
        result = self.client.get("/api/distributions", headers={"Origin": "http://127.0.0.1:3101"})
        self.assertEqual(result.headers["X-AyudaChain-Session"], "active")
        self.assertIn("X-AyudaChain-Session", result.headers["access-control-expose-headers"])
        with SessionLocal() as db:
            db.query(auth.DemoSession).update({"expires_at": 0})
            db.commit()
        self.assertEqual(self.client.get("/api/distributions").status_code, 401)
        verification = self.client.post("/api/blockchain/verify", json={"distribution_id": "DIST-0001"})
        self.assertEqual(verification.status_code, 200)
        self.assertEqual(verification.headers["X-AyudaChain-Session"], "ended")
        self.assertIsNone(verification.json()["beneficiary_id"])
        self.assertEqual(self.client.get("/api/public/receipts").status_code, 200)

    def test_shared_template_does_not_leak_other_household_to_scoped_accounts(self):
        for identity in ("demo-beneficiary-01", "demo-disbursing-002"):
            self.login(identity)
            self.assertEqual(self.client.get("/receipts/sample_relief_receipt.svg").status_code, 404)
            self.assertTrue(all(row["receipt_file_path"] is None and row["ocr_text"] is None for row in self.client.get("/api/distributions").json()))
        self.login("demo-auditor-01")
        self.assertEqual(self.client.get("/receipts/sample_relief_receipt.svg").status_code, 200)

    def test_http_reset_is_disabled_without_deleting_records(self):
        self.assertEqual(self.client.post("/api/demo/reset").status_code, 410)
        self.login()
        self.assertEqual(self.client.post("/api/demo/reset").status_code, 410)
        with SessionLocal() as db:
            self.assertEqual(db.query(Beneficiary).count(), 24)

    def test_bad_credentials_limits_and_validation_do_not_echo_secrets(self):
        secret = "private-test-input" * 50
        result = self.client.post("/api/auth/login", json={"username": "demo-officer-01", "password": secret})
        self.assertEqual(result.status_code, 422)
        self.assertNotIn(secret, result.text)
        for _ in range(5):
            self.assertEqual(self.client.post("/api/auth/login", json={"username": "unknown", "password": "wrong"}).status_code, 401)
        self.assertEqual(self.client.post("/api/auth/login", json={"username": "unknown", "password": "wrong"}).status_code, 429)

    def test_missing_or_invalid_account_file_fails_closed(self):
        self.login()
        business._accounts_path.write_text("{}")
        self.assertEqual(self.client.get("/api/beneficiaries").status_code, 503)
        self.assertEqual(self.client.post("/api/auth/login", json={"username": "demo-officer-01", "password": TEST_PASSWORD}).status_code, 503)

    def test_parallel_failed_logins_do_not_lose_rate_limit_counts(self):
        from concurrent.futures import ThreadPoolExecutor
        def attempt(_):
            client = TestClient(business.app, base_url="http://127.0.0.1", headers=HEADERS)
            return client.post("/api/auth/login", json={"username": "parallel-unknown", "password": "wrong"}).status_code
        with ThreadPoolExecutor(max_workers=6) as workers:
            self.assertTrue(all(code in {401, 429} for code in workers.map(attempt, range(6))))
        self.assertEqual(attempt(0), 429)

    def test_cross_site_login_and_insecure_nonlocal_login_are_denied(self):
        payload = {"username": "demo-officer-01", "password": TEST_PASSWORD}
        self.assertEqual(self.client.post("/api/auth/login", json=payload, headers={"Origin": "https://outside.invalid"}).status_code, 403)
        with patch.object(config, "CORS_ORIGINS", ["https://shared.example"]):
            self.assertEqual(self.client.post("/api/auth/login", json=payload, headers={"Origin": "https://shared.example"}).status_code, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
