"""
Cryptographic Integrity Hashing Pipeline.
Calculates SHA-256 digests over normalized receipt payloads and off-chain audit logs.
Provides deterministic local recalculation and on-chain hash verification.
"""

import hashlib
import json
from typing import Any, Dict, Tuple

def canonical_json(data: Dict[str, Any]) -> str:
    """
    Serializes a dictionary into deterministic canonical JSON
    (sorted keys, no extraneous whitespace, UTF-8).
    """
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def compute_sha256_hex(content: str) -> str:
    """
    Computes SHA-256 hex digest prefixed with 0x (bytes32 compatible).
    """
    digest = hashlib.sha256(content.encode('utf-8')).hexdigest()
    return f"0x{digest}"

def compute_receipt_hash(
    distribution_id: str,
    beneficiary_id: str,
    batch_id: str,
    amount: float,
    ocr_text: str,
    verification_method: str = "QR_VOUCHER_PHYSICAL_RECEIPT"
) -> str:
    """
    Normalizes the receipt's OCR and distribution metadata to produce
    the canonical 32-byte cryptographic anchor hash.
    """
    # Clean and normalize OCR lines
    normalized_ocr = " ".join([line.strip() for line in (ocr_text or "").splitlines() if line.strip()])
    
    payload = {
        "amount": f"{amount:.2f}",
        "batch_id": batch_id.strip(),
        "beneficiary_id": beneficiary_id.strip(),
        "distribution_id": distribution_id.strip(),
        "ocr_content": normalized_ocr,
        "verification_method": verification_method
    }
    canonical_str = canonical_json(payload)
    return compute_sha256_hex(canonical_str)

def verify_receipt_integrity(
    local_hash: str,
    onchain_hash: str
) -> Tuple[bool, str]:
    """
    Compares local recalculated hash with on-chain anchored hash.
    """
    local_clean = local_hash.lower().strip()
    onchain_clean = onchain_hash.lower().strip()

    if not onchain_clean or onchain_clean == "0x" or onchain_clean == "0x" + "0"*64:
        return False, "Record has not been anchored on the blockchain yet."

    if local_clean == onchain_clean:
        return True, "INTEGRITY VERIFIED: Off-chain record strictly matches immutable on-chain proof."
    else:
        return False, "INTEGRITY CHECK FAILED: Hash mismatch! Off-chain data or receipt has been modified."
