# AyudaChain — API Contract Documentation

Base URL: `http://127.0.0.1:8000`

All endpoints return JSON (except the sample CSV) and include CORS headers allowing multi-origin access. The server is the FastAPI app in `backend/app/main.py`; interactive docs are at `/docs`. Errors use FastAPI's `{"detail": "..."}` shape.

Amounts: requests send pesos with at most two decimal places (`5000` or `5000.50`); more precision is rejected with 422. Responses include `amount` (pesos) and `amount_centavos` (exact integer). The database and smart contract store integer centavos.

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

- Fund release (`POST /api/funds/releases`) also accepts `standard_grant` (default 5000) and `max_grant` (default 10000), in pesos. These are fictional demo policy values per batch; the standard grant cannot exceed the maximum. Payouts above `max_grant` are rejected; payouts different from `standard_grant` are flagged for review.

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
  - Rules: the batch must exist (404) and be `ACTIVE`; the barangay must be one of the known demo barangays in `backend/app/barangays.py` with its matching name; the amount must be positive and must not exceed the batch's unallocated funds (400 with the remaining amount). Each barangay gets one allocation per batch. The contract enforces the same total limit.

---

### 4. Beneficiaries & AI Entity Resolution
- **Endpoint**: `GET /api/beneficiaries?flagged_only=false`
- **Endpoint**: `POST /api/beneficiaries`
  - Triggers live AI Entity Resolution against existing records.
  - The batch must exist (404) and the barangay must be a known demo barangay with its matching name (400).
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
- **Endpoint**: `GET /api/beneficiaries/sample-csv`
  - Returns the fictional sample masterlist as `text/csv`.
- **Endpoint**: `POST /api/beneficiaries/upload-csv`
  - Body: `{"csv_content": "..."}`. Runs pairwise duplicate analysis and returns flagged pairs. An empty body analyzes the sample CSV. Does not import records.
- **Endpoint**: `DELETE /api/beneficiaries/{beneficiary_id}` (fallback: `POST /api/beneficiaries/{beneficiary_id}/delete`)
  - Removes a beneficiary record and logs a `BENEFICIARY_DELETED` audit event.

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
  - Rules: `batch_id` must match the beneficiary's batch; the beneficiary's barangay must have an allocation in that batch; the amount must not exceed what is left in that allocation (400 states the remaining amount). One payout per household; ₱10,000 demo maximum. The response includes `allocation_id`. The contract enforces the allocation limit too.

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
