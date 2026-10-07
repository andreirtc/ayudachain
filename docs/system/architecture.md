# AyudaChain — System Architecture & Technical Specifications

## 1. Executive Overview

**AyudaChain** is a tamper-evident digital verification and public transparency layer for Philippine disaster calamity relief operations. It tracks emergency relief funds from national agency release (e.g., DSWD Central) to local government allocation (Province/City), through AI entity-resolution beneficiary verification, to household disbursement confirmation with on-chain cryptographic proofs.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           OFF-CHAIN DATA LAYER                              │
│                                                                             │
│  FastAPI / Python REST Server (Port 8000)                                   │
│  • Operational metadata (Batch ID, Barangay, Household Names, Amounts)     │
│  • Fictional vouchers & receipts (sample_relief_receipt.svg)                │
│  • Deterministic AI entity resolution (fuzzy matching, token similarity)   │
│  • Statistical anomaly detection (disbursement velocity, amount variances) │
│  • Persistent SQLite / PostgreSQL store (ayudachain.db)                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       │ SHA-256 Canonical JSON Normalization
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ON-CHAIN INTEGRITY LAYER                           │
│                                                                             │
│  Polygon (Amoy Testnet / EVM Local Node) — AyudaChainRegistry.sol          │
│  • Compact 32-byte cryptographic hashes (bytes32 receiptHash, recordHash)   │
│  • Immutable, append-only chronological log of releases & disbursements    │
│  • Zero personally identifiable information (PII) on-chain                  │
│  • Publicly verifiable via smart contract getters & Polygonscan            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       │ Real-Time Verification API
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PUBLIC TRANSPARENCY FRONTEND                         │
│                                                                             │
│  Next.js 15 + React 19 + TypeScript + Tailwind CSS (Port 3000)              │
│  • Public Transparency Dashboard (aggregate totals, live audit trail)      │
│  • Relief Batch Detail (allocations by barangay, transaction references)   │
│  • Beneficiary Registry (AI duplicate inspection drawer, similarity %)      │
│  • Household Distribution (receipt OCR preview, SHA-256 anchoring)         │
│  • Blockchain Verification Tool (interactive hash comparison, tamper demo) │
│  • 5-Minute Pitch Mode shortcuts bar & One-Click Demo Reset                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Hybrid Storage Architecture & Data Boundary

AyudaChain adheres to the fundamental Web3 architecture principle:
> **"The blockchain is an immutable public audit witness, not a bulk file database."**

| Data Type | Storage Location | Privacy & Security Rationale |
| :--- | :--- | :--- |
| **Household Names & Contact** | Off-Chain Database | Protects citizen privacy; complies with Data Privacy Act of 2012. |
| **Scanned Receipts & Photos** | Off-Chain Filesystem | Prevents high gas fees and blockchain state bloat. |
| **AI Matching Confidence** | Off-Chain Database | Enables iterative model tuning and human auditor review notes. |
| **Fund Release Events** | On-Chain Polygon | Guarantees authorized appropriation amounts cannot be secretly altered. |
| **Barangay Allocation Events** | On-Chain Polygon | Proves exact allocation amounts committed to each locality. |
| **Receipt Integrity Hashes** | On-Chain Polygon | 32-byte SHA-256 digest proves receipt authenticity and prevents forgery. |

---

## 3. Cryptographic Hash Pipeline

When a relief distribution is confirmed:
1. Canonical payload is constructed containing:
   - `distribution_id` (e.g. `DIST-0001`)
   - `beneficiary_id` (e.g. `BEN-0001`)
   - `batch_id` (e.g. `RELIEF-2026-001`)
   - `amount` (formatted to 2 decimal places: `5000.00`)
   - `ocr_content` (normalized, whitespace-stripped voucher text)
   - `verification_method` (`QR_VOUCHER_PHYSICAL_RECEIPT`)
2. Deterministic JSON serialization ensures key ordering is consistent.
3. SHA-256 digest is generated (`0x...` 66 characters hex).
4. Digest is recorded off-chain and committed to the `AyudaChainRegistry` smart contract.
5. In the Public Verification tool, the local hash is recalculated and compared against the contract. Any modified letter or amount flips the hash and results in `✕ INTEGRITY MISMATCH`.

---

## 4. AI Verification vs Human Authority

AyudaChain implements strict governance boundaries:
- The AI performs **entity resolution** (expanding Filipino honorifics, prefixes, nicknames, and calculating token-set Levenshtein distance).
- Suspected records are labeled `FLAGGED_FOR_HUMAN_REVIEW` with an exact similarity percentage and matched record ID.
- The AI **never automatically denies aid or accuses citizens of fraud**. Final determination requires a human barangay officer or COA auditor to confirm or flag the record.
