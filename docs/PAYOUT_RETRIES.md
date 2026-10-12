# Payout retries

Implemented 2026-10-12 as the next bounded section 3 task. Predecessor: [one payout per household per batch, PR #11](https://github.com/andreirtc/ayudachain/pull/11). All records and amounts remain synthetic.

## Request behavior

Send a stable `Idempotency-Key` to `POST /api/distributions/confirm` and reuse it with the same payload on retries. Omit `distribution_id` for a server-generated `DIST-<UUID>`, or provide a stable ID for compatibility. A legacy caller may use its stable distribution ID without a header. A request with neither identity is rejected with 422.

The first accepted request returns 201. A matching retry returns the persisted payout with 200, even if beneficiary eligibility or batch status has subsequently changed. Changes to beneficiary, batch, amount, caller-supplied ID, verification method, receipt filename, or OCR content return 409 when the key/ID is reused. Decimal spellings that resolve to the same centavos and equivalent effective defaults compare equally. A different key cannot claim an existing distribution ID.

The database enforces a unique key and the existing unique household/batch constraint. Concurrent workers that lose an insert race roll back and return the winning payout for a matching request. No additional payout or audit event is written, and only the insert winner attempts anchoring.

The payout form sends a random 128-bit key and lets the server generate its ID. It retains the key and exact payload for retries while that page remains open; editing details creates a new request identity. A synchronous guard blocks repeated clicks, inputs are disabled while submitting, and errors retain the inputs. The success state is set after the API response. The form no longer derives IDs from four timestamp digits or displays invented local progress steps.

## Persistence and failure behavior

The payout, retry metadata, and audit event commit before contacting the blockchain. A failed initial database commit produces no anchor submission. A blockchain exception or unsuccessful response leaves the recorded payout available for replay with no invented transaction hash. If the process stops after the first commit but before submitting, the record remains available and is not automatically submitted by a payout retry.

If anchoring succeeds but storing transaction metadata fails, the payout still exists. Retrying returns the saved record without another anchor submission. Its local transaction hash may be absent even though the receipt is on-chain. A replay concurrent with anchoring can likewise return before anchor metadata is available; later reads may contain the transaction hash.

Startup adds nullable retry columns and a unique index to the preceding SQLite schema without deleting or re-anchoring historical payouts. Migration startup is serialized and recovers an interrupted index creation. Older schemas missing prior accounting/uniqueness changes still follow the existing incompatible-schema startup guard. Historical payouts have null retry metadata and cannot be reclaimed using an identical-looking request.

## Validation

- API suite: 43 tests pass, including durable replay, changed payload conflicts, invalid identities, database uniqueness, concurrent requests with the process lock disabled, initial and post-anchor database failures, chain exceptions, and non-destructive/interrupted migration.
- Backend hashing/entity-resolution suite: 12 tests pass.
- Contract suite: 13 tests pass.
- Separate frontend TypeScript check and production build pass. The existing Next.js build configuration still skips its embedded type validation and linting; removing that setting belongs to section 7.
- Browser connection was attempted, but the browser runtime listed no available browsers. Visual and interactive verification remains pending.

## Remaining work

Payout replay does not retry anchoring. Explicit anchor states, receipt confirmation, reconciliation after unknown transaction outcomes, and restarted-chain recovery remain in section 4. The old fabricated fallback behavior has since been removed in [truthful verification](TRUTHFUL_VERIFICATION.md). New operations preserve failures and do not invent hashes; existing historical transaction metadata still needs reconciliation. Database commit-before-anchor cannot guarantee exactly one submission across a process crash; it deliberately prevents automatic resubmission until reconciliation exists.

The form key is held in memory, so refreshing the page discards the pending request identity. Persistent offline queues and reconnect behavior remain in section 6. A fresh request still encounters the household/batch uniqueness protection if an earlier payout was saved. The current `CONFIRMED` status means recorded payout, not confirmed anchor or physical cash delivery. Demo reset intentionally deletes the synthetic dataset and its retry identities.
