# AyudaChain, explained

Finalist briefing, 14 October 2026. Candidate: `design-proposal`, starting at `4377db1`, with the local finals changes described in [readiness](FINALIST_READINESS.md). This is a local prototype using invented households. No government endorsement, live deployment or real payment is claimed.

## The one-sentence explanation

AyudaChain connects the evidence behind disaster cash assistance—from funding documents to household decisions and recorded handovers—and lets an independent reviewer check whether committed records still match their blockchain fingerprints.

The software records cash assistance; it does not transfer pesos, issue tokens or replace government approval. A blockchain match means the saved evidence matches its commitment. It cannot tell whether an uploaded document was genuine, an officer told the truth, a household was affected, or cash physically changed hands.

## The problem we address

A payout has several different questions: Was funding recorded? Why was this household included? How was the amount calculated? Who recorded the handover? What did the recipient say afterward? Has the supporting evidence changed? A spreadsheet of totals does not by itself connect those answers.

AyudaChain preserves linked versions, originals and human decisions. It separates recorded handover, recipient report and current integrity check. A disagreement becomes evidence for human review, rather than an automatic fraud accusation or an automatic second payment.

## Five people, five jobs

| Person | Their job in this prototype | Important boundary |
|---|---|---|
| Beneficiary | Register the household, submit damage information, inspect own decision/amount/appointment, authorize an attempt, privately report what was received | Cannot approve themselves or record cash handover |
| Barangay Officer | Assist registration, attest residence/affectedness, give category opinion, reply to referrals; Punong Barangay submits responded threads with a council resolution | Cannot approve eligibility, set amounts, pay, or see private recipient outcomes; an assister cannot endorse that household |
| DSWD Officer | Record funding and operation authority; open intake; review registry/claims; record documentary calculation inputs; publish lists; schedule staff; resolve cases | Does not hand over cash or type an individual household's grant amount; own-household decisions are barred |
| Disbursing Officer | Work an assigned session, compare the person/photo ID, present the computed cash and record the authorized handover once | Cannot change eligibility/amount, pay outside assignment, or answer privately for a payout they made |
| Auditor | Inspect exceptions, original evidence, versions, recorded amounts/outcomes and fresh chain comparisons | No approval, rejection, deletion, payment or business-note action; inspections are separately logged |

These are stored workflow scopes for a selected actor. **There is no sign-in gate on this branch. Anyone can impersonate an active actor.** Scope checks are implemented, but secure authorization, operational privacy and authenticated accountability remain pending. Never enter real citizen data.

## What happens from beginning to end

1. **Record funding evidence.** DSWD uploads an original release PDF. Actual PDF text extraction can prefill fields; a person confirms the reference, amount, purpose, coverage and printed signatories. Image-only/scanned documents may need manual confirmation; this is not a universal OCR service. Both extracted and confirmed values remain inspectable. A correction appends reversal and replacement records; it does not rewrite the original. Funding authority is not reconciled physical cash.
2. **Open intake deliberately.** Recording a release does not open claims. DSWD separately supplies operation authority, covered barangays and a response window.
3. **Register a household.** A recipient can register directly or obtain help. Contact phone and ID are optional at registration. A no-ID household can claim, but payment waits for documented field checking and accepted photo ID. Private identity/contact details use a separate recipient panel. Declaring an address alone does not grant access to residents' lists.
4. **Submit and review the claim.** Submission freezes the relevant household/claim version. Barangay responses attest residence and affectedness; DSWD decides eligibility and final category. Recusal prevents an officer responding to their own or assisted household. Missing staffing/response/submission produces a labelled system-forwarded snapshot; it never invents endorsement, sender or resolution.
5. **Run checks without replacing judgment.** Local duplicate checks compare household/person/ID/contact and related assistance records, including near matches. Flags direct attention; they are neither an automatic rejection nor proof of fraud. Review acknowledgments refer to the current check; changed evidence can require rechecking.
6. **Calculate and publish.** DSWD records supported wage/day inputs or supported fixed-category values. The wage mode is `ceil((0.75 × daily wage) / ₱10) × ₱10 × documented days`. The demonstration's invented ₱435 wage and 15 days yield ₱4,950. This is a synthetic calculation example, not a claim about today's mandated regional rate. Missing inputs mean awaiting amount. A list publishes only after its own matching chain confirmation and current-version checks.
7. **Schedule the payout.** DSWD records a date/site, current published members and named staff. Notice SMS is explicitly simulated; a saved notice does not establish handset delivery. Cash actions need an open session on its Manila date. Cash availability, advances and liquidation remain external/deferred.
8. **Authorize and record cash once.** The recipient opens a short-lived attempt under a stable transaction ID. A six-digit code is revealed once and expires after ten minutes. The officer compares identity and presents the fixed amount for counting. The recipient reveals the code at handover. The final review dialog restates household/amount before the request; the backend still checks current eligibility, versions, assignment, date, comparison and unused authorization atomically.
9. **Support a person without a phone.** The supported assisted path uses the recipient's privately established PIN after identity comparison, an officer's connected device, and a distinct eligible assigned checker. PIN and payout code are different. PINs/codes are stored as salted verifiers, never in blockchain material. General PIN recovery and registered-phone assistance are pending. These are prototype product controls, not asserted government requirements.
10. **Keep the receipt and hear the recipient.** Recorded handover locks the amount and consumes entitlement once, even if anchoring fails. The recipient later reports full, less or not received. Adverse answers open/reopen a private grievance for human handling. No answer after 72 business hours becomes neutral unconfirmed. Late/revised answers retain history and never create another payment. An assisted checker may record the answer; the actual payer cannot.
11. **Inspect independently.** An Auditor opens the actual evidence and requests a fresh integrity comparison. The signer-free CLI can recompute the exact saved envelope and original-byte hashes, then query the pinned deployment without database access or signing key. It still needs authorized access to private evidence material.

## What blockchain adds, and what it does not

PostgreSQL stores the private business record and its history. Private files hold original bytes. A separate local EVM registry stores opaque references and hashes; funding entries also expose signed centavo amounts. Household names, ID numbers/photos, phone numbers, receipt contents, payout codes, PINs and private answers stay off-chain. Public metadata and linkage can still carry privacy risks that require assessment before a real deployment.

The evidence-v1 envelope binds the exact saved version, original-file descriptors, context, predecessor/related references and a private random nonce. Its hash is SHA-256 over `AYUDACHAIN-EVIDENCE-v1\n` plus the canonical UTF-8 envelope. This is a separate versioned protocol; the original receipt hasher and legacy registry remain unchanged.

There are ten actual commitment kinds: document, amount input, barangay submission, system fallback, approved list, handover, outcome, fund release, reversal and replacement. Not every audit event is separately anchored. A compromised privileged database operator may alter local storage; independent comparison with an independently retained chain is intended to reveal divergence in committed evidence. Omitted events, false initial statements and collusion remain outside that proof.

The current node is Hardhat on loopback, chain ID 31337, with one mined local block as the prototype confirmation policy. It is not a public Polygon deployment or independently governed distributed trust system. It demonstrates the protocol and failure behavior. Real benefit beyond the operator requires an approved independently retained network/checkpoint and key governance. A signed database log or external timestamping service is a legitimate alternative to evaluate.

## Truthful states

| Display/result | What can be said |
|---|---|
| Not checked / checking | No current integrity conclusion yet |
| `match` / Verified | Actual pinned chain read agrees with the required committed evidence |
| `mismatch` | Evidence or committed fields disagree; investigate, without assuming why |
| `required_anchor_absent` | The pinned chain was read and that required record was absent |
| `chain_unreachable` | The chain could not be read; neither match nor absence was established |
| `evidence_unavailable` | Required private evidence/deployment material could not be obtained or validated |
| Confirmed submission | A stored historical submission observation; use a new integrity check for a current conclusion |

After a failed refresh, a former match is explicitly historical. A transaction candidate hash is not mined confirmation. Funding remains recorded during an anchor failure; publication waits; a handover remains consumed.

## Technical inventory

| Area | Implementation evidence | State/limit |
|---|---|---|
| API / commands | `backend/app/main.py`, `commands.py`, `actor.py`, `routes_*.py` | Actual FastAPI commands, stored actor scope, revisions/idempotency and transactional audits; identities are claimed |
| Data | `backend/app/models/mvp.py`, `database.py`, `backend/migrations/catalogue.py` | PostgreSQL typed relationships, immutable versions/current projections and grants; privileged owner can bypass local safeguards |
| Originals | `services/evidence.py`, `extraction.py`, `EvidenceUpload.tsx` | Actual private-file writes/retrieval and bounded PDF extraction; no authenticity/signature validation |
| Funds | `services/funds.py`, `Funds.tsx` | Exact centavos, duplicate-source controls, appended correction pair; no advances/returns/liquidation or certified cash |
| Registry/claims | `services/registry.py`, `claims.py`, `checks.py`, `Registry.tsx`, `Claims.tsx` | Assisted registration, responses/recusals, fallback/referral, human decisions; no national registry connection |
| Amounts/lists | `services/entitlements.py`, `Lists.tsx` | Documentary inputs, exact calculation, paid locking and own-anchor publication |
| Sessions/payouts | `services/sessions.py`, `payouts.py`, `Sessions.tsx`, `Payouts.tsx` | Assigned/date/version guards, PIN/code workflow, once-only handover, unknown-reply recovery; online only |
| Outcomes/audit | `services/outcomes.py`, `audit_views.py`, `routes_audit.py` | Private revised answers/cases, separate handover/outcome totals and private Auditor access logs; authenticated privacy pending |
| Blockchain | `services/commitments.py`, `evidence_protocol.py`, `integrity.py`, `contracts/scripts/anchor_worker.js`, `AyudaChainEvidenceRegistry.sol` | Actual local submission/read, durable exact-signature recovery, deployment pinning; no public deployment |
| UI | `frontend/components/mvp/`, `mvp.css`, `DESIGN.md` | Material 3 Sea-and-Sun, light/dark, five role routes, phone layout, English/Filipino guidance; translations/device accessibility need further validation |
| CSV / lookup | `services/csv_intake.py`, `routes_lookup.py`, `CsvIntake.tsx`, `SessionLookup.tsx` | Staged head declarations and manual/optional native QR lookup; CSV is not full private onboarding, physical camera not validated |
| Legacy | `backend/server.py`, original hasher/registry, retained frontend routes | Separate historical interface. `/verify` reads frozen legacy evidence; use `/mvp` for this journey |

**Simulated:** National ID check, notice SMS, any explicitly accelerated business clock, represented physical cash. Core business persistence, original bytes, calculations, local chain operations and recovery are actual.

**Incomplete:** authenticated accounts/recovery, secure hosted file access, government signatures/approvals, live identity/SMS integrations, offline payout, full official FACED mapping, selective resident inclusion proofs, operational backup objectives, network/key governance, financial liquidation and production security review.

**Reproduced defects in the starting candidate:** duplicate registration text broke the journey selector; verification concatenated status/time; raw errors lacked permitted next steps; cash saved without a final review; several tests assumed Windows Python; a journey test invoked reset. Finals changes and current test results are listed in [readiness](FINALIST_READINESS.md). Historical validation is not a substitute for today's results.

## Useful branches and why they cannot simply be combined

`design-proposal` adds the Tonal visual layer over the complete MVP. `feat/five-role-mvp` has the same substantive backend/contract baseline plus useful later role-error recovery (commit `1644f59`); its UI recovery changes were selectively brought into this worktree. Its published source-copy/showreel artifacts are not a reason to import the whole tree. `pivot/ideation` preserves process/design history. `main` contains the old prototype.

BinkzBooze's open PR stack independently adds authentication, allocation caps, legacy receipt improvements and a Tonal adaptation to a FastAPI/SQLite architecture. These are useful ideas and separate implementations, not interchangeable MVP files. It changes original contract/hash/accounting surfaces in parts of the stack. The current PRD deliberately separates recorded authority from cash and does not implement that stack's allocation caps. Choosing a future consolidation baseline needs an explicit product/accounting/compatibility decision. See [triage](GITHUB_TRIAGE.md).

## How to present it honestly

Say: “We have a local five-role prototype with actual document-backed records and local blockchain checks. It preserves a reviewable trail; people still decide.” Show a saved document, a human decision, the calculated amount, one recorded handover, the private recipient answer and a fresh chain comparison.

Do not say “fraud-proof,” “government-approved,” “production-secure,” “offline-ready,” “all citizens need smartphones,” “AI approves claims,” “the blockchain proves cash arrived,” “public Polygon deployment,” or “zero-cost nationwide rollout.” Our next request is a supervised workflow-validation partner and agreed production-readiness criteria, not permission to use real citizen records tonight.
