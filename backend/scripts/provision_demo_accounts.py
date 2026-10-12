"""Create local synthetic credentials without touching records, receipts or chain."""
import json
import os
import secrets
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from app.auth import password_hash


def provision(path, passwords=None):
    profiles = [
        {"id": "demo-officer-01", "role": "DSWD", "display_name": "Demo DSWD officer"},
        {"id": "demo-barangay-01", "role": "BARANGAY", "display_name": "Demo barangay officer", "barangay_id": "BRGY-001"},
        {"id": "demo-auditor-01", "role": "AUDITOR", "display_name": "Demo auditor"},
        {"id": "demo-beneficiary-01", "role": "BENEFICIARY", "display_name": "Demo household account", "beneficiary_id": "BEN-0004"},
    ] + [{"id": f"demo-disbursing-{n:03}", "role": "DISBURSING", "display_name": f"Demo disbursing officer {n}", "barangay_id": f"BRGY-{n:03}"} for n in range(1, 5)]
    credentials = []
    for profile in profiles:
        password = passwords[profile["id"]] if passwords else secrets.token_urlsafe(24)
        salt = secrets.token_hex(32)
        profile.update(enabled=True, salt=salt, password_hash=password_hash(password, salt))
        credentials.append({"username": profile["id"], "password": password, "role": profile["role"]})
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump({"version": 1, "accounts": profiles}, stream, indent=2)
    return credentials


if __name__ == "__main__":
    target = BACKEND / ".demo-accounts.json"
    login_path = BACKEND / ".demo-login.json"
    if target.exists() or login_path.exists():
        raise SystemExit("Existing credentials preserved. Provisioning does not overwrite accounts.")
    credentials = provision(target)
    descriptor = os.open(login_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(credentials, stream, indent=2)
    print("Synthetic accounts provisioned. Credentials are in backend/.demo-login.json (ignored by git).")
