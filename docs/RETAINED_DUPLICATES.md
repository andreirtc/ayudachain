# Retained duplicate household records

Completed 2026-10-12 as the final bounded section 3 task, based on [human review, PR #13](https://github.com/andreirtc/ayudachain/pull/13). All records, reviewers, and payouts are synthetic.

## Resolution workflow

Open [the preview registry](http://127.0.0.1:3001/beneficiaries), choose an officer or auditor demo view, and inspect a household. Enter the demo reviewer and reason, expand **Resolve as a duplicate**, choose the surviving household, and select **Mark duplicate and retain history**. A suggested match can populate the selector, but only this explicit human action resolves the duplicate.

The duplicate keeps its original ID, household details, DAFAC ID, match evidence, payout records, receipt files/hashes, and earlier reviews. Its `record_status` becomes `DUPLICATE`, its `canonical_beneficiary_id` identifies the surviving household, and its verification/review statuses become `REJECTED`. Active detection flags clear. A new decision records the chosen survivor separately from the original detection match, together with the reason, demo reviewer, UTC timestamp, prior notes/state, and flags. A local audit event accompanies the decision.

The default registry shows active records. Enable **Include historical duplicates** to inspect retained records and their histories. Individual detail and review-history URLs continue to return those records. The dashboard counts active households separately from historical duplicates, while payout counts, amounts, and allocation budgets continue to include all historical payouts.

Deletion buttons and automatic delete fallbacks are removed. The old DELETE endpoint and POST /delete fallback return 410 without changing any records. Resolution requires explicit target/reason/reviewer inputs.

## Consistency rules

Both records must exist, differ, and belong to the same batch. The surviving record must be active. Link chains and cycles are rejected, as is retiring a surviving household that already has linked duplicates. A historical decision cannot be changed through this endpoint or reopened with ordinary beneficiary review. An identical resolution retry returns the stored record without another decision or audit event; changed inputs return 409.

A new payout requires an active, approved household and checks whether that household or any of its direct linked aliases was already paid in the batch. Paid duplicates can be linked, including cases where both records already have payouts: those payouts remain as evidence and stay in totals. No further payout is permitted for the resulting group. Existing payout idempotency keys still return their saved payout after its household becomes a historical duplicate.

SQLite claims the write lock before payout eligibility, review, or link checks. A payout concurrent with duplicate resolution therefore waits for the link decision before checking the group. Duplicate status, link decision, and audit event commit atomically; a failed database commit leaves all three unchanged. The contract still enforces one payout per beneficiary ID; alias grouping is enforced by the supported backend API.

Startup adds retained-status and survivor-link fields to beneficiaries and a nullable decision target to review history without deleting prior rows. Existing rows default to ACTIVE. SQLite upgrades and required indexes are safe to run repeatedly.

## Validation

- API suite: 66 tests pass. Added coverage includes disabled delete routes, retained registry/reviews/receipts, paid and unpaid linked groups, payout replay after resolution, invalid/self/cross-batch links, chains/cycles/reparenting, input validation, transaction rollback, repeated concurrent requests, payout/link races without the process lock, and preserved prior rows during migration.
- Backend hashing/entity-resolution suite: 12 tests pass. Contract suite: 13 tests pass.
- Separate TypeScript check, frontend production build, and git diff --check pass. The existing build still skips its embedded type validation/linting; section 7 addresses that configuration.
- Refreshed preview registry/dashboard/review history/OpenAPI and beneficiary page/assets respond successfully. The copied preview retains 24 synthetic records and six original payouts after migration.
- Browser visual/interaction testing remains pending; no browser was available in this session.

## Remaining limits

Reviewer identities are caller supplied demo labels; authenticated permissions remain section 5. History and links are local and are not blockchain protected. There is no reversal or reparenting workflow for a mistaken link, and previously deleted records cannot be recovered by this change. SQLite is the supported demo persistence layer; hosted database coordination still requires its own validation. Demo reset intentionally removes all synthetic records and history. [Truthful verification](TRUTHFUL_VERIFICATION.md) now removes generated fallback evidence and distinguishes the four lookup outcomes. Explicit anchoring states and safe reconciliation remain the next task.
