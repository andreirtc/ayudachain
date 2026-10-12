from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

from app.money import centavos_to_pesos

Base = declarative_base()


class CentavoAmount:
    """Amounts are stored as integer centavos; `amount` is the peso value for API responses."""

    @property
    def amount(self):
        return None if self.amount_centavos is None else centavos_to_pesos(self.amount_centavos)


class ReliefBatch(CentavoAmount, Base):
    __tablename__ = "relief_batches"

    @property
    def standard_grant(self):
        return centavos_to_pesos(self.standard_grant_centavos)

    @property
    def max_grant(self):
        return centavos_to_pesos(self.max_grant_centavos)

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(64), unique=True, index=True, nullable=False) # e.g. RELIEF-2026-001
    calamity_name = Column(String(128), nullable=False) # e.g. Typhoon Salinlahi
    calamity_type = Column(String(64), default="Typhoon")
    source_agency = Column(String(128), default="DSWD Central Office")
    recipient_lgu = Column(String(128), default="Provincial Government of Albay")
    purpose = Column(String(256), default="Emergency Calamity Cash and Food Assistance")
    amount_centavos = Column(Integer, nullable=False) # e.g. 1000000000 (₱10,000,000.00)
    # Fictional per-batch grant policy: payouts above the maximum are rejected,
    # payouts that differ from the standard grant are flagged for review
    standard_grant_centavos = Column(Integer, nullable=False, default=500_000)
    max_grant_centavos = Column(Integer, nullable=False, default=1_000_000)
    status = Column(String(32), default="ACTIVE") # ACTIVE, COMPLETED, SUSPENDED
    blockchain_tx_hash = Column(String(66), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    allocations = relationship("Allocation", back_populates="batch", cascade="all, delete-orphan")
    beneficiaries = relationship("Beneficiary", back_populates="batch", cascade="all, delete-orphan")
    distributions = relationship("Distribution", back_populates="batch", cascade="all, delete-orphan")


class Allocation(CentavoAmount, Base):
    __tablename__ = "allocations"
    # One allocation per barangay per batch; payouts draw from it
    __table_args__ = (UniqueConstraint("batch_id", "barangay_id", name="uq_allocation_batch_barangay"),)

    id = Column(Integer, primary_key=True, index=True)
    allocation_id = Column(String(64), unique=True, index=True, nullable=False) # e.g. ALLOC-0001
    batch_id = Column(String(64), ForeignKey("relief_batches.batch_id"), nullable=False)
    barangay_id = Column(String(32), index=True, nullable=False) # e.g. BRGY-001
    barangay_name = Column(String(128), nullable=False)
    amount_centavos = Column(Integer, nullable=False) # e.g. 250000000 (₱2,500,000.00)
    beneficiary_count = Column(Integer, default=0)
    status = Column(String(32), default="ALLOCATED") # ALLOCATED, DISTRIBUTING, COMPLETED
    blockchain_tx_hash = Column(String(66), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ReliefBatch", back_populates="allocations")


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(String(64), unique=True, index=True, nullable=False) # e.g. BEN-0001
    dafac_id = Column(String(64), nullable=True) # e.g. DFC-2026-0001
    household_name = Column(String(128), nullable=False) # e.g. Juan Dela Cruz
    barangay_id = Column(String(32), index=True, nullable=False)
    barangay_name = Column(String(128), nullable=False)
    batch_id = Column(String(64), ForeignKey("relief_batches.batch_id"), nullable=False)
    contact_number = Column(String(32), nullable=True)
    verification_status = Column(String(32), default="UNVERIFIED") # VERIFIED, FLAGGED_FOR_REVIEW, REJECTED
    duplicate_flag = Column(Boolean, default=False)
    duplicate_confidence = Column(Float, default=0.0)
    duplicate_matched_id = Column(String(64), nullable=True)
    anomaly_flag = Column(Boolean, default=False)
    review_status = Column(String(32), default="PENDING") # PENDING, APPROVED, REJECTED
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ReliefBatch", back_populates="beneficiaries")
    distribution = relationship("Distribution", back_populates="beneficiary", uselist=False)


class Distribution(CentavoAmount, Base):
    __tablename__ = "distributions"

    id = Column(Integer, primary_key=True, index=True)
    distribution_id = Column(String(64), unique=True, index=True, nullable=False) # e.g. DIST-0001
    beneficiary_id = Column(String(64), ForeignKey("beneficiaries.beneficiary_id"), nullable=False)
    batch_id = Column(String(64), ForeignKey("relief_batches.batch_id"), nullable=False)
    allocation_id = Column(String(64), ForeignKey("allocations.allocation_id"), nullable=False)
    amount_centavos = Column(Integer, nullable=False) # e.g. 500000 (₱5,000.00)
    verification_method = Column(String(64), default="QR_VOUCHER_PHYSICAL_RECEIPT")
    receipt_hash = Column(String(66), nullable=False) # SHA-256 (0x...)
    receipt_file_path = Column(String(256), nullable=True)
    ocr_text = Column(Text, nullable=True)
    status = Column(String(32), default="CONFIRMED") # CONFIRMED, REVERSED
    blockchain_tx_hash = Column(String(66), nullable=True)
    distributed_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ReliefBatch", back_populates="distributions")
    beneficiary = relationship("Beneficiary", back_populates="distribution")


class AuditEvent(CentavoAmount, Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(64), index=True, nullable=False)
    event_type = Column(String(64), nullable=False) # FUND_RELEASE, ALLOCATION, BENEFICIARY_VERIFIED, AI_DUPLICATE_FLAG, DISTRIBUTION_CONFIRMED, BLOCKCHAIN_ANCHORED
    description = Column(String(256), nullable=False)
    amount_centavos = Column(Integer, nullable=True)
    entity_id = Column(String(64), nullable=True)
    blockchain_tx_hash = Column(String(66), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
