"""Durable payout anchoring. Business retries never invoke this recovery operation."""
import json
import re
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import text
from app import config
from app.database import SessionLocal
from app.models.entities import Distribution, PayoutAnchorJob, AnchorSignerLease, AnchorObservation, AuditEvent
from app.services.blockchain import blockchain_service, is_hex_hash
from app.services.hasher import compute_receipt_hash

ERRORS = {"RPC_UNAVAILABLE", "CHAIN_CHANGED", "DEPLOYMENT_CHANGED", "ANCHOR_CONFLICT", "ENVELOPE_CHANGED",
          "RECORD_CHANGED", "TRANSACTION_REVERTED", "NONCE_CONFLICT", "BROADCAST_UNCERTAIN", "SIGNER_BUSY"}


def now():
    return datetime.now(timezone.utc).isoformat()


def payload_for(dist):
    return {"batch_id": dist.batch_id, "allocation_id": dist.allocation_id, "distribution_id": dist.distribution_id,
            "beneficiary_id": dist.beneficiary_id, "amount_centavos": dist.amount_centavos, "receipt_hash": dist.receipt_hash}


def new_job(dist):
    payload = {**payload_for(dist), "chain_id": config.CHAIN_ID, "contract_address": config.CONTRACT_ADDRESS}
    return PayoutAnchorJob(distribution_id=dist.distribution_id, snapshot_json=json.dumps(payload, sort_keys=True),
                          chain_id=config.CHAIN_ID, contract_address=config.CONTRACT_ADDRESS, state="PENDING", updated_at=now())


def write_lock(db):
    if db.bind.dialect.name != "sqlite":
        raise RuntimeError("Payout anchor recovery currently requires SQLite.")
    db.execute(text("BEGIN IMMEDIATE"))


def claim(distribution_id=None):
    """One durable lease coordinates payout jobs and legacy funding CLI writes."""
    with SessionLocal() as db:
        write_lock(db)
        lease = db.get(AnchorSignerLease, 1)
        if lease and lease.expires_at > int(time.time()):
            return None
        unresolved = db.query(PayoutAnchorJob).filter(PayoutAnchorJob.raw_transaction.isnot(None), PayoutAnchorJob.state != "CONFIRMED")
        if distribution_id:
            unresolved = unresolved.filter(PayoutAnchorJob.distribution_id != distribution_id)
        if unresolved.first():
            return None
        owner = str(uuid4())
        if lease is None:
            lease = AnchorSignerLease(id=1)
            db.add(lease)
        lease.owner, lease.expires_at = owner, int(time.time()) + 60
        db.commit()
        return owner


def release(owner):
    with SessionLocal() as db:
        db.query(AnchorSignerLease).filter_by(id=1, owner=owner).delete()
        db.commit()


@contextmanager
def legacy_signer():
    owner = claim()
    try:
        yield bool(owner)
    finally:
        if owner:
            release(owner)


def owned(db, owner):
    lease = db.get(AnchorSignerLease, 1)
    if not lease or lease.owner != owner or lease.expires_at <= int(time.time()):
        raise RuntimeError("Anchor signer lease expired; work remains recoverable.")


def observation(db, job):
    db.add(AnchorObservation(distribution_id=job.distribution_id, state=job.state, error_code=job.error_code,
                            checked_at=job.updated_at, transaction_hash=job.candidate_tx_hash,
                            block_number=job.block_number, block_hash=job.block_hash))


def record_matches(dist, payload):
    recalculated = compute_receipt_hash(distribution_id=dist.distribution_id, beneficiary_id=dist.beneficiary_id,
        batch_id=dist.batch_id, amount_centavos=dist.amount_centavos, ocr_text=dist.ocr_text, verification_method=dist.verification_method)
    return payload_for(dist) == {key: payload.get(key) for key in payload_for(dist)} and recalculated.lower() == dist.receipt_hash.lower()


def chain_call(*args):
    try:
        result = blockchain_service.payout_anchor(*args)
        return result if isinstance(result, dict) else {"success": False, "error_code": "RPC_UNAVAILABLE"}
    except Exception:
        return {"success": False, "error_code": "RPC_UNAVAILABLE"}


def finish(distribution_id, owner, result):
    with SessionLocal() as db:
        write_lock(db)
        owned(db, owner)
        job = db.get(PayoutAnchorJob, distribution_id)
        dist = db.query(Distribution).filter_by(distribution_id=distribution_id).one()
        if result.get("state") == "CONFIRMED" and not record_matches(dist, json.loads(job.snapshot_json)):
            result = {"success": False, "error_code": "RECORD_CHANGED"}
        state = result.get("state")
        if result.get("success") is True and state in {"SUBMITTED", "CONFIRMED"} and result.get("tx_hash") == job.candidate_tx_hash:
            if state == "CONFIRMED":
                valid = (result.get("chain_id") == job.chain_id and isinstance(result.get("contract_address"), str)
                         and result["contract_address"].lower() == (job.contract_address or "").lower()
                         and type(result.get("block_number")) is int and result["block_number"] > 0
                         and is_hex_hash(result.get("block_hash"))
                         and type(result.get("receipt_timestamp")) is int and result["receipt_timestamp"] > 0)
                if not valid:
                    result, state = {"error_code": "RPC_UNAVAILABLE"}, "FAILED"
            job.state = state
        else:
            job.state = "FAILED" if not job.raw_transaction else "SUBMITTED"
            if result.get("error_code") in ERRORS - {"RPC_UNAVAILABLE", "BROADCAST_UNCERTAIN"}:
                job.state = "FAILED"
        job.error_code = result.get("error_code") if result.get("error_code") in ERRORS else None
        if result.get("success") is not True and not job.error_code:
            job.error_code = "RPC_UNAVAILABLE"
        job.updated_at = now()
        if job.state == "CONFIRMED":
            first_confirmation = job.confirmed_at is None
            job.confirmed_at = job.confirmed_at or job.updated_at
            job.block_number, job.block_hash = result["block_number"], result["block_hash"]
            job.receipt_timestamp = result["receipt_timestamp"]
            dist.blockchain_tx_hash = job.candidate_tx_hash
            db.query(AuditEvent).filter_by(entity_id=distribution_id, event_type="DISTRIBUTION_CONFIRMED").update({"blockchain_tx_hash": job.candidate_tx_hash})
            if first_confirmation:
                db.add(AuditEvent(batch_id=dist.batch_id, entity_id=distribution_id, event_type="PAYOUT_ANCHOR_CONFIRMED",
                                  description="Observed a mined anchor for a recorded synthetic payout", blockchain_tx_hash=job.candidate_tx_hash))
        observation(db, job)
        db.commit()


def process_job(distribution_id):
    owner = claim(distribution_id)
    if not owner:
        return False
    try:
        with SessionLocal() as db:
            write_lock(db)
            owned(db, owner)
            job = db.get(PayoutAnchorJob, distribution_id)
            if job is None:
                return False
            dist = db.query(Distribution).filter_by(distribution_id=distribution_id).one()
            payload = json.loads(job.snapshot_json)
            matches = record_matches(dist, payload)
            job.attempts += 1
            job.updated_at = now()
            raw, pin = job.raw_transaction, json.loads(job.pin_json) if job.pin_json else None
            candidate = job.candidate_tx_hash
            db.commit()
        if not matches:
            finish(distribution_id, owner, {"success": False, "error_code": "RECORD_CHANGED"})
            return True
        if raw is None:
            prepared = chain_call("prepare", payload)
            p = prepared.get("pin") or {}
            valid = (prepared.get("success") is True and is_hex_hash(prepared.get("tx_hash"))
                     and isinstance(prepared.get("raw_transaction"), str)
                     and re.fullmatch(r"0x[0-9a-fA-F]+", prepared["raw_transaction"]) is not None
                     and prepared.get("chain_id") == payload["chain_id"] and prepared.get("contract_address") == payload["contract_address"]
                     and type(p.get("block_number")) is int and p["block_number"] >= 0
                     and is_hex_hash(p.get("block_hash")) and is_hex_hash(p.get("code_hash")))
            if not valid:
                finish(distribution_id, owner, {"success": False, "error_code": prepared.get("error_code", "RPC_UNAVAILABLE")})
                return True
            raw, pin = prepared["raw_transaction"], p
            candidate = prepared["tx_hash"]
            with SessionLocal() as db:
                write_lock(db)
                owned(db, owner)
                job = db.get(PayoutAnchorJob, distribution_id)
                job.raw_transaction, job.pin_json = raw, json.dumps(pin, sort_keys=True)
                job.candidate_tx_hash, job.state = prepared["tx_hash"], "SUBMITTED"
                job.error_code, job.updated_at = None, now()
                observation(db, job)
                # MUST commit the envelope/hash before the broadcast subprocess.
                db.commit()
        result = chain_call("recover", payload, raw, pin, candidate)
        finish(distribution_id, owner, result)
        return True
    finally:
        release(owner)
