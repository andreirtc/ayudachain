"""Owned live-chain UI fixture; never starts against an existing database."""
import os
import sys
import tempfile
from pathlib import Path

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
os.environ["CORS_ORIGINS"] = "http://127.0.0.1:3102"
from auth_support import accounts_fixture
accounts_fixture(directory)
from app import config
config.CORS_ORIGINS = ["http://127.0.0.1:3102"]
(directory / "receipts").mkdir(exist_ok=True)
(directory / "receipts" / "captured-synthetic.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="120"><text x="20" y="50">Controlled synthetic receipt evidence</text></svg>')
from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8102, log_level="warning")
