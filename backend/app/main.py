"""
AyudaChain Main FastAPI Application
Philippine Calamity Relief Digital Trail & Integrity Layer
"""

import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

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
    allow_origins=["*"],
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

    total_released = batch.amount
    total_allocated = sum(a.amount for a in allocations)
    total_distributed = sum(d.amount for d in distributions)
    unallocated_funds = max(0.0, total_released - total_allocated)

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
        blockchain_status="CONNECTED" if bc_info.get("success") else "STANDBY",
        active_network=bc_info.get("network", "Polygon Amoy"),
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
        "distributed_amount": sum(d.amount for d in distributions),
        "timeline": [AuditEventResponse.from_orm(e) for e in events]
    }

@app.post("/api/funds/releases", response_model=ReliefBatchResponse, status_code=201)
def release_fund(payload: ReliefBatchCreate, db: Session = Depends(get_db)):
    existing = db.query(ReliefBatch).filter(ReliefBatch.batch_id == payload.batch_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Batch ID already exists")

    # On-chain release
    bc_res = blockchain_service.release_fund(
        batch_id=payload.batch_id,
        amount=payload.amount,
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
        amount=payload.amount,
        status="ACTIVE",
        blockchain_tx_hash=tx_hash
    )
    db.add(batch)

    # Audit log
    audit = AuditEvent(
        batch_id=payload.batch_id,
        event_type="FUND_RELEASE",
        description=f"Fund released: ₱{payload.amount:,.2f} for {payload.calamity_name}",
        amount=payload.amount,
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
    batch = db.query(ReliefBatch).filter(ReliefBatch.batch_id == payload.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    existing = db.query(Allocation).filter(Allocation.allocation_id == payload.allocation_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Allocation ID already exists")

    # On-chain allocation
    bc_res = blockchain_service.allocate_fund(
        batch_id=payload.batch_id,
        allocation_id=payload.allocation_id,
        barangay_id=payload.barangay_id,
        amount=payload.amount
    )
    tx_hash = bc_res.get("txHash")

    alloc = Allocation(
        allocation_id=payload.allocation_id,
        batch_id=payload.batch_id,
        barangay_id=payload.barangay_id,
        barangay_name=payload.barangay_name,
        amount=payload.amount,
        beneficiary_count=payload.beneficiary_count,
        status="ALLOCATED",
        blockchain_tx_hash=tx_hash
    )
    db.add(alloc)

    audit = AuditEvent(
        batch_id=payload.batch_id,
        event_type="ALLOCATION",
        description=f"Allocated ₱{payload.amount:,.2f} to Barangay {payload.barangay_name}",
        amount=payload.amount,
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
    ben = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == payload.beneficiary_id).first()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    existing_dist = db.query(Distribution).filter(Distribution.distribution_id == payload.distribution_id).first()
    if existing_dist:
        raise HTTPException(status_code=400, detail="Distribution ID already exists")

    if payload.amount > 10000.0:
        raise HTTPException(status_code=400, detail=f"Amount ₱{payload.amount:,.2f} exceeds the demo maximum grant of ₱10,000.00.")

    prior_payout = db.query(Distribution).filter(Distribution.beneficiary_id == payload.beneficiary_id).first()
    if prior_payout:
        raise HTTPException(status_code=400, detail=f"Duplicate disbursement rejected: Beneficiary {payload.beneficiary_id} ({ben.household_name}) has already claimed aid.")

    # Flag non-standard amounts (standard demo grant is ₱5,000)
    is_anomalous_amount = payload.amount != 5000.0
    if is_anomalous_amount:
        ben.anomaly_flag = True
        ben.review_notes = f"AI Anomaly: Non-standard grant amount ₱{payload.amount:,.2f} (expected standard ₱5,000.00). Flagged for COA audit."

    # Generate or normalize OCR text
    ocr_content = payload.ocr_raw_text or DEMO_OCR_TEXT

    # Compute Canonical SHA-256 Hash
    receipt_hash = compute_receipt_hash(
        distribution_id=payload.distribution_id,
        beneficiary_id=payload.beneficiary_id,
        batch_id=payload.batch_id,
        amount=payload.amount,
        ocr_text=ocr_content,
        verification_method=payload.verification_method
    )

    # Submit Anchor to Polygon Smart Contract
    bc_res = blockchain_service.confirm_distribution(
        batch_id=payload.batch_id,
        distribution_id=payload.distribution_id,
        beneficiary_id=payload.beneficiary_id,
        amount=payload.amount,
        receipt_hash=receipt_hash
    )
    tx_hash = bc_res.get("txHash")

    # Store off-chain record
    receipt_filename = payload.receipt_filename or "sample_relief_receipt.svg"
    dist = Distribution(
        distribution_id=payload.distribution_id,
        beneficiary_id=payload.beneficiary_id,
        batch_id=payload.batch_id,
        amount=payload.amount,
        verification_method=payload.verification_method,
        receipt_hash=receipt_hash,
        receipt_file_path=f"/receipts/{receipt_filename}",
        ocr_text=ocr_content,
        status="CONFIRMED",
        blockchain_tx_hash=tx_hash
    )
    db.add(dist)

    audit = AuditEvent(
        batch_id=payload.batch_id,
        event_type="DISTRIBUTION_CONFIRMED",
        description=f"Disbursed ₱{payload.amount:,.2f} to {ben.household_name} ({payload.beneficiary_id}) — Receipt anchored on-chain",
        amount=payload.amount,
        entity_id=payload.distribution_id,
        blockchain_tx_hash=tx_hash
    )
    db.add(audit)

    if is_anomalous_amount:
        db.add(AuditEvent(
            batch_id=payload.batch_id,
            event_type="AI_ANOMALY_FLAG",
            description=f"AI Anomaly Engine: Non-standard disbursement of ₱{payload.amount:,.2f} to {payload.beneficiary_id} flagged for COA review (Expected ₱5,000.00)",
            amount=payload.amount,
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
        amount=dist.amount,
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
        network=status_info.get("network", "Polygon Amoy"),
        contract_address=bc_res.get("contractAddress") or status_info.get("contractAddress"),
        explorer_url=f"https://amoy.polygonscan.com/tx/{dist.blockchain_tx_hash}" if dist.blockchain_tx_hash and "amoy" in status_info.get("network", "").lower() else None,
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
