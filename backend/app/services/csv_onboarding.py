"""Actor-bound CSV plans and atomic, review-only registry imports."""
import csv
import hashlib
import io
import json
import re
import time
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text
from app.auth import require_actor
from app.database import get_db
from app.models.entities import Base, Beneficiary, ReliefBatch, AuditEvent
from app.barangays import barangay_error
from app.ai.entity_resolution import token_similarity

class CsvImport(Base):
    __tablename__ = "csv_imports"
    import_id = Column(String(64), primary_key=True)
    actor_id = Column(String(64), nullable=False)
    batch_id = Column(String(64), nullable=False)
    registry_hash = Column(String(64), nullable=False)
    plan_json = Column(Text, nullable=False)
    result_json = Column(Text, nullable=True)
    expires_at = Column(Integer, nullable=False)

class PreviewInput(BaseModel):
    batch_id: str = Field(min_length=1, max_length=64)
    csv_content: str = Field(min_length=1, max_length=131072)

router = APIRouter(prefix="/api/beneficiaries/csv")
REQUIRED = {"beneficiary_id", "household_name", "barangay_id", "barangay_name"}
COLUMNS = REQUIRED | {"dafac_id", "contact_number"}
LIMITS = {"beneficiary_id": 64, "household_name": 128, "barangay_id": 32, "barangay_name": 128, "dafac_id": 64, "contact_number": 32}

def officer(request):
    actor = require_actor(request)
    if actor.role != "DSWD":
        raise HTTPException(403, "CSV onboarding belongs to the DSWD workflow.")
    return actor

def registry(db):
    rows = [{key: getattr(ben, key) for key in ("beneficiary_id", "household_name", "barangay_id", "dafac_id", "batch_id", "record_status", "canonical_beneficiary_id", "verification_status", "review_status")} for ben in db.query(Beneficiary).order_by(Beneficiary.beneficiary_id).all()]
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return rows, digest

def plan_csv(content, existing):
    if len(content.encode("utf-8")) > 131072:
        raise HTTPException(413, "CSV must be at most 128 KiB.")
    reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")), strict=True)
    try:
        fields = reader.fieldnames or []
        if len(set(fields)) != len(fields) or not REQUIRED <= set(fields) or not set(fields) <= COLUMNS:
            raise HTTPException(422, "Use the required CSV headers: beneficiary_id, household_name, barangay_id, barangay_name; optional dafac_id and contact_number.")
        rows, ids = [], set()
        known = {row["beneficiary_id"] for row in existing}
        for raw in reader:
            if len(rows) >= 200:
                raise HTTPException(413, "CSV must contain at most 200 households.")
            errors = []
            if None in raw or any(value is None for value in raw.values()):
                errors.append("Column count does not match the header.")
            data = {key: (raw.get(key) or "").strip() for key in COLUMNS}
            for key, limit in LIMITS.items():
                value = data[key]
                if (key in REQUIRED and not value) or len(value) > limit or re.search(r"[\x00-\x1f\x7f]", value):
                    errors.append(f"{key}: required text must fit {limit} characters with no control characters.")
            for key in ("beneficiary_id", "dafac_id"):
                if data[key] and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", data[key]):
                    errors.append(f"{key}: use letters, numbers, dots, underscores or hyphens.")
            if data["beneficiary_id"] in known:
                errors.append("Household ID already exists, including retained history. Choose a new ID; existing records are never overwritten.")
            if data["beneficiary_id"] in ids:
                errors.append("Repeated household ID in this file.")
            ids.add(data["beneficiary_id"])
            error = barangay_error(data["barangay_id"], data["barangay_name"])
            if error: errors.append(error)
            rows.append({"line": reader.line_num, "data": data, "errors": errors, "matches": []})
    except csv.Error:
        raise HTTPException(422, "Malformed CSV quoting. Correct the file and preview again.") from None
    if not rows:
        raise HTTPException(422, "CSV contains no household rows.")
    candidates = existing + [{**row["data"], "source_line": row["line"], "record_status": "IN_FILE"} for row in rows if not row["errors"]]
    for row in rows:
        if row["errors"]: continue
        matches = []
        for other in candidates:
            if other.get("source_line") == row["line"]: continue
            same_dafac = bool(row["data"]["dafac_id"] and row["data"]["dafac_id"].upper() == (other["dafac_id"] or "").upper())
            score = token_similarity(row["data"]["household_name"], other["household_name"])
            if other["barangay_id"] == row["data"]["barangay_id"]: score = min(1, score * 1.08)
            if same_dafac or score >= .78:
                matches.append({"beneficiary_id": other["beneficiary_id"], "household_name": other["household_name"], "record_status": other["record_status"], "score": round(1 if same_dafac else score, 2), "same_dafac": same_dafac})
        row["matches"] = sorted(matches, key=lambda item: (-item["score"], item["beneficiary_id"]))[:5]
    return {"rows": rows, "valid": not any(row["errors"] for row in rows), "total_rows": len(rows)}

def active_batch(db, batch_id):
    batch = db.query(ReliefBatch).filter_by(batch_id=batch_id).first()
    if not batch or batch.status != "ACTIVE":
        raise HTTPException(409, "Choose a current active relief batch before importing.")

@router.post("/preview")
def preview(payload: PreviewInput, request: Request, db=Depends(get_db)):
    actor = officer(request)
    active_batch(db, payload.batch_id)
    existing, digest = registry(db)
    plan = plan_csv(payload.csv_content, existing)
    plan.update(import_id=None, batch_id=payload.batch_id)
    if plan["valid"]:
        plan["import_id"] = "CSV-" + str(uuid4())
        db.add(CsvImport(import_id=plan["import_id"], actor_id=actor.id, batch_id=payload.batch_id, registry_hash=digest, plan_json=json.dumps(plan), expires_at=int(time.time()) + 1800))
        db.commit()
    return plan

@router.post("/{import_id}/import")
def import_rows(import_id: str, request: Request, response: Response, db=Depends(get_db)):
    actor = officer(request)
    if db.bind.dialect.name == "sqlite": db.connection().exec_driver_sql("BEGIN IMMEDIATE")
    stage = db.query(CsvImport).filter_by(import_id=import_id, actor_id=actor.id).with_for_update().first()
    if not stage: raise HTTPException(404, "Import preview unavailable to this account.")
    if stage.result_json:
        response.status_code = 200
        return json.loads(stage.result_json)
    if stage.expires_at <= int(time.time()): raise HTTPException(409, "Preview expired. Preview the file again before importing.")
    active_batch(db, stage.batch_id)
    _, digest = registry(db)
    if digest != stage.registry_hash: raise HTTPException(409, "Registry changed since preview. Preview the file again before importing.")
    plan = json.loads(stage.plan_json)
    for row in plan["rows"]:
        data = row["data"]
        match = next(iter(row["matches"]), None)
        db.add(Beneficiary(**{**data, "dafac_id": data["dafac_id"] or None, "contact_number": data["contact_number"] or None}, batch_id=stage.batch_id, record_status="ACTIVE", verification_status="FLAGGED_FOR_REVIEW", review_status="PENDING", duplicate_flag=bool(match), duplicate_confidence=match["score"] if match else 0, duplicate_matched_id=match["beneficiary_id"] if match else None, anomaly_flag=False, review_notes=f"CSV import {import_id} by {actor.id}. Pending DSWD eligibility review; matches are suggestions."))
    db.add(AuditEvent(batch_id=stage.batch_id, event_type="CSV_IMPORTED", description=f"{actor.id} imported {len(plan['rows'])} synthetic households for review", entity_id=import_id))
    result = {"import_id": import_id, "batch_id": stage.batch_id, "imported_by": actor.id, "imported_at": datetime.now(timezone.utc).isoformat(), "beneficiary_ids": [row["data"]["beneficiary_id"] for row in plan["rows"]], "review_status": "PENDING"}
    stage.result_json = json.dumps(result)
    db.commit()
    response.status_code = 201
    return result
