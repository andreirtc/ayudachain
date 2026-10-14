"""Versioned per-batch amount rules and the entitlements they produce."""
import json
from decimal import Decimal
from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from app.auth import require_actor
from app.database import get_db
from app.models.entities import AmountRuleVersion, AuditEvent, Beneficiary, DamageClaim, Distribution, ReliefBatch
from app.money import to_centavos, format_peso
from app.services.entitlements import CATEGORIES, current_rules, entitlement, latest_revision
from app.services.validated_lists import digest, now, write_lock

router = APIRouter(prefix="/api")


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Literal["TOTALLY_DAMAGED", "PARTIALLY_DAMAGED"]
    days: int | None = Field(None, gt=0, le=365)
    amount: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)


class SaveRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    batch_id: str = Field(min_length=1, max_length=64)
    request_id: UUID
    expected_version: int = Field(ge=0)
    mode: Literal["FIXED", "WAGE_FORMULA"]
    daily_wage: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)
    rules: list[Rule] = Field(min_length=1, max_length=len(CATEGORIES))
    reason: str = Field(min_length=1, max_length=512)


def version_view(row):
    if not row:
        return None
    return {"version": row.version, "mode": row.mode, "daily_wage_centavos": row.daily_wage_centavos, "rules": json.loads(row.rules_json), "reason": row.reason, "created_by": row.created_by, "created_name": row.created_name, "created_at": row.created_at}


def priced(payload, batch):
    if {rule.category for rule in payload.rules} != set(CATEGORIES) or len(payload.rules) != len(CATEGORIES):
        raise HTTPException(422, "Enter one rule for every damage category.")
    wage = to_centavos(payload.daily_wage) if payload.daily_wage is not None else None
    if payload.mode == "WAGE_FORMULA" and wage is None:
        raise HTTPException(422, "Enter the daily wage used by the formula.")
    rules = {}
    for rule in payload.rules:
        if payload.mode == "WAGE_FORMULA":
            if rule.days is None: raise HTTPException(422, "Enter the number of days for every category.")
            amount = wage * rule.days
        else:
            if rule.amount is None: raise HTTPException(422, "Enter a fixed amount for every category.")
            amount = to_centavos(rule.amount)
        if amount > batch.max_grant_centavos:
            raise HTTPException(422, f"{CATEGORIES[rule.category]} would receive {format_peso(amount)}, above the {format_peso(batch.max_grant_centavos)} maximum grant.")
        rules[rule.category] = {"days": rule.days if payload.mode == "WAGE_FORMULA" else None, "amount_centavos": amount}
    return (wage if payload.mode == "WAGE_FORMULA" else None), rules


@router.get("/amount-rules")
def rules(batch_id: str, request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role not in {"DSWD", "AUDITOR"}:
        raise HTTPException(403, "Amount rules are a DSWD and Auditor workflow.")
    batch = db.query(ReliefBatch).filter_by(batch_id=batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found.")
    history = db.query(AmountRuleVersion).filter_by(batch_id=batch_id).order_by(AmountRuleVersion.version.desc()).all()
    current = history[0] if history else None
    paid = {d.beneficiary_id for d in db.query(Distribution).filter_by(batch_id=batch_id)}
    calculated = []
    for claim in db.query(DamageClaim).filter_by(batch_id=batch_id).order_by(DamageClaim.created_at):
        ben = db.query(Beneficiary).filter_by(beneficiary_id=claim.beneficiary_id).first()
        result = entitlement(db, ben, batch, current)
        calculated.append({"claim_id": claim.claim_id, "beneficiary_id": ben.beneficiary_id, "household_name": ben.household_name, "barangay_name": ben.barangay_name, "claim_status": result["claim_status"], "category": latest_revision(db, claim.claim_id).category, "basis": result["basis"], "amount_centavos": result["amount_centavos"], "blocked": result["blocked"], "payout_recorded": ben.beneficiary_id in paid})
    return {"batch_id": batch.batch_id, "batch_name": batch.calamity_name, "standard_grant_centavos": batch.standard_grant_centavos, "max_grant_centavos": batch.max_grant_centavos, "categories": CATEGORIES, "current": version_view(current), "history": [version_view(row) for row in history], "entitlements": calculated}


@router.post("/amount-rules")
def save(payload: SaveRules, request: Request, response: Response, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role != "DSWD":
        raise HTTPException(403, "Only DSWD can change amount rules.")
    reason = payload.reason.strip()
    if not reason or any(ord(c) < 32 for c in reason):
        raise HTTPException(422, "Enter a readable reason for this rule version.")
    batch = db.query(ReliefBatch).filter_by(batch_id=payload.batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found.")
    wage, values = priced(payload, batch)
    fingerprint = digest({"batch_id": payload.batch_id, "expected": payload.expected_version, "mode": payload.mode, "wage": wage, "rules": values, "reason": reason})
    write_lock(db)
    prior = db.query(AmountRuleVersion).filter_by(created_by=actor.id, request_id=str(payload.request_id)).first()
    if prior:
        if prior.request_fingerprint != fingerprint:
            raise HTTPException(409, "This retry identity belongs to different amount rules.")
        return rules(payload.batch_id, request, db)
    latest = current_rules(db, payload.batch_id)
    if (latest.version if latest else 0) != payload.expected_version:
        raise HTTPException(409, "Someone saved newer amount rules. Review the current version and try again.")
    version = payload.expected_version + 1
    db.add(AmountRuleVersion(batch_id=payload.batch_id, version=version, mode=payload.mode, daily_wage_centavos=wage, rules_json=json.dumps(values, sort_keys=True), reason=reason, created_by=actor.id, created_name=actor.display_name, created_at=now(), request_id=str(payload.request_id), request_fingerprint=fingerprint))
    db.add(AuditEvent(batch_id=payload.batch_id, event_type="AMOUNT_RULES_SAVED", entity_id=f"{payload.batch_id}:v{version}", description=f"{actor.id} saved amount rules version {version} ({payload.mode.lower().replace('_', ' ')})"))
    db.commit()
    response.status_code = 201
    return rules(payload.batch_id, request, db)


@router.get("/entitlements/mine")
def mine(request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role != "BENEFICIARY":
        raise HTTPException(403, "Calculated household amounts belong to linked household accounts.")
    ben = db.query(Beneficiary).filter_by(beneficiary_id=actor.beneficiary_id).first()
    if not ben:
        raise HTTPException(404, "Household record not available to this account.")
    batch = db.query(ReliefBatch).filter_by(batch_id=ben.batch_id).first()
    result = entitlement(db, ben, batch)
    return {key: result[key] for key in ("basis", "category", "amount_centavos", "claim_status", "blocked")}
