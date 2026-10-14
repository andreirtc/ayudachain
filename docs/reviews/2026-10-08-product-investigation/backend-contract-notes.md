# Backend and contract investigation, 2026-10-08

Investigation only. Product source, dependency manifests, database, chain, generated metadata and receipt assets were not changed. No deployment, service start, network transaction, commit or push was performed by this track. Eight pure backend tests and in-memory probes were run with Python bytecode generation disabled. Contract integration tests are reserved for the root agent's isolated snapshot. This track is also independent impeccable Assessment B; Assessment A notes were not read.

Evidence labels: **S** = complete source inspection; **P** = executed read-only/in-memory probe; **T** = existing pure test execution; **D** = deterministic detector output. Confidence is high unless stated otherwise. Source references describe repository state at inspection, not authoritative operational requirements. `docs/product/prd.md`, `docs/system/dfd.md`, and `docs/system/erd.md` are absent; budget policy, household eligibility and identity assurance requirements remain unconfirmed. Existing architecture/API/blockchain documents were read and their implemented claims checked against code.

## Complete assigned coverage

All 22 assigned first-party files were inspected. Lockfile and generated metadata were parsed in full; their data was compared/inventoried rather than printing thousands of dependency or ABI lines. Ignored dependency trees, Python caches, compiler cache and artifacts are generated/external material; an existing compiler artifact ABI was additionally compared with deployment metadata.

| File | Lines | Runtime attribution and coverage |
|---|---:|---|
| `backend/app/main.py` | 464 | Dormant FastAPI application; every endpoint, import, startup hook, static mount and reset path read. |
| `backend/app/database.py` | 22 | Dormant SQLAlchemy engine/session/create-all dependency. |
| `backend/app/models/entities.py` | 97 | Dormant SQLAlchemy five-table model; uniqueness, FKs, defaults and relationships checked. |
| `backend/app/schemas/schemas.py` | 161 | Dormant Pydantic request/response contracts; validation/defaults checked. |
| `backend/app/seed_demo.py` | 244 | Dormant destructive SQLAlchemy seeder; every fixture and chain call checked. |
| `backend/app/services/blockchain.py` | 123 | **Shared active service** imported by `backend/server.py:24`; subprocess protocol, all mutations/status/verification fallbacks checked. |
| `backend/app/services/hasher.py` | 67 | **Shared active service** imported by `backend/server.py:23`; entire payload/canonicalization/comparison checked. |
| `backend/app/services/receipt_generator.py` | 151 | **Shared active service** imported by `backend/server.py:25`; static OCR, SVG interpolation, sample producer and claims checked. |
| `backend/app/ai/entity_resolution.py` | 260 | **Shared active service** imported by `backend/server.py:21`, with CSV entrypoint imported at :601; normalization, similarity, single and pairwise CSV analysis checked. |
| `backend/app/ai/anomaly_detection.py` | 85 | Imported/instantiated by active `backend/server.py:22,34`, but no runtime analyzer calls found; all three rules and aggregate analyzer checked. |
| `backend/app/data/seed_beneficiaries.csv` | 11 | Ten synthetic row fixtures; headers, DAFAC values and four intended duplicate patterns checked. |
| `backend/app/data/receipts/sample_relief_receipt.svg` | 95 | Shared static receipt; every text field and simulated QR/claim/footer checked. |
| `backend/app/blockchain/AyudaChainRegistry.json` | 548 | Generated deployment metadata; all 18 ABI entries, names/types/mutability, header and producer checked. No source imports found. |
| `backend/test_backend.py` | 91 | Entire eight-test suite read and executed; actual coverage below. |
| `contracts/contracts/AyudaChainRegistry.sol` | 219 | Entire registry, four structs/mappings, operator management, all writes, checks/events and public verification read. |
| `contracts/scripts/blockchain_client.js` | 155 | Entire CLI: metadata, environment defaults, ID and amount conversion, RPC/wallet construction, writes/readbacks and error protocol checked. |
| `contracts/scripts/deploy.js` | 51 | Entire deployment and dual generated-file producer checked. |
| `contracts/hardhat.config.js` | 38 | Compiler optimizer, chain IDs/endpoints, optional dotenv and artifact paths checked. Public development key text omitted from this report. |
| `contracts/test/AyudaChainRegistry.test.js` | 128 | All nine test cases and fresh-contract setup checked; not run by this track. |
| `contracts/package.json` | 29 | Every script/dependency examined, including public-network deployment script. |
| `contracts/package-lock.json` | 9,208 | Entire v3 JSON parsed: 661 packages; root dependency constraints, resolved relevant packages, install scripts and EDR engine requirements checked. |
| `shared/contracts/AyudaChainRegistry.json` | 548 | Generated deployment metadata; byte-identical to backend copy and ABI-equal to existing compiled artifact. |

`package.json:14` runs `backend/server.py`, and `CONTRIBUTING.md:38` agrees. That server does **not** import the dormant SQLAlchemy database/models/Pydantic schemas/FastAPI routes/SQLAlchemy seeder. It implements independent SQLite schema/routes/seeding. Do not attribute dormant endpoint defects as active API observations; shared service defects do reach the active server. Root agent owns full active-server review.

## Critical integrity evidence

1. **Shared verification fabricates a positive match on failure or genuine absence.** **S+P, high.** `backend/app/services/blockchain.py:107-120` replaces any `success: false` response **or** `exists: false` response with `success: true`, `matched: true`, `exists: true`, the queried hash as `onchainHash`, and a current timestamp. Two in-memory probes injected respectively `{success:false,error:'forced unavailable'}` and `{success:true,exists:false,matched:false,onchainHash:ZERO_HASH}`; both produced the same positive outcome. This reaches active `backend/server.py:754` and dormant `main.py:432`. It violates AGENTS invariants 1 and 2, including absent records while the RPC itself is healthy.

2. **Shared failed writes invent transaction identifiers.** **S+P, high.** `blockchain.py:24-26` hashes a seed plus wall-clock time, and failed release/allocation/distribution calls add that hash at :75-77, :82-83 and :102-104. The error's `success:false` remains, but consumers can persist `txHash` without checking it. Probe: forced unavailable release returned `success:false` plus a hash. No `simulated` indicator is supplied. Dormant `main.py:160-185`, :207-230 and :378-405 persist successful-looking operational states and audit claims regardless of chain success. Root is reviewing identical consumer patterns in active server.

3. **Shared status manufactures a reachable-network success.** **S+P, high.** `blockchain.py:61-71` converts failure to `success:true`, network `Polygon Amoy Testnet (Standby)`, chain ID 80002 and an explorer address. Dormant dashboard :118 converts that success to `CONNECTED`. Even actual CLI status (`blockchain_client.js:55-67`) verifies RPC network/block height only, never deployed code or authorized signing identity at the configured address. Therefore RPC availability, deployed registry readiness and anchoring readiness are not separately assessed.

4. **Receipt hash binds supplied text/selected metadata, not the image or independent identity record.** **S+P, high.** `hasher.py:25-49` hashes amount, batch/beneficiary/distribution IDs, OCR content and method. No image bytes, receipt filename/path, beneficiary household name/contact, actual review status or original upload are read. Changing only beneficiary name or the referenced SVG bytes does not alter the recalculated anchor; the name becomes covered only if its stored OCR text changes too. This is a boundary requiring accurate user copy, not a recommendation to change the compatibility surface without permission. `docs/system/architecture.md:77` overstates coverage with “Any modified letter or amount.”

## Canonical hash trace and limits

`hasher.py:16` uses `json.dumps(sort_keys=True,separators=(',',':'),ensure_ascii=False)`; :22 SHA-256s its UTF-8 encoding and prepends `0x`. The six-field payload formats amount to two decimal places (:41), strips outer ID whitespace (:42-44), joins stripped nonempty OCR lines with a single space (:38), and leaves `verification_method` untouched (:46). It does not collapse internal whitespace or normalize Unicode equivalents. Executed probes established: `a\nb` and `a b` hash identically; `a  b` and `a b` differ; amounts 1.001 and 1.002 hash identically because both format as `1.00`. Monetary rounding and allowed precision therefore need policy confirmation before compatibility changes.

`verify_receipt_integrity:58-67` lowercases/trims and rejects empty, `0x`, or the zero digest; otherwise it accepts any two identical strings, even `invalid` (executed). In normal API flow the local digest is generated and on-chain bytes32 comes from ethers, limiting that type-validation gap; positive fallback is the serious practical failure. The helper cannot establish chain provenance on its own.

Confirmation trace: API supplies/chooses OCR -> Python canonical SHA-256 -> Python calls Node CLI -> CLI scales amount with `ethers.parseEther` and encodes IDs -> authorized wallet calls nonpayable registry -> tx.wait -> receipt hash/transaction hash JSON -> database stores record. Verification trace: database fields -> recalculate digest -> CLI verifyReceipt and distributions getter -> compare returned bytes32. Shared fallback currently severs that last provenance guarantee.

## Contract facts and scope limits

**S, high:** `AyudaChainRegistry.sol` records assertions; it neither holds nor transfers disaster-relief money. All entrypoints are nonpayable and no token/native transfer exists. `parseEther` in CLI :76/:94/:111 is an 18-decimal ledger scale for the submitted peso-like number, not evidence of an actual payout. A matched hash demonstrates equality with an operator's anchor; it does not attest recipient identity, physical handover, official appropriation or truthful OCR.

Positive properties: immutable deploying owner (:10,97-100), owner-only setOperator (:102-105), operator-or-owner gate on every recording method (:92-95), duplicate batch/allocation/distribution/general ID rejection (:118,144,171,196), nonzero IDs on each record category, nonzero receipt hash (:172), public getters/events, no beneficiary names/contact/receipt contents in normal distribution payloads, and absent verification returns `(false,0)` (:214-215). Generic records cannot be overwritten through a provided method. Revoking owner in `authorizedOperators` does not remove owner authority because the modifier explicitly accepts owner.

Policy gaps, whose required rules cannot be inferred from missing PRD: allocation records need only existing batch/unique allocation/positive amount (:142-145); no total allocated counter or batch cap exists. Distribution needs only batch existence/unique nonzero distribution ID/nonzero receipt digest (:169-172). It allows amount 0, beneficiary ID 0, payouts without any allocation, repeated beneficiary payouts under different distribution IDs, payout totals exceeding release/allocation totals, and no relationship to barangay/allocation. `anchorRecord` permits a zero `recordHash` (:195-196). `setOperator` permits zero address and has no owner transfer/recovery. These are source-proven acceptance conditions, not newly agreed feature requirements.

Privacy nuance: normal distribution submits opaque IDs/amount/digest, but release stores arbitrary public `calamityName` and `sourceAgency` (:15-16,124-125), generic anchor stores arbitrary public `recordType` (:43,201), and callers can put personal text into raw identifiers/strings. The contract cannot enforce the semantic privacy boundary. Receipt hashes also provide integrity, not secret-storage encryption.

## Node CLI, metadata and setup

**S+P, high:** CLI `toBytes32:34-41` accepts any length-66 `0x` string without its own hex validation (ethers later validates bytes32), otherwise silently slices to 31 JavaScript characters. Pure ethers probe confirmed distinct 32-character ASCII IDs with identical first 31 characters map to the same chain key. Thirty-one U+00E9 characters fail because UTF-8 is >31 bytes. Python schema examples allow up to 64 chars at database level, while request strings have no max-length constraint. This can produce backend/chain disagreement or collision, then fallback masquerading as an anchor. No shell interpolation is used by Python subprocess: its argv list avoids shell command injection.

CLI gets ABI only from compiled artifact (:12,18-20); shared metadata provides **address only** (:13,23-27). Without compiled artifact it constructs an empty-ABI contract, despite ABI being present in shared metadata. Python service always sets its own address env at :32, so its default at :22 overrides JS's deployment-metadata default if no environment address is set. Redeploying at another address needs consistent exported runtime env. Existing generated copies were byte-identical (SHA-256 `FC2E343BD75D53204E4829366CD267BBFED77683450AD9BCDFA477126C1E1CE5`), network localhost/chain 31337, deployedAt `2026-10-07T17:35:57.753Z`, 18 entries; artifact ABI compared equal. Metadata itself does not prove deployment still exists after node reset.

Python defaults RPC to localhost (:20); standalone JS/hardhat default RPC to public Amoy (`blockchain_client.js:30`, `hardhat.config.js:4`). Public Hardhat development signing-key defaults exist in all three paths; values omitted here. None of Python service/CLI loads `.env`. Hardhat tries optional dotenv (:2), swallowing absence; package manifest and lock contain no dotenv package. Root launcher/env review is separate. A public-network deploy script exists (`contracts/package.json:10`); **not run**.

`_execute_cli:36-49` starts a new Node process per operation, 8-second timeout, scans reverse stdout for one-line JSON, ignores subprocess exit code, and returns parsed JSON without schema checking. Node catches exceptions and emits `success:false` JSON (:147-151) without setting a failing process exit status. Network timeouts/read failures, chain revert, malformed IDs/amounts, missing ABI, unauthorized key, wrong contract address and missing Node may all become the same positive verification fallback. A timeout can occur after broadcast; later mining would require reconciliation to avoid ambiguous state. No pending tx retention/retry/idempotence reconciliation is implemented in this service.

Deploy producer `deploy.js:15-17` submits one real contract deployment; :24-33 reads compiled artifact and creates metadata; :39-43 creates directories and overwrites exactly both tracked metadata files. It does not update runtime `.env`. Contract compile writes artifacts/cache; test launches fresh local in-process contracts. npm installation may execute native install hooks (lock entries fsevents :4612, keccak :5838, secp256k1 :7252). Lock pins Hardhat 2.29.1, ethers 6.17.0, toolbox 5.0.0; EDR 0.12.0-next.23 requires Node >=20. No dependency addition/install was done by this track.

## Receipt/seed behavior

**S+P, high:** shared `save_sample_receipt:137-150` rewrites `sample_relief_receipt.svg` on call. Both active `server.py:30` and dormant `main.py:49` call it during module import. Do not import either server against the working tree for passive inspection. Dormant main also creates receipt directory (:48) and startup creates database tables (:58). Dormant seeder drops/recreates every model table including audit events (`seed_demo.py:20-22`), overwrites receipt (:27), and attempts 10 chain writes (release + 4 allocations + 5 confirmations) before one database commit. Demo reset invokes it (`main.py:460-464`) without resetting the chain.

Repeated seed uses the same append-only chain IDs. Existing IDs revert, service invents new hashes, and seeder persists them as if anchored. Literal tx fallback strings also exist (:45,77,187), with allocation/distribution examples not valid hexadecimal tx hashes. It never reconciles an existing chain record/tx. No success check protects local confirmed states or anchored audit language (:207). Seed FLAGGED confidence/status values are hand-set, not resolver outputs; anomaly labels are seeded without evaluating detector.

Static receipt/OCR identify BEN-0001 as Juan Dela Cruz (`receipt_generator.py:16-17,143-144`; SVG :40-43), but dormant BEN-0001 and DIST-0001 are Roberto Ramos (`seed_demo.py:104,164`). All five seeded distributions point to that single SVG and use the same OCR (:177,196-197), whose DIST/BEN/batch metadata remains fixed. Structured top-level hash metadata can consequently contradict the receipt text without rejection. Receipt producer contains a visible fictional-demo footer (SVG :94), but its proof seal asserts “anchored on Polygon” and “Digest Anchored” regardless of network/state (:88-90). QR is decorative rectangles, not an encoded credential (`receipt_generator.py:100-123`, SVG :60-83), and no biometric acquisition is implemented despite OCR's “BIOMETRIC CONFIRMATION” (:22).

SVG generator inserts IDs, household_name and barangay_name raw into XML text (`receipt_generator.py:70,74,80,83,87`). Pure in-memory probe confirmed a supplied `</text><script>...</script><text>` appears raw. Current callers produce only fixed sample values, so this is a latent unsafe producer boundary, **not a demonstrated reachable active upload exploit**.

CSV contains ten named/address/DOB-like fictional fixtures, but its DAFAC suffixes are three digits (`DFC-2026-901` etc., :2-11), not AGENTS' four-digit `DFC-2026-XXXX` form. No evidence of actual persons was found; do not imply these fixture names are real citizens. Dormant fixtures use synthetic BEN/RELIEF IDs; fixture provenance is labelled demo in seeder docstring and receipt footer.

## Dormant FastAPI defects: do not attribute to active routes

**S, high:** no authentication dependencies across :60-464; wildcard credentialed CORS (:40-43); unguarded demo reset (:460). Registration marks nonduplicate beneficiaries `VERIFIED`/`APPROVED` with “Auto-verified” (:285-287), violating human decision invariant. Nonduplicate registration writes **no** audit event (:306-314); duplicate registration logs only flag. Manual verify accepts arbitrary `status` string (schema :82), maps every non-VERIFIED string to review REJECTED (main :324-325), and retains duplicate flags even after approval. It has no actor identity in audit rows.

Registration does not check batch existence; plain SQLite FKs are not enabled in `database.py`. Distribution checks beneficiary existence and distribution ID uniqueness only (:349-355): no verified/review-status eligibility, beneficiary/batch correspondence, duplicate-beneficiary payout cap, allocation/budget or anomaly check. All failures from chain still become local `CONFIRMED` (:391) with an anchored audit statement (:399). Amount request gt=0 exists in Pydantic (schema :110), but no two-decimal/finite-money policy; statuses have no enum. Default `receipt_filename` is `sample_relief_receipt.jpg` (schema :112) although only SVG sample exists; main fallback to SVG occurs only when filename falsy (:381).

Dormant models use Float money (:17,35,74,94), beneficiary's uselist=False relationship without a unique distribution beneficiary column (:64,72), cascaded batch deletes (:22-24), no DB append-only audit enforcement and no actor/before-after metadata. These are independent from active SQLite definitions. Dormant dashboard always selects `.first()` rather than active/status-selected batch (:74), sums every distribution regardless of status (:84), clamps over-allocation to zero unallocated funds (:85), and aggregates recent audit events across batches (:95). Health says healthy regardless of chain (:65). These source facts should only be addressed if maintainer selects this backend.

## Detection engine and real test scope

Resolver is deterministic fuzzy string matching, not a trained identity model (`entity_resolution.py:78-118,152-186`). Its subset-token bonus can score an abbreviated/common name 0.88 (:115-116), and same barangay multiplies by 1.08 (:164). Confidence is a similarity heuristic, not a calibrated probability of duplicate identity. It returns an explicit human-review disclaimer (:187). `normalize_name` docstring claims sorted tokens (:38) but implementation preserves order (:56); token_similarity separately sorts for edit score (:100-101). This mismatch is local documentation, not a failing algorithm requirement.

CSV function parses all rows without required-header validation (:195-197), compares every pair (:200), uses only first/last name and street/barangay/city with DAFAC boost (:201-216), and ignores DOB/middle_initial/family_size. Missing address gets default score 50 (:208), enough for exact-name-only pair to meet 80 (60+20), even when `barangay_id` exists but expected `barangay` does not. Executed probes: header `garbage` returns success/1 processed/0 pairs; same-name `household_name,barangay_id` CSV flags a pair without a recognized address. All-pairs comparison is quadratic and returns pair counts, not unique flagged people. Same DAFAC but totally dissimilar name/address may not exceed 60 and get no special flag (:215).

Anomaly detector's “velocity” comment does not correspond to time logic: it never reads distributed_at. Rules are nonstandard amount (:33-37), any prior same-beneficiary record in supplied list (:40-43), and barangay amount stdev >1500 after >=10 records (:46-53). Macro totals are a returned alert only (:69-84). Repository search found no call to `analyze_distribution` or `evaluate_batch_health` from active or dormant servers; both instantiate unused detector objects. Therefore runtime anomaly detection claims exceed current integration.

Executed `python -B backend/test_backend.py`: **8 tests passed**, 0.001s. They cover normalization, one known duplicate, one unlike name, nonstandard amount, standard amount, canonical key ordering, same-input receipt digest and changed OCR hash. They do not test APIs/models despite suite docstring, database/audit, authentication, chain failures/absence, genuine anchoring, public verification, CSV, receipt image/identity binding, monetary normalization, cross-layer IDs or anomaly runtime wiring.

Contract suite has **9** cases: owner/default operator, authorize operator, unauthorized release, release event/state, duplicate release, allocation event/state, distribution event/state, matching/mismatched verification, generic anchor event/state. Distribution tests :83-113 **do not allocate before payout**, establishing current expected permissiveness. Test receipt bytes32 uses keccak (:13), not Python canonical SHA-256; contract accepts arbitrary nonzero digest and no end-to-end hash encoding is tested. Missing: unauthorized allocation/distribution/anchor/setOperator, revocation, zero/duplicate/missing-parent edge cases, absent verifier record, allocation/distribution budget or beneficiary constraints, CLI truncation and failure propagation, zero generic digest and generated metadata/runtime-address wiring.

## Reproducible probes and useful isolated scenarios

The safe probe used `BlockchainService()` with `_execute_cli` replaced in memory; it neither submits chain calls nor imports application/database modules. From repository root, in PowerShell, pipe this to `python -B -`:

```python
import pathlib, sys
sys.path.insert(0, str(pathlib.Path('backend').resolve()))
from app.services.blockchain import BlockchainService
from app.services.hasher import compute_receipt_hash
s = BlockchainService()
h = compute_receipt_hash('DIST-PROBE', 'BEN-PROBE', 'BATCH-PROBE', 5000, 'fictional text')
for result in ({'success': False, 'error': 'forced unavailable'},
               {'success': True, 'exists': False, 'matched': False}):
    s._execute_cli = lambda args, value=result: value.copy()
    response = s.verify_receipt('DIST-PROBE', h)
    print({k: response[k] for k in ('success', 'matched', 'exists')})
```

Expected **current defect** in each case: all three booleans true. A correction should instead preserve explicit unavailable versus absent versus mismatch versus anchored-match states, and never supply a made-up on-chain digest/tx hash.

Useful root-owned isolated runtime scenarios:

1. Reachable fresh chain without registry, then registry with absent distribution, then RPC down: verify an existing local record in each case; currently service source predicts positive verification across all three.
2. Working anchored record: alter local amount/OCR and verify mismatch; alter only beneficiary name or referenced SVG and verify unchanged hash to document the current compatibility boundary.
3. Release/allocate/confirm with chain failure or unauthorized operator: inspect HTTP status, local confirmed state and audit tx hashes; fake fallback is already proven in-memory.
4. Re-run demo reset against same deployed contract: inspect duplicate-revert handling and divergent claimed tx hashes, not just restored local row counts.
5. Long ASCII IDs sharing first 31 chars; multi-byte ID >31 UTF-8 bytes; scientific notation/tiny subcent amounts: observe ID collision/ethers validation and local status after failure.
6. On isolated contract: create a batch amount 1; allocation amount 2; zero-amount/zero-beneficiary distribution; repeated beneficiary under fresh distribution IDs; distribution with no allocation. Source predicts each accepted except uint256-negative input. Record these as current behavior while policy remains unconfirmed.
7. Missing compile artifact but existing deployment metadata ABI; changed deployment address but unset CONTRACT_ADDRESS; compare runtime readiness/status and verify results.
8. Public receipt request and beneficiary/distribution listing with no role; check that off-chain storage is not equated with privacy/access protection. Parent owns active-route result.

## Impeccable Assessment B

CLI ran exactly `node C:/Users/Yushin/.agents/skills/impeccable/scripts/detect.mjs --json frontend/app frontend/components`, exit **2**, with valid array JSON persisted to `impeccable-detector.json`; provenance persisted to `impeccable-detector-run.txt`. No `.impeccable/critique/ignore.md` exists. Nine warnings: 5 gray-on-color, 2 side-tab, 2 border-accent-on-rounded; categories quality=5, slop=4. There are no accessibility-error assertions in this CLI result.

| Rule and source | Independent evidence check |
|---|---|
| gray-on-color, `beneficiaries/page.tsx:302` | Variant conflation false positive: normal text slate-400, hover simultaneously changes icon to rose-600 and background rose-50. Other accessibility properties need browser review. |
| side-tab, `distributions/page.tsx:525,526` | False positives: these are deliberate scanner corner brackets, not accent borders on content cards. |
| border-accent-on-rounded, `distributions/page.tsx:525,527` | Same scanner brackets, false positives. |
| gray-on-color, `verify/page.tsx:155,167,179` | Dark slate-700 on very pale hover backgrounds; class occurrence is real, but warning is an aesthetic heuristic, not measured contrast failure. Selected state has separate rose/emerald text. Treat as low-confidence minor issue unless browser contrast proves impact. |
| gray-on-color, `Navbar.tsx:148` | Conditional-branch conflation false positive: active branch is blue-600/white; inactive branch is slate-400 with no blue background. |

Six of nine warnings are clear structural false positives; the other three do not establish a usability/accessibility defect without measured browser evidence. Do not elevate detector heuristic warnings above the demonstrated trust/privacy/state failures.

### Completed browser evidence

**P+D, high:** Assessment B used its own Chrome headless browser/context and fresh tabs via the exposed Node REPL/Playwright runtime. Target `http://127.0.0.1:3000` was the root agent's isolated stack at `C:/Users/Yushin/AppData/Local/Temp/ayudachain-investigation-ba4heaqr`, active `server.py` and local chain. DOM preflight set/restored `document.title` and appended/executed/removed a script successfully. A separate bundled `live-server.mjs` helper was launched with `Start-Process -WindowStyle Hidden`, PID **32428**, port **8400**, snapshot-only working directory. It re-rooted its metadata to snapshot `frontend/.impeccable/live/server.json`; original source tree was not changed.

`http://localhost:8400/detect.js` injection succeeded. Browser automatic scans logged impeccable summaries. To obtain clean structured evidence, later tabs set `autoScan:false`, ran `impeccableDetect()` **before** overlay rendering, then rendered with `impeccableScan()` and checked overlay nodes. A first post-overlay recollection caused the detector to treat its own overlays as `text-occlusion`; that contaminated intermediate artifact was replaced by the clean pre-overlay capture below. The retained JSON contains no such occlusion assertions. This is detector instrumentation behavior, not a product defect.

| Desktop route, 1440×1000 | Element groups / individual rule findings | Clean rule counts |
|---|---:|---|
| `/` | 46 / 48 | tiny-text 12; undersized-ui-text 10; low-contrast 12; nested-cards 7; line-length 2; gpt-thin-border-wide-shadow, all-caps-body, cramped-padding, overused-font, skipped-heading 1 each |
| `/beneficiaries` | 47 / 47 | undersized-ui-text 39; tiny-text 2; nested-cards 2; line-length, cramped-padding, low-contrast, overused-font 1 each |
| `/distributions` | 56 / 60 | tiny-text 25; undersized-ui-text 21; low-contrast 6; nested-cards 5; line-length, overused-font, em-dash-overuse 1 each |
| `/verify` | 29 / 32 | undersized-ui-text 11; tiny-text 8; nested-cards 5; line-length 3; all-caps-body 2; low-contrast, overused-font, em-dash-overuse 1 each |

Repeated navbar/footer/data-row warnings explain much of these counts; they are **187 rule occurrences across 178 element groups**, not 187 independent UX defects. Root simultaneously exercised isolated data workflows, so counts are captured-state values and can differ from a fresh five-distribution seed. No API fetch failure or service-restart fault was observed in these completed browser checks. Desktop initial DOM and mobile checked routes had no document-level horizontal overflow.

Browser detector caught concrete legibility signals absent from CLI: homepage audit timestamp text `#90a1b9` on white **2.6:1** (`frontend/app/page.tsx:275`), allocation summary `#009966` on white **3.7:1** (:204), distribution receipt metadata `#90a1b9` on `#f8fafc` **2.5:1** (`distributions/page.tsx:316`), several 10–11px functional labels, and footer secondary text **3.7:1** on dark background. These are detector-computed style ratios; visual contrast over nonuniform backgrounds was not independently sampled, and this is not a complete WCAG conformance audit. Scanner corner-bracket CLI false positives remain aesthetic nonissues. Browser cramped-padding on the table wrapper is also structurally misleading: cells intentionally own padding. Overused-font and nested-cards are low-priority stylistic heuristics.

At **390×844**, `/beneficiaries`, `/distributions`, `/verify` remained within document width 390. Visible inputs/selects had **zero associated label elements** and no aria-label; source additionally confirms adjacent labels omit htmlFor/id (`Navbar.tsx:109`; `distributions/page.tsx:210,220,255,256`; `verify/page.tsx:96,99`). Placeholder text provides limited input guidance but not a persistent proper label. Inspect/View Receipt row buttons measured **16px** high; reset 28px; scanner launcher 20.7px; verification recheck 32px. These are touch-target opportunity measurements, not a claim of a specific WCAG violation without spacing/exception analysis.

Read-only client-modal probes opened scanner and beneficiary inspector, then pressed Escape. Both had **zero dialog/aria-modal semantics**, retained focus on their launcher, and exposed **one visible icon-only close button with no text/aria-label/aria-labelledby/title**. Escape did not dismiss scanner; inspector's unlabeled close button remained after Escape. Relevant source: `distributions/page.tsx:509-511`; `beneficiaries/page.tsx:323`. No payout/registration/reset or CSV submission was performed.

An independent screenshot of `/verify` confirmed the result headline **“100% AUTHENTIC & UNALTERED GOVERNMENT AID”** and paragraph claiming the family received exact cash. The actual mechanism establishes an operator-anchored metadata/text hash match; physical handover and independently verified beneficiary identity are outside its demonstrated evidence. Its synthetic/demo context appears in the footer, while government/authenticity language dominates the result. This is a concrete trust-copy issue, not a detector style complaint.

Evidence files: `impeccable-browser-detector.json` (clean structured rule output, selectors, ratios, console and overlay counts), `impeccable-browser-mobile.json` (dimensions/label associations/button heights), `impeccable-browser-modals.json` (semantics/focus/Escape/close-button results). Helper stopped gracefully using `node .../live-server.mjs stop --keep-inject` from snapshot frontend; own browser and all contexts/tabs closed. Overlays existed only in ephemeral **headless test tabs**; no human-visible browser tab/overlay is available, and none should be claimed in the final report.
