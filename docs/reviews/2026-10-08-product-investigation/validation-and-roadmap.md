# Validation and decision roadmap

2026-10-08. **Proposed work only:** no implementation, commit, issue or deployment authorization. Maintainer clarified hackathon-only scope, DSWD as intended government body for disaster-relief funds, no pilot operator/authority, and finance ledger as an alternative. Read [verdict/findings](product-review.md), [evidence](evidence-and-journeys.md) and [target blueprint](redesign-blueprint.md). Institutional adoption, dates, ownership and grant rules remain provisional. Milestones are ordered dependencies, not invented estimates or a promised release schedule.

## Hackathon priorities

These are the next-product proposal for the stated contest context, not permission to make changes:

1. **H1: make the trust demonstration truthful.** Keep genuine local transaction/hash evidence, fail closed on absent/unreachable/rejected anchors, bind results to the selected record and stop the fixed5000/cash-delivered/corruption guarantees. Clearly label simulated scenarios in UI and API; use actual covered-field changes when claiming a genuine mismatch. DSWD is an intended audience, not an endorser.
2. **H2: tell one complete synthetic job.** Prefer Direction C's approved-roster→recorded payout→usable acknowledgement→reconciliation→recipient discrepancy story, with simulated roles/approval/payment explicitly labelled. A matching digest and an unresolved cash complaint can coexist. Scope down to a few invented households; remove national-scale, biometric, OCR, offline-sync and cost claims unsupported by the demo.
3. **H3: make it reproducible and usable.** Isolated reset reconciles existing local anchors/real references or visibly creates a new demo instance; browser/API failures state what happened; receipts work; key mobile/modal interactions are usable. Update README/pitch/API feature statuses together. No real recipient data, production key or external deployment needed.
4. **H4: compare finance-ledger alternative before choosing it.** A compact document-release→human review→correction→retained export story may be better for a finance audience, but this is not the selected direction. Validate the judge/stakeholder job; simulated authority must remain explicit. Do not build both workflows just to enlarge scope.

Authentication, institutional integrations and field studies are not prerequisites to a visibly synthetic local hackathon demonstration. They become requirements before real records, funds or institutional claims. The future-pilot sections below deliberately establish that separate bar; no pilot exists or is authorized now.

## Decisions before operational implementation

1. **Owner and job:** name the buyer, accountable payment authority, data controller, supervisor/accounting owner, grievance owner and technical support contact. Choose one actual program, event, payment channel and site. Is the unmet job payment execution, reconciliation, recipient complaints or interagency eligibility? Approve a PRD around that answer.
2. **Policy pack:** supply approved grant/eligibility/representative/repeated-assistance rules and current SOP; obtain ECT MC24/2025 amendment if applicable and current accepted accounting/audit requirements. ECT and AICS differ. Decide what the product records versus what the payment authority/provider actually executes. Do not inherit statutory5000 or10000 assumptions from code.
3. **Evidence and witnessing:** determine original acknowledgement evidence, recipient confirmation, independence of reviewer/checkpoint retainer and exact covered fields. Test whether signed retained closing packages are enough, or public roots add needed assurance. A signed-only output is never chain-verified; a chain result always requires a real read/match. Decide acceptable pending-anchor interval and consequences of missing proof.
4. **Operating boundaries:** online controlled site initially, or a demonstrated offline requirement? Specify paper/alternate-channel fallback, device/work ownership, unknown-payment handling and reconciliation before adding queues. Choose one supported backend; active `server.py` and dormant FastAPI must not continue as ambiguous release targets.
5. **Privacy/custody:** obtain controller/DPO decisions on audience/fields, lawful processing, retention, access/lookup, dispute confidentiality and public aggregates. Name signing-key custodians and independent retainer; plan compromise, revocation and recovery. No compliance certificate follows from storing names off-chain.

PRD, DFD and ERD are missing; ADR empty. Two finance-first scratch drafts appeared during review and were fully inspected; the maintainer confirmed they are an alternative, not authoritative chosen scope. These gaps do not prevent an honest synthetic demo or evaluating observed defects, but they prevent claiming institutional approval. Before consequential development, choose scoped Direction C or finance-ledger Direction D, document requirements and approve required schema/hash/interface/dependency decisions, with compatibility/migration ADRs. Do not delete a backend or change generated manifests by hand.

## Integrity blockers before real recipients or funds

| Gate | Required behavior / owner | Evidence that closes it |
|---|---|---|
| F01 truthful proof | Engineering + evidence owner preserve absent/unreachable/pending/rejected/mismatch/matched; never invent tx/hash; verdict bound to exact version | E01/E02/E10 failure matrix, independent chain reads, stale/out-of-order response checks and readable UI/API state snapshots |
| F02 truthful evidence claim | Product/evidence owner describes covered fields and cash acknowledgement separately; accurate variable approved amounts; all simulation labelled | Name/file/covered-field probes E03; recipient comprehension test; simulated UI and API labels verified |
| F03 accountable access | Controller + owner assign named staff scopes and least necessary permissions; public fields approved | Direct HTTP role/scope tests, public enumeration/redaction review; auditor cannot pay/reset; actor in events |
| F04 recoverable payment | Payout authority + engineering define attempt identity, atomic entitlement claim and handover protocol; reconcile ambiguous chain/provider results | E06/E07 concurrent/lost-response/failure-order tests with one durable attempt, actionable recovery and no duplicate authorized handover |
| F05 governed roster/resources | Authority approves entitlement/amount/version and resolves identity cases as humans; scope/budget rules explicit | Rejected/unknown/foreign-session and legitimate-repeat tests; false-positive resolved without deletion; amounts and totals agree with approval |
| F06 history/corrections | Records owner retains originals, append-only audit and superseding corrections; demo reset absent operationally | Every state change reconstructable with actor/reason; rejected action correctly described; correction/dispute closure and export traceability |
| F07–F09 complete operation | Supervisor has usable acknowledgement, recovery, reconciliation, assigned exceptions and retained closing package | End-to-end drill from approved roster through receipt and private dispute to signed closure/independent retention |
| F10/F11 support readiness | Operator owns supported versions, access/config readiness, backup/restore, logging, monitoring and support; task UI accessible | Restore rehearsal with original evidence/proofs, key incident drill, dependency applicability review, keyboard/mobile/failure walkthrough and truthful docs |

An anchored match cannot close a physical-payment dispute. A green screen is not acceptable evidence for these gates. No real pilot should rely on the existing fail-open implementation even if all current tests/builds pass.

## Coherent delivery slices

These milestones apply only if the project pursues an institutional product beyond the hackathon. M0 is not a prerequisite for a labelled synthetic H1–H4 demonstration.

| Milestone | Depends on | Complete user outcome / exit evidence |
|---|---|---|
| **M0: decide and validate job** | Named institution and policy/evidence pack | Approved bounded PRD, current workflow observation, accepted closing-package prototype and chosen trust/witness boundary; reject/change direction if unnecessary |
| **M1: make the supported lab honest** | Backend selection, F01/F02 state contract | Existing seeded record genuinely matches or explicitly fails; demos visibly simulated; no fake authority/status/tx; documented integrated failure checks pass. Still synthetic-only |
| **M2: approve a roster and open a session** | Scope/access/audit/schema decisions | Authorized humans publish a sourced roster/amount version, resolve ambiguity and assign payment work. No unsupported automatic eligibility; approved limits and private fields tested |
| **M3: record and recover one payment job** | M2 + attempt/evidence/hand-over policy | Correct original acknowledgement and stable receipt; lost response/retry/concurrent attempt recover safely; pending/failed anchor separate; explicit stop/fallback. Drill remains synthetic |
| **M4: close and challenge a session** | M3 + correction/retention/witness decisions | Supervisor reconciles resources/channel outcomes and exceptions; independent package retained; recipient can privately dispute matching or missing evidence; correction retains old versions/proof |
| **M5: authorize bounded real pilot** | All gates + support/restore/privacy/security review | Accountable owner approves pilot protocol, trained operators, recipient help/complaint channel, monitoring, rollback/fallback and independent observation; required network deployment separately approved |
| **M6: expand only on evidence** | Observed safe pilot and adoption benefit | Measured workload/connectivity, staff outcome improvement and witness usefulness justify specific scale/integration work |

M1 is necessary safety work, not a replacement for M0 or a complete MVP. Each later slice completes a user job rather than adding disconnected pages. Choose smallest useful intake: an approved roster can avoid building a new eligibility platform or speculative AI pipeline.

**Conditional finance-first track:** if Direction D is confirmed, replace M2–M4's payout scope with (1) document-backed release intake and logical duplicate review; (2) named authorization/approval and truthful authority-versus-transfer balances; (3) correction, exact file-plus-entry integrity check and retained export/closure. Do not build entitlements/scanners/payout attempts until a separately validated payment job calls for them. Source evidence, approval, audit, privacy, recovery, key/restore and compatibility gates still apply; cash-delivery and liquidation claims remain out of scope. Research finance workers and accounting recipients first. Challenge the draft's deferred sign-in/approval, file-hash-only deduplication and immediately counted entries before treating it as pilot-ready.

## Acceptance gate

These future-pilot criteria are proposed, measurable and unmeasured today; the immediate synthetic-demo scope is H1–H4 above:

- Every completed drill entitlement is explainable as unpaid, recorded with channel/acknowledgement evidence, unknown, held or disputed; no unexplained totals. Closure cannot skip required evidence/exception resolution. Compare funds/outcomes to the authoritative channel/cash records, not just the app's own rows.
- Every money-related attempt has a stable recoverable reference. Parallel/repeated requests and loss before/after server commit resolve to one authorized claim under the approved policy. Unknown outcomes never instruct blind repayment.
- All chain-outage/absence/rejection/mismatch tests produce truthful distinct API/UI states; no fabricated identifiers. Actual matches include record/version/network and covered-field provenance. Slow/out-of-order requests cannot attach another record's verdict.
- Original acknowledgement is accessible to authorized users after refresh and restore; covered payload/version and retained evidence are consistent. Discrepancy copy states uncertainty and does not accuse a person automatically.
- Every registration/approval/rejection/payment/correction/configuration state change writes an accurate actor/reason event; no operational audit deletion. Human review decisions and disputes are independently reconstructable.
- A recipient can find their scoped record or receive assisted/paper help and report a short/missing payment even when the anchor matches. Private reference, named response owner and next step are available; response target is agreed with that office.
- Role/cross-program direct API tests deny unauthorized operations and private data. Public field/retention policy is approved; no identifying unresolved-fraud flags public by default.
- Keyboard-only and narrow-screen users can complete applicable tasks: proper form names, focus entry/trap/return, error instructions, no raw-hash layout expansion. Language and amount/proof comprehension are validated with actual users.
- Backup/restore and signer/reconciliation drills retain originals, history, proof material and truthful unknown states. Named staff know stop/fallback and support escalation. Supported runtime/dependency review is complete.

Do not announce pilot readiness until the responsible owner signs these results. Pre-register success thresholds from current baseline rather than choose an arbitrary product score.

## Research with actual people

Recruit with the accountable institution and appropriate privacy/consent arrangements; do not use actual beneficiary data in development artifacts. Proposed samples are recruitment plans, not completed research: observe several payout/reconciliation sessions; interview roughly5–8 field/registration workers,3–5 accounting/supervisor/audit staff, and8–12 recipients/representatives including people without smartphones and people needing assistance. Adjust for language, disability, access and program diversity; these small qualitative samples do not estimate prevalence.

Ask workers to show actual sequence, paper/provider records, duplicate ambiguity and recovery from interruption. Observe the handover/acknowledgement boundary, permitted repeated assistance, session/device assignment, electricity/connectivity and closing/reporting burden. Ask accounting/auditors to reconstruct a case using an existing package and proposed package, then identify what evidence they would accept and what gaps require investigation. Do not ask whether they “like blockchain.”

Ask recipients to explain their approved award, what a matching/absent/unavailable result means, what happens after an incorrect payout and whom they can safely approach. Test receipt access and assisted complaint routes without assuming literacy, Filipino/English comprehension, smartphone possession or willingness to challenge an officer. Do not manufacture quotes or use prototype preference as adoption evidence.

Collect current-baseline event timestamps for preparation, payment recording, unknown-outcome resolution, reconciliation, liquidation and audit independently. Candidate pilot measures: extra transcription steps, unresolved outcome/evidence count and age, wrongly merged/denied cases, duplicate payable attempts, reconciliation discrepancy, recipient proof comprehension/help completion, privacy incidents and staff support burden. Payment/reconciliation correctness is a safety gate, not a tradeoff against faster clicks. Task timings/clicks will be measured only during observed studies.

## Experiments that can disprove the recommendation

| Hypothesis | Proposed experiment | Result that should change direction |
|---|---|---|
| Reconciliation is an unmet job | Walk through existing payroll/provider/FO system and close a historical synthetic drill with/without workbench | Existing process already resolves gaps reliably; workbench adds duplicate entry without meaningful evidence benefit → integrate/export or stop |
| Independent commitment adds useful assurance | Auditor blind comparison: ordinary signed retained package vs package with public root/proof; introduce post-commit edit and missing record | Root changes no detection/action, retention already sufficient or proof material too burdensome → keep signed witness, reduce blockchain |
| Recipient evidence can reveal shortfall | Role-play same anchored record with declared full payment and contradictory recipient report; test independent help route | Matching hash is mistaken for cash proof, or report reaches only accused cashier/no remedy owner → fix channel/governance or prefer recipient service B |
| Approved roster and attempt controls fit work | Simulate same-name distinct families, legitimate repeat aid, representative change, concurrent officers and interrupted response | Legitimate recipients blocked or staff must bypass system to pay → revise domain/assignment before pilot |
| Online bounded pilot is viable | Observe connectivity; rehearse stop/paper fallback/reconciliation at chosen site | Outages routinely force untraceable work or unsafe retries → choose digital-provider import/reconciliation scope or approve governed offline design first |
| Closing package will be accepted | Target accounting/audit staff review evidence and current documentary requirements | Package cannot support accepted reporting or lacks material acknowledgement → change evidence intake/scope; do not claim hash replaces documents |

## Scale constraints and explicit triggers

No load benchmark was performed. Illustrative workloads below are assumptions, not adoption predictions: a session with1,000 households/day and5 devices; later10,000 roster rows; eventually many independently owned programs. For10,000 rows the current all-pairs CSV path considers49,995,000 pairs before processing details. That arithmetic identifies a cost mechanism, not measured elapsed time.

| Constraint | Evidence now | Expand only when / proposed response |
|---|---|---|
| Duplicate matching | Deterministic name/address pair comparison O(n²); uncalibrated confidence | Measured imports miss agreed preparation window or false-positive burden is high → block candidates/index/validate household attributes; humans still decide |
| Concurrent work | Two same-household claims saved; one race anchor absent; shared signer nonce contention is a possible mechanism, not a retained observed error; SQLite thread interactions | Pilot concurrency verified first; observed contention/independent teams exceed simple deployment → atomic scoped transactions, explicit work assignments and durable signer serialization; datastore change only after measured need and approval |
| Chain latency/cost | Node subprocess/wait8seconds;183265 gas one local receipt, no production fees | Synchronous dependency already unnecessary for cash recording; measure cadence/backlog/retries/fees → durable jobs/checkpoint batches; public deployment approval and fee budget required |
| Files/storage/privacy | One sample receipt, no actual retention/backup operation | Actual evidence size/retention and access requirements established → private object/file storage with integrity/access/backup; dependencies approved, no public bucket assumption |
| Backups/reconciliation | No institutional restore exercise; DB/chain can diverge | Required before pilot regardless of volume → restore original versions/proofs plus reconcile pending/unknown jobs; monitor missing acknowledgements and balances |
| Key custody/witnessing | Local dev signer/node; operator controls assertions | Required before independent proof claim → accountable key custodian, independent retention and revocation/incident procedure; production keys never copied from development |
| Support/monitoring | UI status conflates readiness; no assigned support | Required before pilot → monitor attempt unknowns, failed/old anchors, receipt errors and reconciliation exceptions; staffed escalation. Add infrastructure only when measured operating needs justify it |
| Multi-institution scale | One-batch UI, public entire registry, missing scope | Independent owners/policies appear → explicit tenancy/scope/governance and accepted exports; validate organizational ownership before centralizing personal records |

One public root can reduce transactions, but needs proof distribution/retention, correction/version policy and an explicit interval of unanchored records. It does not prove roster completeness, truthful original input or actual cash receipt. No microservices, Kubernetes or extra cloud stack is justified by this investigation.

## Highest-impact cause-to-decision mapping

| Observed problem | Underlying cause | Product decision | Proposed behavior | Acceptance evidence |
|---|---|---|---|---|
| Chain outage/absence green (F01) | Fail-open fallback / boolean evidence | Integrity is independently read evidence, never convenience fallback | Explicit unknown/absent/failed states, exact-record proof | E01/E02/E10 cannot produce green without match |
| Recorded2000 with API-reported match displayed as delivered5000 (F02) | Demo award and cash truth conflated | Separate entitlement, recorded amount, acknowledgement and integrity | Evidence/source values with shortfall dispute despite match | Variable-award + comprehension + complaint drill |
| Two concurrent claims / lost response confusion (F04) | No stable attempt/atomic claim | Payable work is an accountable recoverable attempt | Same reference/status on retry; unknown handover protocol | Parallel/lost-response/two-system-failure matrix |
| Blank auto-approved / rejected claim recorded (F05) | Similarity treated as eligibility | Humans authorize a program-specific entitlement | Approved roster/version gates assigned payment | False-positive, rejected, cross-program and repeat-aid tests |
| Delete/reset hides history (F06) | Demo admin / mutable current state | Corrections preserve evidence; operations cannot reset | Superseding versions + actor/reason + private disputes | Reconstruct complete case before/after restore |
| No usable receipt/closing job (F07/F09) | Pitch flow ends at anchor | MVP closes an approved session | Original acknowledgement + channel reconciliation + retained package | Independent reviewer explains every outcome/fund |

The direction should survive these experiments before scope grows. Unknown field facts are the reason for this validation plan, not evidence that the current mechanism already works operationally.
