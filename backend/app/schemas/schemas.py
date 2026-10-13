from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

# --- Dashboard ---
class DashboardStats(BaseModel):
    batch_id: str
    calamity_name: str
    total_released: float
    total_allocated: float
    total_distributed: float
    unallocated_funds: float
    total_beneficiaries: int
    historical_beneficiaries: int = 0
    verified_beneficiaries: int
    flagged_records: int
    confirmed_distributions: int
    blockchain_status: str
    active_network: str
    contract_address: Optional[str] = None
    recent_transactions: List[dict] = []

# --- Relief Batch ---
class ReliefBatchCreate(BaseModel):
    batch_id: str = Field(..., example="RELIEF-2026-001")
    calamity_name: str = Field(..., example="Typhoon Salinlahi")
    calamity_type: str = "Typhoon"
    source_agency: str = "DSWD Central Office"
    recipient_lgu: str = "Provincial Government of Albay"
    purpose: str = "Emergency Calamity Cash & Relief Assistance"
    amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2, example=10000000.0)
    standard_grant: Decimal = Field(Decimal("5000"), gt=0, max_digits=15, decimal_places=2)
    max_grant: Decimal = Field(Decimal("10000"), gt=0, max_digits=15, decimal_places=2)

class ReliefBatchResponse(BaseModel):
    id: int
    batch_id: str
    calamity_name: str
    calamity_type: str
    source_agency: str
    recipient_lgu: str
    purpose: str
    amount: float
    amount_centavos: int
    standard_grant: float
    standard_grant_centavos: int
    max_grant: float
    max_grant_centavos: int
    status: str
    blockchain_tx_hash: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Allocation ---
class AllocationCreate(BaseModel):
    allocation_id: str = Field(..., example="ALLOC-0001")
    batch_id: str = Field(..., example="RELIEF-2026-001")
    barangay_id: str = Field(..., example="BRGY-001")
    barangay_name: str = Field(..., example="San Isidro")
    amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2, example=2500000.0)
    beneficiary_count: int = Field(0, ge=0)

class AllocationResponse(BaseModel):
    id: int
    allocation_id: str
    batch_id: str
    barangay_id: str
    barangay_name: str
    amount: float
    amount_centavos: int
    beneficiary_count: int
    status: str
    blockchain_tx_hash: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Beneficiary ---
class BeneficiaryCreate(BaseModel):
    beneficiary_id: str = Field(..., example="BEN-0001")
    household_name: str = Field(..., example="Juan Dela Cruz")
    barangay_id: str = Field(..., example="BRGY-001")
    barangay_name: str = Field(..., example="San Isidro")
    batch_id: str = Field(..., example="RELIEF-2026-001")
    dafac_id: Optional[str] = None
    contact_number: Optional[str] = "0917-123-4567"

class BeneficiaryReviewInput(BaseModel):
    review_notes: str = Field(..., min_length=1, max_length=2000)
    reviewed_by: Optional[str] = Field(default=None, min_length=1, max_length=64)

    @field_validator("review_notes", mode="before")
    @classmethod
    def strip_reason(cls, value):
        return value.strip() if isinstance(value, str) else value


class BeneficiaryVerifyRequest(BeneficiaryReviewInput):
    status: Literal["VERIFIED", "FLAGGED_FOR_REVIEW", "REJECTED"]


class BeneficiaryDuplicateRequest(BeneficiaryReviewInput):
    canonical_beneficiary_id: str = Field(..., min_length=1, max_length=64)


class BeneficiaryReviewResponse(BaseModel):
    review_id: str
    beneficiary_id: str
    batch_id: str
    decision: str
    reason: str
    reviewed_by: str
    reviewed_at: datetime
    previous_verification_status: str
    previous_review_status: str
    previous_review_notes: Optional[str]
    duplicate_flag_before: bool
    anomaly_flag_before: bool
    duplicate_flag_after: bool
    anomaly_flag_after: bool
    linked_beneficiary_id: Optional[str]
    matched_beneficiary_id: Optional[str]
    duplicate_confidence: float

    class Config:
        from_attributes = True

class BeneficiaryResponse(BaseModel):
    id: int
    beneficiary_id: str
    dafac_id: Optional[str]
    record_status: str
    canonical_beneficiary_id: Optional[str]
    household_name: str
    barangay_id: str
    barangay_name: str
    batch_id: str
    contact_number: Optional[str]
    verification_status: str
    duplicate_flag: bool
    duplicate_confidence: float
    duplicate_matched_id: Optional[str]
    anomaly_flag: bool
    review_status: str
    review_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Distribution ---
class DistributionConfirmRequest(BaseModel):
    distribution_id: Optional[str] = Field(None, min_length=1, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$", example="DIST-0001")
    beneficiary_id: str = Field(..., example="BEN-0001")
    batch_id: str = Field(..., example="RELIEF-2026-001")
    amount: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2, example=5000.0)
    verification_method: str = "QR_VOUCHER_PHYSICAL_RECEIPT"
    receipt_filename: Optional[str] = "sample_relief_receipt.svg"
    ocr_raw_text: Optional[str] = None

class PayoutAnchorResponse(BaseModel):
    state: Literal["PENDING", "SUBMITTED", "CONFIRMED", "FAILED"]
    chain_id: int
    contract_address: Optional[str]
    candidate_tx_hash: Optional[str]
    attempts: int
    error_code: Optional[str]
    updated_at: str
    confirmed_at: Optional[str]
    block_number: Optional[int]
    block_hash: Optional[str]
    receipt_timestamp: Optional[int]

    class Config:
        from_attributes = True


from app.services.recipient_acknowledgement import AcknowledgementResponse

class DistributionResponse(BaseModel):
    id: int
    distribution_id: str
    beneficiary_id: str
    batch_id: str
    allocation_id: str
    amount: float
    amount_centavos: int
    verification_method: str
    receipt_hash: str
    receipt_file_path: Optional[str]
    ocr_text: Optional[str]
    status: str
    blockchain_tx_hash: Optional[str]
    distributed_at: datetime
    anchor_job: Optional[PayoutAnchorResponse] = None
    recipient_acknowledgement: Optional[AcknowledgementResponse] = None
    receipt_version: int = 1
    receipt_snapshot: Optional[dict] = None

    class Config:
        from_attributes = True

# --- Blockchain Verification ---
class BlockchainVerifyRequest(BaseModel):
    distribution_id: Optional[str] = None
    receipt_hash: Optional[str] = None

class BlockchainVerifyResponse(BaseModel):
    receipt_version: int = 1
    record_id: str
    beneficiary_id: Optional[str] = None
    receipt_hash_local: str
    receipt_hash_onchain: Optional[str]
    verification_status: Literal["UNAVAILABLE", "UNANCHORED", "MISMATCH", "VERIFIED"]
    is_verified: bool
    blockchain_tx_hash: Optional[str]
    timestamp: Optional[int]
    network: str
    contract_address: Optional[str]
    explorer_url: Optional[str]
    status_message: str

# --- Audit Event ---
class AuditEventResponse(BaseModel):
    id: int
    batch_id: str
    event_type: str
    description: str
    amount: Optional[float]
    amount_centavos: Optional[int]
    entity_id: Optional[str]
    blockchain_tx_hash: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True
