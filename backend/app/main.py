"""
AyudaChain Main FastAPI Application
Philippine Calamity Relief Digital Trail & Integrity Layer
"""

import os
import threading
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import config
from app.database import init_db, get_db
from app.models.entities import ReliefBatch, Allocation, Beneficiary, Distribution, AuditEvent
from app.schemas.schemas import (
    DashboardStats, ReliefBatchCreate, ReliefBatchResponse,
    AllocationCreate, AllocationResponse,
    BeneficiaryCreate, BeneficiaryResponse, BeneficiaryVerifyRequest,
    DistributionConfirmRequest, DistributionResponse,
    BlockchainVerifyRequest, BlockchainVerifyResponse,
    AuditEventResponse
)
from app.ai.entity_resolution import EntityResolutionEngine, process_csv_batch
from app.ai.anomaly_detection import DistributionAnomalyDetector
from app.services.hasher import compute_receipt_hash, verify_receipt_integrity
from app.money import to_centavos, centavos_to_pesos, format_peso
from app.barangays import barangay_error
from app.services.blockchain import blockchain_service
from app.services.receipt_generator import save_sample_receipt, DEMO_OCR_TEXT
from app.seed_demo import seed_database, seed_if_empty

app = FastAPI(
    title="AyudaChain API",
    description="Calamity Relief Verification, Entity-Resolution & Blockchain Integrity Layer",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_CSV_PATH = os.path.join(APP_DIR, "data", "seed_beneficiaries.csv")

# Static files for sample receipts
RECEIPTS_DIR = os.path.join(APP_DIR, "data", "receipts")
os.makedirs(RECEIPTS_DIR, exist_ok=True)
save_sample_receipt(RECEIPTS_DIR)
app.mount("/receipts", StaticFiles(directory=RECEIPTS_DIR), name="receipts")

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
def get_dashboard(db: Session = Depends(get_db)):
    batch = db.query(ReliefBatch).first()
    if not batch:
        raise HTTPException(status_code=404, detail="No active relief batch found. Run seed script.")

    allocations = db.query(Allocation).filter(Allocation.batch_id == batch.batch_id).all()
    beneficiaries = db.query(Beneficiary).filter(Beneficiary.batch_id == batch.batch_id).all()
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

    # Recent activity
    recent_events = (
        db.query(AuditEvent)
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
def get_batch_detail(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(ReliefBatch).filter(ReliefBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    allocations = db.query(Allocation).filter(Allocation.batch_id == batch_id).all()
    distributions = db.query(Distribution).filter(Distribution.batch_id == batch_id).all()
    events = db.query(AuditEvent).filter(AuditEvent.batch_id == batch_id).order_by(AuditEvent.timestamp.asc()).all()

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
    tx_hash = bc_res.get("txHash")

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
    tx_hash = bc_res.get("txHash")

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
    batch_id: Optional[str] = None,
    status: Optional[str] = None,
    flagged_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Beneficiary)
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
    return query.order_by(Beneficiary.id.asc()).all()

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
def get_beneficiary(beneficiary_id: str, db: Session = Depends(get_db)):
    ben = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return ben

@app.post("/api/beneficiaries", response_model=BeneficiaryResponse, status_code=201)
def register_beneficiary(payload: BeneficiaryCreate, db: Session = Depends(get_db)):
    existing = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == payload.beneficiary_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Beneficiary ID already exists")

    if not db.query(ReliefBatch).filter(ReliefBatch.batch_id == payload.batch_id).first():
        raise HTTPException(status_code=404, detail=f"Batch {payload.batch_id} not found")

    error = barangay_error(payload.barangay_id, payload.barangay_name)
    if error:
        raise HTTPException(status_code=400, detail=error)

    # Run AI Duplicate Check against existing beneficiaries
    other_bens = db.query(Beneficiary).filter(Beneficiary.batch_id == payload.batch_id).all()
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
    return ben

@app.post("/api/beneficiaries/{beneficiary_id}/verify", response_model=BeneficiaryResponse)
def verify_beneficiary(beneficiary_id: str, payload: BeneficiaryVerifyRequest, db: Session = Depends(get_db)):
    ben = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    ben.verification_status = payload.status
    ben.review_status = "APPROVED" if payload.status == "VERIFIED" else "REJECTED"
    if payload.review_notes:
        ben.review_notes = payload.review_notes

    db.add(AuditEvent(
        batch_id=ben.batch_id,
        event_type="BENEFICIARY_VERIFIED",
        description=f"Beneficiary {beneficiary_id} manually reviewed & set to {payload.status}",
        entity_id=beneficiary_id
    ))
    db.commit()
    db.refresh(ben)
    return ben

def _delete_beneficiary(beneficiary_id: str, db: Session):
    ben = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    db.delete(ben)
    db.add(AuditEvent(
        batch_id=ben.batch_id,
        event_type="BENEFICIARY_DELETED",
        description=f"Deleted duplicate beneficiary {beneficiary_id} ({ben.household_name})",
        entity_id=beneficiary_id
    ))
    db.commit()
    return {"success": True, "message": f"Beneficiary {beneficiary_id} deleted successfully."}

@app.delete("/api/beneficiaries/{beneficiary_id}")
def delete_beneficiary(beneficiary_id: str, db: Session = Depends(get_db)):
    return _delete_beneficiary(beneficiary_id, db)

@app.post("/api/beneficiaries/{beneficiary_id}/delete")
def delete_beneficiary_fallback(beneficiary_id: str, db: Session = Depends(get_db)):
    return _delete_beneficiary(beneficiary_id, db)

# --- Distributions API ---
@app.get("/api/distributions", response_model=List[DistributionResponse])
def get_distributions(batch_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Distribution)
    if batch_id:
        query = query.filter(Distribution.batch_id == batch_id)
    return query.order_by(Distribution.distributed_at.desc()).all()

@app.post("/api/distributions/confirm", response_model=DistributionResponse, status_code=201)
def confirm_distribution(payload: DistributionConfirmRequest, db: Session = Depends(get_db)):
    with _funds_lock:
        return _confirm_distribution(payload, db)

def _confirm_distribution(payload: DistributionConfirmRequest, db: Session):
    amount_c = to_centavos(payload.amount)
    ben = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == payload.beneficiary_id).first()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    existing_dist = db.query(Distribution).filter(Distribution.distribution_id == payload.distribution_id).first()
    if existing_dist:
        raise HTTPException(status_code=400, detail="Distribution ID already exists")

    prior_payout = db.query(Distribution).filter(
        Distribution.beneficiary_id == payload.beneficiary_id,
        Distribution.batch_id == ben.batch_id
    ).first()
    if prior_payout:
        raise HTTPException(status_code=400, detail=f"Duplicate disbursement rejected: Beneficiary {payload.beneficiary_id} ({ben.household_name}) was already paid in batch {ben.batch_id} ({prior_payout.distribution_id}).")

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

    # Compute Canonical SHA-256 Hash
    receipt_hash = compute_receipt_hash(
        distribution_id=payload.distribution_id,
        beneficiary_id=payload.beneficiary_id,
        batch_id=payload.batch_id,
        amount_centavos=amount_c,
        ocr_text=ocr_content,
        verification_method=payload.verification_method
    )

    # Store off-chain record first. The flush claims the (batch, beneficiary) unique
    # constraint and holds the SQLite write lock, so a concurrent duplicate payout
    # fails here instead of after anchoring.
    receipt_filename = payload.receipt_filename or "sample_relief_receipt.svg"
    dist = Distribution(
        distribution_id=payload.distribution_id,
        beneficiary_id=payload.beneficiary_id,
        batch_id=payload.batch_id,
        allocation_id=allocation.allocation_id,
        amount_centavos=amount_c,
        verification_method=payload.verification_method,
        receipt_hash=receipt_hash,
        receipt_file_path=f"/receipts/{receipt_filename}",
        ocr_text=ocr_content,
        status="CONFIRMED"
    )
    db.add(dist)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate disbursement rejected: Beneficiary {payload.beneficiary_id} already has a payout in batch {ben.batch_id}."
        )

    # Submit anchor to the smart contract
    bc_res = blockchain_service.confirm_distribution(
        batch_id=payload.batch_id,
        allocation_id=allocation.allocation_id,
        distribution_id=payload.distribution_id,
        beneficiary_id=payload.beneficiary_id,
        amount_centavos=amount_c,
        receipt_hash=receipt_hash
    )
    tx_hash = bc_res.get("txHash")
    dist.blockchain_tx_hash = tx_hash

    audit = AuditEvent(
        batch_id=payload.batch_id,
        event_type="DISTRIBUTION_CONFIRMED",
        description=f"Disbursed {format_peso(amount_c)} to {ben.household_name} ({payload.beneficiary_id}) — Receipt anchored on-chain",
        amount_centavos=amount_c,
        entity_id=payload.distribution_id,
        blockchain_tx_hash=tx_hash
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

    db.commit()
    db.refresh(dist)
    return dist

# --- Blockchain Verification API ---
@app.post("/api/blockchain/verify", response_model=BlockchainVerifyResponse)
def verify_blockchain_record(payload: BlockchainVerifyRequest, db: Session = Depends(get_db)):
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
    local_recalculated_hash = compute_receipt_hash(
        distribution_id=dist.distribution_id,
        beneficiary_id=dist.beneficiary_id,
        batch_id=dist.batch_id,
        amount_centavos=dist.amount_centavos,
        ocr_text=dist.ocr_text,
        verification_method=dist.verification_method
    )

    # 2. Query smart contract for anchored hash
    bc_res = blockchain_service.verify_receipt(dist.distribution_id, local_recalculated_hash)
    onchain_hash = bc_res.get("onchainHash", "0x" + "0"*64)
    matched = bc_res.get("matched", False)

    # Compare
    is_valid, msg = verify_receipt_integrity(local_recalculated_hash, onchain_hash)

    status_info = blockchain_service.get_status()

    return BlockchainVerifyResponse(
        record_id=dist.distribution_id,
        beneficiary_id=dist.beneficiary_id,
        receipt_hash_local=local_recalculated_hash,
        receipt_hash_onchain=onchain_hash,
        is_verified=matched and is_valid,
        blockchain_tx_hash=dist.blockchain_tx_hash,
        timestamp=bc_res.get("timestamp"),
        network=status_info.get("network", config.NETWORK_NAME),
        contract_address=bc_res.get("contractAddress") or status_info.get("contractAddress"),
        explorer_url=f"{config.EXPLORER_TX_URL}{dist.blockchain_tx_hash}" if dist.blockchain_tx_hash and config.EXPLORER_TX_URL else None,
        status_message=msg
    )

# --- Audit Trail API ---
@app.get("/api/audit-trail/{batch_id}", response_model=List[AuditEventResponse])
def get_audit_trail(batch_id: str, db: Session = Depends(get_db)):
    return db.query(AuditEvent).filter(AuditEvent.batch_id == batch_id).order_by(AuditEvent.timestamp.desc()).all()

# --- Demo Reset API ---
@app.post("/api/demo/reset")
def reset_demo():
    seed_database()
    return {"success": True, "message": "Demo data reset to Typhoon Salinlahi (Batch RELIEF-2026-001) successfully."}
