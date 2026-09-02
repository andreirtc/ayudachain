from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Dashboard ---
class DashboardStats(BaseModel):
    batch_id: str
    calamity_name: str
    total_released: float
    total_allocated: float
    total_distributed: float
    unallocated_funds: float
    total_beneficiaries: int
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
    amount: float = Field(..., gt=0, example=10000000.0)

class ReliefBatchResponse(BaseModel):
    id: int
    batch_id: str
    calamity_name: str
    calamity_type: str
    source_agency: str
    recipient_lgu: str
    purpose: str
    amount: float
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
    amount: float = Field(..., gt=0, example=2500000.0)
    beneficiary_count: int = Field(0, ge=0)

class AllocationResponse(BaseModel):
    id: int
    allocation_id: str
    batch_id: str
    barangay_id: str
    barangay_name: str
    amount: float
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
    contact_number: Optional[str] = "0917-123-4567"

class BeneficiaryVerifyRequest(BaseModel):
    status: str = Field(..., example="VERIFIED") # VERIFIED, FLAGGED_FOR_REVIEW, REJECTED
    review_notes: Optional[str] = None

class BeneficiaryResponse(BaseModel):
    id: int
    beneficiary_id: str
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
    distribution_id: str = Field(..., example="DIST-0001")
    beneficiary_id: str = Field(..., example="BEN-0001")
    batch_id: str = Field(..., example="RELIEF-2026-001")
    amount: float = Field(..., gt=0, example=5000.0)
    verification_method: str = "QR_VOUCHER_PHYSICAL_RECEIPT"
    receipt_filename: Optional[str] = "sample_relief_receipt.jpg"
    ocr_raw_text: Optional[str] = None

class DistributionResponse(BaseModel):
    id: int
    distribution_id: str
    beneficiary_id: str
    batch_id: str
    amount: float
    verification_method: str
    receipt_hash: str
    receipt_file_path: Optional[str]
    ocr_text: Optional[str]
    status: str
    blockchain_tx_hash: Optional[str]
    distributed_at: datetime

    class Config:
        from_attributes = True

# --- Blockchain Verification ---
class BlockchainVerifyRequest(BaseModel):
    distribution_id: Optional[str] = None
    receipt_hash: Optional[str] = None

class BlockchainVerifyResponse(BaseModel):
    record_id: str
    receipt_hash_local: str
    receipt_hash_onchain: str
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
    entity_id: Optional[str]
    blockchain_tx_hash: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True
