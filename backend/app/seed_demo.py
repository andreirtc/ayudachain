"""
AyudaChain Demo Seeder & Reset Engine
Populates the realistic fictional calamity scenario:
Typhoon Salinlahi — Calamity Relief Batch 2026-001
Includes intentional duplicates and anomalies for pitch demonstration.
"""

import os
from app import config
from datetime import datetime, timedelta
from app.database import SessionLocal, init_db, engine
from app.models.entities import Base, ReliefBatch, Allocation, Beneficiary, Distribution, AuditEvent
from app.services.hasher import compute_receipt_hash
from app.services.receipt_generator import save_sample_receipt, DEMO_OCR_TEXT
from app.services.blockchain import blockchain_service, confirmed_transaction_hash
from app.money import format_peso
from app.barangays import DEMO_BARANGAYS

def seed_database():
    init_db()
    db = SessionLocal()

    # Drop and recreate tables for clean reset
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Save sample receipt SVG asset
    receipts_dir = config.RECEIPTS_DIR
    os.makedirs(receipts_dir, exist_ok=True)
    save_sample_receipt(receipts_dir)

    now = datetime.utcnow()

    # 1. Calamity Relief Batch
    batch_id = "RELIEF-2026-001"
    calamity_name = "Typhoon Salinlahi"
    source_agency = "DSWD Central Office"
    recipient_lgu = "Provincial Government of Albay"
    total_fund = 1_000_000_000 # centavos (₱10,000,000.00)

    # Submit or record blockchain fund release
    bc_release = blockchain_service.release_fund(
        batch_id=batch_id,
        amount_centavos=total_fund,
        calamity_name=calamity_name,
        source_agency=source_agency
    )
    release_tx = confirmed_transaction_hash(bc_release)

    batch = ReliefBatch(
        batch_id=batch_id,
        calamity_name=calamity_name,
        calamity_type="Super Typhoon",
        source_agency=source_agency,
        recipient_lgu=recipient_lgu,
        purpose="Emergency Calamity Cash & Relief Food Pack Assistance",
        amount_centavos=total_fund,
        standard_grant_centavos=500_000, # ₱5,000.00 (fictional demo policy)
        max_grant_centavos=1_000_000, # ₱10,000.00 (fictional demo policy)
        status="ACTIVE",
        blockchain_tx_hash=release_tx,
        created_at=now - timedelta(hours=3)
    )
    db.add(batch)

    # 2. Barangay Allocations
    barangays = [(b_id, b_name, 250_000_000, 500) for b_id, b_name in DEMO_BARANGAYS.items()]
    allocation_by_barangay_name = {}

    for b_idx, (b_id, b_name, b_amt, b_count) in enumerate(barangays):
        alloc_id = f"ALLOC-000{b_idx+1}"
        allocation_by_barangay_name[b_name] = alloc_id
        bc_alloc = blockchain_service.allocate_fund(
            batch_id=batch_id,
            allocation_id=alloc_id,
            barangay_id=b_id,
            amount_centavos=b_amt
        )
        alloc_tx = confirmed_transaction_hash(bc_alloc)

        alloc = Allocation(
            allocation_id=alloc_id,
            batch_id=batch_id,
            barangay_id=b_id,
            barangay_name=b_name,
            amount_centavos=b_amt,
            beneficiary_count=b_count,
            status="ALLOCATED",
            blockchain_tx_hash=alloc_tx,
            created_at=now - timedelta(hours=2, minutes=45 - b_idx*10)
        )
        db.add(alloc)

        db.add(AuditEvent(
            batch_id=batch_id,
            event_type="ALLOCATION",
            description=f"Allocated {format_peso(b_amt)} to Barangay {b_name}",
            amount_centavos=b_amt,
            entity_id=alloc_id,
            blockchain_tx_hash=alloc_tx,
            timestamp=now - timedelta(hours=2, minutes=45 - b_idx*10)
        ))

    # 3. Beneficiaries (Realistic Fictional Filipino Names with Seeded Duplicates & Anomaly)
    beneficiary_templates = [
        ("BEN-0001", "Roberto Ramos", "BRGY-001", "San Isidro", "VERIFIED", False, 0.0, None, False),
        ("BEN-0002", "Juan Dela Cruz", "BRGY-001", "San Isidro", "VERIFIED", False, 0.0, None, False),
        ("BEN-0003", "Elena Bautista", "BRGY-001", "San Isidro", "VERIFIED", False, 0.0, None, False),
        ("BEN-0004", "Danilo Soriano", "BRGY-001", "San Isidro", "VERIFIED", False, 0.0, None, False),
        ("BEN-0005", "Carmencita Reyes", "BRGY-001", "San Isidro", "VERIFIED", False, 0.0, None, False),
        ("BEN-0006", "Antonio Mercado", "BRGY-001", "San Isidro", "VERIFIED", False, 0.0, None, False),
        # Seeded Duplicate 1: Juan D. Cruz matches Juan Dela Cruz
        ("BEN-0007", "Juan D. Cruz", "BRGY-001", "San Isidro", "FLAGGED_FOR_REVIEW", True, 0.94, "BEN-0002", False),
        
        ("BEN-0008", "Rodrigo Mendoza", "BRGY-002", "Santa Elena", "VERIFIED", False, 0.0, None, False),
        ("BEN-0009", "Teresa Villanueva", "BRGY-002", "Santa Elena", "VERIFIED", False, 0.0, None, False),
        ("BEN-0010", "Eduardo Flores", "BRGY-002", "Santa Elena", "VERIFIED", False, 0.0, None, False),
        ("BEN-0011", "Consuelo Garcia", "BRGY-002", "Santa Elena", "VERIFIED", False, 0.0, None, False),
        ("BEN-0012", "Felipe Castro", "BRGY-002", "Santa Elena", "VERIFIED", False, 0.0, None, False),
        ("BEN-0013", "Maria Santos", "BRGY-002", "Santa Elena", "VERIFIED", False, 0.0, None, False),
        # Seeded Duplicate 2: Ma. Santos matches Maria Santos
        ("BEN-0014", "Ma. Santos", "BRGY-002", "Santa Elena", "FLAGGED_FOR_REVIEW", True, 0.91, "BEN-0013", False),
        
        ("BEN-0015", "Francisco Aguilar", "BRGY-003", "San Roque", "VERIFIED", False, 0.0, None, False),
        ("BEN-0016", "Luzviminda Ocampo", "BRGY-003", "San Roque", "VERIFIED", False, 0.0, None, False),
        ("BEN-0017", "Vicente Navarro", "BRGY-003", "San Roque", "VERIFIED", False, 0.0, None, False),
        ("BEN-0018", "Rosario Padilla", "BRGY-003", "San Roque", "VERIFIED", False, 0.0, None, False),
        ("BEN-0019", "Gerardo Alcantara", "BRGY-003", "San Roque", "VERIFIED", False, 0.0, None, False),
        
        ("BEN-0020", "Manuel Guinto", "BRGY-004", "Maligaya", "VERIFIED", False, 0.0, None, False),
        ("BEN-0021", "Corazon Tolentino", "BRGY-004", "Maligaya", "VERIFIED", False, 0.0, None, False),
        # Seeded Anomaly: Irregular distribution amount request & duplicate claim velocity
        ("BEN-0022", "Bernardo Magno", "BRGY-004", "Maligaya", "FLAGGED_FOR_REVIEW", False, 0.0, None, True),
        ("BEN-0023", "Corazon Tolentino", "BRGY-004", "Maligaya", "FLAGGED_FOR_REVIEW", True, 0.98, "BEN-0021", False),
        ("BEN-0024", "Gregorio Pineda", "BRGY-004", "Maligaya", "VERIFIED", False, 0.0, None, False),
    ]

    for ben_id, name, brgy_id, brgy_name, status, is_dup, dup_conf, matched_id, is_anom in beneficiary_templates:
        review_notes = None
        if is_dup:
            review_notes = f"AI Entity Resolution: {int(dup_conf*100)}% name match with {matched_id}. Human auditor review required."
        elif is_anom:
            review_notes = "AI Statistical Anomaly: Irregular disbursement amount request (₱15,000 vs standard ₱5,000)."

        ben = Beneficiary(
            beneficiary_id=ben_id,
            dafac_id=f"DFC-2026-{ben_id[-4:]}",
            household_name=name,
            barangay_id=brgy_id,
            barangay_name=brgy_name,
            batch_id=batch_id,
            contact_number="0917-555-" + ben_id.replace("BEN-", ""),
            verification_status=status,
            duplicate_flag=is_dup,
            duplicate_confidence=dup_conf,
            duplicate_matched_id=matched_id,
            anomaly_flag=is_anom,
            review_status="PENDING" if (is_dup or is_anom) else "APPROVED",
            review_notes=review_notes,
            created_at=now - timedelta(hours=2, minutes=20)
        )
        db.add(ben)

    # 4. Fictional payout records, with anchoring attempted on the configured chain
    distributed_bens = [
        ("DIST-0001", "BEN-0001", 500_000, "Roberto Ramos", "San Isidro"),
        ("DIST-0002", "BEN-0002", 500_000, "Juan Dela Cruz", "San Isidro"),
        ("DIST-0003", "BEN-0003", 500_000, "Elena Bautista", "San Isidro"),
        ("DIST-0004", "BEN-0008", 500_000, "Rodrigo Mendoza", "Santa Elena"),
        ("DIST-0005", "BEN-0009", 500_000, "Teresa Villanueva", "Santa Elena"),
    ]

    for d_id, ben_id, amt, h_name, b_name in distributed_bens:
        r_hash = compute_receipt_hash(
            distribution_id=d_id,
            beneficiary_id=ben_id,
            batch_id=batch_id,
            amount_centavos=amt,
            ocr_text=DEMO_OCR_TEXT
        )

        alloc_id = allocation_by_barangay_name[b_name]
        bc_dist = blockchain_service.confirm_distribution(
            batch_id=batch_id,
            allocation_id=alloc_id,
            distribution_id=d_id,
            beneficiary_id=ben_id,
            amount_centavos=amt,
            receipt_hash=r_hash
        )
        dist_tx = confirmed_transaction_hash(bc_dist)

        dist = Distribution(
            distribution_id=d_id,
            beneficiary_id=ben_id,
            batch_id=batch_id,
            allocation_id=alloc_id,
            amount_centavos=amt,
            verification_method="QR_VOUCHER_PHYSICAL_RECEIPT",
            receipt_hash=r_hash,
            receipt_file_path="/receipts/sample_relief_receipt.svg",
            ocr_text=DEMO_OCR_TEXT,
            status="CONFIRMED",
            blockchain_tx_hash=dist_tx,
            distributed_at=now - timedelta(minutes=45 - int(d_id[-1])*5)
        )
        db.add(dist)

        db.add(AuditEvent(
            batch_id=batch_id,
            event_type="DISTRIBUTION_CONFIRMED",
            description=f"Recorded fictional payout of {format_peso(amt)} to {h_name} ({ben_id})",
            amount_centavos=amt,
            entity_id=d_id,
            blockchain_tx_hash=dist_tx,
            timestamp=now - timedelta(minutes=45 - int(d_id[-1])*5)
        ))

    # Audit log event for AI Duplicate Detection
    db.add(AuditEvent(
        batch_id=batch_id,
        event_type="AI_DUPLICATE_FLAG",
        description="AI Entity Resolution: Flagged BEN-0007 (Juan D. Cruz) ↔ BEN-0002 (Juan Dela Cruz) [94% match]",
        entity_id="BEN-0007",
        timestamp=now - timedelta(minutes=30)
    ))

    db.add(AuditEvent(
        batch_id=batch_id,
        event_type="AI_DUPLICATE_FLAG",
        description="AI Entity Resolution: Flagged BEN-0014 (Ma. Santos) ↔ BEN-0013 (Maria Santos) [91% match]",
        entity_id="BEN-0014",
        timestamp=now - timedelta(minutes=28)
    ))

    db.add(AuditEvent(
        batch_id=batch_id,
        event_type="AI_ANOMALY_FLAG",
        description="AI Anomaly Engine: Flagged BEN-0022 for non-standard disbursement amount (₱15,000)",
        entity_id="BEN-0022",
        timestamp=now - timedelta(minutes=25)
    ))

    db.commit()
    db.close()
    print("Database seeded successfully with Typhoon Salinlahi (RELIEF-2026-001)!")

def seed_if_empty():
    init_db()
    db = SessionLocal()
    try:
        has_batch = db.query(ReliefBatch).first() is not None
    finally:
        db.close()
    if not has_batch:
        seed_database()

if __name__ == "__main__":
    seed_database()
