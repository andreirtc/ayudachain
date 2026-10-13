# Accepted product direction

Accepted by the user on 2026-10-14 after the branch/design comparison and Philippine disaster-assistance discussion. This records the chosen direction and bounded delivery sequence. The [shared Tonal foundation](TONAL_FOUNDATION.md) is implemented. The [household starting point](HOUSEHOLD_START.md) is also delivered. [Versioned validated lists](VALIDATED_LISTS.md) and [payout arrangements](PAYOUT_ARRANGEMENTS.md) are delivered. The [focused payout desk](PAYOUT_DESK.md), [household concerns and assisted intake](HOUSEHOLD_CONCERNS.md), and [staff audit workspace](STAFF_AUDIT.md) complete the demo feature wiring. The [actual Material frontend layouts](MATERIAL_FRONTEND.md) are now delivered for visual evaluation. Human design acceptance and non-demo recovery/release work remain separate.

## Product and household journey

Use a staff-managed validated-list and organized payout workflow with current accounting safeguards. Reuse existing household information or import it for review; households already on validated lists should not have to re-enter the same application.

The household journey should answer:

1. Are my details and assistance status correct?
2. What amount, date, place and accepted requirements apply?
3. Where is my receipt, and how can I report a concern?

People missing from a list need a review or assisted route. Registering, importing and matching do not themselves establish eligibility. Humans resolve uncertain evidence and eligibility, authorize required decisions, check recipients and handle exceptions. Software performs exact calculations, completeness/duplicate checks, routing and retained records.

Keep five authenticated roles as permission boundaries: Beneficiary, Barangay, DSWD, Disbursing and read-only Auditor. This does not require five separate human approvals per household. Any batch action must preserve required approval, individual exceptions and attributable history.

Extra review paths cover possible duplicates, disputed identity/residence, missing evidence, funding constraints, representatives and payout discrepancies. Map accepted documentary alternatives explicitly. Do not make the MVP's exact two-officer, PIN/code or chain-confirmed publication steps universal requirements merely because that branch implements them.

## Selected visual direction

The user chose **Tonal / Material 3, Sea and Sun**, rather than the current treatment or the agent's earlier typography/layout hybrid.

The [original Tonal reference at 4377db1](https://github.com/andreirtc/ayudachain/blob/4377db103bb525b2d8c83746eda28b12473095ce/docs/design/tonal-design-reference.html) governs the palette, light/dark schemes, tonal surfaces, Open Sans interface and Source Code Pro references, next actions, accessible decision controls, desktop list/detail patterns and small phone navigation set. Vendor licensed fonts locally. Retain the AyudaChain identity and synthetic disclosure.

This supersedes earlier Manrope/Source Sans 3 and blue/slate preservation requirements for the new redesign. Historical typography work and screenshots remain valid records. The reference's illustrated totals, records and proof results are not application data; several interactions are still planned on design-proposal. Its unverified-actor notices describe that branch and must not replace our truthful authenticated-session state.

## Supported baseline and invariants

Continue from PR #30 (e78aee1): current FastAPI/SQLite API, authenticated accounts and allocation-aware contract. The groupmate's PostgreSQL /api/v1 MVP and evidence registry are references, not compatible replacement files. No wholesale merge or database migration is needed for visual work.

Preserve:

- Exact centavos, authorized budgets and grant policy. Insufficient funds is an explicit funding block, not evidence that a household is ineligible.
- Retained duplicate aliases, decisions and payout history; no destructive reset or silent identity replacement.
- Once-only payouts, idempotent uncertain-response retries and durable anchor recovery.
- Legacy receipts, v2 captured originals, protected files and four current proof outcomes.
- Authenticated role scopes, public redaction, read-only Auditor and separate review/payout authority.
- Distinct recorded payout, recipient statement and chain confirmation; none proves physical cash delivery.

Do not lose allocation caps by copying the MVP funding ledger. A different program funding boundary requires an explicit, tested accounting bridge. Additive schema/API changes belong to the feature they support.

## Bounded delivery sequence

Follow [STACKED_PRS.md](STACKED_PRS.md): one complete task per successor draft PR, based on the preceding task. PR #31 records the direction; [the shared Tonal foundation](TONAL_FOUNDATION.md) is the first completed implementation.

1. **Tonal foundation.** Adapt the authenticated shell, palette/theme, locally served fonts and shared controls. Preserve supported routes, query references, sign-in destinations and actual states. Validate desktop/phone in both schemes, keyboard/focus, theme persistence, font loading and permission regressions.
2. **Household starting point.** Show own-household status, relevant payout/receipt and one grounded next action. Keep pending, approved, rejected, historical, no-payout and unavailable states distinct. Display scheduling instructions only when actual arrangements exist.
3. **Validated lists and staff review.** Connect registration/CSV and individual review to versioned preparation/finalization for the relevant batch/area. Preserve flags, exclusions, required approvals and frozen history. Test repeated submissions, changed/stale records and unauthorized finalization. Mapping approval authority/documents belongs to this feature; it does not certify official signatures.
4. **Payout arrangements.** Store scoped date, site, requirements and responsible staff linked to the permitted batch/list/area. Test edits/cancellations with retained history, private household instructions and denied/stale links. A schedule alone cannot authorize payment. No real SMS/provider integration.
5. **Focused payout and assisted route.** Use the selected tablet layout with actual approval, budget and retry guards. Keep amount/household visible and failed/uncertain outcomes explicit. Assistance must not require sharing credentials or allow impersonation. Add mandatory PIN/code/checker controls only with a mapped requirement or explicit risk decision.
6. **Receipts, concerns and audit.** Preserve simple public verification and own-recipient acknowledgement. Deliver concerns and staff inspection as separately bounded features: retained concerns do not award/reverse cash, Auditor remains read-only, and current checks cannot be replaced by illustrated or historical success. New evidence types need real APIs before being displayed.

Split the last stage into complete receipt, concern and audit tasks where appropriate. Dependencies/CI, funding/allocation recovery and historical reconciliation remain separate bounded work. Stacked-PR checks and release hardening are required before shared deployment.

## Evidence and limits

Official ECT sources informing the recommendation:

- [MC 24, s.2025](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2025/12/MC-No.-24-S-2025.pdf), especially pages 5 and 7-9: masterlist validation/review, approval before cash distribution, recipient documentation, concurrent preparation, notification and digital/direct payout arrangements.
- [MC 20, s.2026](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2026/08/MC-020-s.2026.pdf): amended rate inputs and specified alternative identity/residency/eligibility documentation.
- [DSWD's April 2026 ECT report](https://www.dswd.gov.ph/dswd-disburses-php949-5m-in-emergency-cash-assistance-for-typhoon-hit-households-in-central-visayas/): digital and cash payout options in actual operations.

This is not comprehensive compliance mapping or a universal workflow for AICS, 4Ps, NGOs or every LGU. The large original MC 11, s.2025 PDF was not fully downloaded/read. No official approval, real-household readiness, document authenticity or real payment is claimed.

The local comparison at tmp/ayudachain-workflow-design-study/comparison.html contains a workflow view and four screen pairs: actual isolated PR #30 captures and rendered original Tonal references. Its 16 desktop/phone observations and offline/keyboard/zoom checks validate the comparison, not a delivered redesign or comprehension study.

## Delivery and preservation

Use invented data and local/test networks. Preserve the original database, frontend 3000, chain 8545, retained builds/deployment artifacts and read-only provider pane. The persistent preview remains stopped. Temporary test services must use owned isolated data/builds/ports, refuse occupied ports and stop afterward.

Every implementation task needs actual authenticated API journeys, denied roles, relevant regression/fault tests, independent types/build, real desktop/phone browser checks and screenshot inspection. Use owned live-chain checks for hash/anchor/contract changes. Report physical-device, translation/comprehension and deployment limits honestly. Never merge or force-push.
