"""Owned live-chain UI fixture; never starts against an existing database."""
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

BACKEND = Path(__file__).resolve().parents[1]
directory = Path(sys.argv[1]).resolve()
if directory.parent != Path(tempfile.gettempdir()).resolve() or not directory.name.startswith("ayudachain-verification-ui-"):
    raise SystemExit("Refusing an unowned fixture directory")
if os.environ.get("POLYGON_RPC_URL") != "http://127.0.0.1:8547":
    raise SystemExit("Live UI tests require the owned local chain")
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "tests"))
os.environ["DATABASE_URL"] = "sqlite:///" + (directory / "records.db").as_posix()
os.environ["RECEIPTS_DIR"] = str(directory / "receipts")
os.environ["DEMO_ACCOUNTS_FILE"] = str(directory / "accounts.json")
frontend_origin = os.environ.get("AYUDACHAIN_LIVE_BASE_URL", "http://127.0.0.1:3312")
api_url = urlsplit(os.environ.get("AYUDACHAIN_LIVE_API_URL", "http://127.0.0.1:8312"))
if api_url.scheme != "http" or api_url.hostname not in {"127.0.0.1", "localhost"}:
    raise SystemExit("Live UI tests require a loopback API")
os.environ["CORS_ORIGINS"] = frontend_origin
from auth_support import accounts_fixture
accounts_fixture(directory)
from app import config
config.CORS_ORIGINS = [frontend_origin]
(directory / "receipts").mkdir(exist_ok=True)
(directory / "receipts" / "captured-synthetic.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120"><text x="20" y="50">Controlled synthetic receipt evidence</text></svg>')
from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=api_url.port or 8312, log_level="warning")
