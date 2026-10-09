# AyudaChain siteflow and userflow mockup

Open [index.html](index.html) in a browser. It runs directly from the local file; no server, installation or backend is required.

This is a proposed screen and navigation mockup for the redesign. The process rules come from the settled ideation documents. Every person, document, household, amount, code and verification state is a fictional demo fixture. All actions are labelled simulations.

## How to present it

1. Start with **From funding to full receipt**. Use the blue action in the screen or the presenter guide to move through the handoffs.
2. Select **Proposed site map** to see each role's navigation. Select a screen to explore it.
3. Use **Preview role** to inspect the same scenario state from another role's perspective. **Return to guided screen** resumes the walkthrough.
4. Expand **See the complete journey** to jump to a stage. **Previous step** and **Start again** rewind the fictional fixture for presentation; these are not product undo actions.
5. Choose another scenario to demonstrate an exception. Disbursing Officer previews also let the presenter switch between the payer and independent checker accounts within that same role.

The forms show fixed example values. Buttons advance scripted fixtures; this mockup does not implement editable forms, authentication or production permissions.

## Example scenarios and userflows

| Scenario | Demo journey | What to point out |
| --- | --- | --- |
| 1. Funding to full receipt | DSWD nomination/accounts → release → explicit intake opening → Beneficiary registration/claim → Barangay response/signed batch → DSWD eligibility/amount/publication/session → Beneficiary attempt → Disbursing ID check/handover → private recipient answer → Auditor evidence | Release coverage does not open claims. Approval can await the amount. Publication waits for the approved-list anchor. Scheduling triggers the linkless notice. Handover and receipt answer are separate. |
| 2. Missing endorsement or signed submission | Barangay handoff unavailable → labelled system snapshot → DSWD human decision/residence check → amount and confirmed publication → Beneficiary entitlement | On the first screen, compare **No eligible endorser**, **No barangay response**, and **No barangay submission**. Actual negative responses are retained. No fallback manufactures a signature or council resolution. |
| 3. Changed unpaid amount | DSWD new inputs → Beneficiary old/new amount and hold → revised confirmed list → session amendment → new attempt under the same transaction → current handover → Auditor comparison | Lina's unpaid amount changes from ₱4,950 to ₱5,100. The earlier code expires. Tomas's recorded ₱4,950 handover stays fixed; the ₱150 difference is flagged for human handling. |
| 4. Private shortfall and reopening | Beneficiary adverse answer → DSWD private case/resolution → session closure → later adverse report → payer view → Auditor history | The linked grievance reopens with the earlier resolution retained. Payer and barangay cannot read private answers or cases. No second payment becomes available. |
| 5. Silence and late answer | Recorded handover → simulated 72-hour timeout → neutral unconfirmed → session closure → late private answer → Auditor history | Unconfirmed is neutral. An unused attempt expires instead. A late answer remains possible after closure and does not add another handover. |
| 6. Assisted payout | Payer identity check → recipient private assisted authorisation → handover → closure → independent assigned checker records recipient answer → Auditor | Bea and Miko are two Disbursing Officer accounts. The checker is neither payer nor household member and is not a sixth role. The mockup captures no real PIN. |
| 7. Failed ID check | Payer records stop/reason → DSWD review/clearance → later session → recipient attempt 2 → handover → Auditor | The entitlement is held, not deleted. One transaction retains both attempts. The stopped attempt has no receipt and no post-handover timeout. |
| 8. Failed release anchor/correction | DSWD saves release → explicit simulated anchor failure → retry same commitment → linked correction → Auditor funding ledger | Authority counts once despite anchor failure. Original, reversal and replacement remain. Funding totals stay separate from payout totals; advanced remains zero. |

All examples use Bagyo Tala, Barangay San Isidro and one Field Office. Household identifiers **DFC-2026-0101** and **DFC-2026-0102** identify invented records. Short-lived codes are invented scenario values, unrelated to account authentication.

## Proposed siteflow

| Role | Proposed screens | Boundary demonstrated |
| --- | --- | --- |
| DSWD Officer | Disaster overview; Funding ledger; Claim operations; Staff nominations & accounts; Claim review; Amount basis; Approved lists; Payout sessions; Private cases | Eligibility, amount inputs, publication/session control and private human case review. Funding authority is separate from payout totals. |
| Barangay Officer | Claim responses; Signed batches; Residents' list; Payout counts | Own barangay. No amounts, identity photos/ID numbers/phones or private outcomes/cases. Payout progress uses aggregate counts. |
| Beneficiary | My household; My claim; Barangay list; My entitlement; My payout; My private reports | Own household records and answers. Residents' list access requires current confirmed residence and publication. |
| Disbursing Officer | Assigned sessions; Pay recipient; Transaction history; Independent exit check | Assigned sessions; computed amount; identity and recipient authorisation. Independent exit recording uses a separate eligible account in the same role. |
| Auditor | Exceptions; Evidence timeline; Funding totals; Payout outcomes | Read-only evidence and verification. Record-specific identity access is logged privately and hidden from the Field Office. |

The mockup has 27 proposed screen destinations. These names and their grouping are layout proposals, not approved routes or a backend design. Seeded disaster/account arrangements are used; this does not propose a disaster declaration workflow.

## Sources and design boundaries

- [Settled end-to-end process](../process.md) supplies handoffs, records, role gates and exceptions. Each guided stage shows its corresponding process reference.
- [Decision record, section 16](../decisions-2026-10-08.md#16-end-to-end-process-2026-10-09) records the completed session. Earlier decisions and the [five role descriptions](../roles/) remain the permission authority.
- [Redesign DFD](../dfd.md) describes data movement and the private/off-chain anchoring boundary.
- [DSWD funds flow draft](../drafts/dswd-officer-user-flow.md) supplies the funds evidence and correction example.

No application files, database or contract were changed to make this mockup. It selects no backend architecture, ERD, SMS provider or live integration.

Phone signup/sign-in is Proposed planning. SMS authentication and its free-tier feasibility remain unresolved. Outbound notice SMS is a separate required capability with no selected provider; its delivery here is simulated. Basic-phone transaction/reply protocol, cash advances, returns and liquidation are Later. Physical cash arrangements and notices for recipients without a usable SMS contact occur outside this mockup.

Automatic checks use fictional AyudaChain records and produce flags for human decisions. The National ID check is explicitly an internal simulation; there is no live PSA or external DSWD database connection. Anchor states and verification comparisons are also explicitly simulated, with no fabricated real chain hashes.

The mockup is an offline presenter artifact: all fixtures can be read in its HTML source, and role previews filter the display only. It does not provide security or persist a real audit trail. Private outcome visibility and Auditor access logging illustrate the intended product rules.

The scenario set is illustrative, not an exhaustive process or exception specification. The process document remains authoritative for unshown routes such as no eligible independent checker, cancellation, lost acknowledgements, claim resubmission and other dispute outcomes.

## Validation

Checked in existing headless Chrome at 1440-pixel desktop and 390-pixel mobile widths, then visually inspected the desktop and mobile renders. All eight scenarios (57 guided stages), 27 proposed destinations, site-map links, role switching, replay and resume controls passed the scripted browser checks with no script/console errors or HTTP requests. No installation was needed.

The checks cover residence/publication gates, scheduling versus publication, distinct unsigned fallbacks and retained responses, one transaction with appended attempts, fixed handed-over amounts, stale-code expiry, separate handover/answer outcomes, neutral timeout and late answers, grievance reopening, role display restrictions, independent checker identity, simulated fail-closed results, and private Auditor access. All 134 existing authority/protected files matched their starting hashes.

Validation is of a scripted presenter mockup, not a production implementation or access-control audit. Mobile checks use a browser viewport, not a physical phone. The available Impeccable detector ran in its degraded regex mode because its optional HTML parser modules were absent; it reported no findings but did not evaluate computed contrast or selector matching. Browser inspection supplies the visual check; full accessibility certification and real integrations remain outside this artifact.
