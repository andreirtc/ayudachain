# Truthful demo workflow

Follow-up: [DEMO_SESSIONS.md](DEMO_SESSIONS.md) implements authenticated five-role permissions, limited public responses, disabled HTTP reset and actual headless desktop/phone checks. The comparisons and validation below describe the earlier PR #17 boundary.

Bounded follow-up to [PR #16](https://github.com/andreirtc/ayudachain/pull/16), based on [the three-source comparison](BLUEPRINT_COMPARISON.md). All records and money remain synthetic; no workmate branch merge, database migration, contract change or deployment was performed.

## Corrected behavior

- The shared shell labels a fictional prototype rather than a government portal. Navigation uses concise task labels, active-page semantics, touch-sized links and a skip link. Ordinary navigation no longer exposes destructive database reset.
- The demo-view chooser works at phone widths and offers each existing view a relevant next action. It explicitly describes selection without sign-in and unauthenticated permissions. The staff view retains the existing `Barangay Officer` internal key for compatibility; it is not a new DSWD account or a five-role backend.
- An expandable example journey links funds, household review, recorded payout and receipt checks. It no longer invents a duplicate score, pitch duration or live fraud result.
- The payout screen uses the loaded registry's manual household selection. The fake camera/viewfinder and hardcoded voucher identities were removed. Existing DAFAC values remain selectable; absent card references are not fabricated. Real camera decoding remains pending.
- The cosmetic offline switch and claims of device storage/batch sync were removed. Browser connectivity comes from `navigator.onLine` plus online/offline events; listeners detach when no longer used. The submit boundary checks connectivity again before calling the API. An offline attempt sends nothing and explicitly says no payout was queued. Reconnecting does not submit automatically.
- API loading, empty and error states are visible. A failed refresh blocks form submission until records reload; retrying keeps the existing form/request identity. Browser online state does not prove API availability or a successful anchor. A connection lost after sending remains an uncertain failure; existing idempotency semantics still apply.
- Payout entry is offered in the staff demo view, with an active-batch check and the existing eligibility/maximum/duplicate guards. This is UI guidance, not server authorization. The API remains authoritative for eligibility, budgets, linked-alias payout checks and request replay.
- The sample receipt is labelled a fictional template rather than an official DSWD voucher or working upload/OCR interface. Recording a payout, presence of transaction metadata and a fresh integrity result remain distinct. Differences from a grant standard are not described as an AI finding or a promised auditor queue that does not exist.
- The dashboard no longer offers a cosmetic network dropdown, custom contract editor, default address substitution or fabricated explorer target. Network/address details come from the dashboard API under an expandable panel. A failed refresh labels older totals and suppresses a stale connected status. Unsupported pipeline success and secure-storage claims were removed; current receipt coverage and unfinished authenticated privacy are stated accurately.

## Validation

- Seven Node tests passed: four receipt-reference regressions plus offline send rejection/reconnection with retained request identity, uncertain-response failure and connection-event subscription cleanup.
- Final independent TypeScript check and production build passed after fixing removed scanner references and completing the disclosure layout. The build still skips embedded type/lint validation; the separate typecheck was run, lint was not.
- Production serving checks passed for seven routes, including the unknown receipt query, and all twelve referenced JavaScript assets. Rendered operational pages include the synthetic/sign-in disclosures, skip link and example journey; payout prerender shows a checking state instead of guessing browser connectivity. These are HTTP/rendered-shell checks, not browser interaction tests. The temporary frontend used port 3001 and was stopped afterward.
- Browser plugin could not connect because no browser is available. Desktop/mobile visual QA, keyboard interaction, actual offline browser events and the complete user journey remain pending. Event fixtures and HTTP checks do not establish those results.
- Backend and contract behavior were untouched; their full suites were not repeated. No data reset, payout submission or chain redeployment was used for this UI task.

## Remaining work

Authenticated synthetic sessions, server-enforced five-role permissions, restricted public responses, anchor jobs/reconciliation and immutable identity/document coverage remain necessary. The old backend reset endpoint still exists and must be gated as part of backend authorization; hiding its button does not secure it. Auditor review mutations in the older registry are a separate coordinated permissions change. Persistent retry identity, offline sync, actual camera scanning and CSV confirmation are not implemented by this task.
