# AyudaChain — API Contract Documentation

Base URL: `http://127.0.0.1:8000`

API endpoints return JSON except the sample CSV; receipt files use their file content type. Credentialed CORS uses exact configured origins. Validation errors omit submitted values. The server is the FastAPI app in `backend/app/main.py`; interactive docs are at `/docs`. Errors use FastAPI's `{"detail": "..."}` shape.

Amounts: requests send pesos with at most two decimal places (`5000` or `5000.50`); more precision is rejected with 422. Responses include `amount` (pesos) and `amount_centavos` (exact integer). The database and smart contract store integer centavos.

### Synthetic sessions and permissions

- POST /api/auth/login accepts username/password and returns account, csrf_token and synthetic=true, setting an opaque HttpOnly SameSite=Strict cookie. The raw cookie token is never returned in JSON.
- GET /api/auth/session restores account/CSRF state; anonymous or expired sessions return 401.
- POST /api/auth/logout revokes the stored session and clears the cookie. Mutations require X-AyudaChain-Client: web and the session's X-CSRF-Token. Supplied Origin must match exact configured frontend origins. Login also validates application header and Origin.
- Missing/invalid local account provisioning returns 503. Non-local insecure sign-in is rejected. Expiry, logout, account disablement and account configuration changes revoke access. Failed login attempts are limited within one API process.
- Public routes: health, dashboard, GET batches, limited receipt references, hash verification and the always-disabled reset. Public batch/dashboard activity includes funding/allocation events without household narratives.
- GET /api/public/receipts returns distribution_id and batch_id only. Public POST /api/blockchain/verify returns beneficiary_id=null; DSWD/Auditor may receive the local ID.
- All household, payout, sample CSV, private audit and receipt-file routes require sign-in. DSWD and Auditor have office reads. Barangay/Disbursing household queries use assigned barangay scope; Beneficiary queries use its linked household. Out-of-scope household IDs return 404.
- Barangay cannot access named payouts/receipt files. Barangay/Disbursing cannot read review histories. Contact, review notes and matched IDs are redacted in their household responses. Private audit and sample CSV have separate office restrictions.
- Registration permits DSWD/Barangay. Barangay registrations stay PENDING for DSWD review, even with no duplicate suggestion. Review/link/CSV/funding/allocation writes permit DSWD only. Payout writes permit Disbursing only and check household scope before business/replay logic. Auditor and Beneficiary have no business writes.
- GET /receipts/{filename} checks private account scope and a referenced file. The older shared sample image/OCR is withheld from scoped accounts because it includes another fictional household's details. Their payout representations omit that template path/text; stored hashes/evidence stay unchanged. A missing file never substitutes a sample image.

See [DEMO_SESSIONS.md](DEMO_SESSIONS.md) for provisioning, local configuration, validation and remaining identity/assignment limitations.

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
  "historical_beneficiaries": 0,
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
- **Endpoint**: `GET /api/beneficiaries?flagged_only=false&include_historical=false`
  - Defaults to active registry rows. Set `include_historical=true` to include retained duplicates. Responses include `record_status` (`ACTIVE` or `DUPLICATE`) and optional `canonical_beneficiary_id`. Individual detail and review history remain readable for retained records. Dashboard `total_beneficiaries` counts active rows; `historical_beneficiaries` counts retained duplicates.
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
  - Body: `{"status":"VERIFIED","review_notes":"Different fictional household after review"}`.
  - Allowed decisions: `VERIFIED` -> review `APPROVED`; `REJECTED` -> review `REJECTED`; `FLAGGED_FOR_REVIEW` -> review `PENDING`. A required reason is trimmed and must contain 1–2000 characters. The reviewer is the authenticated DSWD account. An optional `reviewed_by` must match that account (403 otherwise). Invalid/missing decision/reason inputs return 422; unknown beneficiary returns 404.
  - Each accepted decision appends a UUID review record with a server-generated UTC timestamp, prior state/notes, match evidence, active flags before/after, reason, and demo reviewer. The record, registry update, and local `BENEFICIARY_REVIEWED` audit event commit atomically.
  - Approve and reject resolve active duplicate/anomaly flags; original match ID/confidence remain as evidence. Pending review restores known detection flags and blocks payout. Rejected households also remain ineligible. Existing payouts and receipt hashes are preserved.
  - Retained duplicate records cannot be approved or reopened through this action (409).
  - Authenticated DSWD attribution applies to new decisions. Historical caller-supplied labels are preserved. Auditor accounts cannot submit decisions; review history is local and is not blockchain protected.
- **Endpoint**: `GET /api/beneficiaries/{beneficiary_id}/reviews`
  - Returns recorded decisions newest first, or an empty list for an existing household with no recorded review. Each record includes `review_id`, `decision`, `reason`, `reviewed_by`, `reviewed_at`, prior state, detection evidence, and flags before/after. Unknown IDs with no history return 404. See [Human reviews](HUMAN_REVIEW.md).
- **Endpoint**: `GET /api/beneficiaries/sample-csv`
  - Returns the fictional sample masterlist as `text/csv`.
- **Endpoint**: `POST /api/beneficiaries/upload-csv`
  - Body: `{"csv_content": "..."}`. Runs pairwise duplicate analysis and returns flagged pairs. An empty body analyzes the sample CSV. Does not import records.
- **Endpoint**: `POST /api/beneficiaries/{beneficiary_id}/resolve-duplicate`
  - Body: `{"canonical_beneficiary_id":"BEN-0002","review_notes":"Same fictional household after review"}`.
  - Requires a nonempty reason and an authenticated DSWD account; optional reviewer input must match it. Both records must exist (404), differ, and belong to the same batch (400). The surviving record must be active; link chains, cycles, changing a historical link, or retiring a record with linked duplicates return 409.
  - Returns 200 with the retained record: `record_status=DUPLICATE`, `canonical_beneficiary_id` set, review/verification `REJECTED`, active flags cleared. Appends a `DUPLICATE` decision with `linked_beneficiary_id`, reason, reviewer, UTC time, and prior evidence, plus a local `BENEFICIARY_DUPLICATE_RESOLVED` audit event. An identical repeat returns the same record without another decision/event.
  - Keeps original IDs, household details, prior payouts, receipt hashes/files, and earlier reviews. Already-paid records can be linked; their payout amounts remain in budgets/totals. A surviving household cannot receive a new payout if it or any linked alias was already paid in the batch. Ordinary verify/reopen on retained duplicates returns 409.
  - See [Retained duplicates](RETAINED_DUPLICATES.md) for constraints and validation.
- **Retired endpoints**: `DELETE /api/beneficiaries/{beneficiary_id}` and `POST /api/beneficiaries/{beneficiary_id}/delete`
  - Return 410 without changing data; callers must use the explicit reviewed resolution endpoint.

---

### 5. Distribution Confirmation & Blockchain Anchoring
- **Endpoint**: `GET /api/distributions`
- **Endpoint**: `POST /api/distributions/confirm`
  - Records a fictional payout and its canonical SHA-256 receipt hash, then attempts anchoring on the configured local chain or public testnet.
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
  - Send a stable `Idempotency-Key` header (1–128 characters: letters, digits, `.`, `_`, `:`, or `-`, starting with a letter or digit). With this header, `distribution_id` may be omitted; the server generates `DIST-<UUID>`. Legacy callers may supply a stable `distribution_id` (1–64 characters with the same character rules) without the header. Omitting both returns 422.
  - First accepted request returns 201. An identical retry returns 200 with the stored payout, without adding another payout/audit event or submitting another anchor. Reusing a key or ID with different effective inputs returns 409; changing the key for an existing ID also returns 409. Amounts such as `5000` and `5000.00` are equivalent. Defaults for receipt/OCR inputs are resolved before comparison.
  - The payout and audit event commit before anchoring. A blockchain failure leaves the payout recorded with a null `blockchain_tx_hash`; an ordinary payout retry returns it. A process crash or failed metadata commit can leave an anchor on-chain without a local hash. Safe anchor reconciliation is still pending in backlog section 4. `CONFIRMED` currently identifies a recorded payout, not proof of anchor confirmation or physical cash delivery.
  - Historical records from before this change have no request fingerprint and cannot be claimed through retry; reusing their distribution IDs returns 409. The SQLite schema update preserves those records. See [Payout retries](PAYOUT_RETRIES.md) for validation and limits.
  - Rules: the beneficiary must be `VERIFIED` with review `APPROVED`; the batch must be `ACTIVE`; `batch_id` must match the beneficiary's batch; the beneficiary's barangay must have an allocation in that batch; the amount must not exceed what is left in that allocation (400 states the remaining amount). One payout per household per batch, including linked aliases (400 if any member was already paid, 409 if a simultaneous request won the race); retained duplicate records cannot receive new payouts; amount at most the batch's `max_grant`. The response includes `allocation_id`. The contract enforces the allocation limit too.

---

### 6. Blockchain Verification Tool
- **Endpoint**: `POST /api/blockchain/verify`
  - Recomputes the local receipt hash and performs a read of the configured contract. No offline, missing-record, or fabricated verification fallback.
  - Body:
  ```json
  {
    "distribution_id": "DIST-0001"
  }
  ```
  - Response includes `verification_status`: `VERIFIED` for a consistent matching anchor; `MISMATCH` for a successful read of an existing different anchor; `UNANCHORED` for a successful read reporting no receipt; or `UNAVAILABLE` for failed/malformed/inconsistent reads, a missing/incompatible contract, or a wrong configured chain/contract. `is_verified` is true only for `VERIFIED`.
  - `receipt_hash_onchain` is nullable and is never replaced by the local hash. `timestamp` is nullable and is read from the actual existing receipt, not generated on lookup. Unknown local record IDs still return 404. The four verification outcomes return 200 as results of the requested check.
  - Verification requires observed chain ID and contract address to match backend configuration, an explicit existing receipt, a valid hash, a boolean contract match result, and a positive receipt timestamp. Conflicting evidence returns `UNAVAILABLE`.
  - `blockchain_tx_hash` is saved historical metadata, not independently verified by this comparison. `explorer_url` remains null until transaction metadata reconciliation is implemented. New release/allocation/payout/seed writes save a hash only from a successful CLI confirmation with a valid hash; failed operations store no invented hash.
  - Matching the current receipt hash cannot prove physical cash delivery, household names, allocation linkage, or file contents that are not yet covered by the versioned receipt snapshot. See [Truthful verification](TRUTHFUL_VERIFICATION.md).

---

### 7. Demo Reset
- **Endpoint**: `POST /api/demo/reset`
  - Returns 410 and performs no deletion/reset, regardless of role. Isolated test fixtures seed their own temporary data directly.
