"""Scoped collection instructions for a finalized list; never a payout authorization."""
import json
from datetime import date, datetime, timedelta, timezone
from typing import Literal
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from app.auth import require_actor
from app.database import get_db
from app.models.entities import PayoutArrangement, ArrangementRevision, ValidatedList, ListFinalization, AuditEvent
from app.services.validated_lists import area_scope, digest, now, snapshot, write_lock

router = APIRouter(prefix="/api/arrangements")
MANILA = timezone(timedelta(hours=8))

def readable(value, limit):
    value = value.strip()
    if not value or len(value) > limit or any(ord(c) < 32 for c in value): raise HTTPException(422, "Enter readable arrangement details without control characters.")
    return value

class Details(BaseModel):
    model_config = ConfigDict(extra="forbid")
    collection_date: date
    time_window: str = Field(min_length=1, max_length=64)
    site: str = Field(min_length=1, max_length=200)
    requirements: list[str] = Field(min_length=1, max_length=10)
    responsible_staff: str = Field(min_length=1, max_length=128)

class Create(Details):
    list_id: str = Field(min_length=1, max_length=64)
    request_id: UUID

class Revise(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    expected_revision: int = Field(ge=1)
    action: Literal["EDIT", "CANCEL"]
    reason: str = Field(min_length=1, max_length=512)
    details: Details | None = None

def clean(details):
    if details.collection_date < datetime.now(MANILA).date(): raise HTTPException(422, "Choose a collection date that has not passed.")
    return {"collection_date": details.collection_date.isoformat(), "time_window": readable(details.time_window, 64), "site": readable(details.site, 200), "requirements": [readable(item, 120) for item in details.requirements], "responsible_staff": readable(details.responsible_staff, 128)}

def revisions(db, arrangement_id):
    return db.query(ArrangementRevision).filter_by(arrangement_id=arrangement_id).order_by(ArrangementRevision.revision).all()

def entry(rev, private):
    item = {"revision": rev.revision, "state": rev.state, "collection_date": rev.collection_date, "time_window": rev.time_window, "site": rev.site, "requirements": json.loads(rev.requirements_json), "responsible_staff": rev.responsible_staff, "revised_at": rev.revised_at}
    if private: item.update(reason=rev.reason, revised_by=rev.revised_by)
    return item

def superseded(db, listed):
    newer = db.query(ValidatedList.list_id).filter(ValidatedList.batch_id == listed.batch_id, ValidatedList.barangay_id == listed.barangay_id, ValidatedList.version > listed.version).all()
    return any(db.get(ListFinalization, list_id) for (list_id,) in newer)

def view(db, row, actor):
    area_scope(actor, row.barangay_id)
    listed = db.get(ValidatedList, row.list_id)
    history = revisions(db, row.arrangement_id)
    frozen = json.loads(listed.snapshot_json)
    return {"arrangement_id": row.arrangement_id, "list_id": row.list_id, "list_version": listed.version, "batch_id": row.batch_id, "batch_name": frozen["batch_name"], "barangay_id": row.barangay_id, "barangay_name": frozen["barangay_name"], "included_households": sum(r["included"] for r in frozen["rows"]), "created_by": row.created_by, "created_at": row.created_at, "superseded": superseded(db, listed), "current": entry(history[-1], True), "history": [entry(rev, True) for rev in reversed(history)]}

def add_revision(db, row, actor, number, state, values, reason, request_id, fingerprint):
    db.add(ArrangementRevision(arrangement_id=row.arrangement_id, revision=number, state=state, collection_date=values["collection_date"], time_window=values["time_window"], site=values["site"], requirements_json=json.dumps(values["requirements"], ensure_ascii=False), responsible_staff=values["responsible_staff"], reason=reason, revised_by=actor.id, revised_at=now(), request_id=str(request_id), request_fingerprint=fingerprint))
    event = "ARRANGEMENT_PUBLISHED" if number == 1 else "ARRANGEMENT_CANCELLED" if state == "CANCELLED" else "ARRANGEMENT_REVISED"
    db.add(AuditEvent(batch_id=row.batch_id, event_type=event, entity_id=row.arrangement_id, description=f"{actor.id} saved {row.barangay_id} arrangement revision {number} ({state.lower()})"))

@router.get("")
def staff_list(request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    query = db.query(PayoutArrangement)
    if actor.role in {"BARANGAY", "DISBURSING"}: query = query.filter_by(barangay_id=actor.barangay_id)
    return [view(db, row, actor) for row in query.order_by(PayoutArrangement.created_at.desc()).all()]

@router.get("/mine")
def mine(request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role != "BENEFICIARY": raise HTTPException(403, "Household instructions belong to linked household accounts.")
    result = []
    for row in db.query(PayoutArrangement).order_by(PayoutArrangement.created_at.desc()).all():
        listed = db.get(ValidatedList, row.list_id)
        if superseded(db, listed): continue
        frozen = json.loads(listed.snapshot_json)
        if not any(r["beneficiary_id"] == actor.beneficiary_id and r["included"] for r in frozen["rows"]): continue
        history = revisions(db, row.arrangement_id)
        result.append({"arrangement_id": row.arrangement_id, "batch_name": frozen["batch_name"], "barangay_name": frozen["barangay_name"], "current": entry(history[-1], False), "updated": len(history) > 1})
    return result

@router.get("/{arrangement_id}")
def detail(arrangement_id: str, request: Request, db: Session = Depends(get_db)):
    row = db.get(PayoutArrangement, arrangement_id)
    if not row: raise HTTPException(404, "Arrangement not available.")
    return view(db, row, require_actor(request))

@router.post("")
def create(payload: Create, request: Request, response: Response, db: Session = Depends(get_db)):
    actor = require_actor(request)
    values = clean(payload)
    fingerprint = digest({"list_id": payload.list_id, **values})
    write_lock(db)
    prior = db.query(PayoutArrangement).filter_by(created_by=actor.id, request_id=str(payload.request_id)).first()
    if prior:
        if revisions(db, prior.arrangement_id)[0].request_fingerprint != fingerprint: raise HTTPException(409, "This retry identity belongs to a different arrangement.")
        return view(db, prior, actor)
    listed = db.get(ValidatedList, payload.list_id)
    if not listed: raise HTTPException(404, "List not available.")
    area_scope(actor, listed.barangay_id)
    if not db.get(ListFinalization, listed.list_id): raise HTTPException(409, "Only a staff-finalized list version can receive arrangements.")
    if superseded(db, listed): raise HTTPException(409, "A newer finalized version exists. Arrange collection for that version.")
    frozen = json.loads(listed.snapshot_json)
    if digest(snapshot(db, listed.batch_id, listed.barangay_id, frozen["exclusions"])) != listed.revision_hash: raise HTTPException(409, "Records changed after finalization. Prepare and finalize a new version first.")
    if db.query(PayoutArrangement).filter_by(list_id=listed.list_id).first(): raise HTTPException(409, "This list version already has an arrangement. Edit the existing one.")
    row = PayoutArrangement(arrangement_id="ARR-" + str(uuid4()), list_id=listed.list_id, batch_id=listed.batch_id, barangay_id=listed.barangay_id, created_by=actor.id, created_at=now(), request_id=str(payload.request_id))
    db.add(row); db.flush()
    add_revision(db, row, actor, 1, "SCHEDULED", values, "Initial arrangement", payload.request_id, fingerprint)
    db.commit(); response.status_code = 201
    return view(db, row, actor)

@router.post("/{arrangement_id}/revisions")
def revise(arrangement_id: str, payload: Revise, request: Request, response: Response, db: Session = Depends(get_db)):
    actor = require_actor(request)
    reason = readable(payload.reason, 512)
    if payload.action == "EDIT" and payload.details is None: raise HTTPException(422, "Enter the updated arrangement details.")
    values = clean(payload.details) if payload.action == "EDIT" else None
    fingerprint = digest({"arrangement_id": arrangement_id, "expected": payload.expected_revision, "action": payload.action, "reason": reason, "details": values})
    write_lock(db)
    row = db.get(PayoutArrangement, arrangement_id)
    if not row: raise HTTPException(404, "Arrangement not available.")
    area_scope(actor, row.barangay_id)
    prior = db.query(ArrangementRevision).filter_by(revised_by=actor.id, request_id=str(payload.request_id)).first()
    if prior:
        if prior.request_fingerprint != fingerprint: raise HTTPException(409, "This retry identity belongs to a different change.")
        return view(db, row, actor)
    history = revisions(db, arrangement_id); latest = history[-1]
    if latest.revision != payload.expected_revision: raise HTTPException(409, "Someone changed this arrangement after you opened it. Review the latest revision and try again.")
    if latest.state == "CANCELLED": raise HTTPException(409, "A cancelled arrangement stays retained. Create instructions on a new finalized list version.")
    if values is None: values = entry(latest, False)
    add_revision(db, row, actor, latest.revision + 1, "CANCELLED" if payload.action == "CANCEL" else "SCHEDULED", values, reason, payload.request_id, fingerprint)
    db.commit(); response.status_code = 201
    return view(db, row, actor)
