"""An account's synthetic acknowledgement; never evidence of physical delivery."""
from datetime import datetime, timezone
from uuid import uuid4
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from app.database import get_db
from app.models.entities import Distribution, Beneficiary, AuditEvent, RecipientAcknowledgement
from app.auth import require_actor, assert_household_scope

class Consent(BaseModel):
    acknowledge: Literal[True]
    model_config = {"extra": "forbid"}

class AcknowledgementResponse(BaseModel):
    distribution_id: str
    acknowledgement_id: str
    beneficiary_id: str
    batch_id: str
    account_id: str
    account_display_name: str
    amount_centavos: int
    receipt_hash: str
    acknowledged_at: str
    model_config = {"from_attributes": True}

router = APIRouter(prefix="/api/distributions")

def scoped_record(db, request, distribution_id):
    actor = require_actor(request)
    if actor.role == "BARANGAY": raise HTTPException(403, "Named payouts are outside your role.")
    dist = db.query(Distribution).filter_by(distribution_id=distribution_id).first()
    ben = db.query(Beneficiary).filter_by(beneficiary_id=dist.beneficiary_id).first() if dist else None
    assert_household_scope(actor, ben)
    return actor, dist

@router.get("/{distribution_id}/acknowledgement", response_model=AcknowledgementResponse | None)
def read_ack(distribution_id: str, request: Request, db=Depends(get_db)):
    scoped_record(db, request, distribution_id)
    return db.get(RecipientAcknowledgement, distribution_id)

@router.post("/{distribution_id}/acknowledgement", response_model=AcknowledgementResponse)
def acknowledge(distribution_id: str, consent: Consent, request: Request, response: Response, db=Depends(get_db)):
    if require_actor(request).role != "BENEFICIARY": raise HTTPException(403, "Only the linked Beneficiary account can acknowledge its demo payout.")
    if db.bind.dialect.name == "sqlite": db.connection().exec_driver_sql("BEGIN IMMEDIATE")
    actor, dist = scoped_record(db, request, distribution_id)
    previous = db.get(RecipientAcknowledgement, distribution_id)
    if previous: return previous
    if dist.status != "CONFIRMED": raise HTTPException(409, "This payout is not currently recorded. Earlier acknowledgements remain retained.")
    saved = RecipientAcknowledgement(distribution_id=dist.distribution_id, acknowledgement_id="ACK-" + str(uuid4()), beneficiary_id=dist.beneficiary_id, batch_id=dist.batch_id, account_id=actor.id, account_display_name=actor.display_name, amount_centavos=dist.amount_centavos, receipt_hash=dist.receipt_hash, acknowledged_at=datetime.now(timezone.utc).isoformat())
    db.add(saved)
    db.add(AuditEvent(batch_id=dist.batch_id, event_type="RECIPIENT_ACKNOWLEDGED", description=f"Synthetic account {actor.id} acknowledged recorded payout {dist.distribution_id}", entity_id=dist.distribution_id))
    db.commit(); db.refresh(saved)
    response.status_code = 201
    return saved
