"""Tamper/restore only a test-owned receipt, or create a genuinely unanchored fixture."""
import os
import sys
import tempfile
from pathlib import Path

directory = Path(sys.argv[1]).resolve()
if directory.parent != Path(tempfile.gettempdir()).resolve() or not directory.name.startswith("ayudachain-verification-ui-") or not (directory / "records.db").is_file():
    raise SystemExit("Refusing an unowned fixture database")
os.environ["DATABASE_URL"] = "sqlite:///" + (directory / "records.db").as_posix()
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database import SessionLocal
from app.models.entities import Distribution, Allocation
from app.services.hasher import compute_receipt_hash

action = sys.argv[2]
with SessionLocal() as db:
    if action in {"mismatch", "restore"}:
        record = db.query(Distribution).filter_by(distribution_id="DIST-0001").one()
        if record.amount_centavos not in {500000, 500001}:
            raise SystemExit("Unexpected fixture amount; refusing to rewrite it")
        record.amount_centavos = 500001 if action == "mismatch" else 500000
    elif action == "unanchored":
        if not db.query(Distribution).filter_by(distribution_id="DIST-UI-UNANCHORED").first():
            allocation = db.query(Allocation).filter_by(batch_id="RELIEF-2026-001", barangay_id="BRGY-001").one()
            values = dict(distribution_id="DIST-UI-UNANCHORED", beneficiary_id="BEN-0005", batch_id="RELIEF-2026-001", amount_centavos=12345, ocr_text="Synthetic unanchored UI fixture", verification_method="SYNTHETIC_UI_FIXTURE")
            db.add(Distribution(**values, allocation_id=allocation.allocation_id, receipt_hash=compute_receipt_hash(**values), status="CONFIRMED"))
    else:
        raise SystemExit("Unknown fixture action")
    db.commit()
