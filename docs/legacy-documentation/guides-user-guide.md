# AYUDACHAIN USER GUIDE 📖
### Complete Operations Manual for Citizens, Barangay Field Workers, and COA Auditors

---

## 🧭 System Overview & User Roles

AyudaChain is built to address the **₱10-billion annual disaster relief trust gap** in the Philippines. It connects the national government (DSWD/NDRRMC), local government units (LGUs), frontline relief workers, state auditors (COA), and disaster survivors through an auditable, transparent digital pipeline.

### Switching Your Role
In the top navigation bar, click the **Role Selector Dropdown** to toggle between three distinct operating modes:

| Role | Target User | Permitted Actions |
| :--- | :--- | :--- |
| **Public Citizen (Mamamayan)** | Calamity survivors, evacuees, journalists, watchdog NGOs | • Read-only access to LGU allocations and national batch fund.<br>• Verify family voucher authenticity on the blockchain.<br>• Inspect public audit timeline. *(Cannot delete or disburse).* |
| **Barangay Officer (Kawani)** | Barangay captains, kagawads, DSWD field workers, evacuation center desk | • Scan DAFAC QR codes with camera viewfinder.<br>• Disburse ₱5,000 statutory cash grants.<br>• Cache vouchers offline during downed connectivity.<br>• Review AI duplicate flags and delete invalid duplicate records. |
| **COA / Auditor (Tagasuri)** | Commission on Audit officials, municipal internal auditors | • Full investigative audit access.<br>• Trigger real-world fraud simulations (Scenario A & B).<br>• Purge verified fraudulent duplicates with audit logging.<br>• Inspect raw cryptographic hashes on Polygon blockchain. |

---

## 🖥️ Screen-by-Screen Walkthrough

---

### 1. Public Transparency Dashboard (`/`)

The central command center providing macro-level transparency for active disaster operations (e.g., *Typhoon Salinlahi*, Province of Albay).

#### Key Components:
1. **5-Step Auditable Pipeline**:
   - `1. Fund Release`: ₱10,000,000 released by DSWD Central, anchored on-chain.
   - `2. Barangay Allocation`: 100% allocated across 4 barangays in Albay.
   - `3. AI Entity Resolution`: AI pre-screens masterlists for duplicate claimants.
   - `4. Relief Distribution`: Real-time count of households who claimed aid.
   - `5. Blockchain Seal`: Cryptographic SHA-256 seal guarantees unalterability.
2. **Top-Level Metric Cards**:
   - **Total Fund Released**: Total cash allocation from the National Treasury.
   - **Total LGU Allocation**: Amount transferred to local barangay relief accounts.
   - **Total Distributed**: Confirmed payouts backed by signed vouchers.
   - **AI Flagged Records**: Suspicious records requiring human officer inspection.
3. **Live Calamity Relief Audit Timeline**:
   - Real-time chronological audit trail showing every fund release, allocation, and payout with corresponding transaction hashes.
4. **Interactive Blockchain Ledger Card**:
   - **Network Selector**: Toggle between `Local EVM (Port 8545)` and `Polygon Amoy Testnet`.
   - **Smart Contract Address**: Displays `0x5FbDB2315678afecb367f032d93F642f64180aa3` with 1-click copy and custom address editing.
   - **"What is a Smart Contract?"**: Expandable explainer in plain Filipino and English.

---

### 2. Relief Batch Detail (`/batch/[id]`)

Deep-dive operational view of a specific calamity batch (e.g., `RELIEF-2026-001`).

#### Key Components:
- **DSWD Sub-Allotment Advice (SAA)**: Official national government authorization document reference.
- **Barangay Allocations Table**: Breakdown of funds disbursed to each barangay (*San Isidro*, *Santa Elena*, *San Roque*, *Maligaya*).
- **Audit Event Log**: Chronological record of administrative changes and field activities.

---

### 3. AI Beneficiary Registry & CSV Analyzer (`/beneficiaries`)

Combines official **DSWD DAFAC** (*Disaster Assistance Family Access Card*) tracking with deterministic AI Entity Resolution to eliminate ghost beneficiaries.

#### How to Use:
1. **Bulk LGU CSV Masterlist Analyzer**:
   - Click **"Batch CSV AI Analyzer"** in the top-right corner.
   - Click **"Run 1-Click Test Masterlist"** (loads `seed_beneficiaries.csv` with 10 real-world calamity households), or upload your own CSV.
   - The AI displays a pairwise comparison table with 4 real-world anomaly types:
     - **Clerical Typo**: *Juan Dela Cruz* ↔ *Jhon Dela Cruz* (95.0% match).
     - **Swapped Name Fields**: *Maria Santos* ↔ *Santos Maria* (95.6% match).
     - **Cross-Barangay Duplicate Claim**: *Ricardo Reyes (Brgy 628)* ↔ *Riccardo Reyes (Brgy 630)* (92.8% match).
     - **Exact Duplicate**: Direct double-claim attempt.
2. **Inspecting Flagged Records**:
   - Click **"Inspect"** on any flagged row (e.g., *Juan D. Cruz `BEN-0007`*).
   - The drawer displays the similarity score %, matched record ID, and phonetic reasoning.
3. **Deleting Duplicate Records (Role-Gated)**:
   - If in **Public Citizen Mode**: The modal displays a read-only lock with an instant `[Switch to Officer Mode →]` button.
   - If in **Barangay Officer / COA Mode**: Click the red **"🗑️ Tanggalin ang Doble (Delete Duplicate)"** button.
   - Confirm the deletion prompt. The duplicate is permanently removed, and a `BENEFICIARY_DELETED` entry is recorded in the public audit trail.

---

### 4. Point-of-Payout Relief Distribution (`/distributions`)

Designed specifically for field workers distributing cash grants at evacuation covered courts.

#### Step-by-Step Distribution Protocol:
1. **Step 1: Scan or Select Evacuee**:
   - Click **"Scan DAFAC QR Code"** to open the simulated camera viewfinder modal.
   - Click any sample voucher (*Danilo Soriano `DFC-2026-0004`*, *Antonio Mercado `DFC-2026-0006`*, *Carmencita Reyes `DFC-2026-0005`*).
   - The app simulates instant QR detection, auto-selects the evacuee, and locks the grant to **₱5,000.00**.
2. **Step 2: Hand Out ₱5,000.00 Ayuda**:
   - The field officer physically releases the cash to the family head.
   - The evacuee signs or thumbmarks the physical paper DAFAC voucher.
3. **Step 3: Confirm & Anchor On-Chain**:
   - Click **"Confirm & Anchor Disbursement (₱5,000.00)"**.
   - The app computes the SHA-256 hash of the transaction and immediately stamps it into the Polygon Smart Contract.
   - An instant digital receipt with a QR code and Transaction Hash is generated for the family.

#### Evacuation Center Offline Mode:
- If typhoon winds knock down cellular towers, toggle the **"Test Offline Mode"** button.
- The status pill switches to **"Evacuation Center Mode: Offline Caching"**.
- Payouts continue uninterrupted. Signed vouchers are stored locally on the tablet and automatically sync with the blockchain as soon as internet is restored.

---

### 5. Public Blockchain Integrity Checker (`/verify`)

The public anti-corruption tool empowering every citizen and auditor to verify voucher integrity against the blockchain.

#### How to Verify:
1. Select any distribution voucher from the dropdown (e.g., `DIST-0001` for Danilo Soriano).
2. Click **"Re-Check Authentic Record"**.
3. The system compares the local database hash against the on-chain smart contract seal.
4. **Green Result**:
   > **`✓ 100% CRYPTOGRAPHIC MATCH`**  
   > *The database record is identical to the immutable on-chain seal created on payout day.*

#### Real-Life Fraud Demonstrations (For Judges):
- **Scenario A: Pocketing Cash (Kupit sa Pera)**:
  - Click the **"Scenario A: Pocketing Cash"** button.
  - Simulates a corrupt clerk altering the database record from ₱5,000 to ₱2,000.
  - The system recalculates the local hash and compares it to the original on-chain hash created with ₱5,000.
  - Result: Immediate **RED CORRUPTION ALERT** — *"TAMPERING DETECTED: The local database record was modified from ₱5,000.00 to ₱2,000.00 after on-chain anchoring!"*
- **Scenario B: Ghost Beneficiary Swap (Multong Claim)**:
  - Click the **"Scenario B: Ghost Beneficiary"** button.
  - Simulates secretly changing the claimant's name in the database to an unauthorized relative.
  - Result: Immediate **RED CORRUPTION ALERT** — *"TAMPERING DETECTED: The claimant name was secretly changed in the database!"*
- **Restore Authentic Record**:
  - Click **"✓ Restore Authentic Record"** to return to the genuine, verified ₱5,000 voucher.

---

## ❓ Frequently Asked Questions & Pitch Defense

### Q1: "What if cell towers are destroyed by the typhoon?"
**AyudaChain Answer:** We built an **Offline-First Caching Architecture**. Field tablets cache signed distribution vouchers locally in browser storage (`IndexedDB`). When connectivity returns via municipal satellite/Starlink or field worker transit, queued transactions batch-commit their hashes to Polygon.

### Q2: "Doesn't storing citizen names on a public blockchain violate the Data Privacy Act (RA 10173)?"
**AyudaChain Answer:** **Yes, putting raw names on-chain is illegal in the Philippines.** This is why AyudaChain uses a **Hybrid Off-Chain/On-Chain Architecture**:
- **Off-Chain (Protected Database):** Full names, contact numbers, and voucher photos remain strictly in secure operational databases.
- **On-Chain (Polygon Blockchain):** Only a **32-byte cryptographic SHA-256 hash** is anchored. A hash is mathematical one-way; zero private information can ever be decoded from it.

### Q3: "What if a citizen lies and claims they only got ₱2,000 when they really got ₱5,000?"
**AyudaChain Answer:** The system uses **Dual-Binding Verification**:
1. Statutory entitlement is pre-set to ₱5,000 on-chain.
2. The physical signed DAFAC voucher with the evacuee's thumbmark/signature is photographed and bound to the payout receipt hash.
3. COA auditors compare the physical paper signature against the on-chain timestamp, refuting false claims immediately.

---

*AyudaChain — Bringing mathematical integrity and public trust to Philippine disaster relief.* 🇵🇭
