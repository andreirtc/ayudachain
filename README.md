# AyudaChain

A fictional disaster-relief prototype with authenticated workflows, budget-constrained payouts and receipt hash evidence.

## The problem this prototype explores

Relief records can contain duplicate household claims, differences between recorded payouts and reported delivery, and missing or altered audit evidence. AyudaChain explores these risks with invented households, fictional budgets and simulated payments.

Staff register and review households, record payouts and inspect receipt evidence. Public readers see limited funding and receipt information. Beneficiary and Auditor accounts have separate read permissions. Blockchain integrity and physical cash delivery remain distinct.

## Implemented prototype features

### 1. Authenticated synthetic workflows
- Sign in with a locally provisioned account. The API enforces five roles: DSWD, Barangay, Disbursing, Beneficiary and read-only Auditor.
- DSWD handles eligibility; Disbursing records payouts; Barangay registers within its area; Beneficiary sees its linked household. Browser role fields cannot grant access.
- Public views show funding aggregates and limited receipt checks. Private records, receipt files and audit evidence require permitted accounts. See [sessions and permissions](docs/DEMO_SESSIONS.md).

### 2. Registration and human review
- Duplicate suggestions support human decisions with a required reason and authenticated DSWD reviewer.
- Retained duplicate links preserve original IDs, payout records and local review history. Payout checks include linked aliases.
- CSV validation, preview and explicit pending import connect to the registry and DSWD review.

### 3. Recording and checking payouts
- The server enforces exact centavos, active batches, eligibility, remaining allocation budgets, fictional grant limits and durable payout replay.
- A saved payout links to its exact receipt check. An unknown reference never substitutes another payout.
- Browser offline state blocks submission; no persistent offline queue or automatic sync is implemented. Camera QR decoding remains pending.

### 4. Truthful receipt verification
- An actual configured-contract read yields verified, mismatch, no anchor found or verification unavailable. Failed reads never become verified.
- The public check omits private household context. Permitted accounts can inspect local context and technical evidence.
- Hash matching does not prove cash delivery or all identity/document fields. New payouts have [durable anchor recovery](docs/PAYOUT_ANCHORS.md). New payouts retain immutable v2 receipt snapshots and own-account simulated recipient acknowledgement. Funding/historical recovery remains deferred.
- The dashboard reports configured network/contract information; its controls do not change the network. See [current user guide](docs/USER_GUIDE.md).

### 5. Organized collection and connected follow-up
- DSWD finalizes versioned validated lists; scoped staff publish and revise collection arrangements. Households see their actual instructions.
- The Disbursing desk reads approval, linked payout history and budget checks before recording. Staff-assisted concerns retain the staff actor without household credentials.
- Households submit and follow up concerns; DSWD replies with separate private reasons. Auditor inspects actual accounting, exceptions and receipt facts in a read-only workspace. See [the supported demo script](docs/demo-script.md).

---

## Quick start

### 1. Prerequisites
- **Node.js** v20+ or v24+
- **Python** 3.10+ or 3.13+

### 2. Environment Setup
Public views use local defaults. Private workflows need locally provisioned synthetic credentials; see [DEMO_SESSIONS.md](docs/DEMO_SESSIONS.md). Preserve existing datasets and chains when continuing a session. See [docs/WINDOWS_LOCAL.md](docs/WINDOWS_LOCAL.md) for optional variables and for Windows start, stop, and reset steps.

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

## Testing

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
python3 test_auth.py
```
Run every backend suite with `python scripts/run_tests.py` from `backend`. Current results, frontend unit/type/build commands, full desktop/phone browser setup and real-chain helpers are recorded in [FULL_REGRESSION_VALIDATION.md](docs/FULL_REGRESSION_VALIDATION.md). The earlier account setup remains in [DEMO_SESSIONS.md](docs/DEMO_SESSIONS.md).

### 3. TypeScript Compilation Audit
```bash
cd frontend
./node_modules/.bin/tsc --noEmit
```
*Passes with 0 errors across all routes and components.*

---

## Documentation

- [Material frontend and real screenshots](docs/MATERIAL_FRONTEND.md) — The groupmate’s Google-style layouts applied to the actual routes.

- [User Guide & Role Walkthrough](docs/USER_GUIDE.md) — Current authenticated role tasks and public receipt checks.
- [Technical Architecture Specification](docs/architecture.md) — In-depth hybrid off-chain/on-chain design.
- [Smart Contract & Blockchain Spec](docs/blockchain-spec.md) — Gas optimization, data structures, and Polygon Amoy deployment.
- [5-Minute Hackathon Demo Script](docs/demo-script.md) — Minute-by-minute pitch guide with winning talking points.

---

## License
MIT License. Built for disaster resilience and public transparency in the Republic of the Philippines. 🇵🇭

