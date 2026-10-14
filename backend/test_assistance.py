"""Damage claims, amount rules and payout sessions through authenticated role clients."""
import unittest
from datetime import date, timedelta
from uuid import uuid4
import test_api as business
from fastapi.testclient import TestClient
from auth_support import HEADERS, TEST_PASSWORD
from app import auth
from app.database import SessionLocal
from app.models.entities import AuditEvent, Beneficiary
from app.seed_demo import seed_database

BATCH = "RELIEF-2026-001"
SOON = (date.today() + timedelta(days=3)).isoformat()


class TestAssistance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(business.app, base_url="http://127.0.0.1", headers=HEADERS)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls): cls.client.__exit__(None, None, None)

    def setUp(self):
        seed_database(); auth._attempts.clear(); self.as_("demo-officer-01")
        self.assertEqual(self.client.post("/api/beneficiaries/BEN-0004/verify", json={"status": "VERIFIED", "review_notes": "Inspected synthetic household"}).status_code, 200)

    def as_(self, identity):
        self.client.cookies.clear()
        r = self.client.post("/api/auth/login", json={"username": identity, "password": TEST_PASSWORD})
        self.assertEqual(r.status_code, 200, r.text)
        self.client.headers["X-CSRF-Token"] = r.json()["csrf_token"]

    def submit(self, category="PARTIALLY_DAMAGED", **extra):
        self.as_("demo-beneficiary-01")
        return self.client.post("/api/claims", json={"request_id": str(uuid4()), "category": category, "description": "Roof and one wall damaged", **extra})

    def step(self, identity, claim, action, **extra):
        self.as_(identity)
        return self.client.post(f"/api/claims/{claim['claim_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": claim["current"]["revision"], "action": action, **extra})

    def approved_claim(self, category="TOTALLY_DAMAGED"):
        claim = self.submit().json()
        claim = self.step("demo-barangay-01", claim, "ENDORSE", staff_reason="Resident; damage seen on visit").json()
        result = self.step("demo-officer-01", claim, "APPROVE", category=category, staff_reason="Photos show collapsed roof")
        self.assertEqual(result.status_code, 201, result.text)
        return result.json()

    def finalized_list(self):
        self.as_("demo-officer-01")
        list_id = self.client.post("/api/validated-lists/prepare", json={"batch_id": BATCH, "barangay_id": "BRGY-001", "request_id": str(uuid4()), "exclusions": {}}).json()["list_id"]
        self.assertEqual(self.client.post(f"/api/validated-lists/{list_id}/finalize", json={"reason": "Inspected", "confirm": True}).status_code, 201)
        return list_id

    def pay(self, amount=5000, identity="demo-disbursing-001"):
        self.as_(identity)
        return self.client.post("/api/distributions/confirm", json={"beneficiary_id": "BEN-0004", "batch_id": BATCH, "amount": amount}, headers={"Idempotency-Key": "pay-" + uuid4().hex})

    def test_claim_journey_prices_payout_and_locks_after_payment(self):
        key = str(uuid4())
        self.as_("demo-beneficiary-01")
        body = {"request_id": key, "category": "PARTIALLY_DAMAGED", "description": "Roof and one wall damaged"}
        first = self.client.post("/api/claims", json=body); self.assertEqual(first.status_code, 201, first.text)
        self.assertEqual(self.client.post("/api/claims", json=body).json()["claim_id"], first.json()["claim_id"])
        self.assertEqual(self.client.post("/api/claims", json={**body, "description": "Different"}).status_code, 409)
        self.assertEqual(self.client.post("/api/claims", json={**body, "request_id": str(uuid4())}).status_code, 409)
        self.assertEqual(self.client.post("/api/claims", json={**body, "request_id": str(uuid4()), "beneficiary_id": "BEN-0005"}).status_code, 404)
        self.assertEqual(self.client.get("/api/entitlements/mine").json()["basis"], "PENDING")
        self.as_("demo-disbursing-001")
        desk = self.client.get("/api/payout-desk/BEN-0004").json()
        self.assertFalse(desk["can_record"]); self.assertFalse(next(c for c in desk["checks"] if c["code"] == "ENTITLEMENT")["passed"])
        self.assertEqual(self.pay().status_code, 409)
        self.assertEqual(self.client.get("/api/claims").status_code, 403)
        self.as_("demo-officer-01")
        rows = self.client.post("/api/validated-lists/prepare", json={"batch_id": BATCH, "barangay_id": "BRGY-001", "request_id": str(uuid4()), "exclusions": {}}).json()["snapshot"]["rows"]
        row = next(r for r in rows if r["beneficiary_id"] == "BEN-0004")
        self.assertFalse(row["included"]); self.assertIn("Damage claim awaiting decision", row["exclusion_reasons"])
        self.assertEqual(self.step("demo-officer-01", first.json(), "APPROVE", staff_reason="Too early").status_code, 409)
        endorsed = self.step("demo-barangay-01", first.json(), "ENDORSE", staff_reason="Resident; damage seen on visit")
        self.assertEqual(endorsed.status_code, 201, endorsed.text)
        approved = self.step("demo-officer-01", endorsed.json(), "APPROVE", category="TOTALLY_DAMAGED", staff_reason="Photos show collapsed roof").json()
        self.assertEqual(approved["current"]["status"], "APPROVED"); self.assertEqual(approved["entitlement"]["amount_centavos"], 1_000_000)
        self.as_("demo-beneficiary-01")
        mine = self.client.get("/api/claims").json()[0]
        self.assertNotIn("staff_reason", mine["current"]); self.assertEqual(mine["current"]["household_message"], "Your claim was approved as totally damaged house.")
        self.assertEqual(self.client.get("/api/entitlements/mine").json()["amount_centavos"], 1_000_000)
        self.as_("demo-disbursing-001")
        desk = self.client.get("/api/payout-desk/BEN-0004").json()
        self.assertEqual(desk["amount_centavos"], 1_000_000); self.assertTrue(desk["can_record"]); self.assertFalse(desk["nonstandard_amount"])
        self.assertEqual(self.pay(10000).status_code, 201)
        with SessionLocal() as db:
            self.assertFalse(db.query(Beneficiary).filter_by(beneficiary_id="BEN-0004").one().anomaly_flag)
            self.assertEqual(db.query(AuditEvent).filter_by(event_type="CLAIM_APPROVE").count(), 1)
        self.assertEqual(self.step("demo-officer-01", approved, "DECLINE", household_message="No", staff_reason="Late").status_code, 409)

    def test_information_requests_declines_scope_and_stale_steps(self):
        claim = self.submit().json()
        self.assertEqual(self.step("demo-officer-01", claim, "ENDORSE", staff_reason="x").status_code, 403)
        self.as_("demo-barangay-01")
        self.assertEqual(len(self.client.get("/api/claims").json()), 1)
        asked = self.step("demo-barangay-01", claim, "REQUEST_INFO", household_message="Which rooms were damaged?", staff_reason="Unclear description")
        self.assertEqual(asked.status_code, 201, asked.text)
        self.assertEqual(self.step("demo-barangay-01", claim, "ENDORSE", staff_reason="Stale").status_code, 409)
        self.assertEqual(self.step("demo-beneficiary-01", asked.json(), "RESPOND").status_code, 422)
        answered = self.step("demo-beneficiary-01", asked.json(), "RESPOND", description="Kitchen and roof").json()
        self.assertEqual(answered["current"]["status"], "SUBMITTED"); self.assertEqual(answered["current"]["description"], "Kitchen and roof")
        refused = self.step("demo-barangay-01", answered, "NOT_ENDORSE", staff_reason="Not on the damage survey").json()
        self.assertEqual(self.step("demo-officer-01", refused, "DECLINE", staff_reason="Survey").status_code, 422)
        declined = self.step("demo-officer-01", refused, "DECLINE", household_message="The damage survey did not list your house.", staff_reason="Survey").json()
        self.assertEqual(declined["entitlement"]["basis"], "STANDARD"); self.assertEqual(declined["entitlement"]["amount_centavos"], 500_000)
        self.as_("demo-officer-01")
        self.assertEqual(self.client.post(f"/api/claims/{claim['claim_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 1, "action": "RESPOND", "description": "x"}).status_code, 403)
        self.client.cookies.clear()
        self.as_("demo-barangay-01")
        assisted = self.client.post("/api/claims", json={"request_id": str(uuid4()), "beneficiary_id": "BEN-0005", "category": "TOTALLY_DAMAGED", "description": "House destroyed"})
        self.assertEqual(assisted.status_code, 201, assisted.text); self.assertEqual(assisted.json()["source"], "STAFF_ASSISTED")
        self.assertEqual(self.client.post("/api/claims", json={"request_id": str(uuid4()), "beneficiary_id": "BEN-0008", "category": "TOTALLY_DAMAGED", "description": "x"}).status_code, 404)

    def test_amount_rule_versions(self):
        self.as_("demo-auditor-01")
        current = self.client.get(f"/api/amount-rules?batch_id={BATCH}").json()
        self.assertEqual(current["current"]["version"], 1)
        payload = {"batch_id": BATCH, "request_id": str(uuid4()), "expected_version": 1, "mode": "FIXED", "rules": [{"category": "TOTALLY_DAMAGED", "amount": "8000"}, {"category": "PARTIALLY_DAMAGED", "amount": "4500.50"}], "reason": "Revised fictional budget"}
        self.assertEqual(self.client.post("/api/amount-rules", json=payload).status_code, 403)
        self.as_("demo-barangay-01")
        self.assertEqual(self.client.get(f"/api/amount-rules?batch_id={BATCH}").status_code, 403)
        self.approved_claim("PARTIALLY_DAMAGED")
        self.as_("demo-officer-01")
        self.assertEqual(self.client.post("/api/amount-rules", json={**payload, "rules": payload["rules"][:1]}).status_code, 422)
        self.assertEqual(self.client.post("/api/amount-rules", json={**payload, "rules": [{"category": "TOTALLY_DAMAGED", "amount": "20000"}, payload["rules"][1]]}).status_code, 422)
        self.assertEqual(self.client.post("/api/amount-rules", json={**payload, "mode": "WAGE_FORMULA"}).status_code, 422)
        saved = self.client.post("/api/amount-rules", json=payload)
        self.assertEqual(saved.status_code, 201, saved.text)
        self.assertEqual(self.client.post("/api/amount-rules", json=payload).status_code, 200)
        self.assertEqual(self.client.post("/api/amount-rules", json={**payload, "request_id": str(uuid4())}).status_code, 409)
        body = saved.json()
        self.assertEqual(body["current"]["version"], 2); self.assertEqual([h["version"] for h in body["history"]], [2, 1])
        self.assertEqual(body["entitlements"][0]["amount_centavos"], 450_050)
        wage = self.client.post("/api/amount-rules", json={**payload, "request_id": str(uuid4()), "expected_version": 2, "mode": "WAGE_FORMULA", "daily_wage": "450", "rules": [{"category": "TOTALLY_DAMAGED", "days": 20}, {"category": "PARTIALLY_DAMAGED", "days": 10}]})
        self.assertEqual(wage.status_code, 201, wage.text); self.assertEqual(wage.json()["current"]["rules"]["TOTALLY_DAMAGED"]["amount_centavos"], 900_000)

    def test_sessions_gate_payouts_to_assigned_open_staff(self):
        list_id = self.finalized_list()
        self.assertEqual([s["id"] for s in self.client.get("/api/payout-sessions/staff?barangay_id=BRGY-001").json()], ["demo-disbursing-001"])
        base = {"list_id": list_id, "session_date": SOON, "site": "San Isidro covered court", "assigned": ["demo-disbursing-001"]}
        self.assertEqual(self.client.post("/api/payout-sessions", json={**base, "request_id": str(uuid4()), "assigned": ["demo-disbursing-002"]}).status_code, 422)
        self.assertEqual(self.client.post("/api/payout-sessions", json={**base, "request_id": str(uuid4()), "session_date": "2000-01-01"}).status_code, 422)
        created = self.client.post("/api/payout-sessions", json={**base, "request_id": str(uuid4())})
        self.assertEqual(created.status_code, 201, created.text)
        session = created.json(); self.assertEqual(session["current"]["state"], "SCHEDULED"); self.assertEqual(session["progress"]["included"], 1)
        self.assertEqual(self.client.post("/api/payout-sessions", json={**base, "request_id": str(uuid4())}).status_code, 409)
        self.assertEqual(self.pay().status_code, 409)
        desk = self.client.get("/api/payout-desk/BEN-0004").json()
        self.assertFalse(desk["can_record"]); self.assertEqual(desk["session"]["message"], "The payout session has not been opened yet.")
        self.as_("demo-disbursing-002"); self.assertEqual(self.client.get("/api/payout-sessions").json(), [])
        self.as_("demo-beneficiary-01"); self.assertEqual(self.client.get("/api/payout-sessions").status_code, 403)
        self.as_("demo-barangay-01")
        visible = self.client.get("/api/payout-sessions").json()[0]
        self.assertNotIn("roster", visible); self.assertNotIn("reason", visible["current"])
        self.assertEqual(self.client.post(f"/api/payout-sessions/{session['session_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 1, "action": "OPEN"}).status_code, 403)
        self.as_("demo-disbursing-001")
        opened = self.client.post(f"/api/payout-sessions/{session['session_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 1, "action": "OPEN"})
        self.assertEqual(opened.status_code, 201, opened.text); self.assertEqual(opened.json()["current"]["state"], "OPEN")
        self.assertEqual(self.client.post(f"/api/payout-sessions/{session['session_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 2, "action": "CANCEL", "reason": "x"}).status_code, 403)
        paid = self.pay(); self.assertEqual(paid.status_code, 201, paid.text)
        roster = self.client.get(f"/api/payout-sessions/{session['session_id']}").json()
        self.assertEqual(roster["roster"][0]["distribution_id"], paid.json()["distribution_id"]); self.assertEqual(roster["progress"]["remaining"], 0)
        closed = self.client.post(f"/api/payout-sessions/{session['session_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 2, "action": "CLOSE"}).json()
        self.assertEqual(closed["current"]["state"], "CLOSED")
        self.as_("demo-officer-01")
        self.assertEqual(self.client.post(f"/api/payout-sessions/{session['session_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 3, "action": "CANCEL", "reason": "x"}).status_code, 409)
        self.assertEqual(self.client.post(f"/api/payout-sessions/{session['session_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 3, "action": "REOPEN"}).status_code, 422)
        reopened = self.client.post(f"/api/payout-sessions/{session['session_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 3, "action": "REOPEN", "reason": "Late arrivals"})
        self.assertEqual(reopened.status_code, 201); self.assertEqual([h["action"] for h in reopened.json()["history"]], ["REOPEN", "CLOSE", "OPEN", "SCHEDULE"])

    def test_cancelled_session_blocks_until_rescheduled(self):
        list_id = self.finalized_list()
        session = self.client.post("/api/payout-sessions", json={"list_id": list_id, "request_id": str(uuid4()), "session_date": SOON, "site": "Hall", "assigned": ["demo-disbursing-001"]}).json()
        edited = self.client.post(f"/api/payout-sessions/{session['session_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 1, "action": "EDIT", "reason": "Venue moved", "details": {"session_date": SOON, "site": "Covered court", "assigned": ["demo-disbursing-001"]}})
        self.assertEqual(edited.json()["current"]["site"], "Covered court")
        self.client.post(f"/api/payout-sessions/{session['session_id']}/revisions", json={"request_id": str(uuid4()), "expected_revision": 2, "action": "CANCEL", "reason": "Storm warning"})
        self.as_("demo-disbursing-001")
        self.assertIn("cancelled", self.pay().json()["detail"])
        self.as_("demo-officer-01")
        again = self.client.post("/api/payout-sessions", json={"list_id": list_id, "request_id": str(uuid4()), "session_date": SOON, "site": "Hall", "assigned": ["demo-disbursing-001"]})
        self.assertEqual(again.status_code, 201, again.text)


if __name__ == "__main__": unittest.main(verbosity=2)
