# Durable payout anchor recovery

Bounded follow-up to [PR #18](https://github.com/andreirtc/ayudachain/pull/18), implemented 2026-10-13. This adds durable anchor recovery for new payouts while keeping existing SQLite accounting, receipt hashing, aliases, review history and payout replay. It adapts the workmate's saved signed-transaction and observed-confirmation pattern without importing its PostgreSQL schema or evidence registry.

## What a saved payout means

A recorded payout is a durable local business record. It reserves the fictional allocation budget and household/batch uniqueness before any blockchain write. It is not proof of cash delivery or a confirmed anchor. Its recovery job is committed atomically with the payout and audit event; no job is created for a rejected or rolled-back payout.

- PENDING: no signed transaction has been prepared.
- SUBMITTED: an exact signed transaction/hash is saved. It may be prepared but unsent, pending, or uncertain after a lost response. This state never claims network acceptance or mining.
- CONFIRMED: a successful mined receipt, its canonical block and full registry record were observed for the saved transaction.
- FAILED: preparation failed or recovery found evidence needing investigation. The payout and its accounting reservation remain recorded.

Confirmation records chain/address, candidate transaction hash, block number/hash, registry timestamp and observation time. Job state is separate from the existing payout status field. A confirmed observation is historical evidence with one observed mined block, not irreversible finality. Current receipt verification still has its four independent outcomes.

## Recovery boundary

New jobs capture the immutable submission parameters: existing distribution/household/batch/allocation IDs, exact centavos and receipt hash, plus chain/address configuration. This is not the planned complete versioned receipt snapshot; household names and raw file bytes are still outside the current hash coverage.

The CLI prepares and signs without broadcasting. The API saves the exact signed envelope and its candidate hash before starting the broadcast subprocess. Raw envelopes travel through stdin and remain private database fields; public/private response schemas omit them. Error responses use safe codes without echoing signing keys, raw transactions or RPC request bodies.

Recovery checks the saved chain/address, runtime-code hash and a retained block hash before replay. It validates the envelope's hash, target, encoded payout arguments and zero value. It checks any existing receipt and registry record before sending. Only the identical stored transaction can be resent. Unknown consumed nonce, record/hash changes, conflicting receipt data, revert or lost deployment cause refusal; recovery never invents a replacement nonce, payout ID or successful hash.

A successful confirmation requires the exact candidate transaction's successful receipt to the pinned contract, a canonical matching block, and registry fields matching the saved IDs, allocation, amount, hash and timestamp. The API independently checks reported confirmation fields and the current saved payout before applying metadata. Observations append to a local history; one confirmation audit event is added, and repeated rechecks do not duplicate it.

SQLite write transactions acquire the lease using [BEGIN IMMEDIATE](https://www.sqlite.org/lang_transaction.html). One expiring, owner-checked lease coordinates payout workers and legacy funding CLI writes. A stale worker cannot delete another worker's lease or persist an envelope after expiry. Unresolved signed jobs block preparation for other payouts and legacy signer use. An interrupted lease can expire; the envelope/job then remains recoverable. External wallet activity is outside this lease and is handled by the nonce/conflict refusal.

The signing/broadcast split uses the official [ethers signer and provider APIs](https://docs.ethers.org/v6/api/providers/). Automatic replacement after a revert, fee changes and multi-signer throughput are not implemented.

## User workflow and permissions

On /distributions, the success card distinguishes Payout recorded from its anchor state. Disbursing staff can choose Recover anchor or Recheck anchor. After refresh, expand Anchor status and recovery on the recorded payout to access the same job. Failures stay visible and leave the payout intact. Offline browsers disable recovery; reconnecting does not submit automatically.

POST /api/distributions/{distribution_id}/anchor/retry is a separate Disbursing-only operation with CSRF/origin checks and own-barangay scope. It returns the existing payout with current anchor_job metadata; it never creates another payout. Auditor, DSWD, Barangay, Beneficiary and anonymous requests cannot invoke recovery. Permitted private readers can inspect the returned job metadata. Public verification remains limited and exposes no envelope.

Ordinary POST /api/distributions/confirm replay returns its recorded result without processing the anchor job. A new payout attempts its job once after recording. Further work is explicit recovery; there is no background retry daemon in this PR.

Older/seeded payouts retain their receipt hashes and historical transaction references. They have no new job/envelope and are labeled Anchor not tracked. Their recovery endpoint returns 409; their existing receipt checks continue to work. No historical proof is rehashed or silently reanchored.

## Validation

- 76 business/API regressions, 19 session/permission checks and 10 recovery fault tests passed using isolated databases and role-authenticated clients. Recovery tests cover durable envelope before send, interruption, lost mined metadata, repeat recovery/audit uniqueness, before/during-send record changes, malformed confirmation, scope/CSRF, lease concurrency/expiry, unresolved signer blocking and additive startup.
- 21 backend units and 21 existing contract/CLI tests passed. Seven frontend Node tests, independent TypeScript and production build passed.
- 16 headless Edge Playwright tests passed at desktop 1440x900 and phone 390x844. The payout case now exercises failed recovery, persisted attempts, refresh and available recovery controls, one recorded payout, and the exact receipt link. Its isolated API explicitly reports the chain unavailable.
- Five real-chain scenarios passed on an owned disposable Hardhat node at 8547: mined confirmation/current verification, lost mined response with the original hash and no new transaction, actual pending transaction followed by mining, unknown nonce consumption refusal, and deployment loss with payout/proof/envelope preservation.
- Six browser screenshots were captured; payout layouts at both sizes were inspected. The original database, original chain/provider session, groupmate branch and retained deployment artifacts were not modified. Test-owned services stop on completion.

Run the real-chain checks from the repository root with node contracts/scripts/test_payout_anchor_live.js. It refuses an occupied port and deploys directly from compiled artifacts without rewriting retained deployment files. The backend live check refuses the default RPC and needs this helper. Run isolated faults with backend/.venv/Scripts/python.exe backend/test_payout_anchors.py.

## Still separate work

Release/allocation durability, importing historical recovery evidence, operator repair/replacement approvals, signer administration, reorg/finality policy, a background worker/backoff, synchronized reset recovery and complete immutable versioned identity/document receipts remain unfinished. Deployment loss is detected and paused; it is not repaired by resetting or recreating funds. Existing runtime dependency advisories still precede shared hosting.

These are synthetic transactions on local/test networks only. No real recipient, funds or mainnet use is enabled. Anchor job/observation history is locally editable by a database operator and is not itself blockchain-protected history.
