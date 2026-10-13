"""Private read-only audit facts; recorded lifecycle is separate from current proof."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.auth import require_actor
from app.database import get_db
from app.models.entities import ReliefBatch, Allocation, Beneficiary, Distribution, AuditEvent, PayoutAnchorJob, HouseholdConcern, ConcernRevision

router = APIRouter(prefix="/api/audit-workspace")

@router.get("")
def workspace(request: Request, batch_id: str, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role not in {"DSWD", "AUDITOR"}:
        raise HTTPException(403, "The office audit workspace is for DSWD and read-only Auditor accounts.")
    batch = db.query(ReliefBatch).filter_by(batch_id=batch_id).first()
    if not batch:
        raise HTTPException(404, "Relief batch not found.")
    allocations = db.query(Allocation).filter_by(batch_id=batch_id).order_by(Allocation.barangay_id).all()
    paid = dict(db.query(Distribution.allocation_id, func.sum(Distribution.amount_centavos)).filter_by(batch_id=batch_id).group_by(Distribution.allocation_id).all())
    budgets = [{"allocation_id": a.allocation_id, "barangay_id": a.barangay_id, "barangay_name": a.barangay_name, "allocated_centavos": a.amount_centavos, "recorded_centavos": paid.get(a.allocation_id,0), "remaining_centavos": a.amount_centavos-paid.get(a.allocation_id,0)} for a in allocations]
    flagged = db.query(Beneficiary).filter(Beneficiary.batch_id==batch_id, Beneficiary.record_status=="ACTIVE", (Beneficiary.duplicate_flag==True) | (Beneficiary.anomaly_flag==True)).order_by(Beneficiary.beneficiary_id).all()
    concerns = db.query(HouseholdConcern).filter_by(batch_id=batch_id).all()
    latest_revisions = db.query(ConcernRevision.concern_id, func.max(ConcernRevision.revision).label("revision")).group_by(ConcernRevision.concern_id).subquery()
    states = dict(db.query(ConcernRevision.concern_id,ConcernRevision.status).join(latest_revisions, (ConcernRevision.concern_id==latest_revisions.c.concern_id)&(ConcernRevision.revision==latest_revisions.c.revision)).all())
    open_concerns = sum(states.get(c.concern_id)!="RESOLVED" for c in concerns)
    payout_query = db.query(Distribution).filter_by(batch_id=batch_id)
    distributions = []
    for dist in payout_query.order_by(Distribution.id.desc()).limit(200):
        saved = dist.receipt_snapshot
        distributions.append({"distribution_id": dist.distribution_id, "beneficiary_id": dist.beneficiary_id, "amount_centavos": dist.amount_centavos, "recorded_at": dist.distributed_at, "recorded_status": dist.status, "receipt_version": dist.receipt_version, "recorded_by": saved.get("recorded_by") if saved else None, "anchor_state": dist.anchor_job.state if dist.anchor_job else "LEGACY", "anchor_error": dist.anchor_job.error_code if dist.anchor_job else None, "anchor_confirmed_at": dist.anchor_job.confirmed_at if dist.anchor_job else None, "recipient_acknowledged_at": dist.recipient_acknowledgement.acknowledged_at if dist.recipient_acknowledgement else None, "current_proof": "NOT_CHECKED"})
    events_query = db.query(AuditEvent).filter_by(batch_id=batch_id)
    events = [{"id": e.id, "event_type": e.event_type, "description": e.description, "entity_id": e.entity_id, "amount_centavos": e.amount_centavos, "timestamp": e.timestamp, "blockchain_tx_hash": e.blockchain_tx_hash} for e in events_query.order_by(AuditEvent.id.desc()).limit(200)]
    jobs = dict(db.query(PayoutAnchorJob.state, func.count()).join(Distribution, Distribution.distribution_id==PayoutAnchorJob.distribution_id).filter(Distribution.batch_id==batch_id).group_by(PayoutAnchorJob.state).all())
    allocated = sum(a.amount_centavos for a in allocations)
    return {"batch_id": batch_id, "batch_name": batch.calamity_name, "released_centavos": batch.amount_centavos, "allocated_centavos": allocated, "unallocated_centavos": batch.amount_centavos-allocated, "recorded_centavos": sum(paid.values()), "allocations": budgets, "flagged_households": [{"beneficiary_id": b.beneficiary_id, "household_name": b.household_name, "barangay_name": b.barangay_name, "duplicate_flag": b.duplicate_flag, "anomaly_flag": b.anomaly_flag, "review_status": b.review_status} for b in flagged], "open_concerns": open_concerns, "concern_count": len(concerns), "anchor_counts": jobs, "payout_count": payout_query.count(), "payouts": distributions, "event_count": events_query.count(), "events": events, "row_limit": 200, "audit_protection": "LOCAL_HISTORY", "evidence_scope": "Audit history is local, not blockchain-anchored. Receipt confirmation records an earlier chain observation; use Check receipt for a current contract read. Recorded payout and household acknowledgement do not prove physical cash delivery."}
