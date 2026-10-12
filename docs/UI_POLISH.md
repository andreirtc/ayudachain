# Shared UI and remaining screen polish

Bounded presentation follow-up to [PR #24](https://github.com/andreirtc/ayudachain/pull/24), completing the requested typography → payout → receipt → verification → remaining UI sequence. The current app's existing routes are polished; this does not implement every future product feature.

## Shared shell and typography

The blue/slate branding, logos and local Manrope/Source Sans pairing remain. The operational header is smaller on phones, with the synthetic-demo label retained at every size. Navigation follows the authenticated server role: public viewers see public entry points; Barangay has no payout link; Beneficiary gets own-household/own-payout labels. API permissions remain authoritative. Native mobile disclosure supports Escape, closes when focus leaves or navigation/account changes, and focuses main content after route navigation. The account banner retains identity and sign-out while avoiding a duplicate next-action link on its task page.

The example journey appears on the overview rather than preceding every task. Small operational labels have a readable minimum size, heading weights are calmer, keyboard focus is consistent and reduced-motion preferences disable decorative animation. The landing explains the records/receipt purpose directly and preserves its fictional illustration and primary demo entry.

## Overview and batch details

Overview amounts and counts come from the existing API. Recorded payouts are no longer labeled verified receipts. Fixed allocation percentage/locality claims and unsupported sealed-funding claims were removed. Recent activity and stored transaction references are separate from current receipt verification; network metadata is expandable. Refresh is explicit, with loading, error/retry and previous-read disclosure.

Batch allocations use readable rows rather than a six-column phone table. Initial and subsequent route loads clear stale batch content; failures offer retry. Funding transaction references are expandable and do not claim that this page verified them. Amounts are recorded synthetic funds; payout counts do not prove cash delivery. Public versus office activity still comes from the existing server projection.

## Date correction

Legacy DateTime API strings use `datetime.utcnow()` without an offset. Browsers previously parsed these as local time, shifting the displayed instant. `recordedDate.ts` interprets those known UTC values as UTC, retains explicit offsets and displays unavailable for invalid dates. Epoch-based chain/client observation times are unchanged. No stored timestamp, receipt hash or database record is rewritten.

## Validation

On 2026-10-13, all 56 real Edge desktop/phone cases passed. The eight polish cases passed again after final screenshot-driven metric spacing, landmark focus styling and phone sign-in link fixes. They cover all five navigation roles, Barangay payout denial, keyboard/mobile disclosure and skip links, reduced motion, overview labels and failed refresh, and batch retry/phone layout. Existing registration, duplicate history, payout retry/recovery, exact receipts, scopes and verification cases passed. Independent TypeScript, production build, diff checks, three UTC-date tests, seven existing Node checks and 19 authenticated API regressions passed. Landing, overview, batch, receipt/payout and verification screenshots were inspected across the sequence. The ten actual-chain observations are recorded separately in [UI_VERIFICATION.md](UI_VERIFICATION.md). Owned preview/test listeners are stopped.

Human preference/comprehension and a full accessibility audit are not established by automated checks. Complete receipt snapshots, recipient acknowledgement, CSV import, institution/account administration, licensing, dependency hardening and deployment remain future work. See [TODO.md](TODO.md).
