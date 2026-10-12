"""Real-chain recovery checks. Run through the owned-node helper, never default RPC."""
import os
import tempfile
import json
import urllib.request
from pathlib import Path
from unittest.mock import patch

if os.environ.get("POLYGON_RPC_URL") != "http://127.0.0.1:8547" or os.environ.get("CHAIN_ID") != "31337":
    raise SystemExit("Run contracts/scripts/test_payout_anchor_live.js with its owned isolated node.")
directory = Path(tempfile.mkdtemp(prefix="ayudachain-live-anchor-"))
os.environ["DATABASE_URL"] = "sqlite:///" + (directory / "records.db").as_posix()
os.environ["RECEIPTS_DIR"] = str(directory / "receipts")
os.environ["DEMO_ACCOUNTS_FILE"] = str(directory / "accounts.json")
os.environ["CORS_ORIGINS"] = "http://127.0.0.1:3001"
import sys
sys.path.insert(0, str(Path(__file__).parent / "tests"))
from auth_support import accounts_fixture, HEADERS, TEST_PASSWORD
accounts_fixture(directory)
from app import config
config.CORS_ORIGINS = ["http://127.0.0.1:3001"]
from app.main import app
from app.services.blockchain import blockchain_service
from app.database import SessionLocal
from app.models.entities import Distribution, PayoutAnchorJob
from fastapi.testclient import TestClient


def rpc(method, params):
    request = urllib.request.Request(config.RPC_URL, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(), headers={"Content-Type": "application/json"})
    result = json.load(urllib.request.urlopen(request, timeout=10))
    assert "error" not in result, result
    return result["result"]


with TestClient(app, base_url="http://127.0.0.1", headers=HEADERS) as client:
    def login(identity):
        result = client.post("/api/auth/login", json={"username": identity, "password": TEST_PASSWORD})
        assert result.status_code == 200, result.text
        client.headers["X-CSRF-Token"] = result.json()["csrf_token"]

    def pay(ben):
        result = client.post("/api/distributions/confirm", headers={"Idempotency-Key": "live-" + ben}, json={"beneficiary_id": ben, "batch_id": "RELIEF-2026-001", "amount": 5000})
        assert result.status_code == 201, result.text
        return result.json()

    def retry(record):
        result = client.post("/api/distributions/" + record["distribution_id"] + "/anchor/retry")
        assert result.status_code == 200, result.text
        return result.json()

    login("demo-disbursing-001")
    normal = pay("BEN-0004")
    assert normal["anchor_job"]["state"] == "CONFIRMED", normal["anchor_job"]
    assert client.post("/api/blockchain/verify", json={"distribution_id": normal["distribution_id"]}).json()["verification_status"] == "VERIFIED"
    print("PASS real mined anchor, saved confirmation metadata and live integrity check", flush=True)

    original = blockchain_service.payout_anchor
    def lost_response(action, *args):
        result = original(action, *args)
        if action == "recover":
            assert result.get("state") == "CONFIRMED", result
            return {"success": False, "error_code": "RPC_UNAVAILABLE"}
        return result
    with patch.object(blockchain_service, "payout_anchor", side_effect=lost_response):
        lost = pay("BEN-0006")
    assert lost["anchor_job"]["state"] == "SUBMITTED" and lost["blockchain_tx_hash"] is None
    height = rpc("eth_blockNumber", [])
    recovered = retry(lost)
    assert recovered["anchor_job"]["state"] == "CONFIRMED"
    assert recovered["blockchain_tx_hash"] == lost["anchor_job"]["candidate_tx_hash"]
    retry(recovered)
    assert rpc("eth_blockNumber", []) == height
    print("PASS lost mined response recovered with original hash and no new transaction", flush=True)

    login("demo-officer-01")
    for ben in ("BEN-0005", "BEN-0007"):
        result = client.post("/api/beneficiaries/" + ben + "/verify", json={"status": "VERIFIED", "review_notes": "Distinct synthetic household for isolated recovery evaluation"})
        assert result.status_code == 200, result.text
    login("demo-disbursing-001")
    rpc("evm_setAutomine", [False])
    pending = pay("BEN-0005")
    assert pending["anchor_job"]["state"] == "SUBMITTED" and pending["blockchain_tx_hash"] is None
    rpc("evm_mine", [])
    rpc("evm_setAutomine", [True])
    confirmed = retry(pending)
    assert confirmed["anchor_job"]["state"] == "CONFIRMED"
    assert confirmed["blockchain_tx_hash"] == pending["anchor_job"]["candidate_tx_hash"]
    print("PASS actual pending transaction reconciled after mining", flush=True)

    def interrupt_before_send(action, *args):
        return original(action, *args) if action == "prepare" else {"success": False, "error_code": "RPC_UNAVAILABLE"}
    with patch.object(blockchain_service, "payout_anchor", side_effect=interrupt_before_send):
        interrupted = pay("BEN-0007")
    assert interrupted["anchor_job"]["state"] == "SUBMITTED"
    signer = rpc("eth_accounts", [])[0]
    # Deliberately consume the prepared nonce on this disposable chain only.
    rpc("eth_sendTransaction", [{"from": signer, "to": signer, "value": "0x0"}])
    conflict = retry(interrupted)
    assert conflict["anchor_job"]["state"] == "FAILED" and conflict["anchor_job"]["error_code"] == "NONCE_CONFLICT", conflict["anchor_job"]
    assert conflict["blockchain_tx_hash"] is None
    print("PASS unknown nonce consumption refuses a replacement transaction", flush=True)

    with SessionLocal() as db:
        before = [(d.distribution_id, d.receipt_hash) for d in db.query(Distribution)]
        raw = db.get(PayoutAnchorJob, interrupted["distribution_id"]).raw_transaction
    rpc("hardhat_reset", [])
    reset = retry(interrupted)
    assert reset["anchor_job"]["error_code"] == "DEPLOYMENT_CHANGED"
    with SessionLocal() as db:
        assert before == [(d.distribution_id, d.receipt_hash) for d in db.query(Distribution)]
        assert raw == db.get(PayoutAnchorJob, interrupted["distribution_id"]).raw_transaction
    print("PASS deployment loss refuses replay and preserves all payout records/proofs", flush=True)
print("5 live isolated recovery scenarios passed", flush=True)
