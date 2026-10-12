# Truthful blockchain verification

Completed 2026-10-12 as the first bounded section 4 task, based on [retained duplicate records, PR #14](https://github.com/andreirtc/ayudachain/pull/14). All records, amounts, wallets, and transactions are synthetic demo data on a local chain or public testnet.

## Evidence and outcomes

The blockchain service no longer generates fallback transaction hashes or turns failed/missing receipt reads into successful verification. The seeder and release/allocation/payout endpoints save transaction metadata only when the CLI reports successful confirmation and supplies a valid hash. Failed operations leave the hash null. Seeded payout audit text describes the locally recorded fictional payout without an unconditional claim that it was anchored.

Receipt verification recalculates the current local hash and requires a successful read of the configured chain and contract. The response exposes four outcomes:

- **VERIFIED**: An existing receipt has a valid observed hash and timestamp, and both the contract match result and independent hash comparison agree.
- **MISMATCH**: A successful read finds an existing different receipt hash, with consistent contract/comparison results.
- **UNANCHORED**: A successful contract read reports no receipt record.
- **UNAVAILABLE**: The read fails, configuration differs from the observed chain/contract, required evidence is missing/malformed, or the returned evidence is inconsistent.

Only VERIFIED sets `is_verified=true`. The on-chain hash and timestamp are nullable and are never copied from local data or generated from the current time. An unknown local record still returns 404. A stored transaction hash is historical metadata rather than evidence for the comparison; the verification response does not construct an explorer link from it.

The CLI reads the actual chain ID instead of inferring the network from the RPC URL. It rejects a configured chain-ID mismatch, absent ABI, or absent contract bytecode. Receipt/status reads use a provider without needing a signing key. Writes report success only after a mined receipt reports successful execution. Nonzero process exits, malformed output, and timeouts remain failures in the Python adapter.

## Interface

Open [the current verification preview](http://127.0.0.1:3001/verify). The page displays the four backend outcomes with separate labels and states, loading/empty/error/retry feedback, local record context, and optional hash/contract details. It no longer labels unavailable or missing anchors as corruption, supplies sample household names or amounts, invents successful transaction text, or claims that a matching hash proves cash delivery or household-name integrity. Selecting another receipt clears the result; cancelled/stale lookups cannot overwrite the current selection.

The old fraud-scenario buttons changed displayed values and results without changing the database. They have been removed. Building an actual interactive synthetic tampering/restoration workflow remains a later section 4 task. Batch/allocation views also no longer fabricate a fallback release hash or a successful anchor label when a hash is absent.

## Live preview validation

The original chain at port 8545 runs an older contract whose receipt getter is incompatible with the current ABI. The actual read returned **could not decode result data**. The new verification flow correctly returned UNAVAILABLE; the previous fallback had hidden this incompatibility. RPC/bytecode health alone does not guarantee that a particular receipt getter is compatible.

The original provider pane, database, and chain were left unchanged. For current-contract validation, a separate local chain was started at **http://127.0.0.1:8546**, chain 31337, and the current registry was deployed there. The copied preview database's one batch, four allocations, and six receipts were anchored using real local test transactions. Receipt contents and hashes were preserved; only copied preview transaction metadata was updated. All six receipt comparisons returned VERIFIED.

A separate temporary copy of that database exercised the real chain through the FastAPI app: VERIFIED -> change amount -> MISMATCH -> restore amount -> VERIFIED; change the local record ID to one absent from the contract -> UNANCHORED; point the lookup at an unreachable local RPC -> UNAVAILABLE; restore the RPC -> VERIFIED. The preview and original datasets were unchanged by these checks.

The running frontend is **http://127.0.0.1:3001**, backend **http://127.0.0.1:8000**, preview RPC **http://127.0.0.1:8546**, and preview contract **0x5FbDB2315678afecb367f032d93F642f64180aa3**. The RPC override exists in the preview backend process; default repository configuration still points to port 8545. Restarting without the matching current-contract preview configuration may correctly return unavailable verification. Automatic chain recovery is not implemented by this setup.

## Checks

- API suite: 76 tests pass, including unavailable/missing/mismatch/verified outcomes, real local-row tampering, malformed/inconsistent/wrong-chain/wrong-contract evidence, lookup exceptions, and failed release/allocation/seed operations without fabricated hashes.
- Backend unit suite: 21 tests pass, including service failure propagation, missing configuration, timeouts/nonzero exits/malformed output, and transaction hash acceptance.
- Contract/CLI suite: 21 tests pass (13 registry tests and eight CLI evidence checks), including missing contracts/ABI, wrong chains, read-only queries, and failed transaction receipts.
- Separate frontend TypeScript check, production build, and git diff --check pass. The existing build still skips embedded type validation/linting; section 7 addresses that configuration.
- Live local-chain checks passed for all four states and restoration. Preview page and JavaScript assets return HTTP 200. Browser visual/interactive checks remain pending because no browser was available in this session.

## Remaining work

Recorded payout state is still distinct from proof of an anchor: the existing CONFIRMED database status currently means a recorded fictional payout. Explicit pending/submitted/confirmed/failed anchor states, confirmation metadata, retries, reconciliation, and synchronized reset/recovery remain next in section 4.

Previously persisted transaction metadata is retained and is not automatically trusted or erased by this change. Existing receipt hashing covers IDs, batch, amount, OCR, and verification method; it does not yet cover household names, allocation links, or actual receipt file contents. The versioned immutable receipt snapshot remains planned. A mismatch reports different hash evidence; it does not identify an actor or prove corruption. Review/audit history remains local, and matching hashes cannot prove physical cash delivery.
