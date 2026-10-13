"""Retained concerns are review requests, never eligibility or payment decisions."""
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session
from app.auth import require_actor, assert_household_scope
from app.database import get_db
from app.models.entities import HouseholdConcern, ConcernRevision, Beneficiary, Distribution, ReliefBatch, AuditEvent
from app.services.validated_lists import write_lock, now, digest

router = APIRouter(prefix="/api/concerns")

class CreateConcern(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
    beneficiary_id: str | None = Field(None, max_length=64)
    batch_id: str = Field(min_length=1, max_length=64)
    distribution_id: str | None = Field(None, max_length=64)
    category: Literal["DETAILS", "ELIGIBILITY", "PAYOUT", "ARRANGEMENT", "OTHER"]
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def clean_message(cls, value):
        return clean_text(value)

class ReplyConcern(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
    expected_revision: int = Field(ge=1)
    status: Literal["OPEN", "IN_REVIEW", "RESOLVED"]
    household_message: str = Field(min_length=1, max_length=2000)
    staff_reason: str = Field(min_length=1, max_length=2000)

    @field_validator("household_message", "staff_reason")
    @classmethod
    def clean_reply(cls, value):
        return clean_text(value)

def clean_text(value):
    value = value.strip()
    if not value or any(ord(c) < 32 and c not in "\n\r\t" for c in value) or "\x7f" in value:
        raise ValueError("Enter a readable message.")
    return value

def scoped(query, actor):
    if actor.role == "BENEFICIARY":
        return query.filter(HouseholdConcern.beneficiary_id == actor.beneficiary_id)
    if actor.role in {"BARANGAY", "DISBURSING"}:
        return query.filter(HouseholdConcern.barangay_id == actor.barangay_id)
    return query

def available(db, concern_id, actor):
    row = scoped(db.query(HouseholdConcern), actor).filter(HouseholdConcern.concern_id == concern_id).first()
    if not row:
        raise HTTPException(404, "Concern not available to this account.")
    return row

def view(db, row, actor):
    history = []
    for rev in db.query(ConcernRevision).filter_by(concern_id=row.concern_id).order_by(ConcernRevision.revision.desc()):
        item = {"revision": rev.revision, "status": rev.status, "household_message": rev.household_message, "revised_at": rev.revised_at, "revised_name": rev.revised_name}
        if actor.role in {"DSWD", "AUDITOR"}:
            item.update(staff_reason=rev.staff_reason, revised_by=rev.revised_by)
        history.append(item)
    result = {key: getattr(row, key) for key in ("concern_id", "beneficiary_id", "batch_id", "distribution_id", "category", "message", "source", "created_at")}
    result.update(current=history[0], history=history)
    if actor.role != "BENEFICIARY":
        result.update(created_by=row.created_by, created_name=row.created_name, barangay_id=row.barangay_id)
    return result

@router.get("")
def concerns(request: Request, beneficiary_id: str | None = None, db: Session = Depends(get_db)):
    actor = require_actor(request)
    query = scoped(db.query(HouseholdConcern), actor)
    if beneficiary_id:
        query = query.filter(HouseholdConcern.beneficiary_id == beneficiary_id)
    return [view(db, row, actor) for row in query.order_by(HouseholdConcern.created_at.desc())]

@router.get("/{concern_id}")
def detail(concern_id: str, request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    return view(db, available(db, concern_id, actor), actor)

@router.post("", status_code=201)
def create(payload: CreateConcern, request: Request, response: Response, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role not in {"BENEFICIARY", "BARANGAY", "DISBURSING", "DSWD"}:
        raise HTTPException(403, "This account cannot submit a concern.")
    beneficiary_id = payload.beneficiary_id
    if actor.role == "BENEFICIARY":
        if beneficiary_id and beneficiary_id != actor.beneficiary_id:
            raise HTTPException(404, "Household record not available to this account.")
        beneficiary_id = actor.beneficiary_id
    if not beneficiary_id:
        raise HTTPException(422, "Select the household needing assistance.")
    write_lock(db)
    fingerprint = digest(payload.model_dump() | {"beneficiary_id": beneficiary_id})
    existing = db.query(HouseholdConcern).filter_by(created_by=actor.id, request_id=payload.request_id).first()
    if existing:
        if existing.request_fingerprint != fingerprint:
            raise HTTPException(409, "This request identity was used for different concern details.")
        response.status_code = 200
        return view(db, available(db, existing.concern_id, actor), actor)
    ben = db.query(Beneficiary).filter_by(beneficiary_id=beneficiary_id).first()
    if ben:
        assert_household_scope(actor, ben)
        if payload.batch_id != ben.batch_id:
            raise HTTPException(422, "Concern batch must match the household record.")
    elif actor.role != "BENEFICIARY":
        raise HTTPException(404, "Register the missing synthetic household before staff-assisted intake.")
    if not db.query(ReliefBatch).filter_by(batch_id=payload.batch_id).first():
        raise HTTPException(404, "Relief batch not found.")
    if payload.distribution_id:
        payout = db.query(Distribution).filter_by(distribution_id=payload.distribution_id, beneficiary_id=beneficiary_id, batch_id=payload.batch_id).first()
        if not payout or actor.role == "BARANGAY":
            raise HTTPException(404, "Payout not available to this account.")
    row = HouseholdConcern(concern_id="CON-"+str(uuid4()), beneficiary_id=beneficiary_id, batch_id=payload.batch_id, barangay_id=ben.barangay_id if ben else None, distribution_id=payload.distribution_id, category=payload.category, message=payload.message, source="HOUSEHOLD" if actor.role=="BENEFICIARY" else "STAFF_ASSISTED", created_by=actor.id, created_name=actor.display_name, created_at=now(), request_id=payload.request_id, request_fingerprint=fingerprint)
    db.add(row)
    db.add(ConcernRevision(concern_id=row.concern_id, revision=1, status="OPEN", household_message="Your concern was received. Staff will review it.", staff_reason="", revised_by=actor.id, revised_name=actor.display_name, revised_at=row.created_at, request_id="intake-"+str(uuid4()), request_fingerprint=fingerprint))
    db.add(AuditEvent(batch_id=row.batch_id, event_type="CONCERN_SUBMITTED", entity_id=row.concern_id, description=f"Synthetic concern submitted by {actor.id}; source {row.source}."))
    db.commit()
    return view(db, row, actor)

@router.post("/{concern_id}/revisions", status_code=201)
def reply(concern_id: str, payload: ReplyConcern, request: Request, response: Response, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role != "DSWD":
        raise HTTPException(403, "Only DSWD can reply to and change a concern's review status.")
    write_lock(db)
    row = available(db, concern_id, actor)
    fingerprint = digest(payload.model_dump() | {"concern_id": concern_id})
    existing = db.query(ConcernRevision).filter_by(revised_by=actor.id, request_id=payload.request_id).first()
    if existing:
        if existing.request_fingerprint != fingerprint:
            raise HTTPException(409, "This request identity was used for a different reply.")
        response.status_code = 200
        return view(db, row, actor)
    latest = db.query(ConcernRevision).filter_by(concern_id=concern_id).order_by(ConcernRevision.revision.desc()).first()
    if latest.revision != payload.expected_revision:
        raise HTTPException(409, "This concern changed. Refresh it before replying.")
    db.add(ConcernRevision(concern_id=concern_id, revision=latest.revision+1, status=payload.status, household_message=payload.household_message, staff_reason=payload.staff_reason, revised_by=actor.id, revised_name=actor.display_name, revised_at=now(), request_id=payload.request_id, request_fingerprint=fingerprint))
    db.add(AuditEvent(batch_id=row.batch_id, event_type="CONCERN_REPLIED", entity_id=row.concern_id, description=f"Concern review status {payload.status}; reply by {actor.id}."))
    db.commit()
    return view(db, row, actor)
