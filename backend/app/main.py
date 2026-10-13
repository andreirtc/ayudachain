"""
AyudaChain Main FastAPI Application
Philippine Calamity Relief Digital Trail & Integrity Layer
"""

import logging
import os
import threading
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException, Body, Header, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import config
from app.auth import router as auth_router, authorize_request, require_actor, optional_actor, scope_query, assert_household_scope, bind_reviewer
from app.database import init_db, get_db
from app.models.entities import ReliefBatch, Allocation, Beneficiary, BeneficiaryReview, Distribution, AuditEvent, PayoutAnchorJob
from app.services.payout_anchors import new_job, process_job
from app.services.receipt_snapshots import capture_document, capture, current_receipt_hash
from app.schemas.schemas import (
    DashboardStats, ReliefBatchCreate, ReliefBatchResponse,
    AllocationCreate, AllocationResponse,
    BeneficiaryCreate, BeneficiaryResponse, BeneficiaryVerifyRequest, BeneficiaryReviewResponse, BeneficiaryDuplicateRequest,
    DistributionConfirmRequest, DistributionResponse,
    BlockchainVerifyRequest, BlockchainVerifyResponse,
    AuditEventResponse
)
from app.ai.entity_resolution import EntityResolutionEngine, process_csv_batch
from app.ai.anomaly_detection import DistributionAnomalyDetector
from app.services.hasher import canonical_json, compute_sha256_hex, compute_receipt_hash, verify_receipt_integrity
from app.money import to_centavos, centavos_to_pesos, format_peso
from app.barangays import barangay_error
from app.services.blockchain import blockchain_service, confirmed_transaction_hash, is_hex_hash
from app.services.receipt_generator import save_sample_receipt, DEMO_OCR_TEXT
from app.seed_demo import seed_if_empty

app = FastAPI(
    title="AyudaChain API",
    description="Calamity Relief Verification, Entity-Resolution & Blockchain Integrity Layer",
    version="1.0.0",
    dependencies=[Depends(authorize_request)]
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-AyudaChain-Session"],
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_CSV_PATH = os.path.join(APP_DIR, "data", "seed_beneficiaries.csv")

# Static files for sample receipts
RECEIPTS_DIR = config.RECEIPTS_DIR
os.makedirs(RECEIPTS_DIR, exist_ok=True)
save_sample_receipt(RECEIPTS_DIR)
app.include_router(auth_router)
from app.services.csv_onboarding import router as csv_router
app.include_router(csv_router)
from app.services.recipient_acknowledgement import router as acknowledgement_router
app.include_router(acknowledgement_router)

@app.middleware("http")
async def no_store(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/api/", "/receipts/")):
        response.headers["Cache-Control"] = "no-store"
        if not request.url.path.startswith("/api/auth/"):
            # Public endpoints may succeed after revocation. Tell the client to
            # discard its previous private context without restricting public reads.
            response.headers["X-AyudaChain-Session"] = "active" if public_actor(request) else "ended"
    return response

@app.exception_handler(RequestValidationError)
async def invalid_input(request, exc):
    return JSONResponse(status_code=422, content={"detail": "Invalid request fields", "errors": [{"loc": list(e["loc"]), "type": e["type"]} for e in exc.errors()]})


def public_actor(request):
    try:
        return optional_actor(request)
    except HTTPException:
        return None


def household_projection(ben, actor):
    result = BeneficiaryResponse.model_validate(ben).model_dump()
    if actor.role in {"BARANGAY", "DISBURSING"}:
        result.update(contact_number=None, review_notes=None, duplicate_matched_id=None)
    return result


def distribution_projection(dist, actor):
    result = DistributionResponse.model_validate(dist).model_dump()
    # Older fixtures reuse a template containing a different household's details.
    # Preserve stored evidence/hashes, but do not disclose that template to scoped accounts.
    shared_snapshot = bool(dist.receipt_snapshot and dist.receipt_snapshot.get("receipt", {}).get("document", {}).get("kind") == "SHARED_TEMPLATE")
    if actor.role in {"DISBURSING", "BENEFICIARY"}:
        if shared_snapshot:
            result["receipt_file_path"] = None
            result["ocr_text"] = None
            result["receipt_snapshot"]["receipt"]["ocr_text"] = None
        if dist.receipt_file_path == "/receipts/sample_relief_receipt.svg":
            result["receipt_file_path"] = None
        if dist.ocr_text == DEMO_OCR_TEXT:
            result["ocr_text"] = None
    return result


@app.get("/receipts/{filename}")
def receipt_file(filename: str, request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if os.path.basename(filename) != filename or "/" in filename or "\\" in filename or filename in {".", ".."}:
        raise HTTPException(404, "Receipt not available")
    records = db.query(Distribution).filter(Distribution.receipt_file_path == "/receipts/" + filename).all()
    if filename == "sample_relief_receipt.svg":
        if actor.role not in {"DSWD", "AUDITOR"}:
            raise HTTPException(404, "Shared sample template is not a household receipt")
        records = db.query(Distribution).all()
    for dist in records:
        ben = db.query(Beneficiary).filter_by(beneficiary_id=dist.beneficiary_id).first()
        try:
            assert_household_scope(actor, ben)
        except HTTPException:
            continue
        if dist.receipt_file_path == "/receipts/" + filename and dist.snapshot_record and dist.snapshot_record.document_bytes is not None:
            if actor.role not in {"DSWD", "AUDITOR"} and dist.receipt_snapshot["receipt"]["document"]["kind"] == "SHARED_TEMPLATE":
                continue
            return Response(content=dist.snapshot_record.document_bytes, media_type=dist.snapshot_record.document_media_type, headers={"X-Content-Type-Options": "nosniff", "Content-Security-Policy": "default-src 'none'; sandbox"})
        full_path = os.path.join(RECEIPTS_DIR, filename)
        if os.path.isfile(full_path):
            return FileResponse(full_path)
    raise HTTPException(404, "Receipt not available to this account")

# AI Engines
entity_resolver = EntityResolutionEngine(confidence_threshold=0.78)
anomaly_detector = DistributionAnomalyDetector(standard_grant_amount=5000.0)

@app.on_event("startup")
def on_startup():
    init_db()
    seed_if_empty()

# --- Health Check ---
@app.get("/api/health")
def health_check():
    bc_status = blockchain_service.get_status()
    return {
        "status": "healthy",
        "service": "AyudaChain Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "blockchain": bc_status
    }

# --- Dashboard API ---
@app.get("/api/dashboard", response_model=DashboardStats)
def get_dashboard(request: Request, db: Session = Depends(get_db)):
    batch = db.query(ReliefBatch).first()
    if not batch:
        raise HTTPException(status_code=404, detail="No active relief batch found. Run seed script.")

    allocations = db.query(Allocation).filter(Allocation.batch_id == batch.batch_id).all()
    beneficiaries = db.query(Beneficiary).filter(Beneficiary.batch_id == batch.batch_id, Beneficiary.record_status == "ACTIVE").all()
    historical_bens = db.query(Beneficiary).filter(Beneficiary.batch_id == batch.batch_id, Beneficiary.record_status == "DUPLICATE").count()
    distributions = db.query(Distribution).filter(
        Distribution.batch_id == batch.batch_id,
        Distribution.status == "CONFIRMED"
    ).all()

    released_c = batch.amount_centavos
    allocated_c = sum(a.amount_centavos for a in allocations)
    distributed_c = sum(d.amount_centavos for d in distributions)
    total_released = centavos_to_pesos(released_c)
    total_allocated = centavos_to_pesos(allocated_c)
    total_distributed = centavos_to_pesos(distributed_c)
    unallocated_funds = centavos_to_pesos(max(0, released_c - allocated_c))

    total_bens = len(beneficiaries)
    verified_bens = len([b for b in beneficiaries if b.verification_status == "VERIFIED"])
    flagged_recs = len([b for b in beneficiaries if b.verification_status == "FLAGGED_FOR_REVIEW" or b.duplicate_flag or b.anomaly_flag])
    confirmed_dists = len(distributions)

    bc_info = blockchain_service.get_status()

    # Public activity omits household/review/payout narratives.
    actor = public_actor(request)
    visible_events = db.query(AuditEvent)
    if not actor or actor.role not in {"DSWD", "AUDITOR"}:
        visible_events = visible_events.filter(AuditEvent.event_type.in_(["FUND_RELEASE", "ALLOCATION"]))
    recent_events = (
        visible_events
        .filter(AuditEvent.batch_id == batch.batch_id)
        .order_by(AuditEvent.timestamp.desc())
        .limit(8)
        .all()
    )
    recent_txs = [
        {
            "event_type": ev.event_type,
            "description": ev.description,
            "amount": ev.amount,
            "tx_hash": ev.blockchain_tx_hash,
            "timestamp": ev.timestamp.isoformat()
        }
        for ev in recent_events
    ]

    return DashboardStats(
        batch_id=batch.batch_id,
        calamity_name=batch.calamity_name,
        total_released=total_released,
        total_allocated=total_allocated,
        total_distributed=total_distributed,
        unallocated_funds=unallocated_funds,
        total_beneficiaries=total_bens,
        historical_beneficiaries=historical_bens,
        verified_beneficiaries=verified_bens,
        flagged_records=flagged_recs,
        confirmed_distributions=confirmed_dists,
        blockchain_status="CONNECTED" if bc_info.get("success") else "UNAVAILABLE",
        active_network=bc_info.get("network", config.NETWORK_NAME),
        contract_address=bc_info.get("contractAddress"),
        recent_transactions=recent_txs
    )

# --- Batches API ---
@app.get("/api/batches", response_model=List[ReliefBatchResponse])
def get_batches(db: Session = Depends(get_db)):
    return db.query(ReliefBatch).order_by(ReliefBatch.id.desc()).all()

@app.get("/api/batches/{batch_id}")
def get_batch_detail(batch_id: str, request: Request, db: Session = Depends(get_db)):
    batch = db.query(ReliefBatch).filter(ReliefBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    allocations = db.query(Allocation).filter(Allocation.batch_id == batch_id).all()
    distributions = db.query(Distribution).filter(Distribution.batch_id == batch_id).all()
    events = db.query(AuditEvent).filter(AuditEvent.batch_id == batch_id).order_by(AuditEvent.timestamp.asc()).all()

    actor = public_actor(request)
    if not actor or actor.role not in {"DSWD", "AUDITOR"}:
        events = [event for event in events if event.event_type in {"FUND_RELEASE", "ALLOCATION"}]
    return {
        "batch": ReliefBatchResponse.from_orm(batch),
        "allocations": [AllocationResponse.from_orm(a) for a in allocations],
        "total_distributions": len(distributions),
        "distributed_amount": centavos_to_pesos(sum(d.amount_centavos for d in distributions)),
        "timeline": [AuditEventResponse.from_orm(e) for e in events]
    }

@app.post("/api/funds/releases", response_model=ReliefBatchResponse, status_code=201)
def release_fund(payload: ReliefBatchCreate, db: Session = Depends(get_db)):
    amount_c = to_centavos(payload.amount)
    standard_c = to_centavos(payload.standard_grant)
    max_c = to_centavos(payload.max_grant)
    if standard_c > max_c:
        raise HTTPException(status_code=400, detail="The standard grant cannot be larger than the maximum grant.")
    existing = db.query(ReliefBatch).filter(ReliefBatch.batch_id == payload.batch_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Batch ID already exists")

    # On-chain release
    bc_res = blockchain_service.release_fund(
        batch_id=payload.batch_id,
        amount_centavos=amount_c,
        calamity_name=payload.calamity_name,
        source_agency=payload.source_agency
    )
    tx_hash = confirmed_transaction_hash(bc_res)

    batch = ReliefBatch(
        batch_id=payload.batch_id,
        calamity_name=payload.calamity_name,
        calamity_type=payload.calamity_type,
        source_agency=payload.source_agency,
        recipient_lgu=payload.recipient_lgu,
        purpose=payload.purpose,
        amount_centavos=amount_c,
        standard_grant_centavos=standard_c,
        max_grant_centavos=max_c,
        status="ACTIVE",
        blockchain_tx_hash=tx_hash
    )
    db.add(batch)

    # Audit log
    audit = AuditEvent(
        batch_id=payload.batch_id,
        event_type="FUND_RELEASE",
        description=f"Fund released: {format_peso(amount_c)} for {payload.calamity_name}",
        amount_centavos=amount_c,
        entity_id=payload.batch_id,
        blockchain_tx_hash=tx_hash
    )
    db.add(audit)
    db.commit()
    db.refresh(batch)
    return batch

# --- Allocations API ---
@app.post("/api/allocations", response_model=AllocationResponse, status_code=201)
def create_allocation(payload: AllocationCreate, db: Session = Depends(get_db)):
    # Serialize fund writes so two requests cannot both pass a remaining-funds check
    with _funds_lock:
        return _create_allocation(payload, db)

_funds_lock = threading.Lock()

def _create_allocation(payload: AllocationCreate, db: Session):
    amount_c = to_centavos(payload.amount)
    batch = db.query(ReliefBatch).filter(ReliefBatch.batch_id == payload.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    if batch.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Batch {batch.batch_id} is {batch.status}, not ACTIVE.")

    existing = db.query(Allocation).filter(Allocation.allocation_id == payload.allocation_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Allocation ID already exists")

    error = barangay_error(payload.barangay_id, payload.barangay_name)
    if error:
        raise HTTPException(status_code=400, detail=error)

    same_barangay = db.query(Allocation).filter(
        Allocation.batch_id == batch.batch_id,
        Allocation.barangay_id == payload.barangay_id
    ).first()
    if same_barangay:
        raise HTTPException(
            status_code=400,
            detail=f"Barangay {payload.barangay_id} already has allocation {same_barangay.allocation_id} in batch {batch.batch_id}."
        )

    allocated_c = sum(a.amount_centavos for a in db.query(Allocation).filter(Allocation.batch_id == batch.batch_id))
    remaining_c = batch.amount_centavos - allocated_c
    if amount_c > remaining_c:
        raise HTTPException(
            status_code=400,
            detail=f"Allocation of {format_peso(amount_c)} exceeds the {format_peso(remaining_c)} not yet allocated in batch {batch.batch_id}."
        )

    # On-chain allocation
    bc_res = blockchain_service.allocate_fund(
        batch_id=payload.batch_id,
        allocation_id=payload.allocation_id,
        barangay_id=payload.barangay_id,
        amount_centavos=amount_c
    )
    tx_hash = confirmed_transaction_hash(bc_res)

    alloc = Allocation(
        allocation_id=payload.allocation_id,
        batch_id=payload.batch_id,
        barangay_id=payload.barangay_id,
        barangay_name=payload.barangay_name,
        amount_centavos=amount_c,
        beneficiary_count=payload.beneficiary_count,
        status="ALLOCATED",
        blockchain_tx_hash=tx_hash
    )
    db.add(alloc)

    audit = AuditEvent(
        batch_id=payload.batch_id,
        event_type="ALLOCATION",
        description=f"Allocated {format_peso(amount_c)} to Barangay {payload.barangay_name}",
        amount_centavos=amount_c,
        entity_id=payload.allocation_id,
        blockchain_tx_hash=tx_hash
    )
    db.add(audit)
    db.commit()
    db.refresh(alloc)
    return alloc

# --- Beneficiaries API ---
@app.get("/api/beneficiaries", response_model=List[BeneficiaryResponse])
def get_beneficiaries(
    request: Request,
    batch_id: Optional[str] = None,
    status: Optional[str] = None,
    flagged_only: bool = False,
    include_historical: bool = False,
    db: Session = Depends(get_db)
):
    actor = require_actor(request)
    query = scope_query(db.query(Beneficiary), actor, Beneficiary)
    if not include_historical:
        query = query.filter(Beneficiary.record_status == "ACTIVE")
    if batch_id:
        query = query.filter(Beneficiary.batch_id == batch_id)
    if status:
        query = query.filter(Beneficiary.verification_status == status)
    if flagged_only:
        query = query.filter(
            (Beneficiary.verification_status == "FLAGGED_FOR_REVIEW") |
            (Beneficiary.duplicate_flag == True) |
            (Beneficiary.anomaly_flag == True)
        )
    return [household_projection(ben, actor) for ben in query.order_by(Beneficiary.id.asc()).all()]

@app.get("/api/beneficiaries/sample-csv", response_class=PlainTextResponse)
def get_sample_csv():
    if not os.path.exists(SAMPLE_CSV_PATH):
        raise HTTPException(status_code=404, detail="Sample CSV not found")
    with open(SAMPLE_CSV_PATH, "r", encoding="utf-8") as f:
        return PlainTextResponse(f.read(), media_type="text/csv; charset=utf-8")

@app.post("/api/beneficiaries/upload-csv")
def upload_beneficiary_csv(payload: dict = Body(default={})):
    csv_text = payload.get("csv_content") or ""
    if not csv_text and os.path.exists(SAMPLE_CSV_PATH):
        with open(SAMPLE_CSV_PATH, "r", encoding="utf-8") as f:
            csv_text = f.read()
    return process_csv_batch(csv_text)

@app.get("/api/beneficiaries/{beneficiary_id}", response_model=BeneficiaryResponse)
def get_beneficiary(beneficiary_id: str, request: Request, db: Session = Depends(get_db)):
    ben = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    actor = require_actor(request)
    assert_household_scope(actor, ben)
    return household_projection(ben, actor)

@app.post("/api/beneficiaries", response_model=BeneficiaryResponse, status_code=201)
def register_beneficiary(payload: BeneficiaryCreate, request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    if actor.role == "BARANGAY" and payload.barangay_id != actor.barangay_id:
        raise HTTPException(403, "Register households only in your assigned barangay.")
    existing = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == payload.beneficiary_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Beneficiary ID already exists")

    if not db.query(ReliefBatch).filter(ReliefBatch.batch_id == payload.batch_id).first():
        raise HTTPException(status_code=404, detail=f"Batch {payload.batch_id} not found")

    error = barangay_error(payload.barangay_id, payload.barangay_name)
    if error:
        raise HTTPException(status_code=400, detail=error)

    # Run AI Duplicate Check against existing beneficiaries
    other_bens = db.query(Beneficiary).filter(Beneficiary.batch_id == payload.batch_id, Beneficiary.record_status == "ACTIVE").all()
    bens_dict = [
        {"beneficiary_id": b.beneficiary_id, "household_name": b.household_name, "barangay_id": b.barangay_id}
        for b in other_bens
    ]

    dup_eval = entity_resolver.evaluate_duplicate(
        candidate_name=payload.household_name,
        candidate_barangay=payload.barangay_id,
        existing_records=bens_dict
    )

    is_dup = dup_eval["is_duplicate"]
    conf = dup_eval["confidence"]
    matched_id = dup_eval["matched_id"]

    verification_status = "FLAGGED_FOR_REVIEW" if is_dup else "VERIFIED"
    review_status = "PENDING" if is_dup else "APPROVED"
    review_notes = f"AI Flag: {int(conf*100)}% match with {matched_id} ({dup_eval.get('matched_name')})" if is_dup else "Auto-verified: Zero duplicate matches found"
    if actor.role == "BARANGAY":
        verification_status, review_status = "FLAGGED_FOR_REVIEW", "PENDING"
        if not is_dup:
            review_notes = "Registered for DSWD eligibility review"

    ben = Beneficiary(
        beneficiary_id=payload.beneficiary_id,
        dafac_id=payload.dafac_id or f"DFC-2026-{payload.beneficiary_id[-4:]}",
        household_name=payload.household_name,
        barangay_id=payload.barangay_id,
        barangay_name=payload.barangay_name,
        batch_id=payload.batch_id,
        contact_number=payload.contact_number,
        verification_status=verification_status,
        duplicate_flag=is_dup,
        duplicate_confidence=conf,
        duplicate_matched_id=matched_id,
        anomaly_flag=False,
        review_status=review_status,
        review_notes=review_notes
    )
    db.add(ben)

    if is_dup:
        db.add(AuditEvent(
            batch_id=payload.batch_id,
            event_type="AI_DUPLICATE_FLAG",
            description=f"AI Entity Resolution: Possible duplicate {payload.beneficiary_id} ↔ {matched_id} ({int(conf*100)}% confidence)",
            entity_id=payload.beneficiary_id
        ))

    db.commit()
    db.refresh(ben)
    return household_projection(ben, actor)

@app.get("/api/beneficiaries/{beneficiary_id}/reviews", response_model=List[BeneficiaryReviewResponse])
def get_beneficiary_reviews(beneficiary_id: str, request: Request, db: Session = Depends(get_db)):
    ben = db.query(Beneficiary).filter_by(beneficiary_id=beneficiary_id).first()
    assert_household_scope(require_actor(request), ben)
    reviews = db.query(BeneficiaryReview).filter_by(beneficiary_id=beneficiary_id).order_by(BeneficiaryReview.id.desc()).all()
    if not reviews and not db.query(Beneficiary).filter_by(beneficiary_id=beneficiary_id).first():
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return reviews


def _registry_write_lock(db: Session):
    # SQLite is the supported demo database. Claim its writer before checking eligibility/links.
    if db.bind.dialect.name == "sqlite":
        db.connection().exec_driver_sql("BEGIN IMMEDIATE")


def _review_record(ben, payload, decision, duplicate_after=False, anomaly_after=False, linked_id=None):
    return BeneficiaryReview(
        review_id=f"REVIEW-{uuid4()}", beneficiary_id=ben.beneficiary_id, batch_id=ben.batch_id,
        decision=decision, reason=payload.review_notes, reviewed_by=payload.reviewed_by,
        previous_verification_status=ben.verification_status, previous_review_status=ben.review_status,
        previous_review_notes=ben.review_notes, duplicate_flag_before=ben.duplicate_flag,
        anomaly_flag_before=ben.anomaly_flag, duplicate_flag_after=duplicate_after,
        anomaly_flag_after=anomaly_after, linked_beneficiary_id=linked_id,
        matched_beneficiary_id=ben.duplicate_matched_id, duplicate_confidence=ben.duplicate_confidence,
    )


@app.post("/api/beneficiaries/{beneficiary_id}/verify", response_model=BeneficiaryResponse)
def verify_beneficiary(beneficiary_id: str, payload: BeneficiaryVerifyRequest, request: Request, db: Session = Depends(get_db)):
    bind_reviewer(request, payload)
    with _funds_lock:
        _registry_write_lock(db)
        ben = db.query(Beneficiary).filter_by(beneficiary_id=beneficiary_id).with_for_update().first()
        if not ben:
            raise HTTPException(status_code=404, detail="Beneficiary not found")

        if ben.record_status != "ACTIVE":
            raise HTTPException(status_code=409, detail="This historical duplicate cannot be approved or reopened for payout.")

        duplicate_after = False
        anomaly_after = False
        if payload.status == "FLAGGED_FOR_REVIEW":
            duplicate_after = bool(ben.duplicate_matched_id) or ben.duplicate_flag
            anomaly_after = ben.anomaly_flag or db.query(BeneficiaryReview).filter_by(
                beneficiary_id=beneficiary_id, anomaly_flag_before=True
            ).first() is not None

        review = _review_record(ben, payload, payload.status, duplicate_after, anomaly_after)
        ben.verification_status = payload.status
        ben.review_status = {"VERIFIED": "APPROVED", "REJECTED": "REJECTED", "FLAGGED_FOR_REVIEW": "PENDING"}[payload.status]
        ben.review_notes = payload.review_notes
        ben.duplicate_flag = duplicate_after
        ben.anomaly_flag = anomaly_after
        db.add(review)
        db.add(AuditEvent(
            batch_id=ben.batch_id,
            event_type="BENEFICIARY_REVIEWED",
            description=f"{payload.reviewed_by} reviewed {beneficiary_id}: {payload.status}. Decision {review.review_id}",
            entity_id=beneficiary_id,
        ))
        db.commit()
        db.refresh(ben)
        return ben

@app.post("/api/beneficiaries/{beneficiary_id}/resolve-duplicate", response_model=BeneficiaryResponse)
def resolve_duplicate(beneficiary_id: str, payload: BeneficiaryDuplicateRequest, request: Request, db: Session = Depends(get_db)):
    bind_reviewer(request, payload)
    with _funds_lock:
        _registry_write_lock(db)
        records = db.query(Beneficiary).filter(
            Beneficiary.beneficiary_id.in_([beneficiary_id, payload.canonical_beneficiary_id])
        ).order_by(Beneficiary.id).with_for_update().all()
        by_id = {b.beneficiary_id: b for b in records}
        ben = by_id.get(beneficiary_id)
        canonical = by_id.get(payload.canonical_beneficiary_id)
        if not ben or not canonical:
            raise HTTPException(status_code=404, detail="Household or surviving household record not found")
        if ben.beneficiary_id == canonical.beneficiary_id:
            raise HTTPException(status_code=400, detail="A household cannot be linked to itself.")
        if ben.batch_id != canonical.batch_id:
            raise HTTPException(status_code=400, detail="Duplicate records must belong to the same batch.")
        if ben.record_status == "DUPLICATE":
            prior = db.query(BeneficiaryReview).filter_by(beneficiary_id=beneficiary_id, decision="DUPLICATE").order_by(BeneficiaryReview.id.desc()).first()
            if prior and ben.canonical_beneficiary_id == canonical.beneficiary_id and prior.reason == payload.review_notes and prior.reviewed_by == payload.reviewed_by:
                return ben
            raise HTTPException(status_code=409, detail="This household already has a retained duplicate decision.")
        if canonical.record_status != "ACTIVE":
            raise HTTPException(status_code=409, detail="Select an active surviving household; duplicate link chains are not allowed.")
        if db.query(Beneficiary).filter_by(canonical_beneficiary_id=beneficiary_id).first():
            raise HTTPException(status_code=409, detail="This household is already the surviving record for linked duplicates.")

        review = _review_record(ben, payload, "DUPLICATE", linked_id=canonical.beneficiary_id)
        ben.record_status = "DUPLICATE"
        ben.canonical_beneficiary_id = canonical.beneficiary_id
        ben.verification_status = "REJECTED"
        ben.review_status = "REJECTED"
        ben.review_notes = payload.review_notes
        ben.duplicate_flag = False
        ben.anomaly_flag = False
        db.add(review)
        db.add(AuditEvent(
            batch_id=ben.batch_id, event_type="BENEFICIARY_DUPLICATE_RESOLVED", entity_id=beneficiary_id,
            description=f"{payload.reviewed_by} retained {beneficiary_id} as duplicate of {canonical.beneficiary_id}. Decision {review.review_id}",
        ))
        db.commit()
        db.refresh(ben)
        return ben


@app.delete("/api/beneficiaries/{beneficiary_id}")
@app.post("/api/beneficiaries/{beneficiary_id}/delete")
def delete_beneficiary_retired(beneficiary_id: str):
    raise HTTPException(status_code=410, detail="Deletion is disabled. Use resolve-duplicate with a surviving household, reason, and demo reviewer to retain history.")

# --- Distributions API ---
@app.get("/api/distributions", response_model=List[DistributionResponse])
def get_distributions(request: Request, batch_id: Optional[str] = None, db: Session = Depends(get_db)):
    actor = require_actor(request)
    households = scope_query(db.query(Beneficiary.beneficiary_id), actor, Beneficiary)
    query = db.query(Distribution).filter(Distribution.beneficiary_id.in_(households))
    if batch_id:
        query = query.filter(Distribution.batch_id == batch_id)
    return [distribution_projection(dist, actor) for dist in query.order_by(Distribution.distributed_at.desc()).all()]

def _payout_fingerprint(payload: DistributionConfirmRequest):
    # Compare effective inputs, including receipt contents that are not hashed yet.
    return compute_sha256_hex(canonical_json({
        "distribution_id": payload.distribution_id,
        "beneficiary_id": payload.beneficiary_id,
        "batch_id": payload.batch_id,
        "amount_centavos": to_centavos(payload.amount),
        "verification_method": payload.verification_method,
        "receipt_filename": payload.receipt_filename or "sample_relief_receipt.svg",
        "ocr_raw_text": payload.ocr_raw_text or DEMO_OCR_TEXT,
    }))


def _replayed_payout(payload, db, idempotency_key, fingerprint):
    existing = None
    if idempotency_key:
        existing = db.query(Distribution).filter(Distribution.idempotency_key == idempotency_key).first()
    if existing is None and payload.distribution_id:
        existing = db.query(Distribution).filter(Distribution.distribution_id == payload.distribution_id).first()
    if existing is None:
        return None
    if existing.request_fingerprint != fingerprint:
        raise HTTPException(status_code=409, detail="Idempotency key or distribution ID already used for a different request.")
    if idempotency_key and existing.idempotency_key != idempotency_key:
        raise HTTPException(status_code=409, detail="Distribution ID already used with another idempotency key.")
    return existing


@app.post("/api/distributions/confirm", response_model=DistributionResponse, status_code=201)
def confirm_distribution(
    request: Request,
    payload: DistributionConfirmRequest,
    response: Response,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"),
):
    if not idempotency_key and not payload.distribution_id:
        raise HTTPException(status_code=422, detail="Supply Idempotency-Key or a stable distribution_id to retry safely.")
    with _funds_lock:
        actor = require_actor(request)
        assert_household_scope(actor, db.query(Beneficiary).filter_by(beneficiary_id=payload.beneficiary_id).first())
        return distribution_projection(_confirm_distribution(payload, db, idempotency_key, response, actor), actor)


def _confirm_distribution(payload: DistributionConfirmRequest, db: Session, idempotency_key: Optional[str], response: Response, actor):
    _registry_write_lock(db)
    fingerprint = _payout_fingerprint(payload)
    existing = _replayed_payout(payload, db, idempotency_key, fingerprint)
    if existing is not None:
        response.status_code = 200
        return existing

    distribution_id = payload.distribution_id or f"DIST-{uuid4()}"
    amount_c = to_centavos(payload.amount)
    ben = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == payload.beneficiary_id).first()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    if ben.record_status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Historical duplicate {ben.beneficiary_id} is linked to {ben.canonical_beneficiary_id} and cannot receive a new payout.")

    household_ids = [b.beneficiary_id for b in db.query(Beneficiary).filter(
        Beneficiary.batch_id == ben.batch_id,
        (Beneficiary.beneficiary_id == ben.beneficiary_id) | (Beneficiary.canonical_beneficiary_id == ben.beneficiary_id),
    )]
    prior_payout = db.query(Distribution).filter(
        Distribution.beneficiary_id.in_(household_ids),
        Distribution.batch_id == ben.batch_id
    ).first()
    if prior_payout:
        raise HTTPException(status_code=400, detail=f"Duplicate disbursement rejected: Beneficiary {payload.beneficiary_id} ({ben.household_name}) or a linked duplicate was already paid in batch {ben.batch_id} ({prior_payout.distribution_id}, {prior_payout.beneficiary_id}).")

    if payload.batch_id != ben.batch_id:
        raise HTTPException(status_code=400, detail=f"Beneficiary {ben.beneficiary_id} is registered in batch {ben.batch_id}, not {payload.batch_id}.")

    if ben.verification_status != "VERIFIED" or ben.review_status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail=f"{ben.household_name} ({ben.beneficiary_id}) is not approved for payout (status {ben.verification_status}, review {ben.review_status})."
        )

    batch = db.query(ReliefBatch).filter(ReliefBatch.batch_id == ben.batch_id).first()
    if batch.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Batch {batch.batch_id} is {batch.status}, not ACTIVE.")
    if amount_c > batch.max_grant_centavos:
        raise HTTPException(
            status_code=400,
            detail=f"Amount {format_peso(amount_c)} is above the {format_peso(batch.max_grant_centavos)} maximum grant for batch {batch.batch_id}."
        )

    allocation = db.query(Allocation).filter(
        Allocation.batch_id == ben.batch_id,
        Allocation.barangay_id == ben.barangay_id
    ).first()
    if not allocation:
        raise HTTPException(status_code=400, detail=f"Barangay {ben.barangay_name} has no allocation in batch {ben.batch_id}.")

    paid_c = sum(d.amount_centavos for d in db.query(Distribution).filter(Distribution.allocation_id == allocation.allocation_id))
    remaining_c = allocation.amount_centavos - paid_c
    if amount_c > remaining_c:
        raise HTTPException(
            status_code=400,
            detail=f"Payout of {format_peso(amount_c)} exceeds the {format_peso(remaining_c)} left in {ben.barangay_name}'s allocation {allocation.allocation_id}."
        )

    # Flag amounts that differ from this batch's standard grant
    is_anomalous_amount = amount_c != batch.standard_grant_centavos
    if is_anomalous_amount:
        ben.anomaly_flag = True
        ben.review_notes = f"AI Anomaly: Non-standard grant amount {format_peso(amount_c)} (batch standard {format_peso(batch.standard_grant_centavos)}). Flagged for auditor review."

    # Generate or normalize OCR text
    ocr_content = payload.ocr_raw_text or DEMO_OCR_TEXT

    document = capture_document(payload.receipt_filename, db, actor)

    dist = Distribution(
        distribution_id=distribution_id,
        idempotency_key=idempotency_key,
        request_fingerprint=fingerprint,
        beneficiary_id=payload.beneficiary_id,
        batch_id=payload.batch_id,
        allocation_id=allocation.allocation_id,
        amount_centavos=amount_c,
        verification_method=payload.verification_method,
        receipt_hash="",
        receipt_file_path=None,
        ocr_text=ocr_content,
        status="CONFIRMED",
        distributed_at=datetime.utcnow(),
    )
    if document[1] is not None:
        dist.receipt_file_path = f"/receipts/snapshot-{distribution_id}"
    snapshot, dist.receipt_hash = capture(dist, ben, batch, allocation, actor, document)
    dist.snapshot_record = snapshot
    db.add(dist)
    db.add(new_job(dist))
    audit = AuditEvent(
        batch_id=payload.batch_id,
        event_type="DISTRIBUTION_CONFIRMED",
        description=f"Recorded fictional payout of {format_peso(amount_c)} to {ben.household_name} ({payload.beneficiary_id})",
        amount_centavos=amount_c,
        entity_id=distribution_id,
    )
    db.add(audit)

    if is_anomalous_amount:
        db.add(AuditEvent(
            batch_id=payload.batch_id,
            event_type="AI_ANOMALY_FLAG",
            description=f"AI Anomaly Engine: Non-standard disbursement of {format_peso(amount_c)} to {payload.beneficiary_id} flagged for auditor review (batch standard {format_peso(batch.standard_grant_centavos)})",
            amount_centavos=amount_c,
            entity_id=payload.beneficiary_id
        ))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # A different worker may have persisted the same request first.
        existing = _replayed_payout(payload, db, idempotency_key, fingerprint)
        if existing is not None:
            response.status_code = 200
            return existing
        raise HTTPException(status_code=409, detail="A payout already exists for this household and batch.")

    # Business replay never processes a job. Recovery has its own authorized route.
    process_job(distribution_id)
    db.refresh(dist)
    return dist


@app.post("/api/distributions/{distribution_id}/anchor/retry", response_model=DistributionResponse)
def retry_payout_anchor(distribution_id: str, request: Request, db: Session = Depends(get_db)):
    actor = require_actor(request)
    dist = db.query(Distribution).filter_by(distribution_id=distribution_id).first()
    if not dist:
        raise HTTPException(404, "Payout not available to this account.")
    assert_household_scope(actor, db.query(Beneficiary).filter_by(beneficiary_id=dist.beneficiary_id).first())
    if not db.get(PayoutAnchorJob, distribution_id):
        raise HTTPException(409, "This historical payout has no recovery envelope. Its receipt can still be verified.")
    # Release the read session before another session claims/writes the durable lease.
    db.rollback()
    if not process_job(distribution_id):
        raise HTTPException(409, "Another unresolved anchor owns the signer. Reconcile it before retrying this one.")
    db.expire_all()
    return distribution_projection(db.query(Distribution).filter_by(distribution_id=distribution_id).one(), actor)

# --- Blockchain Verification API ---
@app.post("/api/blockchain/verify", response_model=BlockchainVerifyResponse)
def verify_blockchain_record(payload: BlockchainVerifyRequest, request: Request, db: Session = Depends(get_db)):
    dist = None
    if payload.distribution_id:
        dist = db.query(Distribution).filter(Distribution.distribution_id == payload.distribution_id).first()
    elif payload.receipt_hash:
        dist = db.query(Distribution).filter(Distribution.receipt_hash == payload.receipt_hash).first()
    else:
        dist = db.query(Distribution).order_by(Distribution.id.desc()).first()

    if not dist:
        raise HTTPException(status_code=404, detail="Distribution record not found in off-chain database.")

    # 1. Recalculate local hash from off-chain stored document/metadata
    local_recalculated_hash = current_receipt_hash(dist)

    # A successful contract read is required; local hashes alone prove no anchor.
    try:
        bc_res = blockchain_service.verify_receipt(dist.distribution_id, local_recalculated_hash)
    except Exception:
        logging.getLogger(__name__).exception("Blockchain receipt lookup failed")
        bc_res = {"success": False}

    outcome = "UNAVAILABLE"
    message = "Blockchain verification is unavailable. Check the configured chain and contract, then retry."
    onchain_hash = None
    timestamp = None
    observed_chain = bc_res.get("chainId")
    correct_chain = type(observed_chain) is int and observed_chain == config.CHAIN_ID
    observed_contract = bc_res.get("contractAddress")
    correct_contract = isinstance(observed_contract, str) and bool(config.CONTRACT_ADDRESS) and observed_contract.lower() == config.CONTRACT_ADDRESS.lower()
    if bc_res.get("success") is True and correct_chain and correct_contract:
        if bc_res.get("exists") is False:
            outcome = "UNANCHORED"
            message = "No receipt anchor exists for this record on the configured blockchain."
        elif bc_res.get("exists") is True and is_hex_hash(bc_res.get("onchainHash")) and type(bc_res.get("matched")) is bool and type(bc_res.get("timestamp")) is int and bc_res["timestamp"] > 0:
            onchain_hash = bc_res["onchainHash"]
            timestamp = bc_res["timestamp"]
            hashes_match, _ = verify_receipt_integrity(local_recalculated_hash, onchain_hash)
            if hashes_match and bc_res["matched"]:
                outcome = "VERIFIED"
                message = "The locally calculated receipt hash matches the blockchain anchor."
            elif not hashes_match and not bc_res["matched"]:
                outcome = "MISMATCH"
                message = "The locally calculated receipt hash differs from the blockchain anchor."
            else:
                message = "The blockchain lookup returned inconsistent evidence. Retry verification."
    elif observed_chain is not None and not correct_chain:
        message = "The connected chain differs from the configured chain. Verification is unavailable."
    elif observed_contract is not None and not correct_contract:
        message = "The lookup did not use the configured contract. Verification is unavailable."

    viewer = public_actor(request)
    return BlockchainVerifyResponse(
        record_id=dist.distribution_id,
        beneficiary_id=dist.beneficiary_id if viewer and viewer.role in {"DSWD", "AUDITOR"} else None,
        receipt_version=dist.receipt_version,
        receipt_hash_local=local_recalculated_hash,
        receipt_hash_onchain=onchain_hash,
        verification_status=outcome,
        is_verified=outcome == "VERIFIED",
        # Historical transaction metadata is not proof of an anchor or transaction confirmation.
        blockchain_tx_hash=dist.blockchain_tx_hash,
        timestamp=timestamp,
        network=bc_res.get("network", config.NETWORK_NAME),
        contract_address=bc_res.get("contractAddress", config.CONTRACT_ADDRESS),
        explorer_url=None,
        status_message=message,
    )

# --- Audit Trail API ---
@app.get("/api/audit-trail/{batch_id}", response_model=List[AuditEventResponse])
def get_audit_trail(batch_id: str, db: Session = Depends(get_db)):
    return db.query(AuditEvent).filter(AuditEvent.batch_id == batch_id).order_by(AuditEvent.timestamp.desc()).all()

# --- Demo Reset API ---
@app.post("/api/demo/reset")
def reset_demo():
    raise HTTPException(410, "HTTP demo reset is disabled. Use an explicit local synthetic reset procedure.")


@app.get("/api/public/receipts")
def public_receipts(db: Session = Depends(get_db)):
    return [{"distribution_id": row.distribution_id, "batch_id": row.batch_id} for row in db.query(Distribution).order_by(Distribution.id).all()]
