"""Damage claims: household or staff-assisted submission, barangay endorsement, DSWD decision."""
from typing import Literal
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from app.auth import require_actor, assert_household_scope
from app.database import get_db
from app.models.entities import AuditEvent, Beneficiary, ClaimRevision, DamageClaim, Distribution, ReliefBatch
from app.services.entitlements import CATEGORIES, entitlement
from app.services.validated_lists import digest, now, write_lock

router = APIRouter(prefix="/api/claims")
Category = Literal["TOTALLY_DAMAGED", "PARTIALLY_DAMAGED"]
DECIDABLE = {"ENDORSED", "NOT_ENDORSED", "APPROVED", "DECLINED"}
# action -> (roles, statuses it may follow, resulting status)
ACTIONS = {
    "ENDORSE": ({"BARANGAY"}, {"SUBMITTED"}, "ENDORSED"),
    "NOT_ENDORSE": ({"BARANGAY"}, {"SUBMITTED"}, "NOT_ENDORSED"),
    "REQUEST_INFO": ({"BARANGAY", "DSWD"}, {"SUBMITTED", "ENDORSED", "NOT_ENDORSED"}, "NEEDS_INFO"),
    "RESPOND": ({"BENEFICIARY", "BARANGAY"}, {"NEEDS_INFO"}, "SUBMITTED"),
    "APPROVE": ({"DSWD"}, DECIDABLE, "APPROVED"),
    "DECLINE": ({"DSWD"}, DECIDABLE, "DECLINED"),
}
HOUSEHOLD_NOTICE = {
    "SUBMITTED": "Your damage claim was received. Your barangay will review it first.",
    "ENDORSED": "Your barangay reviewed your claim. DSWD will decide next.",
    "NOT_ENDORSED": "Your barangay reviewed your claim. DSWD will decide next.",
}


def readable(value, limit, message):
    value = (value or "").strip()
    if not value or len(value) > limit or any(ord(c) < 32 and c not in "\n\r\t" for c in value) or "\x7f" in value:
        raise HTTPException(422, message)
    return value


class Submit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    beneficiary_id: str | None = Field(None, max_length=64)
    category: Category
    description: str = Field(min_length=1, max_length=2000)


class Revise(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    expected_revision: int = Field(ge=1)
    action: Literal["ENDORSE", "NOT_ENDORSE", "REQUEST_INFO", "RESPOND", "APPROVE", "DECLINE"]
    category: Category | None = None
    description: str | None = Field(None, max_length=2000)
    household_message: str | None = Field(None, max_length=2000)
    staff_reason: str | None = Field(None, max_length=2000)


def scoped(query, actor):
    if actor.role == "BENEFICIARY":
        return query.filter(DamageClaim.beneficiary_id == actor.beneficiary_id)
    if actor.role == "BARANGAY":
        return query.filter(DamageClaim.barangay_id == actor.barangay_id)
    if actor.role in {"DSWD", "AUDITOR"}:
        return query
    raise HTTPException(403, "Damage claims are not part of this account's workflow.")


def available(db, claim_id, actor):
    row = scoped(db.query(DamageClaim), actor).filter(DamageClaim.claim_id == claim_id).first()
    if not row:
        raise HTTPException(404, "Claim not available to this account.")
    return row


def view(db, row, actor):
    staff = actor.role != "BENEFICIARY"
    history = []
    for rev in db.query(ClaimRevision).filter_by(claim_id=row.claim_id).order_by(ClaimRevision.revision.desc()):
        item = {"revision": rev.revision, "action": rev.action, "status": rev.status, "category": rev.category, "category_label": CATEGORIES[rev.category], "description": rev.description, "household_message": rev.household_message, "revised_name": rev.revised_name, "revised_at": rev.revised_at}
        if staff:
            item.update(staff_reason=rev.staff_reason, revised_by=rev.revised_by)
        history.append(item)
    ben = db.query(Beneficiary).filter_by(beneficiary_id=row.beneficiary_id).first()
    batch = db.query(ReliefBatch).filter_by(batch_id=row.batch_id).first()
    amount = entitlement(db, ben, batch)
    result = {"claim_id": row.claim_id, "beneficiary_id": row.beneficiary_id, "household_name": ben.household_name, "barangay_id": row.barangay_id, "barangay_name": ben.barangay_name, "batch_id": row.batch_id, "batch_name": batch.calamity_name, "source": row.source, "created_at": row.created_at, "current": history[0], "history": history, "entitlement": {key: amount[key] for key in ("basis", "amount_centavos", "rule_version", "blocked")}, "payout_recorded": paid(db, row) is not None}
    if staff:
        result.update(created_by=row.created_by, created_name=row.created_name)
    return result


def paid(db, row):
    return db.query(Distribution).filter_by(beneficiary_id=row.beneficiary_id, batch_id=row.batch_id).first()


def add_revision(db, row, actor, number, action, status, category, description, household_message, staff_reason, request_id, fingerprint):
    db.add(ClaimRevision(claim_id=row.claim_id, revision=number, action=action, status=status, category=category, description=description, household_message=household_message, staff_reason=staff_reason, revised_by=actor.id, revised_name=actor.display_name, revised_at=now(), request_id=str(request_id), request_fingerprint=fingerprint))
    db.add(AuditEvent(batch_id=row.batch_id, event_type="CLAIM_" + action, entity_id=row.claim_id, description=f"{actor.id} recorded {action.lower().replace('_', ' ')} on {row.beneficiary_id} damage claim ({status.lower().replace('_', ' ')}, {CATEGORIES[category].lower()})"))


@router.get("")
def claims(request: Request, status: str | None = None, beneficiary_id: str | None = None, db: Session = Depends(get_db)):
    actor = require_actor(request)
    query = scoped(db.query(DamageClaim), actor)
    if beneficiary_id:
        query = query.filter(DamageClaim.beneficiary_id == beneficiary_id)
    rows = [view(db, row, actor) for row in query.order_by(DamageClaim.created_at.desc())]
    return [row for row in rows if not status or row["current"]["status"] == status]


@router.get("/{claim_id}")
def detail(claim_id: str, request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    return view(db, available(db, claim_id, actor), actor)


@router.post("")
def submit(payload: Submit, request: Request, response: Response, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role not in {"BENEFICIARY", "BARANGAY"}:
        raise HTTPException(403, "Claims are submitted by the household or with barangay assistance.")
    beneficiary_id = payload.beneficiary_id
    if actor.role == "BENEFICIARY":
        if beneficiary_id and beneficiary_id != actor.beneficiary_id:
            raise HTTPException(404, "Household record not available to this account.")
        beneficiary_id = actor.beneficiary_id
    if not beneficiary_id:
        raise HTTPException(422, "Select the household making the claim.")
    description = readable(payload.description, 2000, "Describe the damage in readable text.")
    fingerprint = digest({"beneficiary_id": beneficiary_id, "category": payload.category, "description": description})
    write_lock(db)
    prior = db.query(DamageClaim).filter_by(created_by=actor.id, request_id=str(payload.request_id)).first()
    if prior:
        if prior.request_fingerprint != fingerprint:
            raise HTTPException(409, "This retry identity belongs to a different claim.")
        response.status_code = 200
        return view(db, prior, actor)
    ben = db.query(Beneficiary).filter_by(beneficiary_id=beneficiary_id).first()
    assert_household_scope(actor, ben)
    if ben.record_status != "ACTIVE":
        raise HTTPException(409, "Retained duplicate records cannot start a new claim. Use the linked household.")
    batch = db.query(ReliefBatch).filter_by(batch_id=ben.batch_id).first()
    if not batch or batch.status != "ACTIVE":
        raise HTTPException(409, "Claims need an active relief batch.")
    if db.query(DamageClaim).filter_by(beneficiary_id=ben.beneficiary_id, batch_id=ben.batch_id).first():
        raise HTTPException(409, "A damage claim already exists for this household. Follow up the existing claim.")
    if db.query(Distribution).filter_by(beneficiary_id=ben.beneficiary_id, batch_id=ben.batch_id).first():
        raise HTTPException(409, "A payout is already recorded for this household in this batch.")
    row = DamageClaim(claim_id="CLM-" + str(uuid4()), beneficiary_id=ben.beneficiary_id, batch_id=ben.batch_id, barangay_id=ben.barangay_id, source="HOUSEHOLD" if actor.role == "BENEFICIARY" else "STAFF_ASSISTED", created_by=actor.id, created_name=actor.display_name, created_at=now(), request_id=str(payload.request_id), request_fingerprint=fingerprint)
    db.add(row)
    add_revision(db, row, actor, 1, "SUBMIT", "SUBMITTED", payload.category, description, HOUSEHOLD_NOTICE["SUBMITTED"], "", "submit-" + str(payload.request_id), fingerprint)
    db.commit()
    response.status_code = 201
    return view(db, row, actor)


@router.post("/{claim_id}/revisions")
def revise(claim_id: str, payload: Revise, request: Request, response: Response, db: Session = Depends(get_db)):
    actor = require_actor(request)
    roles, allowed_from, status = ACTIONS[payload.action]
    if actor.role not in roles:
        raise HTTPException(403, "This account cannot record that claim step.")
    fingerprint = digest(payload.model_dump(mode="json") | {"claim_id": claim_id})
    write_lock(db)
    row = available(db, claim_id, actor)
    prior = db.query(ClaimRevision).filter_by(revised_by=actor.id, request_id=str(payload.request_id)).first()
    if prior:
        if prior.request_fingerprint != fingerprint:
            raise HTTPException(409, "This retry identity belongs to a different claim step.")
        response.status_code = 200
        return view(db, row, actor)
    latest = db.query(ClaimRevision).filter_by(claim_id=claim_id).order_by(ClaimRevision.revision.desc()).first()
    if latest.revision != payload.expected_revision:
        raise HTTPException(409, "This claim changed after you opened it. Review the latest step and try again.")
    if latest.status not in allowed_from:
        raise HTTPException(409, f"A claim that is {latest.status.lower().replace('_', ' ')} cannot take that step.")
    if paid(db, row):
        raise HTTPException(409, "A payout is already recorded for this household. The claim is now locked.")
    category, description = latest.category, latest.description
    household_message = HOUSEHOLD_NOTICE.get(status, latest.household_message)
    staff_reason = ""
    if payload.action == "RESPOND":
        description = readable(payload.description, 2000, "Add the requested information in readable text.")
        category = payload.category or category
        household_message = "Your added information was received. Your barangay will review the claim again."
    else:
        staff_reason = readable(payload.staff_reason, 2000, "Enter a staff-only reason for this step.")
    if payload.action == "REQUEST_INFO":
        household_message = readable(payload.household_message, 2000, "Write the question the household should answer.")
    if payload.action == "APPROVE":
        category = payload.category or category
        household_message = (payload.household_message or "").strip() or f"Your claim was approved as {CATEGORIES[category].lower()}."
    if payload.action == "DECLINE":
        household_message = readable(payload.household_message, 2000, "Tell the household why the claim was declined.")
    add_revision(db, row, actor, latest.revision + 1, payload.action, status, category, description, household_message, staff_reason, payload.request_id, fingerprint)
    db.commit()
    response.status_code = 201
    return view(db, row, actor)
