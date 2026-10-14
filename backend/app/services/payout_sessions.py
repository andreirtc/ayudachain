"""Payout sessions: a finalized list worked by assigned disbursing staff on a set day."""
import json
from datetime import date, datetime
from typing import Literal
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from app.auth import require_actor, load_accounts
from app.database import get_db
from app.models.entities import AuditEvent, Distribution, ListFinalization, PayoutSession, SessionRevision, ValidatedList
from app.services.payout_arrangements import MANILA, readable, superseded
from app.services.validated_lists import area_scope, digest, now, snapshot, write_lock

router = APIRouter(prefix="/api/payout-sessions")
# action -> (roles, states it may follow, resulting state)
ACTIONS = {
    "OPEN": ({"DSWD", "DISBURSING"}, {"SCHEDULED"}, "OPEN"),
    "CLOSE": ({"DSWD", "DISBURSING"}, {"OPEN"}, "CLOSED"),
    "REOPEN": ({"DSWD"}, {"CLOSED"}, "OPEN"),
    "EDIT": ({"DSWD"}, {"SCHEDULED", "OPEN"}, None),
    "CANCEL": ({"DSWD"}, {"SCHEDULED"}, "CANCELLED"),
}


class Details(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_date: date
    site: str = Field(min_length=1, max_length=200)
    assigned: list[str] = Field(min_length=1, max_length=20)


class Create(Details):
    list_id: str = Field(min_length=1, max_length=64)
    request_id: UUID


class Revise(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    expected_revision: int = Field(ge=1)
    action: Literal["OPEN", "CLOSE", "REOPEN", "EDIT", "CANCEL"]
    reason: str | None = Field(None, max_length=512)
    details: Details | None = None


def clean(details, barangay_id):
    if details.session_date < datetime.now(MANILA).date():
        raise HTTPException(422, "Choose a session date that has not passed.")
    accounts = load_accounts()
    assigned = sorted(set(details.assigned))
    for identity in assigned:
        account = accounts.get(identity)
        if not account or not account["enabled"] or account["role"] != "DISBURSING" or account.get("barangay_id") != barangay_id:
            raise HTTPException(422, "Assign enabled disbursing accounts from this barangay only.")
    return {"session_date": details.session_date.isoformat(), "site": readable(details.site, 200), "assigned": assigned}


def revisions(db, session_id):
    return db.query(SessionRevision).filter_by(session_id=session_id).order_by(SessionRevision.revision).all()


def staff_names():
    try:
        return {identity: account["display_name"] for identity, account in load_accounts().items()}
    except HTTPException:
        return {}


def entry(rev, names, private):
    item = {"revision": rev.revision, "action": rev.action, "state": rev.state, "session_date": rev.session_date, "site": rev.site, "assigned": [{"id": identity, "name": names.get(identity, identity)} for identity in json.loads(rev.assigned_json)], "revised_name": rev.revised_name, "revised_at": rev.revised_at}
    if private:
        item.update(reason=rev.reason, revised_by=rev.revised_by)
    return item


def visible(actor, current):
    if actor.role == "DISBURSING":
        return actor.id in json.loads(current.assigned_json)
    return actor.role in {"DSWD", "AUDITOR", "BARANGAY"}


def view(db, row, actor):
    area_scope(actor, row.barangay_id)
    history = revisions(db, row.session_id)
    if not visible(actor, history[-1]):
        raise HTTPException(404, "Session not available to this account.")
    listed = db.get(ValidatedList, row.list_id)
    frozen = json.loads(listed.snapshot_json)
    included = [r for r in frozen["rows"] if r["included"]]
    payouts = {d.beneficiary_id: d.distribution_id for d in db.query(Distribution).filter(Distribution.batch_id == row.batch_id, Distribution.beneficiary_id.in_([r["beneficiary_id"] for r in included]))}
    names = staff_names()
    result = {"session_id": row.session_id, "list_id": row.list_id, "list_version": listed.version, "batch_id": row.batch_id, "batch_name": frozen["batch_name"], "barangay_id": row.barangay_id, "barangay_name": frozen["barangay_name"], "superseded": superseded(db, listed), "created_at": row.created_at, "current": entry(history[-1], names, actor.role != "BARANGAY"), "history": [entry(rev, names, actor.role != "BARANGAY") for rev in reversed(history)], "progress": {"included": len(included), "recorded": len(payouts), "remaining": len(included) - len(payouts)}}
    if actor.role != "BARANGAY":
        result["roster"] = [{"beneficiary_id": r["beneficiary_id"], "household_name": r["household_name"], "amount_centavos": (r.get("entitlement") or {}).get("amount_centavos", frozen["standard_grant_centavos"]), "category": (r.get("entitlement") or {}).get("category"), "distribution_id": payouts.get(r["beneficiary_id"])} for r in included]
    return result


def add_revision(db, row, actor, number, action, state, values, reason, request_id, fingerprint):
    db.add(SessionRevision(session_id=row.session_id, revision=number, action=action, state=state, session_date=values["session_date"], site=values["site"], assigned_json=json.dumps(values["assigned"]), reason=reason, revised_by=actor.id, revised_name=actor.display_name, revised_at=now(), request_id=str(request_id), request_fingerprint=fingerprint))
    db.add(AuditEvent(batch_id=row.batch_id, event_type="SESSION_" + action, entity_id=row.session_id, description=f"{actor.id} recorded {action.lower()} on {row.barangay_id} payout session (revision {number}, {state.lower()})"))


def session_gate(db, ben, actor):
    """None when no session governs this household; otherwise whether `actor` may record its payout now."""
    latest = db.query(ValidatedList).join(ListFinalization, ValidatedList.list_id == ListFinalization.list_id).filter(ValidatedList.batch_id == ben.batch_id, ValidatedList.barangay_id == ben.barangay_id).order_by(ValidatedList.version.desc()).first()
    if not latest or not any(r["beneficiary_id"] == ben.beneficiary_id and r["included"] for r in json.loads(latest.snapshot_json)["rows"]):
        return None
    sessions = [(row, revisions(db, row.session_id)[-1]) for row in db.query(PayoutSession).filter_by(list_id=latest.list_id)]
    if not sessions:
        return None
    for row, rev in sessions:
        if rev.state == "OPEN" and actor.id in json.loads(rev.assigned_json):
            return {"passed": True, "session_id": row.session_id, "message": f"Session open on {rev.session_date} at {rev.site}."}
    if any(rev.state == "OPEN" for _, rev in sessions):
        message = "Only staff assigned to the open payout session can record this payout."
    elif all(rev.state == "CANCELLED" for _, rev in sessions):
        message = "The payout session for this list was cancelled. Wait for DSWD to schedule a new one."
    elif any(rev.state == "SCHEDULED" for _, rev in sessions):
        message = "The payout session has not been opened yet."
    else:
        message = "The payout session is closed."
    return {"passed": False, "session_id": sessions[0][0].session_id, "message": message}


@router.get("")
def staff_list(request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role == "BENEFICIARY":
        raise HTTPException(403, "Payout sessions are a staff workflow; open your household home.")
    query = db.query(PayoutSession)
    if actor.role in {"BARANGAY", "DISBURSING"}:
        query = query.filter_by(barangay_id=actor.barangay_id)
    result = []
    for row in query.order_by(PayoutSession.created_at.desc()).all():
        try:
            result.append(view(db, row, actor))
        except HTTPException:
            pass
    return result


@router.get("/staff")
def assignable_staff(barangay_id: str, request: Request):
    actor = require_actor(request)
    if actor.role != "DSWD":
        raise HTTPException(403, "Only DSWD assigns session staff.")
    return [{"id": identity, "name": account["display_name"]} for identity, account in sorted(load_accounts().items()) if account["enabled"] and account["role"] == "DISBURSING" and account.get("barangay_id") == barangay_id]


@router.get("/{session_id}")
def detail(session_id: str, request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    row = db.get(PayoutSession, session_id)
    if not row or actor.role == "BENEFICIARY":
        raise HTTPException(404, "Session not available to this account.")
    return view(db, row, actor)


@router.post("")
def create(payload: Create, request: Request, response: Response, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role != "DSWD":
        raise HTTPException(403, "Only DSWD can schedule payout sessions.")
    write_lock(db)
    listed = db.get(ValidatedList, payload.list_id)
    if not listed:
        raise HTTPException(404, "List not available.")
    values = clean(payload, listed.barangay_id)
    fingerprint = digest({"list_id": payload.list_id, **values})
    prior = db.query(PayoutSession).filter_by(created_by=actor.id, request_id=str(payload.request_id)).first()
    if prior:
        if revisions(db, prior.session_id)[0].request_fingerprint != fingerprint:
            raise HTTPException(409, "This retry identity belongs to a different session.")
        return view(db, prior, actor)
    if not db.get(ListFinalization, listed.list_id):
        raise HTTPException(409, "Only a staff-finalized list version can have a payout session.")
    if superseded(db, listed):
        raise HTTPException(409, "A newer finalized version exists. Schedule the session for that version.")
    frozen = json.loads(listed.snapshot_json)
    if digest(snapshot(db, listed.batch_id, listed.barangay_id, frozen["exclusions"])) != listed.revision_hash:
        raise HTTPException(409, "Records changed after finalization. Prepare and finalize a new version first.")
    if any(revisions(db, s.session_id)[-1].state != "CANCELLED" for s in db.query(PayoutSession).filter_by(list_id=listed.list_id)):
        raise HTTPException(409, "This list version already has an active session. Change the existing one.")
    row = PayoutSession(session_id="SES-" + str(uuid4()), list_id=listed.list_id, batch_id=listed.batch_id, barangay_id=listed.barangay_id, created_by=actor.id, created_at=now(), request_id=str(payload.request_id))
    db.add(row)
    db.flush()
    add_revision(db, row, actor, 1, "SCHEDULE", "SCHEDULED", values, "Session scheduled", payload.request_id, fingerprint)
    db.commit()
    response.status_code = 201
    return view(db, row, actor)


@router.post("/{session_id}/revisions")
def revise(session_id: str, payload: Revise, request: Request, response: Response, db: Session = Depends(get_db)):
    actor = require_actor(request)
    roles, allowed_from, state = ACTIONS[payload.action]
    if actor.role not in roles:
        raise HTTPException(403, "This account cannot make that session change.")
    needs_reason = payload.action in {"EDIT", "CANCEL", "REOPEN"}
    reason = readable(payload.reason or "", 512) if needs_reason or (payload.reason or "").strip() else {"OPEN": "Session opened", "CLOSE": "Session closed"}[payload.action]
    if payload.action == "EDIT" and payload.details is None:
        raise HTTPException(422, "Enter the updated session details.")
    write_lock(db)
    row = db.get(PayoutSession, session_id)
    if not row:
        raise HTTPException(404, "Session not available to this account.")
    view(db, row, actor)
    values = clean(payload.details, row.barangay_id) if payload.action == "EDIT" else None
    fingerprint = digest({"session_id": session_id, "expected": payload.expected_revision, "action": payload.action, "reason": reason, "details": values})
    prior = db.query(SessionRevision).filter_by(revised_by=actor.id, request_id=str(payload.request_id)).first()
    if prior:
        if prior.request_fingerprint != fingerprint:
            raise HTTPException(409, "This retry identity belongs to a different change.")
        return view(db, row, actor)
    latest = revisions(db, session_id)[-1]
    if latest.revision != payload.expected_revision:
        raise HTTPException(409, "Someone changed this session after you opened it. Review the latest revision and try again.")
    if latest.state not in allowed_from:
        raise HTTPException(409, f"A {latest.state.lower()} session cannot take that change.")
    if actor.role == "DISBURSING" and actor.id not in json.loads(latest.assigned_json):
        raise HTTPException(403, "Only assigned staff can open or close this session.")
    current = {"session_date": latest.session_date, "site": latest.site, "assigned": json.loads(latest.assigned_json)}
    add_revision(db, row, actor, latest.revision + 1, payload.action, state or latest.state, values or current, reason, payload.request_id, fingerprint)
    db.commit()
    response.status_code = 201
    return view(db, row, actor)
