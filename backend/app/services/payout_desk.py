"""Read-only payout desk checks. Confirm remains the transactional authority."""
from decimal import Decimal
import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.auth import require_actor, assert_household_scope
from app.database import get_db
from app.models.entities import Beneficiary, Distribution, ReliefBatch, Allocation, ValidatedList, ListFinalization, PayoutArrangement, ArrangementRevision
from app.money import to_centavos

router = APIRouter(prefix="/api/payout-desk")

@router.get("/{beneficiary_id}")
def inspect_payout(beneficiary_id: str, request: Request, amount: Decimal | None = Query(None, gt=0, max_digits=15, decimal_places=2), db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role not in {"DISBURSING", "DSWD", "AUDITOR"}:
        raise HTTPException(403, "This account cannot inspect the payout desk.")
    ben = db.query(Beneficiary).filter_by(beneficiary_id=beneficiary_id).first()
    assert_household_scope(actor, ben)
    batch = db.query(ReliefBatch).filter_by(batch_id=ben.batch_id).first()
    allocation = db.query(Allocation).filter_by(batch_id=ben.batch_id, barangay_id=ben.barangay_id).first()
    root_id = ben.canonical_beneficiary_id or ben.beneficiary_id
    aliases = db.query(Beneficiary.beneficiary_id).filter(Beneficiary.batch_id == ben.batch_id, (Beneficiary.beneficiary_id == root_id) | (Beneficiary.canonical_beneficiary_id == root_id))
    prior = db.query(Distribution).filter(Distribution.batch_id == ben.batch_id, Distribution.beneficiary_id.in_(aliases)).order_by(Distribution.id).first()
    spent = db.query(func.coalesce(func.sum(Distribution.amount_centavos), 0)).filter(Distribution.allocation_id == allocation.allocation_id).scalar() if allocation else 0
    remaining = allocation.amount_centavos - spent if allocation else 0
    requested = to_centavos(amount) if amount is not None else (batch.standard_grant_centavos if batch else 0)
    checks = []
    def check(code, passed, message):
        checks.append({"code": code, "passed": bool(passed), "message": message})
    check("ACTIVE_HOUSEHOLD", ben.record_status == "ACTIVE", "Household is active." if ben.record_status == "ACTIVE" else "Retained duplicates cannot receive another payout.")
    approved = ben.verification_status == "VERIFIED" and ben.review_status == "APPROVED"
    check("APPROVAL", approved, "DSWD approval recorded." if approved else "DSWD approval is required.")
    check("ACTIVE_BATCH", batch and batch.status == "ACTIVE", "Relief batch is active." if batch and batch.status == "ACTIVE" else "Relief batch is unavailable or inactive.")
    check("PRIOR_PAYOUT", prior is None, "No earlier payout for this household or linked duplicates." if prior is None else "A payout is already recorded for this household or a linked duplicate.")
    check("ALLOCATION", allocation is not None, "Barangay allocation recorded." if allocation else "No allocation for this barangay and batch.")
    check("GRANT_LIMIT", batch and 0 < requested <= batch.max_grant_centavos, "Amount fits the fictional grant limit." if batch and 0 < requested <= batch.max_grant_centavos else "Amount exceeds the fictional grant limit.")
    check("BUDGET", allocation and 0 < requested <= remaining, "Recorded allocation covers this amount." if allocation and 0 < requested <= remaining else "The recorded allocation cannot cover this amount.")
    latest = db.query(ValidatedList).join(ListFinalization, ValidatedList.list_id == ListFinalization.list_id).filter(ValidatedList.batch_id == ben.batch_id, ValidatedList.barangay_id == ben.barangay_id).order_by(ValidatedList.version.desc()).first()
    membership = None
    arrangement = None
    if latest:
        row = next((r for r in json.loads(latest.snapshot_json)["rows"] if r["beneficiary_id"] == ben.beneficiary_id), None)
        membership = {"list_id": latest.list_id, "version": latest.version, "included": bool(row and row["included"])}
        plan = db.query(PayoutArrangement).filter_by(list_id=latest.list_id).first()
        if plan and membership["included"]:
            rev = db.query(ArrangementRevision).filter_by(arrangement_id=plan.arrangement_id).order_by(ArrangementRevision.revision.desc()).first()
            arrangement = {"state": rev.state, "collection_date": rev.collection_date, "time_window": rev.time_window, "site": rev.site, "requirements": json.loads(rev.requirements_json), "responsible_staff": rev.responsible_staff}
    return {"beneficiary_id": ben.beneficiary_id, "household_name": ben.household_name, "barangay_name": ben.barangay_name, "batch_id": ben.batch_id, "amount_centavos": requested, "remaining_centavos": remaining, "standard_grant_centavos": batch.standard_grant_centavos if batch else None, "max_grant_centavos": batch.max_grant_centavos if batch else None, "can_record": actor.role == "DISBURSING" and all(c["passed"] for c in checks), "checks": checks, "existing_distribution_id": prior.distribution_id if prior else None, "list_membership": membership, "arrangement": arrangement, "nonstandard_amount": bool(batch and requested != batch.standard_grant_centavos), "evidence_scope": "Current recorded checks only. Saving rechecks eligibility and budget. Assistance does not authorize payment."}
