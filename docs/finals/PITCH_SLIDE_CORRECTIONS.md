# 19-slide replacement copy and visual corrections

**Canva access/inspection is cancelled at the team's request.** Apply the copy below manually to your deck. These 19 items are a recommended sequence; the original slides were not inspected or edited. Prioritize the claim corrections below over cosmetic reordering. This outline assumes the current `design-proposal` finals candidate; if choosing PR #39, apply the scope changes in [PRESENTATION_CHOICE](PRESENTATION_CHOICE.md).

Use Sea-and-Sun from [DESIGN.md](../../DESIGN.md): sea-blue primary `#2b5ea7`, near-white surface `#f9f9ff`, sun-gold container `#ffdf9e`, dark ink `#191c20`. Use Open Sans, short sentence-case headings and readable body text. Keep raw hashes out of the main slides. Screenshots must carry “Actual local application · synthetic records · captured 14 Oct 2026”; design references must carry “Illustration / proposed design.”

| # | Replacement title | Exact on-slide copy | Visual recommendation / presenter note |
|---|---|---|---|
| 1 | AyudaChain | **A checkable trail for disaster cash assistance.** Local five-role prototype · PUP Main Hackathon 2026 finalist | Kubo Link mark, one genuine app crop. Finalist status is user-provided; no government seal/endorsement. |
| 2 | One household, several unanswered questions | Why was this household included? How was the amount calculated? What handover was recorded? What did the recipient report? | Four simple questions around an explicitly invented household. No unsourced loss/corruption statistic. |
| 3 | Connect the evidence | Funding → claim → human decision → amount basis → handover → recipient report → integrity check | One horizontal flow. Distinguish physical cash from software record. |
| 4 | Five users, clear responsibilities | Beneficiary · Barangay Officer · DSWD Officer · Disbursing Officer · Auditor | Five role icons with one verb each: claim, attest, decide, hand over, inspect. |
| 5 | Start with the original | Upload evidence. Review extracted fields. Confirm the saved record. Correct by appending. | Actual Funding ledger and document preview. Caption “PDF text extraction; manual confirmation remains available.” |
| 6 | Human decisions remain human | Automatic checks flag possible issues. Barangay responses inform review. DSWD records the decision and reason. | Actual claim/check panel. Remove “AI eliminates fraud” or automatic approval/rejection claims. |
| 7 | Show how the amount was worked out | **Invented example:** ₱435 wage × 75%, rounded up to ₱330/day × 15 documented days = **₱4,950** | Simple arithmetic plus actual amount basis. Footnote: synthetic inputs; current program rates require official mapping. |
| 8 | Publish a version we can check | Saved list ≠ published list. Publication waits for that list’s matching chain confirmation. Earlier versions remain in history. | Actual list state/version. Do not depict a pending anchor as verified. |
| 9 | Organize the payout | Current list · named members and staff · date and site · open session | Actual session. Note “SMS notice is simulated; no handset delivery claimed.” |
| 10 | Record handover once | Compare photo ID. Count the fixed cash. Recipient authorizes. Review and record once. | Actual receipt or handover review. Never show PIN/code as an authentication guarantee. |
| 11 | Access without mandatory QR | Manual reference lookup. Assisted registration. No-phone assisted payout with private authorization and independent checker. | Phone screenshot plus assisted-route diagram. Footnote: connected staff device required; current photo-ID/PIN/checker limitations. |
| 12 | Listen after the handover | Received in full · received less · not received. Private follow-up retains every answer and resolution. | Actual private outcome/case screen. Separate handover count from recipient-confirmed full receipt. |
| 13 | Private records, checkable commitments | PostgreSQL + private originals → exact evidence fingerprint → pinned local EVM → fresh independent comparison | Actual architecture, three boxes. Public: opaque IDs/hashes and funding amounts. Private: identity, receipt contents, secrets and answers. |
| 14 | What “Verified” means | The saved committed evidence matches a fresh chain read. **It does not prove document authenticity or physical cash delivery.** | Actual successful check with timestamp. A second small truthful failure state if captured; never fabricate a chain result. |
| 15 | Built and tested, with limits visible | Original-backed forms · five-role workflow · exact amounts · once-only handover · current chain checks | Use exact fresh results from FINALIST_READINESS at export time. Avoid old “all tests pass” claims, unspecified test counts or full security-audit badges. |
| 16 | What remains before real households | Authentication · approved procedures/privacy · secure hosting/files · real notices · network/key governance · operational recovery | Plain readiness gates. Explicit “Synthetic evaluation only.” Offline payout, signature validation and full liquidation are pending. |
| 17 | Validate, then pilot | 1. Synthetic workflow validation. 2. Security/privacy and operational hardening. 3. Authorized supervised pilot and measurement. | Three gates, no invented calendar promise, customer logo or adoption count. |
| 18 | Sustainable service, defensible costs | Proposed institutional implementation, training and support. No beneficiary fee. No percentage of relief funds. Pricing awaits scoped costs and customer validation. | Cost categories, not an unsupported revenue chart. Reference the clearly hypothetical worksheet in JUDGES_QA. |
| 19 | A trail we can defend | **Every verified result must mean a real comparison.** Seeking a supervised workflow-validation partner. | Closing mark and repository reference. Keep proposal distinct from signed partnership or live deployment. |

## Mandatory claim corrections wherever they appear

| Replace / qualify | Defensible wording |
|---|---|
| “Fraud-proof / eliminates corruption” | Makes changes to committed evidence detectable; flags support human investigation |
| “AI validates beneficiaries” | Local automatic duplicate/exception checks; humans decide |
| “Blockchain proves receipt” | Chain matches committed record; recipient statement and physical delivery remain separate |
| “Deployed on Polygon” | Actual local EVM prototype; public-network deployment pending and unauthorized tonight |
| “Secure five-role authentication” | This MVP uses selectable, claimed, unverified identities; the separate PR stack has a different synthetic-session implementation |
| “SMS/OTP/National ID integration” | Notice SMS and National ID checks are explicitly simulated; payout code is not SMS OTP |
| “Offline payouts / automatic sync” | No offline payout; recover connectivity and inspect the same transaction before safe retry |
| “All records immutable/on-chain” | Selected evidence versions are committed; private records/originals and append-only histories are off-chain |
| “Remaining cash / budget enforcement” | Current MVP ledger is recorded funding authority; advances/returns/liquidation/cash certification are deferred |
| “Verified digital signature” | Printed signatories/original evidence retained; signatures are `not_validated` |
| “Government-compliant / endorsed” | Workflow prototype awaiting institutional, privacy, security and current-program mapping |
| “₱X nationwide savings / guaranteed ROI” | Hypothesis to measure with a scoped baseline and full costs; no savings study or customer contract claimed |

## Submission checklist

- Check actual slide order against this outline; this file does not certify the unseen original.
- Use current application captures from `docs/finals/evidence/`, with provenance. Avoid historical legacy screens and illustrated reference totals.
- Keep every screenshot readable at projection size; use one task per crop, not a full desktop shrunk into a corner.
- Put detailed architecture, gas/cost assumptions and limitations in notes/backup material rather than overwhelming the main slides.
- Export and open the final file to verify 19 slides, readable text and correct simulation labels. The team should verify its own export; no external deck access or submission is part of this handoff.
- Do not submit or publish through this agent; external submission remains with the team.

## Supplied Under the Hood slide — reviewed correction

The actual screenshot supplied by the team claims PWA, public Polygon testnet, Random Forest/Isolation Forest and Supabase Auth. Those are not demonstrated in the selected candidate. Replace cards with: Frontend **Next.js · React · Responsive web**; Backend **FastAPI · PostgreSQL · Off-chain document storage**; Blockchain **Solidity · Hardhat · ethers.js · Local EVM prototype**; Review Checks **Rule-based duplicate/anomaly flags · Human decisions**; Role Workflows **Five selectable demo roles · Authentication pending**.

Separate **Proposed deployment** row: hosted app/API/worker, managed or agency-hosted PostgreSQL, private object storage with authorized retrieval/backups, authenticated institutional accounts/RBAC, and approved chain/network governance. PostgreSQL can remain in deployment; private S3-compatible storage is a proposed option, not integrated. Supabase Auth may be named only as a future option if chosen, not shipped capability. Sources: [PostgreSQL](https://www.postgresql.org/about/), [S3 public-access controls](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).

For SDGs use [SDG_ALIGNMENT](SDG_ALIGNMENT.md): primary16/16.6, supporting1/1.5and10/10.2. Proposed alignment, not measured impact or UN endorsement.
