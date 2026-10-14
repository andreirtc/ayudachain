from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, UniqueConstraint, LargeBinary
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
    record_status = Column(String(32), nullable=False, default="ACTIVE", server_default="ACTIVE", index=True)
    canonical_beneficiary_id = Column(String(64), nullable=True, index=True)
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


class BeneficiaryReview(Base):
    """Human decisions are appended; model match evidence is retained as a snapshot."""
    __tablename__ = "beneficiary_reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String(64), unique=True, index=True, nullable=False)
    # No delete cascade: historical decisions outlive registry rows.
    beneficiary_id = Column(String(64), index=True, nullable=False)
    batch_id = Column(String(64), index=True, nullable=False)
    decision = Column(String(32), nullable=False)
    reason = Column(Text, nullable=False)
    reviewed_by = Column(String(64), nullable=False)
    reviewed_at = Column(String(40), nullable=False, default=lambda: datetime.now(timezone.utc).isoformat())
    previous_verification_status = Column(String(32), nullable=False)
    previous_review_status = Column(String(32), nullable=False)
    previous_review_notes = Column(Text, nullable=True)
    duplicate_flag_before = Column(Boolean, nullable=False)
    anomaly_flag_before = Column(Boolean, nullable=False)
    duplicate_flag_after = Column(Boolean, nullable=False)
    anomaly_flag_after = Column(Boolean, nullable=False)
    linked_beneficiary_id = Column(String(64), nullable=True)
    matched_beneficiary_id = Column(String(64), nullable=True)
    duplicate_confidence = Column(Float, nullable=False)


class Distribution(CentavoAmount, Base):
    __tablename__ = "distributions"
    # One payout per household per batch
    __table_args__ = (UniqueConstraint("batch_id", "beneficiary_id", name="uq_distribution_batch_beneficiary"),)

    id = Column(Integer, primary_key=True, index=True)
    distribution_id = Column(String(64), unique=True, index=True, nullable=False) # e.g. DIST-0001
    idempotency_key = Column(String(128), unique=True, index=True, nullable=True)
    request_fingerprint = Column(String(66), nullable=True)
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
    anchor_job = relationship("PayoutAnchorJob", uselist=False, lazy="select")
    snapshot_record = relationship("ReceiptSnapshot", uselist=False, lazy="select")

    @property
    def receipt_version(self):
        return self.snapshot_record.version if self.snapshot_record else 1

    @property
    def receipt_snapshot(self):
        import json
        try:
            return json.loads(self.snapshot_record.snapshot_json) if self.snapshot_record else None
        except (ValueError, TypeError):
            return None

    recipient_acknowledgement = relationship("RecipientAcknowledgement", uselist=False, lazy="select")


class PayoutAnchorJob(Base):
    """Durable payout submission; private envelope is never part of API schemas."""
    __tablename__ = "payout_anchor_jobs"
    distribution_id = Column(String(64), ForeignKey("distributions.distribution_id"), primary_key=True)
    state = Column(String(16), nullable=False, default="PENDING")
    snapshot_json = Column(Text, nullable=False)
    chain_id = Column(Integer, nullable=False)
    contract_address = Column(String(42), nullable=True)
    pin_json = Column(Text, nullable=True)
    raw_transaction = Column(Text, nullable=True)
    candidate_tx_hash = Column(String(66), nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    error_code = Column(String(40), nullable=True)
    updated_at = Column(String(40), nullable=False)
    confirmed_at = Column(String(40), nullable=True)
    block_number = Column(Integer, nullable=True)
    block_hash = Column(String(66), nullable=True)
    receipt_timestamp = Column(Integer, nullable=True)


class AnchorSignerLease(Base):
    __tablename__ = "anchor_signer_lease"
    id = Column(Integer, primary_key=True)
    owner = Column(String(64), nullable=False)
    expires_at = Column(Integer, nullable=False)


class AnchorObservation(Base):
    __tablename__ = "anchor_observations"
    id = Column(Integer, primary_key=True)
    distribution_id = Column(String(64), nullable=False, index=True)
    state = Column(String(16), nullable=False)
    error_code = Column(String(40), nullable=True)
    checked_at = Column(String(40), nullable=False)
    transaction_hash = Column(String(66), nullable=True)
    block_number = Column(Integer, nullable=True)
    block_hash = Column(String(66), nullable=True)


class AuditEvent(CentavoAmount, Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(64), index=True, nullable=False)
    event_type = Column(String(64), nullable=False) # FUND_RELEASE, ALLOCATION, BENEFICIARY_REVIEWED, AI_DUPLICATE_FLAG, DISTRIBUTION_CONFIRMED, BLOCKCHAIN_ANCHORED
    description = Column(String(256), nullable=False)
    amount_centavos = Column(Integer, nullable=True)
    entity_id = Column(String(64), nullable=True)
    blockchain_tx_hash = Column(String(66), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class RecipientAcknowledgement(Base):
    __tablename__ = "recipient_acknowledgements"
    distribution_id = Column(String(64), ForeignKey("distributions.distribution_id"), primary_key=True)
    acknowledgement_id = Column(String(64), unique=True, nullable=False)
    beneficiary_id = Column(String(64), nullable=False)
    batch_id = Column(String(64), nullable=False)
    account_id = Column(String(64), nullable=False)
    account_display_name = Column(String(128), nullable=False)
    amount_centavos = Column(Integer, nullable=False)
    receipt_hash = Column(String(66), nullable=False)
    acknowledged_at = Column(String(40), nullable=False)


class ReceiptSnapshot(Base):
    __tablename__ = "receipt_snapshots"
    distribution_id = Column(String(64), ForeignKey("distributions.distribution_id"), primary_key=True)
    version = Column(Integer, nullable=False)
    snapshot_json = Column(Text, nullable=False)
    document_bytes = Column(LargeBinary, nullable=True)
    document_media_type = Column(String(64), nullable=True)


class ValidatedList(Base):
    __tablename__ = "validated_lists"
    __table_args__ = (UniqueConstraint("prepared_by", "request_id", name="uq_list_preparation_retry"), UniqueConstraint("batch_id", "barangay_id", "version", name="uq_list_area_version"))
    list_id = Column(String(64), primary_key=True)
    batch_id = Column(String(64), nullable=False, index=True)
    barangay_id = Column(String(32), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    prepared_by = Column(String(64), nullable=False)
    prepared_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)
    snapshot_json = Column(Text, nullable=False)
    revision_hash = Column(String(64), nullable=False)


class PayoutArrangement(Base):
    __tablename__ = "payout_arrangements"
    __table_args__ = (UniqueConstraint("created_by", "request_id", name="uq_arrangement_retry"),)
    arrangement_id = Column(String(64), primary_key=True)
    list_id = Column(String(64), ForeignKey("validated_lists.list_id"), nullable=False, unique=True)
    batch_id = Column(String(64), nullable=False, index=True)
    barangay_id = Column(String(32), nullable=False, index=True)
    created_by = Column(String(64), nullable=False)
    created_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)


class ArrangementRevision(Base):
    __tablename__ = "arrangement_revisions"
    __table_args__ = (UniqueConstraint("arrangement_id", "revision", name="uq_arrangement_revision"), UniqueConstraint("revised_by", "request_id", name="uq_arrangement_revision_retry"))
    id = Column(Integer, primary_key=True, autoincrement=True)
    arrangement_id = Column(String(64), ForeignKey("payout_arrangements.arrangement_id"), nullable=False, index=True)
    revision = Column(Integer, nullable=False)
    state = Column(String(16), nullable=False)
    collection_date = Column(String(10), nullable=False)
    time_window = Column(String(64), nullable=False)
    site = Column(String(200), nullable=False)
    requirements_json = Column(Text, nullable=False)
    responsible_staff = Column(String(128), nullable=False)
    reason = Column(Text, nullable=False)
    revised_by = Column(String(64), nullable=False)
    revised_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)


class ListFinalization(Base):
    __tablename__ = "list_finalizations"
    list_id = Column(String(64), ForeignKey("validated_lists.list_id"), primary_key=True)
    finalized_by = Column(String(64), nullable=False)
    finalized_name = Column(String(128), nullable=False)
    finalized_at = Column(String(40), nullable=False)
    reason = Column(Text, nullable=False)


class HouseholdConcern(Base):
    __tablename__ = "household_concerns"
    __table_args__ = (UniqueConstraint("created_by", "request_id", name="uq_concern_retry"),)
    concern_id = Column(String(64), primary_key=True)
    beneficiary_id = Column(String(64), nullable=False, index=True)
    batch_id = Column(String(64), nullable=False, index=True)
    barangay_id = Column(String(32), nullable=True, index=True)
    distribution_id = Column(String(64), nullable=True)
    category = Column(String(24), nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String(24), nullable=False)
    created_by = Column(String(64), nullable=False)
    created_name = Column(String(128), nullable=False)
    created_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)


class DamageClaim(Base):
    __tablename__ = "damage_claims"
    __table_args__ = (UniqueConstraint("beneficiary_id", "batch_id", name="uq_claim_household_batch"), UniqueConstraint("created_by", "request_id", name="uq_claim_retry"))
    claim_id = Column(String(64), primary_key=True)
    beneficiary_id = Column(String(64), nullable=False, index=True)
    batch_id = Column(String(64), nullable=False, index=True)
    barangay_id = Column(String(32), nullable=False, index=True)
    source = Column(String(24), nullable=False)
    created_by = Column(String(64), nullable=False)
    created_name = Column(String(128), nullable=False)
    created_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)


class ClaimRevision(Base):
    __tablename__ = "claim_revisions"
    __table_args__ = (UniqueConstraint("claim_id", "revision", name="uq_claim_revision"), UniqueConstraint("revised_by", "request_id", name="uq_claim_revision_retry"))
    id = Column(Integer, primary_key=True)
    claim_id = Column(String(64), ForeignKey("damage_claims.claim_id"), nullable=False, index=True)
    revision = Column(Integer, nullable=False)
    action = Column(String(24), nullable=False)
    status = Column(String(24), nullable=False)
    category = Column(String(32), nullable=False)
    description = Column(Text, nullable=False)
    household_message = Column(Text, nullable=False)
    staff_reason = Column(Text, nullable=False)
    revised_by = Column(String(64), nullable=False)
    revised_name = Column(String(128), nullable=False)
    revised_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)


class AmountRuleVersion(Base):
    __tablename__ = "amount_rule_versions"
    __table_args__ = (UniqueConstraint("batch_id", "version", name="uq_amount_rule_version"), UniqueConstraint("created_by", "request_id", name="uq_amount_rule_retry"))
    id = Column(Integer, primary_key=True)
    batch_id = Column(String(64), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    mode = Column(String(16), nullable=False)
    daily_wage_centavos = Column(Integer, nullable=True)
    rules_json = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    created_by = Column(String(64), nullable=False)
    created_name = Column(String(128), nullable=False)
    created_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)


class PayoutSession(Base):
    __tablename__ = "payout_sessions"
    __table_args__ = (UniqueConstraint("created_by", "request_id", name="uq_session_retry"),)
    session_id = Column(String(64), primary_key=True)
    list_id = Column(String(64), ForeignKey("validated_lists.list_id"), nullable=False, index=True)
    batch_id = Column(String(64), nullable=False, index=True)
    barangay_id = Column(String(32), nullable=False, index=True)
    created_by = Column(String(64), nullable=False)
    created_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)


class SessionRevision(Base):
    __tablename__ = "session_revisions"
    __table_args__ = (UniqueConstraint("session_id", "revision", name="uq_session_revision"), UniqueConstraint("revised_by", "request_id", name="uq_session_revision_retry"))
    id = Column(Integer, primary_key=True)
    session_id = Column(String(64), ForeignKey("payout_sessions.session_id"), nullable=False, index=True)
    revision = Column(Integer, nullable=False)
    action = Column(String(16), nullable=False)
    state = Column(String(16), nullable=False)
    session_date = Column(String(10), nullable=False)
    site = Column(String(200), nullable=False)
    assigned_json = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    revised_by = Column(String(64), nullable=False)
    revised_name = Column(String(128), nullable=False)
    revised_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)


class ConcernRevision(Base):
    __tablename__ = "concern_revisions"
    __table_args__ = (UniqueConstraint("concern_id", "revision", name="uq_concern_revision"), UniqueConstraint("revised_by", "request_id", name="uq_concern_revision_retry"))
    id = Column(Integer, primary_key=True)
    concern_id = Column(String(64), ForeignKey("household_concerns.concern_id"), nullable=False, index=True)
    revision = Column(Integer, nullable=False)
    status = Column(String(24), nullable=False)
    household_message = Column(Text, nullable=False)
    staff_reason = Column(Text, nullable=False)
    revised_by = Column(String(64), nullable=False)
    revised_name = Column(String(128), nullable=False)
    revised_at = Column(String(40), nullable=False)
    request_id = Column(String(64), nullable=False)
    request_fingerprint = Column(String(64), nullable=False)
