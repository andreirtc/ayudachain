# AYUDACHAIN 🇵🇭
### Single, Tamper-Evident Digital Trail for Disaster Relief & Public Aid
*DSWD Calamity Cash Payouts • DAFAC Household Access Cards • Polygon Blockchain Proofs • AI Entity Resolution*

[![Network: Polygon](https://img.shields.io/badge/Blockchain-Polygon%20%7C%20EVM-8247E5?style=flat&logo=polygon)](https://polygon.technology)
[![Frontend: Next.js 15](https://img.shields.io/badge/Frontend-Next.js%2015%20App%20Router-000000?style=flat&logo=next.js)](https://nextjs.org)
[![Backend: Python](https://img.shields.io/badge/Backend-Python%203.13%20REST-3776AB?style=flat&logo=python)](https://python.org)
[![Smart Contract: Solidity](https://img.shields.io/badge/Contracts-Solidity%200.8.20-363636?style=flat&logo=solidity)](https://soliditylang.org)
[![Security: DSWD DAFAC](https://img.shields.io/badge/Standard-DSWD%20DAFAC%20Voucher-blue)](https://www.dswd.gov.ph)

---

## 🏛️ The Problem: The Calamity Relief Trust Deficit in the Philippines

During major typhoons, volcanic eruptions, and earthquakes in the Philippines, billions of pesos in national calamity funds (e.g. DSWD Emergency Cash Transfer / Assistance to Individuals in Crisis Situations - AICS) are mobilized to local government units (LGUs). However, distribution is plagued by three systemic issues:

1. **"Multong Benepisyaryo" (Ghost Beneficiaries & Duplicate Claims):** Evacuees register multiple times under slight name variations (*Juan Dela Cruz* vs *Jhon Dela Cruz* vs *Cruz, Juan D.*) or across adjacent barangay borders.
2. **"Kupit sa Pera" (Table Deductions & Ledger Tampering):** The national government releases ₱5,000 per family, but local officials hand out only ₱2,000 in cash at the covered court claiming *"₱2,000 lang ang pondo mula sa taas"*, while submitting altered liquidation papers to COA for the full ₱5,000.
3. **The Audit Blackhole:** Commission on Audit (COA) post-disaster audits occur 6 to 12 months after relief operations when physical liquidation paper sheets are lost, water-damaged, or retroactively falsified.

---

## 💡 The AyudaChain Solution

> **"The operational database holds the private family records.**  
> **The AI identifies duplicates and anomalies for field worker review.**  
> **The blockchain anchors the permanent, mathematical proof of payout.**  
> **The public transparency portal empowers 110 million Filipinos to verify their aid."**

AyudaChain creates a closed-loop, verifiable pipeline:
```
[ DSWD National Treasury ]  ──> Releases ₱10M Batch Fund (Anchored on Polygon)
            │
            ▼
[ LGU / Barangay Allocation ] ──> 100% Assigned to 4 Local Barangays
            │
            ▼
[ AI Entity Resolution Engine ] ──> Flags Typo Duplicates, Field Swaps, Cross-Brgy Claims
            │
            ▼
[ Field Payout & DAFAC Scanner ] ──> Worker scans DAFAC QR, disburses ₱5,000, signs receipt
            │
            ▼
[ Cryptographic SHA-256 Hash ] ──> Compact 32-byte receipt hash stamped into Smart Contract
            │
            ▼
[ Public Citizen / COA Portal ] ──> Instant tamper detection (Current Record vs On-Chain Seal)
```

---

## ✨ Key Features Implemented in the MVP

### 1. 📱 Point-of-Payout DAFAC QR Scanner (`/distributions`)
- **Official DSWD Standard**: Full integration with the official **DAFAC** (*Disaster Assistance Family Access Card* No. `DFC-2026-0001` to `DFC-2026-0024`).
- **Simulated Camera Viewfinder**: Mobile-first live camera overlay with animated targeting reticle, scanning laser, and 1-click test vouchers for rapid hackathon demonstrations (*Danilo Soriano `DFC-2026-0004`*, *Antonio Mercado `DFC-2026-0006`*, *Carmencita Reyes `DFC-2026-0005`*).
- **Auto-Locking Entitlement**: Automatically locks to the statutory ₱5,000 relief grant, preventing unauthorized arbitrary deductions.

### 2. 🧠 AI Entity Resolution & LGU CSV Masterlist Analyzer (`/beneficiaries`)
- **Bulk CSV Upload & 1-Click Testing**: Field workers or auditors can upload raw LGU calamity masterlists (`seed_beneficiaries.csv`) or custom spreadsheets.
- **Multi-Vector Fuzzy Token Matching**: Combines Levenshtein distance, token sort ratio, and phonetic analysis to flag:
  - *Clerical Typo / Phonetic Match*: `Juan Dela Cruz` ↔ `Jhon Dela Cruz` (95.0% match)
  - *Swapped Name Fields*: `Maria Santos` ↔ `Santos Maria` (95.6% match)
  - *Cross-Barangay Duplicate Claim*: `Ricardo Reyes (Brgy 628)` ↔ `Riccardo Reyes (Brgy 630)` (92.8% match)
  - *Exact Duplicates*: Instant flagging with direct comparison drawer.
- **Ethical AI Principle**: The AI never denies food or cash autonomously. It flags suspicious records for human review, and field officers make the final call.

### 3. Human reviews and retained duplicates (/beneficiaries)
- Select an officer or auditor demo view, inspect a household, and record a reason and named demo reviewer for each decision. Reviewer identities are simulated and caller supplied; authenticated backend permissions are not implemented yet.
- **Retain duplicate records**: Select the surviving household and choose **"Mark duplicate and retain history"**. The duplicate leaves the active list while its original ID, payouts, receipts, and review history remain available under **"Include historical duplicates"**.
- **Local history**: Resolution appends a review decision and a local `BENEFICIARY_DUPLICATE_RESOLVED` audit event. These records are not blockchain protected. Payout checks include prior payouts under linked household IDs. See [retained duplicate behavior](docs/RETAINED_DUPLICATES.md).

### 4. 📶 Evacuation Center Offline Mode (Downed Cell Tower Resilience)
- Addresses the #1 judge question: *"What happens when typhoon winds topple cell towers?"*
- Field tablets cache signed distribution vouchers locally in browser storage (`IndexedDB` / Service Worker).
- Vouchers queue locally and automatically batch-sync cryptographic hashes to Polygon as soon as Starlink or municipal hall internet reconnects.

### 5. 🛡️ Public Blockchain Verification & Live Fraud Simulator (`/verify`)
- Allows any citizen or auditor to verify receipt integrity against the immutable Polygon Smart Contract.
- **Interactive Pitch Demonstrations**:
  - **Scenario A: Pocketing Cash (Kupit sa Pera)** — Simulates an insider reducing a database record from ₱5,000 to ₱2,000 after payout. The system computes the current hash, detects the mismatch against the original on-chain seal, and raises an instant **RED CORRUPTION ALERT**.
  - **Scenario B: Ghost Beneficiary Swap (Multong Claim)** — Simulates secretly swapping an evacuee's name in the database. Instantly caught by the cryptographic signature.
  - **Restore Authentic Record** — Restores the genuine ₱5,000 record and confirms a 100% cryptographic match.

### 6. ⚙️ Interactive Blockchain Ledger Customization Card (`/dashboard`)
- Accessible directly on the homepage dashboard.
- Allows live switching between **Local EVM (Port 8545)**, **Polygon Amoy Testnet**, and custom RPC endpoints.
- Features **1-click Copy Contract Address**, direct link to **Polygonscan Block Explorer**, and an educational collapsible explainer on how smart contracts work.

### 7. 🌐 Balanced Bilingual UX
- Professional English as the primary clear heading and button text.
- Natural, conversational Filipino as helpful secondary subtext to guide local field workers and evacuees.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Node.js** v20+ or v24+
- **Python** 3.10+ or 3.13+

### 2. Environment Setup
The local defaults need no configuration. See [docs/WINDOWS_LOCAL.md](docs/WINDOWS_LOCAL.md) for optional variables and for Windows start, stop, and reset steps.

### 3. Start Local EVM Blockchain Node (Port 8545)
```bash
cd contracts
npx hardhat node --hostname 127.0.0.1 --port 8545
```
Deploy the smart contract:
```bash
cd contracts
npx hardhat run scripts/deploy.js --network localhost
```
*Deployed Contract Address:* `0x5FbDB2315678afecb367f032d93F642f64180aa3`

### 4. Start the FastAPI Backend (Port 8000)
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
*Creates the SQLite database with the fictional Typhoon Salinlahi (RELIEF-2026-001) batch if it is empty. API docs: http://127.0.0.1:8000/docs*

### 5. Start the Next.js Frontend (Port 3000)
```bash
cd frontend
npm run build && npm start
# or for live development: npm run dev
```
Open **http://localhost:3000** for the public landing page. Select **Explore demo** to open the operational dashboard at **http://localhost:3000/dashboard**.

---

## 🧪 Testing Suite

### 1. Smart Contract Hardhat Tests
```bash
cd contracts
npx hardhat test
```
*Passes 100% of test cases: fund release, allocation, receipt anchoring, access control, and hash verification.*

### 2. Backend Unit & AI Tests
```bash
cd backend
python3 test_backend.py
python3 test_api.py
```
*Passes 100% of test cases: Levenshtein token sort matching, duplicate resolution, statistical anomaly detection, and cryptographic integrity verification.*

### 3. TypeScript Compilation Audit
```bash
cd frontend
./node_modules/.bin/tsc --noEmit
```
*Passes with 0 errors across all routes and components.*

---

## 📖 Additional Documentation

- [User Guide & Role Walkthrough](docs/USER_GUIDE.md) — Comprehensive guide for Citizens, Barangay Workers, and COA Auditors.
- [Technical Architecture Specification](docs/architecture.md) — In-depth hybrid off-chain/on-chain design.
- [Smart Contract & Blockchain Spec](docs/blockchain-spec.md) — Gas optimization, data structures, and Polygon Amoy deployment.
- [5-Minute Hackathon Demo Script](docs/demo-script.md) — Minute-by-minute pitch guide with winning talking points.

---

## ⚖️ License
MIT License. Built for disaster resilience and public transparency in the Republic of the Philippines. 🇵🇭

