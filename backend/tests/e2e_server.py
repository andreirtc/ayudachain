"""Isolated browser-test API. No original database or local chain is used."""
import os
import json
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
directory = Path(tempfile.mkdtemp(prefix="ayudachain-auth-e2e-"))
os.environ["DATABASE_URL"] = "sqlite:///" + (directory / "records.db").as_posix()
os.environ["RECEIPTS_DIR"] = str(directory / "receipts")
os.environ["DEMO_ACCOUNTS_FILE"] = str(directory / "accounts.json")
frontend_origin = os.environ.get("AYUDACHAIN_TEST_BASE_URL", "http://127.0.0.1:3101")
api_url = urlsplit(os.environ.get("AYUDACHAIN_TEST_API_URL", "http://127.0.0.1:8101"))
if api_url.scheme != "http" or api_url.hostname not in {"127.0.0.1", "localhost"}:
    raise RuntimeError("Browser test API must use loopback HTTP")
os.environ["CORS_ORIGINS"] = frontend_origin
sys.path.insert(0, str(BACKEND / "tests"))
from auth_support import accounts_fixture
accounts_path = accounts_fixture(directory)
accounts = json.loads(accounts_path.read_text())
recipient = next(row for row in accounts["accounts"] if row["role"] == "BENEFICIARY")
accounts["accounts"].append({**recipient, "id": "synthetic-beneficiary-phone", "display_name": "Synthetic phone recipient", "beneficiary_id": "BEN-0006"})
for viewport in ("desktop", "phone"):
    for state in ("pending", "approved", "rejected", "historical", "missing"):
        accounts["accounts"].append({**recipient, "id": f"synthetic-home-{state}-{viewport}", "display_name": f"Synthetic home {state}", "beneficiary_id": f"BEN-HOME-{state}-{viewport}"})
accounts_path.write_text(json.dumps(accounts))
from app import config
config.CORS_ORIGINS = [frontend_origin]
from app.services.blockchain import blockchain_service


def unavailable(*args, **kwargs):
    return {"success": False, "error": "Isolated authentication test: chain not connected", "network": "Isolated auth test", "chainId": 31337, "contractAddress": config.CONTRACT_ADDRESS}


for name in ("get_status", "release_fund", "allocate_fund", "confirm_distribution", "verify_receipt", "payout_anchor"):
    setattr(blockchain_service, name, unavailable)

(directory / "receipts").mkdir(exist_ok=True)
(directory / "receipts" / "captured-synthetic.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120"><text x="20" y="50">Controlled synthetic receipt evidence</text></svg>')
from app.main import app

# Registered only by this disposable test launcher, never by the production API.
# Every browser case starts with fresh records rather than inheriting prior payouts.
if os.environ.get("AYUDACHAIN_E2E_RESET_ENABLED") == "1":
    from fastapi import Header, HTTPException
    from app.database import engine, Base, init_db
    from app.seed_demo import seed_if_empty

    @app.post("/__test__/reset", include_in_schema=False)
    def reset_fixture(x_ayudachain_test_reset: str | None = Header(default=None)):
        if x_ayudachain_test_reset != "synthetic-e2e-reset-only":
            raise HTTPException(403, "Browser fixture reset only")
        if Path(engine.url.database).resolve() != (directory / "records.db").resolve():
            raise RuntimeError("Refusing reset outside the owned temporary database")
        Base.metadata.drop_all(bind=engine)
        init_db()
        seed_if_empty()
        return {"reset": True, "synthetic": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=api_url.port or 8101, log_level="warning")
