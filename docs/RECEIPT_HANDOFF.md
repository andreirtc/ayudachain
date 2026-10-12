# Exact receipt handoff

Implemented as one bounded frontend follow-up to [PR #15](https://github.com/andreirtc/ayudachain/pull/15). All households, payouts and money remain synthetic.

Previously, a newly recorded payout linked to plain `/verify`, which could open a different receipt. A missing explicit reference also silently fell back to the first recorded receipt. That could make a valid check appear to concern the payout the user intended to inspect.

The confirmation now shows the saved household, amount and receipt reference, with **Check this receipt** linking to the exact returned ID. Hashes and transaction metadata are expandable. Recorded payout rows and receipt previews share the same encoded link builder.

Verification resolves an explicit ID only when it is present in the loaded records. Unknown and empty references show **Receipt not found**, with no substitute check. Choosing a receipt updates its URL so a refresh or shared link keeps that reference. Direct `/verify` entry selects the first available receipt without assuming `DIST-0001`. Loading a new reference hides the previous household and check result; obsolete reads remain ignored.

Confirmation and payout rows distinguish recorded payouts, presence of anchor transaction metadata and fresh integrity checks. No transaction reference implies current verification, and a missing local transaction reference does not establish an absent on-chain anchor. Payout replay still does not retry anchoring. The existing verification API remains the authority for VERIFIED, MISMATCH, UNANCHORED and UNAVAILABLE.

## Validation

- Four Node receipt-navigation regression tests passed (`node --test tests/receipt-navigation.test.mjs`, frontend directory, Node 24).
- Independent TypeScript checking passed (`node node_modules/typescript/bin/tsc --noEmit --incremental false`).
- Production build passed. Its existing embedded type validation and lint skips remain; lint is not claimed.
- Production HTTP smoke check passed: payout and verification routes, explicit known-shaped/unknown/empty receipt queries, and all eight payout-page JavaScript assets returned 200 on a temporary frontend at port 3001. These checks cover serving the build, not client-side selection behavior. The API and isolated current-contract chain were not running in this session; no payouts were submitted or data reset for this check.
- Browser runtime returned no available browsers. Interactive/mobile/keyboard tests, delayed-read route changes, and a first-look comprehension check remain pending. Helper tests and HTTP checks do not substitute for those checks.

No backend/schema/hash/contract/dependency changes. Full backend and contract suites were not rerun for this frontend task. Persistent payout retry identity, anchor retry/reconciliation and authenticated role workflows remain unfinished. [The groupmate branch review](ROLE_BRANCH_REVIEW.md) records reuse opportunities and compatibility conflicts before any integration.
