# AyudaChain product investigation

Review date: **2026-10-08, Asia/Manila**. Investigated working tree: `main-2`, HEAD `6d92882dcbc4496645b4379561f457d1504aed53`, including the pre-existing uncommitted changes. This is an expert usability evaluation and synthetic role-play, not research with actual recipients, field workers or auditors. No redesign was implemented.

## Executive verdict

**AyudaChain has a credible narrow mechanism, but its hackathon demonstration overstates what that mechanism proves.** The maintainer clarified that this is a hackathon only, targeting DSWD disaster-relief funds, with no intended pilot operator or existing government authority. A well-governed payment record, independently retained commitment and usable reconciliation process could expose changes made after recording. The current demo presents that narrower capability as proof that government money reached the correct family, and sometimes reports success without any matching chain record. Those are credibility failures even in a demonstration.

Its demonstration purpose is now confirmed context, not a flaw by itself or proof that every capability is simulated. A real local contract was deployed, real local transactions anchored synthetic receipt hashes, a changed amount produced a real mismatch, and searches, registration and payout recording worked in the browser. One fixed disaster, pitch controls and browser personas are reasonable hackathon shortcuts when labelled honestly. The consequential issues are fabricated chain success, unsupported cash/identity/corruption claims, and a story that ends at an anchor without explaining reconciliation or a recipient challenge. Missing institutional operations are future-pilot gaps; they are not all requirements for a synthetic contest entry.

**Recommended direction:** demonstrate one complete synthetic payout-and-reconciliation job, with truthful receipt/proof states and a recipient discrepancy path, rather than claim national fraud prevention. Direction C develops this into a private workbench for one approved program/team only if a future DSWD owner validates the need. Independently retained session checkpoints and a smaller chain footprint are alternatives to synchronous per-payout anchoring. Preserve the truth boundary: an anchored match establishes consistency with committed evidence; it does not establish physical cash delivery or eligibility. The finance ledger remains an alternative under consideration, as the maintainer confirmed. See [redesign blueprint](redesign-blueprint.md) and [validation and roadmap](validation-and-roadmap.md).

## Evidence and limits

Labels throughout these artifacts: **R** observed rendered/runtime behavior; **S** source inspection; **T** existing check; **D** documentation claim; **X** external primary source; **I** expert interpretation; **A** assumption/unresolved context; **P** proposed behavior. A criticism's confidence concerns its evidence, not validated product demand. P0 means a failure can create false integrity assurance or an unsafe payment decision; P1 means a future-pilot workflow/accountability blocker; P2 means material usability or operability friction. These are priorities, not a numerical product score. Permission/operability gaps are assessed against possible real use; synthetic public demo data and simulated personas are not, by themselves, a demonstrated privacy incident or unauthorized real payout. Immediate hackathon priorities are separated in the roadmap.

All 73 initial first-party files and two concurrently added finance drafts are accounted for in the [coverage ledger](evidence-and-journeys.md#repository-coverage). All five routes were used at desktop and narrow mobile widths. Root captured 60 journey snapshots; independent tracks captured another 16 screenshots and technical accessibility samples. Backend checks passed 8/8, contract checks 9/9, typecheck and build exited 0. The lint command did not complete configuration. Those small suites do not test the critical failures reproduced here. Raw evidence, setup, exact attribution, reproduction steps and limitations are in [evidence and journeys](evidence-and-journeys.md).

Required PRD, DFD and ERD are absent, and `docs/adr/` contains only `.gitkeep`. The maintainer supplied hackathon-only scope, DSWD as intended body, no pilot operator/authority, and finance-first as an alternative. Actual institutional responsibilities and any future pilot are therefore **provisional**, explicitly requiring decisions rather than assumed authorization. The current ECT amendment MC 24/2025 and full current COA documentary checklist were not retrieved. This review does not certify legal compliance or institutional acceptance.

## The problem and proposed causal chain

**D:** README, guides and pitch describe a national relief transparency trail: funds released, allocations, household payouts, duplicate detection, receipt anchoring and public verification. Screen personas are affected families, barangay officers and COA/auditors. **Maintainer context:** intended government body is DSWD for disaster-relief funds; this is a contest prototype, with no real pilot operator or authority. **A:** eventual buyer, accountable office/data controller, disbursing authority and support owner are not established. A named agency in a synthetic receipt is not evidence of adoption or endorsement.

The user's job has several distinct stages:

| Stage | Institutional job | Recipient job | What AyudaChain currently completes |
|---|---|---|---|
| Before payout | Approve program/amounts; validate a roster and claimant representation; resolve possible duplicate identities; allocate authorized resources | Understand whether approved, amount, place/time and required evidence | Synthetic registration, similarity suggestions and seeded allocations; no complete eligibility or approved-roster process |
| During payout | Locate approved entitlement; establish claimant identity; execute payment through authorized channel; preserve acknowledgement; recover unknown outcomes | Receive the approved assistance and a usable acknowledgement | Records a declared amount and sometimes a real hash anchor; no actual cash/payment-provider integration or per-payout receipt capture |
| After payout | Reconcile paid/unpaid funds and evidence; investigate exceptions; correct records without hiding history; supply accepted audit documents | Check own record, report short payment or errors safely | Hash lookup and audit-like timeline; no completed reconciliation, correction, grievance or accountable response workflow |

**I:** existing alternatives to investigate include signed payroll and claimant acknowledgements, spreadsheets and reconciliation, bank/provider statements, FACED assistance histories, and existing institutional payout systems. DSWD XI announced an ECT Offline Payout System in 2025; this establishes an alternative, not an available integration API. Switching would need a demonstrated reduction in duplicate work or unresolved payment cases and acceptance of the resulting evidence, rather than the appeal of a blockchain screen. [DSWD XI announcement, introduced 2025-06-09; accessed 2026-10-08](https://fo11.dswd.gov.ph/2025/09/%F0%9D%97%97%F0%9D%97%A6%F0%9D%97%AA%F0%9D%97%97-%F0%9D%97%AB%F0%9D%97%9C-%F0%9D%97%A5%F0%9D%97%BC%F0%9D%97%B9%F0%9D%97%B9%F0%9D%98%80-%F0%9D%97%A2%F0%9D%98%82%F0%9D%98%81-%F0%9D%97%98%F0%9D%97%96/)

**P:** the defensible causal chain is: approved roster and payable amount → accountable payment attempt and independently supported acknowledgement → retained original evidence and append-only changes → reconciliation exposes missing/duplicate/contradictory records → independent commitment exposes later alteration → assigned humans resolve exceptions. Each arrow needs evidence. A hash only supports the penultimate arrow.

## Trust boundaries the product must explain

| Distinction | What the present mechanism can establish | What remains outside it |
|---|---|---|
| Recorded payout / cash delivered | An operator recorded an amount; a successful anchor commits selected metadata/text | Cash counted, recipient possession, later deductions or coercion |
| Receipt integrity / original receipt truth | Recomputed covered fields equal an actual chain digest | Whether the original acknowledgement was truthful; whether current image bytes match the digest, because bytes are not covered |
| Identity similarity / eligibility | Fuzzy strings resemble another registration | Same actual family, eligibility for this program/event, lawful representative, legitimate repeat assistance |
| Hash mismatch / corruption | Covered data differ from a prior commitment | Intent, guilty actor or explanation; transcription and authorized correction can also differ |
| Authorized signer / honest signer | Contract permits a configured wallet to write | Proper institutional delegation or truth of its assertions |
| Local chain / independent public witness | One development node retains local history during its lifetime | Independence from its operator, durable shared public observation or real-network cost |

**X:** DSWD's 2025 ECT guidelines as issued calculate benefits from regional wages and assessed days and prefer digital transaction accounts, with a certified direct-cash fallback. The full later amendment remains unresolved. DSWD also reported a specific ₱9,960 historical ECT payment. This contradicts universal statutory ₱5,000 language and requires program-specific amount provenance. FACED succeeded DAFAC under MC 12/2024; official serial/bar-code guidance does not demonstrate the demo's DFC/QR integration. [MC 11/2025, signed 2025-06-19](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2025/07/MC-No.-11-S-2025.pdf), [DSWD payout, 2024-03-05](https://www.dswd.gov.ph/dswd-gives-cash-aid-to-2k-disaster-hit-families-in-davao-oriental/), [MC 12/2024, signed 2024-04-22](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/issuances/MCs/MC_2024-012.pdf). All accessed 2026-10-08.

**X/I:** DSWD's November/December 2025 reports describe alleged deductions after AICS payment and administrative filings. Correctly anchored records could survive such a sequence unchanged. Independent confirmation and safe complaint handling address a different risk from later database edits. These reports are allegations/actions, not adjudicated guilt or prevalence estimates. [DSWD investigation, 2025-11-12](https://www.dswd.gov.ph/dswd-condemns-aics-cash-aid-cut-by-iloilo-barangay-officials-vows-immediate-probe/), [administrative charges, 2025-12-11](https://www.dswd.gov.ph/dswd-chief-files-admin-charges-vs-local-officials-involved-in-aics-corruption/); accessed 2026-10-08.

For a chain-match result, the minimum promise should be: **this exact identified record was read from the declared chain witness, matched the covered evidence version, and has a truthful delivery/reconciliation status with an accountable route for questions.** A signed-only package is labelled signed and retained, never chain-verified. Unknowns must remain unknown. Public verification must never substitute another record or carry an old verdict into a new selection.

## Newly discovered finance-first direction

**D:** two drafts appeared during the investigation and were fully read at final inventory: [finance responsibilities](../../product/drafts/finance-officer-responsibilities.md) and [finance user flow](../../product/drafts/finance-officer-user-flow.md). They explicitly say scratch/planned, not a specification or implemented behavior. They describe a DSWD Field Office Finance Officer as a possible first-version primary user and a document-backed disaster budget ledger, with later advances/liquidation. This is materially narrower than today's citizen/field/auditor pitch and supplies a fourth product direction. The maintainer confirmed it is **an alternative under consideration**, not the chosen next scope.

**I:** this is a promising narrower entry if the actual unmet job is recording and correcting incoming release evidence. Retain original documents, human-checked extraction, explicit failed anchoring, accurate signature claims and reversing corrections. Challenge three planned shortcuts before a real pilot: deferred identity/approval cannot support accountable finance; a duplicate file hash does not detect the same economic release scanned differently; a budget authority document and evidence of cash transfer are different dimensions, so a single “received/remaining” total must not imply available cash or liquidated balances. File integrity alone also does not bind silently edited structured ledger fields. These are design critiques of drafts, not active-runtime defects or certified Philippine accounting requirements.

If maintainers confirm finance-first scope, choose the document-backed ledger MVP described as Direction D in the blueprint, with complete authorized intake→review→correction→closing export. Do not add household registration or payouts merely to preserve the demo. The payout/reconciliation blueprint remains a defensible later direction only if payment-operation demand is validated. This condition materially changes scope, not the reproduced integrity verdict.

## Strongest existing capabilities

- **R/S:** canonical hashing and the real local contract can detect changes to covered amount/OCR fields. A deliberate isolated amount change produced a mismatch, and restoration matched again (E03).
- **S/T:** contract writes are gated by owner/operator authority and reject overwriting existing record IDs. Normal payloads keep names, contacts and receipt text off-chain. The contract itself returns absence correctly; the shared Python fallback destroys that distinction (E01).
- **R/S:** search, duplicate review presentation, plain task labels and bilingual guidance provide a useful starting point. Similarity output explicitly asks for human review. The richer CSV pair comparison can help a reviewer if approval and case resolution become distinct states; the single-record inspector currently supplies only a candidate ID and generic reasoning (E08).
- **R/S:** the active standard-library backend is easy to run locally without pip installation. A small architecture is appropriate to a bounded pilot; there is no evidence requiring microservices or Kubernetes.
- **D:** the newer sitemap/user-flow openly enumerate implementation gaps. Those documents are more useful than assurance-heavy pitch claims, although they do not replace requirements.

## Prioritized findings

Each finding consolidates symptoms around a common cause. Evidence IDs link to reproducible protocols in [evidence and journeys](evidence-and-journeys.md#reproduction-protocols). All proposed actions are decisions for later implementation.

### F01 — P0: the evidence state is allowed to fabricate success

**Evidence:** R/S, high confidence; E01, E02, E10. **Affected:** recipients, auditors, operators. Actual RPC outage and an empty redeployed chain both returned `is_verified: true`; failed writes saved fabricated transaction hashes. A delayed/failed new verification kept the previous green result; a missing reference was replaced with another payout. Repeat reset replaced genuine transaction references with nonexistent ones.

**Consequence:** a user can conclude that a specific payout is independently intact when no such proof was read. **Root cause:** shared blockchain fail-open fallbacks, boolean evidence model, consumers ignoring `success`, and UI results unbound to requested record/version. Active refs: `backend/app/services/blockchain.py:61–120`, `backend/server.py:697–761`, `frontend/app/verify/page.tsx:13–69`; repeated seed `server.py:134–244`.

**Action:** explicit unavailable/absent/pending/rejected/mismatch/matched states; real transaction references only; bind verdict to requested ID/version; clear stale evidence on selection/failure; reconcile ambiguous broadcasts. **Verify improvement:** stop RPC, remove anchor, change selection during delay, fail the second lookup, request a missing ID and repeat reset; none may show a successful match or unrelated record.

### F02 — P0: the proof is presented as more than it proves

**Evidence:** R/S/D/X, high confidence; E03, E04. **Affected:** recipients and accountability staff. A recorded ₱2,000 claim with an API-reported match showed a green conclusion saying the family received exact ₱5,000; changing only a household name or receipt file did not change verification. Scripted scenarios override real API results with invented client hashes and guilt language.

**Consequence:** the app can misstate entitlement, cash delivery, identity and culpability. **Root cause:** demonstration narrative substitutes for a defined evidence contract; one static OCR/receipt and hardcoded seal values. Refs: `hasher.py:25–49`, `receipt_generator.py:8–28,137–150`, `verify/page.tsx:45–69,231–315`; architecture:77.

**Action:** define precisely covered fields, evidence version and provenance; show payment-channel/acknowledgement status separately; describe mismatches as discrepancies for review; label simulated API/UI results visibly and keep them in a separate demo. **Verify:** legitimate variable awards display their approved value; name/image changes are either covered by an approved new version or explicitly outside the claim; cash shortfall can be reported despite a matching hash.

### F03 — P0: public personas conceal unrestricted institutional powers

**Evidence:** R/S/X, high confidence; E05, E09. **Affected:** households, payout team, accountable owner. Anonymous APIs expose contacts, review notes and payouts; anonymous callers can create/review/pay/delete/reset. Browser role switching requires no identity; auditor has the payout action. Citizen can register and reset the demo.

**Consequence:** if used for real private records or funds, an exposed instance permits unauthorized alteration and disclosures; similarity labels can stigmatize identifiable households. The synthetic lab did not demonstrate a real-person privacy breach. **Root cause:** display personas are treated as operating roles; no server-side identity/scope/permission boundary. Refs: `roleContext.tsx:18–29`, `server.py:254–285,415–490,499–840`, `distributions/page.tsx` role condition.

**Action:** decide controller and institutional authority; require named, scoped accounts for private work; restrict payment/review/deletion/configuration and audit actor attribution; provide recipient-scoped lookup and approved aggregate transparency. **Verify:** direct API tests for every role and cross-program scope; public payload field review and enumeration tests. Off-chain placement alone is not compliance. [RA 10173 §§11–13,16,20](https://privacy.gov.ph/data-privacy-act-/), [NPC contextual disclosure opinion 2020-026, 2020-06-26](https://privacy.gov.ph/wp-content/uploads/2020/10/Redacted-Advisory-Opinion-No.-2020-026.pdf); accessed 2026-10-08.

### F04 — P0: payment attempts lack a recoverable identity and atomic guard

**Evidence:** R/S, high confidence; E06, E07. **Affected:** officer, cashier, supervisor. Two concurrent requests recorded two claims for one beneficiary; only one of those records existed on-chain. A committed response deliberately dropped in transit led to a generic failure; retry returned a generic failure until refresh revealed the completed claim. A chain write preceding a database ID collision left a different assertion on-chain and a leaked database lock.

**Consequence:** duplicate recorded claims, unknown outcomes and divergent evidence demand manual investigation during payout. No actual cash duplication was simulated or claimed. **Root cause:** SELECT-then-write guard, short generated IDs, synchronous chain-first operation, no durable attempt/idempotency/reconciliation model, unhandled DB exceptions. Refs: `server.py:648–723`, `distributions/page.tsx:56–115`, `blockchain.py:29–59`.

**Action:** one durable attempt per approved entitlement, atomic claim control, idempotent recovery and separate evidence anchoring; a cash handover decision protocol for unknown outcomes. **Verify:** parallel same-entitlement requests, lost responses before/after commit, chain timeout after broadcast and DB failure after mined tx produce one accountable attempt and an actionable status, never a guessed success.

### F05 — P1: identity review, eligibility, amount policy and budgets are conflated

**Evidence:** R/S/D/X, high confidence; E05, E08, E11. **Affected:** registrar, supervisor and legitimate recipients. Blank nonduplicate registration auto-approved; rejected/flagged households had payouts recorded; arbitrary status accepted; a ₱10 batch accepted ₱1,000,000 allocation and ₱5,000 payout; a beneficiary had a payout recorded against another/absent batch. Rejected UI records remained FLAGGED; approved cases remained unresolved duplicate flags.

**Consequence:** the system cannot explain who is entitled to this payment or protect the team's approved limits. **Root cause:** similarity used as approval, globally coupled beneficiary/payment check, hardcoded award rules, missing governed entitlement and review-case lifecycles. Refs: `server.py:499–641,648–694`, contract:142–172, resolver:152–260.

**Action:** human approval tied to program/event/version, separate identity-review case from eligibility decision, approved amount provenance and explicit permissible repeated aid. Enforce institutional limits at the operational boundary; choose whether contract constraints are necessary separately. **Verify:** rejected/unknown/foreign-program cases cannot be paid; a false-positive duplicate can be resolved without deletion; legitimate later assistance can be permitted under an explicit rule; totals reconcile to approved resources.

### F06 — P1: audit history is incomplete and correction is deletion-shaped

**Evidence:** R/S, high confidence; E05, E09, E10. **Affected:** supervisor/auditor/recipient. Normal registration added no event; a rejection logged an approved-verification description; a household with a recorded claim was anonymously deleted leaving its distribution orphaned; reset erased all audit IDs. No correction/dispute workflow exists.

**Consequence:** investigations cannot reconstruct accountable decisions, and recipients have no safe route to contest the record. **Root cause:** actor-free events and mutable current rows without a version/correction model; operational and demo administration share the same surface. Refs: `server.py:559–641,777–840`; backend/server.py schema:106–117.

**Action:** append actor, reason and before/after reference for every change; superseding corrections and human decisions; retain old proof; demo reset unavailable operationally. **Verify:** registration/rejection/correction/deletion-policy audit completeness, export reconstruction, resolved disputes and inability to erase operational history. Demo-only reset remains the repository's explicit exception.

### F07 — P1: field confirmation and offline promises are incomplete

**Evidence:** R/S/D, high confidence; E04, E07. **Affected:** field officer and recipient. Offline pill still sent an online request; actual browser offline submission failed and did not queue; reconnect created no payout. Scanner selects fixtures; no camera integration. Payout reused the sample receipt, preview fetched the wrong host/path and failed, and the completion card was absent after a successful operation.

**Consequence:** a team cannot depend on the product for an acknowledgement or continuity under disrupted connectivity. **Root cause:** demo affordances without durable capture, transport, evidence or handover procedures. Refs: `distributions/page.tsx:31–115,360–381,509–577`, `api.ts:177–201`, `receipt_generator.py:137–150`.

**Action:** bounded online pilot with explicit stop/paper fallback and reconciliation; actual per-attempt acknowledgement before claiming capture. Defer offline execution until device ownership, sync conflict and duplicate-payment policies are validated. **Verify:** retained correct receipt accessible after refresh; network interruption gives a recoverable attempt or explicit unrecorded state, and no claim of queued work without a durable queue.

### F08 — P1: masterlist review does not complete an operational intake job

**Evidence:** R/S, high confidence; E08. **Affected:** registrar/supervisor. CSV analysis displayed pairs but saved no roster or decisions; the single-record inspector supplied only the matched ID and generic reasoning, with no linked household/address/card comparison; unsupported headers reported successful processing; similarity percentages are uncalibrated heuristics, and pair counts are not counts of unique households.

**Consequence:** a worker must transfer ambiguous results manually, and an apparently successful analysis can hide unusable input. **Root cause:** standalone demonstration analysis rather than staged ingestion with provenance and human decisions. Refs: `server.py:599–613`, `entity_resolution.py:195–260`, `beneficiaries/page.tsx` CSV modal.

**Action:** either honestly label analysis-only and remove the import claim, or design staged validation, mapping, review and approved roster publication. **Verify:** bad headers/required values rejected with row guidance; duplicate cases persist across sessions; accepted/rejected import rows and reviewer decisions are traceable.

### F09 — P1: no owner can close and reconcile the payout operation

**Evidence:** R/S/D, high confidence; E11, route/job ledger. **Affected:** intended supervisor/operator. Second batches can exist through APIs but navigation, registration and payout remain fixed to the seeded batch. No supervisor workspace, session closing, paid/unpaid reconciliation or support workflow exists. RPC/address controls only change local display.

**Consequence:** apparent totals cannot establish accountable completion or guide recovery. **Root cause:** a linear public pitch journey replaces the institutional operating cycle. Refs: Navbar:34–40, dashboard:18–23,329–337,383–395, `server.py:317–369`, registry/payout hardcoded batch values.

**Action:** one explicit active program/session in a private workbench; reconciled totals with evidence requirements and assigned exceptions; read-only real configuration/readiness. **Verify:** an owner can explain every approved entitlement as paid/unpaid/unknown/disputed, reconcile the actual payment channel, and sign a retained closing package.

### F10 — P2: presentation makes working states difficult to perceive and act on

**Evidence:** R/S, high confidence for sampled failures; E02, E12. **Affected:** mobile/keyboard users and hurried officers. Modals retain background focus, Escape fails, form labels are unassociated; batch hashes expand a 390 px viewport to 522 px. Backend outage appears as empty registry/no batch in some routes; permanently connected captions remain. Detector sampled low text contrast and 10–11 px functional labels.

**Consequence:** errors look like absence, and users can operate hidden background controls or miss next steps. **Root cause:** repeated custom dialogs and no common loading/error/evidence vocabulary. **Action:** accessible task screens and dialogs, explicit service/empty/not-found states, concise role-specific actions, wrap/reveal technical hashes. **Verify:** keyboard-only core journey, narrow viewport and failure-state checks; field test language and comprehension. The detector is a sample, not a full WCAG audit.

### F11 — P1: operating assurances exceed tested and documented behavior

**Evidence:** S/T/D/X, high confidence; setup ledger and contradictions. **Affected:** maintainer/operator/buyer. Two independently drifting backends exist; only `server.py` runs. Build skips lint/types, although separate typecheck passed. Existing tests cover helpers/basic contract assertions, not system failure paths. Lint requires configuration; installs reported dependency advisories. README/guide claims about offline sync, statutory awards, anomaly detection and costs exceed evidence.

**Consequence:** maintainers can improve dormant routes or pass checks while leaving unsafe live behavior intact. **S:** identifier truncation and money precision also differ across hash/CLI boundaries (E14), creating compatibility risks when accepting arbitrary IDs/amounts. **Root cause:** unclear executable source of truth and demonstration claims used as release assurance. **Action:** select/document one supported backend, preserve existing work, specify integrated failure and encoding checks and truthful feature statuses; review dependency applicability and supported runtime before pilot. Module removal or dependency changes require approval. **Verify:** documented startup matches running process; checks reproduce F01–F09 and freeze v1 boundary fixtures; supported runtime, restore and security review pass. Advisory counts alone do not establish exploitability.

## MVP readiness and scale

For the hackathon, value is a credible, explainable synthetic demonstration of recorded evidence and later consistency, with honest failure cases. Demand and independent-witness value need field validation before adoption. Operational model, integrity, permissions, privacy boundary, payment recovery, evidence preservation and owner support are future-pilot blockers, not authorization to build or launch a pilot now. Visual polish cannot resolve the evidence overclaims. Cosmetics are secondary.

Scale does not start with nationwide hosting. CSV pairing is O(n²), each chain call spawns Node and waits up to eight seconds, concurrent writers share a wallet and SQLite state, and files/keys/checkpoints have no tested institutional recovery. One local payout consumed 183,265 gas; this is a receipt measurement, not a Polygon throughput or fiat cost benchmark. Mainnet gas estimates observed on review day differed from the docs' fixed 30 gwei assumption; `<$0.001` is unsupported without an executed production fee and exchange rate. [Evidence](direct-chain-evidence.json), [fee mechanics and dated primary sources](primary-source-research.md#polygon-fee-check).

The recommended pilot and explicit scale triggers are in the roadmap. Unknown workload, connectivity, key custody, retention, auditor acceptance and institutional ownership must become measured decisions before expansion. The useful outcome is an accountable closed payout session and independently checkable evidence, rather than a larger version of the current national dashboard.
