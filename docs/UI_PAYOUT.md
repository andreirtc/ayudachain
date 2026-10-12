# Payout workflow clarity

Bounded frontend follow-up to [PR #21](https://github.com/andreirtc/ayudachain/pull/21). The entry form belongs only to Disbursing; DSWD, Auditor and Beneficiary see their permitted payout records. Backend roles and scopes remain authoritative.

Household selection starts empty, rather than silently selecting a recipient. The form shows approval status, actual batch/grant values and remaining recorded allocation. Remaining allocation uses integer-centavo allocation and payout fields from the existing APIs, with compatibility fallbacks for older projections. It represents recorded budget, not physical cash. Server checks remain authoritative when saving, including alias-linked prior payouts that are not inferred by this form.

Pending/rejected households, inactive/missing batches, missing allocation, repeated household/batch payouts, non-positive or over-precision amounts, grant maximums and insufficient recorded budget have visible explanations. Loading or failed refresh prevents payout submission and hides stale record rows. Search, empty results and refresh/retry states are available to readers.

A saved payout replaces the form with its household, exact amount and receipt reference. Anchoring remains a separate state, with existing scoped recovery controls. **Check this receipt** opens that exact record. **Record another payout** explicitly clears the completed form; it does not submit anything. Browser-reported offline status blocks submission/recovery without a queue. Existing durable payout keys are preserved for uncertain same-page retries.

The receipt preview is retained for the following receipt-focused PR. This task does not add acknowledgement, scanning, uploads, immutable identity snapshots or new backend endpoints.

## Validation

On 2026-10-13, all 34 isolated Edge desktop/phone cases passed, including six new payout cases. Real API funding/registration fixtures cover budget and pending-household checks. A lost-response test lets the API actually save a payout and aborts only the browser response; its retry returned one record, the same key, exact centavos and one anchor attempt. Seven frontend Node checks, independent TypeScript, production build and diff checks passed. Entry and saved-result screenshots were inspected at both sizes. The fixture explicitly reports unavailable blockchain verification; no live-mining claim is made.
