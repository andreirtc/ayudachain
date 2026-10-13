# AyudaChain — API Contract Documentation

Base URL: `http://127.0.0.1:8000`

All endpoints return JSON and include CORS headers allowing multi-origin access.

---

### 1. Dashboard Summary
- **Endpoint**: `GET /api/dashboard`
- **Description**: Returns live aggregated statistics derived directly from stored operational data and blockchain status.
- **Response**:
```json
{
  "batch_id": "RELIEF-2026-001",
  "calamity_name": "Typhoon Salinlahi",
  "total_released": 10000000.0,
  "total_allocated": 10000000.0,
  "total_distributed": 25000.0,
  "unallocated_funds": 0.0,
  "total_beneficiaries": 24,
  "verified_beneficiaries": 20,
  "flagged_records": 4,
  "confirmed_distributions": 5,
  "blockchain_status": "CONNECTED",
  "active_network": "Local EVM / Polygon Amoy",
  "contract_address": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
  "recent_transactions": [...]
}
```

---

### 2. Relief Batches
- **Endpoint**: `GET /api/batches`
- **Endpoint**: `GET /api/batches/{batch_id}`
- **Endpoint**: `POST /api/funds/releases`
  - Body:
  ```json
  {
    "batch_id": "RELIEF-2026-001",
    "calamity_name": "Typhoon Salinlahi",
    "calamity_type": "Super Typhoon",
    "source_agency": "DSWD Central Office",
    "recipient_lgu": "Provincial Government of Albay",
    "purpose": "Emergency Aid",
    "amount": 10000000.0
  }
  ```

---

### 3. Allocations
- **Endpoint**: `POST /api/allocations`
  - Body:
  ```json
  {
    "allocation_id": "ALLOC-0001",
    "batch_id": "RELIEF-2026-001",
    "barangay_id": "BRGY-001",
    "barangay_name": "San Isidro",
    "amount": 2500000.0,
    "beneficiary_count": 500
  }
  ```

---

### 4. Beneficiaries & AI Entity Resolution
- **Endpoint**: `GET /api/beneficiaries?flagged_only=false`
- **Endpoint**: `POST /api/beneficiaries`
  - Triggers live AI Entity Resolution against existing records.
  - Body:
  ```json
  {
    "beneficiary_id": "BEN-0007",
    "household_name": "Juan D. Cruz",
    "barangay_id": "BRGY-001",
    "barangay_name": "San Isidro",
    "batch_id": "RELIEF-2026-001"
  }
  ```
- **Endpoint**: `POST /api/beneficiaries/{beneficiary_id}/verify`
  - Manually review & update status (`VERIFIED` or `REJECTED`).

---

### 5. Distribution Confirmation & Blockchain Anchoring
- **Endpoint**: `GET /api/distributions`
- **Endpoint**: `POST /api/distributions/confirm`
  - Generates canonical SHA-256 hash and commits transaction to Polygon smart contract.
  - Body:
  ```json
  {
    "distribution_id": "DIST-0001",
    "beneficiary_id": "BEN-0001",
    "batch_id": "RELIEF-2026-001",
    "amount": 5000.0,
    "receipt_filename": "sample_relief_receipt.svg"
  }
  ```

---

### 6. Blockchain Verification Tool
- **Endpoint**: `POST /api/blockchain/verify`
  - Recomputes hash from database content and verifies against `AyudaChainRegistry.verifyReceipt(...)`.
  - Body:
  ```json
  {
    "distribution_id": "DIST-0001"
  }
  ```

---

### 7. Demo Reset
- **Endpoint**: `POST /api/demo/reset`
  - Restores the clean demonstration dataset for Typhoon Salinlahi.
