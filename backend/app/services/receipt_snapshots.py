"""Version two commits captured registry metadata and actual available receipt bytes.
Legacy hashes are never rewritten; captured labels do not establish real identity.
"""
from datetime import timezone
import hashlib
import json
from pathlib import Path
import re
from fastapi import HTTPException
from app import config
from app.models.entities import ReceiptSnapshot, Distribution, Beneficiary
from app.auth import assert_household_scope
from app.services.hasher import canonical_json, compute_sha256_hex, compute_receipt_hash

MAX_DOCUMENT_BYTES = 2 * 1024 * 1024

def utc(value):
    return value.replace(tzinfo=timezone.utc).isoformat() if value.tzinfo is None else value.astimezone(timezone.utc).isoformat()

def capture_document(filename, db=None, actor=None):
    filename = filename or "sample_relief_receipt.svg"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", filename):
        raise HTTPException(422, "Receipt filename must be a local reference, without path components.")
    shared_template = filename.casefold() == "sample_relief_receipt.svg"
    if not shared_template and db is not None:
        for record in db.query(Distribution).all():
            saved = record.receipt_snapshot
            source_name = saved.get("receipt", {}).get("document", {}).get("source_filename") if saved else None
            if (record.receipt_file_path or "").casefold() == ("/receipts/" + filename).casefold() or (source_name or "").casefold() == filename.casefold():
                assert_household_scope(actor, db.query(Beneficiary).filter_by(beneficiary_id=record.beneficiary_id).first())
    base = Path(config.RECEIPTS_DIR).resolve()
    source = (base / filename).resolve()
    if not source.is_relative_to(base): raise HTTPException(422, "Receipt file is outside configured storage.")
    if not source.is_file():
        return {"kind": "MISSING", "source_filename": filename, "sha256": None, "byte_count": 0, "media_type": None}, None, None
    try:
        with source.open("rb") as stream: content = stream.read(MAX_DOCUMENT_BYTES + 1)
    except OSError: raise HTTPException(503, "Receipt evidence could not be captured. Retry before recording the payout.") from None
    if len(content) > MAX_DOCUMENT_BYTES: raise HTTPException(413, "Receipt evidence exceeds the 2 MiB capture limit.")
    media = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(source.suffix.lower(), "application/octet-stream")
    return {"kind": "SHARED_TEMPLATE" if shared_template else "CAPTURED", "source_filename": filename, "sha256": "0x" + hashlib.sha256(content).hexdigest(), "byte_count": len(content), "media_type": media}, content, media

def payout_values(dist):
    return {key: getattr(dist, key) for key in ("distribution_id", "beneficiary_id", "batch_id", "allocation_id", "amount_centavos", "verification_method", "receipt_file_path")} | {"recorded_at": utc(dist.distributed_at)}

def capture(dist, ben, batch, allocation, actor, document):
    doc, content, media = document
    data = {"format": "ayudachain.receipt", "version": 2, "payout": payout_values(dist),
        "recorded_by": {"account_id": actor.id, "display_name": actor.display_name},
        "household": {key: getattr(ben, key) for key in ("beneficiary_id", "household_name", "dafac_id", "barangay_id", "barangay_name", "batch_id", "verification_status", "review_status", "record_status")},
        "batch": {key: getattr(batch, key) for key in ("batch_id", "calamity_name", "source_agency", "recipient_lgu", "purpose", "standard_grant_centavos", "max_grant_centavos")},
        "allocation": {key: getattr(allocation, key) for key in ("allocation_id", "batch_id", "barangay_id", "barangay_name", "amount_centavos")},
        "receipt": {"ocr_text": dist.ocr_text, "document": doc}}
    encoded = canonical_json(data)
    return ReceiptSnapshot(distribution_id=dist.distribution_id, version=2, snapshot_json=encoded, document_bytes=content, document_media_type=media), compute_sha256_hex(encoded)

def current_receipt_hash(dist):
    saved = dist.snapshot_record
    if saved is None:
        return compute_receipt_hash(distribution_id=dist.distribution_id, beneficiary_id=dist.beneficiary_id, batch_id=dist.batch_id, amount_centavos=dist.amount_centavos, ocr_text=dist.ocr_text, verification_method=dist.verification_method)
    try:
        data = json.loads(saved.snapshot_json)
        if saved.version != 2 or data["version"] != 2 or data["format"] != "ayudachain.receipt": raise ValueError()
        doc = data["receipt"]["document"]
        observed_doc_hash = "0x" + hashlib.sha256(saved.document_bytes).hexdigest() if saved.document_bytes is not None else None
        observed_size = len(saved.document_bytes) if saved.document_bytes is not None else 0
        consistent = data["payout"] == payout_values(dist) and data["receipt"]["ocr_text"] == dist.ocr_text and doc["sha256"] == observed_doc_hash and doc["byte_count"] == observed_size and doc.get("media_type") == saved.document_media_type
        if saved.document_bytes is None and doc["kind"] != "MISSING": consistent = False
        # Hash the frozen payload too; replacing its values could hide corruption.
        if not consistent:
            data["current_record_mismatch"] = {"payout": payout_values(dist), "ocr_text": dist.ocr_text, "document_sha256": observed_doc_hash, "document_byte_count": observed_size}
        return compute_sha256_hex(canonical_json(data))
    except (ValueError, TypeError, KeyError, AttributeError):
        return compute_sha256_hex(canonical_json({"invalid_receipt_snapshot": dist.distribution_id}))
