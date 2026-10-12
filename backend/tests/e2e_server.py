"""Isolated browser-test API. No original database or local chain is used."""
import os
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
directory = Path(tempfile.mkdtemp(prefix="ayudachain-auth-e2e-"))
os.environ["DATABASE_URL"] = "sqlite:///" + (directory / "records.db").as_posix()
os.environ["RECEIPTS_DIR"] = str(directory / "receipts")
os.environ["DEMO_ACCOUNTS_FILE"] = str(directory / "accounts.json")
os.environ["CORS_ORIGINS"] = "http://127.0.0.1:3101"
sys.path.insert(0, str(BACKEND / "tests"))
from auth_support import accounts_fixture
accounts_fixture(directory)
from app import config
config.CORS_ORIGINS = ["http://127.0.0.1:3101"]
from app.services.blockchain import blockchain_service


def unavailable(*args, **kwargs):
    return {"success": False, "error": "Isolated authentication test: chain not connected", "network": "Isolated auth test", "chainId": 31337, "contractAddress": config.CONTRACT_ADDRESS}


for name in ("get_status", "release_fund", "allocate_fund", "confirm_distribution", "verify_receipt", "payout_anchor"):
    setattr(blockchain_service, name, unavailable)

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8101, log_level="warning")
