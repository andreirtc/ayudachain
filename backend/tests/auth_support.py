"""Synthetic credential fixtures; no authentication bypass in production code."""
import os
from pathlib import Path
from fastapi.testclient import TestClient
from scripts.provision_demo_accounts import provision

TEST_PASSWORD = "synthetic-test-password-only"
IDS = ["demo-officer-01", "demo-barangay-01", "demo-auditor-01", "demo-beneficiary-01"] + [f"demo-disbursing-{n:03}" for n in range(1, 5)]
HEADERS = {"X-AyudaChain-Client": "web", "Origin": "http://127.0.0.1:3001"}


def accounts_fixture(directory):
    path = Path(directory) / "accounts.json"
    provision(path, {identity: TEST_PASSWORD for identity in IDS})
    os.environ["DEMO_ACCOUNTS_FILE"] = str(path)
    os.environ["CORS_ORIGINS"] = "http://127.0.0.1:3001,http://127.0.0.1:3101"
    return path


class WorkflowClient:
    """Business regression requests use actual role-appropriate authenticated clients."""
    def __init__(self, app):
        self.app = app
        self.root = TestClient(app, base_url="http://127.0.0.1", headers=HEADERS)
        self.clients = {}

    def __enter__(self):
        self.root.__enter__()
        return self

    def __exit__(self, *args):
        return self.root.__exit__(*args)

    def authenticate_all(self):
        self.clients = {}
        for identity in IDS:
            client = TestClient(self.app, base_url="http://127.0.0.1", headers=HEADERS)
            result = client.post("/api/auth/login", json={"username": identity, "password": TEST_PASSWORD})
            assert result.status_code == 200, result.text
            client.headers["X-CSRF-Token"] = result.json()["csrf_token"]
            self.clients[identity] = client

    def request(self, method, path, **kwargs):
        if not self.clients:
            self.authenticate_all()
        identity = "demo-officer-01"
        if path == "/api/distributions/confirm":
            from app.database import SessionLocal
            from app.models.entities import Beneficiary
            with SessionLocal() as db:
                ben = db.query(Beneficiary).filter_by(beneficiary_id=kwargs.get("json", {}).get("beneficiary_id")).first()
                barangay = ben.barangay_id if ben else "BRGY-001"
            identity = "demo-disbursing-" + barangay.removeprefix("BRGY-")
        return self.clients[identity].request(method, path, **kwargs)

    def get(self, path, **kwargs): return self.request("GET", path, **kwargs)
    def post(self, path, **kwargs): return self.request("POST", path, **kwargs)
    def delete(self, path, **kwargs): return self.request("DELETE", path, **kwargs)
