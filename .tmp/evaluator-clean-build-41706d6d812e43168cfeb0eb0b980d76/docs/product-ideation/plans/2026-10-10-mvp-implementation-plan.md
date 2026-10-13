# AyudaChain functional five-role MVP implementation plan

Date: 2026-10-10. **Status: reconciled proposed execution plan; unimplemented and not approved for execution.**

**Goal:** implement funding evidence → household claim → barangay response/submission → DSWD human approval/computed entitlement → confirmed approved-list publication → session → recipient authorization → once-only recorded handover → private outcome → independent Auditor evidence review.

**Spec:** [authoritative PRD](../../product/prd.md) and [proposed ERD](../../system/erd.md). PRD AC-01–AC-26 are requirements; ERD is the single proposed schema/state/representation authority. This plan defines engineering work, not new institutional rules.

**Architecture proposal:** retain Next.js/React/TypeScript; select one FastAPI API with PostgreSQL and private local originals. Durable Node/ethers work and independent reads use a proposed separate local evidence registry. Preserve legacy protocol/deployment reads. Backend/schema/dependencies/protocol/contract require consolidated approval below.

**Execution:** one integrated serial sequence, independently testable stages, no commits as steps. This session writes documentation only. Do not implement/install/migrate/change contracts/deploy/commit/push from this request. Later execution settles applicable approvals first. No subagent workflow required.

## 1. Authority, scope and reconciliation

Current maintainer instructions and [AGENTS.md](../../../AGENTS.md) outrank historical material. Settled [process](../process.md), [decisions section 16](../decisions-2026-10-08.md#16-end-to-end-process-2026-10-09), [DFD](../dfd.md), consistent [roles](../roles/)/[funds drafts](../drafts/) supply provenance. [Mockup](../mockup/README.md), [integration research](../research/2026-10-10-blockchain-integration.md) and [primary-source research](../research/2026-10-10-blockchain-primary-sources.md) are proposals. Preserve historical ideation.

The current target is the **full functional five-role MVP**, extending funds-only version 1. Editable forms, persistent records, checks, original files, human decisions and actual local chain behavior are core. The funds-to-Auditor slice is an early milestone. Seeds supply reference actors and synthetic inputs; business actions must run through the actual services. Browser timers and fixtures cannot supply business or chain success.

No login gate. Multiple claimed/unverified selectable actors per role, eligible/recused staff and independent payer/checker. Server loads stored active context and applies rules/scoped views; anyone can impersonate another actor. Real sign-in, secure sessions, credential recovery and authenticated authorization **Pending**. Code/PIN are workflow controls, not authenticated identity. Synthetic records only; authenticated access required before real private household records.

National ID and notice-SMS named labelled simulations; in-app notices real persistent records. Optional accelerated business clock labelled; chain timestamps/references/reads actual. No live datasets/auth/SMS provider, production host, FACED mapping or institutional approvals selected. Exclusions/Pending scope follow PRD.

| Earlier plan problem/choice | Reconciled treatment |
|---|---|
| Missing PRD/ERD, plan product/schema authority | Both now govern; remove duplicate tables/payload definitions. Product/model changes first in respective authority. |
| Demonstration could mean presenter output | Functional editable/persistent target; mockup stories references, not implementation state engine. |
| Actor-owned household and JSON members/input/session maps | Stable identity/member rows, distinct versioned contact/account linkage, relational category rules/assignments/membership. Relink never recreates entitlement. |
| Generic record IDs/evidence/replay arrays | ERD exclusive typed FK arcs/XOR/role constraints; domain relations explicit. |
| Stopped retry on compulsory later date | Distinct later session after clearance; same calendar date allowed when valid. No invented next-day rule. |
| Fixed categories/day caps/weights treated settled | Fixtures/versioned reversible check settings, not FACED/legal policy; documentary wage/day/amount no default. |
| Backend/new contract treated selected | Approval-dependent recommendations; refresh official support/security at execution, no future-patch assurance. |
| Duplicate protocol/schema/vector copies | ERD `ayudachain.evidence.v1`, private UUID/public bytes32, states/types/FKs authoritative. T01 ADR precise format/ABI; T03 computes independent vectors. |
| Parent match hid missing components | Exact current per-component coverage, list vs document separate; material only if all fields permitted; resident inclusion Pending. |
| Conditional signature validation in earlier draft; unspecified trust integration | Latest process distinguishes actual validated evidence without selecting a mechanism. Proposed Pending deferral is explicit in PRD; retain original bytes/printed names as not_validated. Decide before execution whether conditional validation is retained as MVP core. |
| Absent amount counted as complete zero total | Computed/locked subtotal plus awaiting count/incomplete label; no zero/default entitlement. |
| Prior 284h underestimated completion | 398h baseline; 497.5h with 25% integration allowance. Includes relational integrity, field visibility, races, restoration and the full journey from reference seeds. |

Inspected actual root scripts/standard-library SQLite server and drifted FastAPI backend, shared chain service/adapter/hasher, frontend/mockup, contracts/tests. Service fabricates failure references/matches; adapter truncates IDs/parseEther/read wallet; legacy payload excludes names/file bytes. Frontend role is localStorage; sample payout/timers/offline label/canned verify. Existing tests cover helpers/legacy chain, not pivot races. [Current sitemap](../../product/sitemap.md), [user flow](../../product/user-flow.md), [existing DFD](../../system/dfd.md) describe legacy; architecture/API/chain docs overstate behavior. No product suites/services run during documentation; research pass counts historical.

## 2. Model and interface authority

ERD defines all persisted entities/fields/relationships/states, private UUID IDs and independent public bytes32, centavo decimal strings, exact NUMERIC totals, UTC/Manila dates, nullable inputs/evidence and I/P history distinctions. No competing schema here.

Identity: `resolve_identity(selected_actor_id) → ActorContext(actor_id,role,office_id,barangay_id?,household_id?,member_link_id?,identity_assurance)`. Resolve stored active role and scope, current beneficiary linkage and staff member linkage; reject body overrides. Future authenticated mapping returns the same context. No token, provider, session or login schema is introduced now.

Command: `execute_command(context,command_name,request,handler) → resource_ack`, with actor, idempotency key, request ID and expected revision. One database transaction owns the action, typed audit and required commitment/job intent. Hash requests with an environment-keyed HMAC; store the ERD's typed result references, never plaintext secrets or cached private payloads. Identical replay returns a currently permitted resource; changed body returns 409. Recheck actor activation/scope. Refusal counters may commit without saving the forbidden action. RPC and extraction run outside the office lock.

Base `/api/v1`; use `X-Demo-Actor-ID`, an `Idempotency-Key` mutation header and expected revision for current-projection changes. Reject extra fields and client handover amounts. Use 403 for prohibited operations, 404 for inaccessible/missing resources, 409 for stale/state/duplicate/key conflicts, 422 for invalid input and 503 for unavailable required database/storage. A fresh integrity result is distinct from an API/network outage. Use bounded deterministic paging and generated OpenAPI/TypeScript types rather than duplicated enums.

Success/error metadata: `mode=local_synthetic_evaluation,identity_assurance=claimed_unverified,authentication=pending`, actor/request ID, simulated services, `blockchain_simulated=false`, clock mode/business time. Actorless catalogue/health no private record data. JSON/binary/material/history/error/replay share projection/no-store; UI actor switch clears secrets and ignores delayed former-actor responses.

| Proposed interface | ERD source/result |
|---|---|
| `GET /actors/catalogue,/disasters,/barangays,/health`; `POST /nominations,/actors/{id}/activation` | Reference/current actors and real nomination provenance, DSWD activation only, no DSWD/Auditor administration/auth. |
| `POST /evidence` multipart; `GET /evidence/{id}/content` | Actual original/version/digest/extraction or manual-required; restricted stream, no upload-only ledger/anchor success. |
| `POST /funds/releases,/funds/{id}/corrections`; `GET /funds` | Confirmed fields/evidence, reason/kind/head revision; entry/set/totals/component anchors. |
| `POST /households,/households/{id}/reviews`; `GET /households/{id}` | Member/registry and separate linkage versions/documented checks; helper no private echo. |
| `POST /operations,/operations/{id}/close` | Explicit basis/coverage/duration/open/close, not inferred from release. |
| `POST /claims,/claims/{id}/resubmissions,/claims/{id}/responses,/claims/{id}/decisions,/claims/bulk-approve,/claims/{id}/category` | Frozen submissions/round/thread parent/current check/human reason/category/question; actor/time server-owned. |
| `POST /submissions`; scheduler due route | Actual Punong responded-version/resolution or exact labelled system exception, no user system-injection endpoint. |
| `POST /amount-inputs,/approved-lists`; `GET /entitlements/{id},/approved-lists/{id},/residents-list` | Documentary mode/rules/scalar map, immutable list/current gate, own amount vs restricted projection. |
| `POST /sessions,/sessions/{id}/commands`; `GET /sessions/{id}` | Date/site/list/member/assignment, DSWD open/close/cancel/amend/followup_assign immutable versions. |
| `POST /sessions/{id}/id-checks,/households/{id}/assisted-pin,/entitlements/{id}/attempts,/transactions/{id}/clearances` | Current comparison/private recipient authorization/path/member, attempt/code first response only; stable stop recovery. |
| `POST /transactions/{id}/handover,/transactions/{id}/notes,/transactions/{id}/outcomes,/transactions/{id}/reports`; `GET /transactions/{id}` | Attempt/revision/code **no amount**, stable receipt ack; separate private outcomes/reports, payer no private history. |
| `POST /list-challenges,/list-challenges/{id}/events,/grievances/{id}/events` | Private target/report/human review/substantiate/dismiss/note/resolve retained histories, no cash reversal. |
| `GET /audit/exceptions,/audit/records/{kind}/{id},/audit-events,/notifications` | Typed projected queries, no arbitrary table access; private Auditor access before disclosure. |
| `POST /integrity/check,/anchor-jobs/{id}/retry`; `GET /commitments/{id}/material` | Fresh block/deployment/component result, permitted exact bytes/originals; DSWD unchanged retry, Auditor read only. |
| `POST /legacy/verify`, compatibility `/api/blockchain/verify` | Explicit legacy record/original protocol/deployment/limited coverage; actual refs, no latest substitution/pivot entitlement. |

Seams: `freeze_commitment(tx,typed_owner,payload)→commitment/job`; `process_due(now)`; `read_commitment(deployment,public_id)`; `reconcile_job(job_id)`; `apply_anchor_observation(observation_id)` under office lock; `check_integrity(context,commitment_id)→result/components/checked_at/deployment/block`. All types and state names from ERD.

## 3. Engineering defaults and ownership

Reversible defaults: office lock plus uniqueness constraints; whole snapshots without Merkle proofs; closed typed FK links; API-proxied local files; one worker/operator and at most one unresolved nonce; durable jobs; a labelled local confirmation policy requiring a successful mined receipt and matching getter; two-second due-work polling. Codes last ten minutes and allow five failed checks. Assisted PINs use salted scrypt and five failures per fifteen-minute window. DSWD enters response duration; 48h is a fixture example only. Reveal a code once in memory. Lost codes expire with the unused attempt before a new opening; general PIN recovery remains Pending. These settings control workflow, not sign-in.

Versioned check defaults: normalized name/birth-date matching, name similarity 0.88 and address-token similarity 0.80. Proposed weights are person 3, ID 5, phone 1, already aided 5, other barangay 4 and other review flags 1. Validate near-match fixtures and document adjustments; these settings never decide eligibility. No invented day cap, default grant or legal ceiling. Accept nonempty PDF/PNG/JPEG up to 10MiB with byte-type checks and generated immutable keys; reject HTML/SVG. Real text-PDF extraction uses bounded processing and manual review for scans/photos/failures. Save final immutable extraction metadata as the ERD specifies; preserve originals through restore. Institutional retention policy remains Pending.

| Proposed owner | Responsibility |
|---|---|
| `backend/app/main.py,database.py,actor.py,commands.py,projections.py,config.py,models/mvp.py,schemas/mvp.py` | One approved runtime/schema/context/atomic/projection authority; inactive legacy models/seeder/server frozen, no dual writes. |
| `backend/app/services/` evidence/extraction/commitments/integrity/funds/registry/claims/checks/entitlements/publication/sessions/payouts/outcomes/cases/notifications/audit_views/legacy modules | Explicit domain commands and serializers; preserve hasher, repair shared fallback only approved compatibility seam. |
| `backend/app/scheduler.py,adapters/simulated_national_id.py,adapters/simulated_notice_sms.py` | Real durable due work and labelled external simulations, no chain simulator. |
| `backend/migrations/,backend/scripts/,backend/tests/` | ERD deferred/typed constraints/grants, setup/export/import and meaningful tests; no startup create/drop. |
| `contracts/contracts/AyudaChainEvidenceRegistry.sol`; `contracts/scripts/` deploy_evidence/anchor_worker/read_chain/verify_evidence/lib | Approved separate contract/actual manifests/reliable submission/pinned reads; old contract/artifacts preserved. |
| `shared/protocol/` | Approved complete vectors, generated OpenAPI/TS, no second schema. |
| Existing frontend shell/roleContext/api; new workspaces `app/dswd/,barangay/,household/,payout/,audit/` and forms/actor selector | Real editable API-backed forms, recipient private panel, actor-clearing; mockup27 destinations not required routes. |
| Existing verify/beneficiaries/distributions/batch pages | Replace fake/offline/legacy mutations as functional alternatives land, retain labelled legacy read; no module deletion. |
| Proposed root `scripts/` setup-mvp/start-mvp/check-mvp/backup-mvp/restore-mvp PowerShell; fixture/CLI | Windows/local-owned processes/real-command journeys/recovery, no auto reset/redeploy. |
| Current README/CONTRIBUTING/AGENTS status/product/system/guides | Update implemented/simulated/Pending behavior as stages land, preserve ideation history. |

Approval-dependent additions: psycopg/alembic/pypdf/httpx, Node pg, dev Playwright/openapi-typescript; activate existing FastAPI/Pydantic/SQLAlchemy/uvicorn/python-multipart only after target decision. Retain ethers/Hardhat major unless official execution-time support requires approval. Exact supported versions/security patches/locks resolved then; no current/future patch guarantee or auth/SMS/cloud/broker/Merkle dependency implied.

Use a native or approved container database; production hosting is undecided. Development binds loopback ports 3000/8000/8545; isolated tests use 3001/8001/8555, separate database and manifests. Missing tooling is a prerequisite failure; install nothing now. Keep DSN, signer, RPC and digest credentials in ignored environment configuration and never print them. Read verification needs no key. Approved deployment scripts generate new artifacts; never hand-edit the two existing artifacts.

## 4. Integrated stages

Start each with named failing regressions; minimal real behavior then relevant checks/status-doc updates. Tests are future specifications/files, **not pass claims**. Real PostgreSQL separate connections for races/local EVM for chain successes. Failure probe cannot invent success. All stages serial and unchecked.

### T01 — Execution decisions/compatibility — 10h

Depends on consolidated approvals; covers AC-02, AC-23, AC-24 and AC-26. Produce the proposed ADR `docs/adr/2026-10-10-mvp-evidence-protocol-and-registry.md`, configuration and dependency locks after approval.

- [ ] Confirm the backend target. Follow CONTRIBUTING's branch rules from main in an isolated permitted checkout where necessary; preserve existing work, legacy data/files and deployments. Do not commit or push without a request.
- [ ] Record the ERD namespace, exact canonical format, public kinds, correction ABI, centavos, operator/deployment identity and legacy routing in the ADR. Compute complete vectors in T03.
- [ ] Record approved tooling, new local/test databases, ports, environment variables, package inventory and artifact paths. Confirm the explicit proposed signature-integration deferral or specify actual validation scope and update design/estimate. Choose no institution, hosting or authentication provider.

Acceptance (`test_preflight`): missing tooling and public-RPC/development-key misuse fail explicitly; repeated setup preserves state; every commitment and legacy route is specified. Revise the authoritative design if a proposal is rejected before building dependent stages.

### T02 — API/ERD/context/atomic commands — 32h

Depends on T01; covers AC-02, AC-03, AC-07, AC-22 and AC-25. Owns foundation models, migrations, actor resolution, commands and projections; tests in `backend/tests/test_foundation.py`.

- [ ] Implement the ERD's typed FKs, scope keys, deferred pointers, uniqueness, correction checks and immutable grants in a new database. Separate worker/reset roles; do not create or seed schema on ordinary startup.
- [ ] Implement stored-actor resolution, honest identity metadata, HMAC request digests, revision checks, typed replay, office locking and the private access-log path.
- [ ] Generate API/TypeScript types and a separate-client PostgreSQL/clock test harness. Distinguish check-data revision from ordinary business/job revisions. Approved runtime cutover retires legacy writes; no dual-write backend.

Acceptance: actor impersonation remains possible and labelled while scoped projections hold. Cross-scope FKs fail. Forced action/audit/intent failure rolls back everything. Replay reveals no secrets and rejects inactive actors. Concurrent stale edits have one winner; no dangling targets persist.

### T03 — Files/protocol/separate real registry — 28h

Depends on T02; covers AC-04, AC-23 and AC-24. Owns evidence, extraction, commitments and approved Solidity/deployment/read interfaces; tests in `test_evidence_protocol.py` and Node/contract vectors.

- [ ] Implement actual uploads, immutable storage, preparation recipient, byte/type/size checks, private retrieval, raw SHA-256 and bounded real extraction/manual review. Save final immutable metadata, never fabricated extraction.
- [ ] Independently test every commitment kind, Unicode/order/null/large-money edge, duplicate keys, surrogates, secret exclusion and legacy compatibility; prove an exact bytes32 Solidity round trip.
- [ ] Implement the approved public fund amounts, atomic correction and generic registry with operator/zero/duplicate/lineage checks. Pin actual local UID/block/code/ABI. Preserve the legacy hasher/artifacts and repair shared fallback only through the approved compatibility seam.

Acceptance: changing bytes while preserving extraction fails integrity; missing originals are unavailable; helper access to private identity evidence is denied; orphan uploads are not business success. Unauthorized/duplicate/invalid reversal submissions fail and correction pairs are atomic. Measure actual gas units; invent no monetary fee.

### T04 — Durable work/current proof/uncertain send — 36h

Depends on T03; covers AC-22–AC-25. Owns durable work, integrity, independent verification and result application; tests in `test_anchor_recovery.py` and worker integration.

- [ ] Implement ERD jobs, dependencies, signed submissions, events, observations and applications. Serialize the signer nonce; save signed bytes before broadcast and retain actual receipts.
- [ ] Apply matching observations once under the business lock with audit. The worker cannot publish or consume entitlements. Use bounded 2/4/8/16/32/60-second backoff and explicit conflict, loss and uncertainty routes; retry unchanged content.
- [ ] Implement the five current integrity results and a signer-free verifier of permitted material. Startup manages only owned hidden processes and never resets state automatically.

Acceptance: kills before/after broadcast, mining and result commit converge on the same commitment. Existing matching chain records recover their actual references; conflicts stop. Cutoff, absence, revert, deployment reset and missing evidence remain explicit. Previous matches become historical when a fresh read fails.

### T05 — Functional funds/Auditor slice and shell — 24h

Depends on T04; covers AC-01, AC-03–AC-06 and AC-22. Owns funds forms and actor shell; tests in `test_funds.py` and the browser funds journey.

- [ ] Confirm real sources, extraction/manual fields, printed signatories and duplicate checks. Retain extracted/confirmed amounts, override and words/figures comparison, warning without blocking. Implement atomic correction sets, heads, history and jobs with independently available files.
- [ ] Show signed funding authority, each proof component and labelled deferred advances/returns. Implement the documented funds exceptions and read-only Auditor slice without certifying available cash.
- [ ] Deliver editable mobile/desktop forms. Actor changes clear secrets/caches and discard delayed responses. Replace fake/offline/obsolete mutations as functional screens land.

Acceptance: required sources are enforced, duplicate refusals audited and concurrent corrections create one complete successor. Overrides retain both values; words/figures disagreement warns while unknown parsing stays absent; all six funds exceptions are inspectable. Failed anchors still count authority once; NTA alone is not a release. Signature labels remain honest. Reload restores edits; actor switching exposes no previous private response.

### T06 — Registry/member/linkage/staff/intake — 28h

Depends on T05; covers AC-07–AC-09. Owns registry/reference forms; tests in `test_registry.py`.

- [ ] Persist candidates, nominations, positions, activation/deactivation and member recusal links across multiple actors.
- [ ] Separate household/member facts from account/contact history. Implement self/assisted registration and a private recipient panel; absent optional facts stay absent.
- [ ] Record residence, dispute, field, fact and contact reviews without rewriting submissions or automatically declining claims. This is not credential recovery.
- [ ] Explicitly record operation evidence, coverage, response duration and opening/closure; funding never opens intake and no disaster creation workflow is added.

Acceptance: relinking preserves household identity; assisting officers are recused and receive no private echo. No-ID households can claim but cannot yet be paid. Residence/dispute rules govern list access. Deactivation retains history and closure preserves existing reviews.

### T07 — Claims/thread/snapshots/fallback/checks — 32h

Depends on T06; covers AC-10–AC-12. Owns claims, checks, simulated ID adapter, routing scheduler and forms; tests in `test_claim_routing.py` and `test_checks.py`.

- [ ] Freeze registry/link/submission facts and deadlines. Persist rounds, replies, reasons, relative declarations and own/assisted-household recusals.
- [ ] Require the Punong's actual resolution for signed submission. Route immediate staffing exceptions and deadline no-response/no-submission fallbacks honestly. Retain opinions; failed anchors cannot veto review; supplementary evidence cannot duplicate the primary route.
- [ ] Implement five local flags, near-matches, missing-value rules and risk ordering. Duplicate-attempt diagnostics reference an existing submission rather than inserting a second claim. Simulated ID returns `identity_verified=false`; checks never decide eligibility.
- [ ] Recover overdue routing and serialize timeout/send races. Recheck late pre-final responses. Tests may construct a persisted referral precondition; T08 adds the actual human referral/resubmission commands.

Acceptance: exercise negative, withdrawn, fewer-than-two, all-barred and responded-unsent routes. Races route once; referral deadlines continue after intake closure. All five checks, phone sharing at three versus four, absent fields and fuzzy names flag only.

### T08 — Human decisions/computation/publication/changes — 40h

Depends on T07; covers AC-06 and AC-11–AC-15. Owns entitlement, publication and human review; tests in `test_entitlements.py` and `test_publication.py`.

- [ ] Implement independent approve/decline/refer/category/bulk actions and one new-information resubmission during intake. Recheck changed data revisions and require human review of changed flags before approval. Create stable entitlement/transaction identities; absent basis/amount and deferred confirmer remain null.
- [ ] Require documentary mode/scalar mappings, exact centavo calculation and overflow checks. Show computed unhanded amounts plus locked handovers once, with awaiting count/incomplete label; excess funding comparison only warns.
- [ ] Build cumulative immutable lists. Publish only the newest current candidate after its own actual anchor. Retain stale proofs and restrict resident fields while exposing the household's own amount separately.
- [ ] Append unpaid versions, holds, notices and invalidations; preserve paid versions and informational differences. T09/T10 complete session authorization. Unrelated list additions keep unchanged codes.

Acceptance: invented ₱435/15-day input computes 495,000 centavos. Test rounding, fixed evidence, absent inputs, no ₱5,000 default and no legacy ₱10,000 ceiling. RPC failure stays pending; a stale request cannot publish. Component failures remain separate without extra publication gates. Forced recalculation failure rolls back.

### T09 — Sessions/assignments/notices — 28h

Depends on T08; covers AC-15 and AC-16. Owns sessions, notices, simulated delivery and forms; tests in `test_sessions.py` and `test_notifications.py`.

- [ ] Implement DSWD lifecycle, immutable date/site/list/member/assignment versions and one current payable session per entitlement. Follow-up assignments cannot reopen cash.
- [ ] Persist in-app and linkless simulated-SMS intent/results on scheduling and changes. Show failure/no-contact; publication sends no session notice. Include no codes or authenticated SMS replies.
- [ ] Invalidate affected unused authorizations; changed basis requires confirmed successor list and session update. Unrelated amendments preserve valid attempts, and closure preserves follow-up.

Acceptance: wrong date/assignment, inactive actors and closed sessions cannot pay. Unrelated changes preserve codes; new list entries do not automatically enroll in a session. Notices are labelled, secret-free and deduplicated.

### T10 — Recipient/assisted authorization/once-only handover — 40h

Depends on T09; covers AC-08, AC-15, AC-17–AC-19 and AC-25. Owns payout and private recipient panel; tests in `test_payouts.py` and `test_payout_concurrency.py`.

- [ ] Preserve transaction identity across attempts, secret verifiers and events. Reveal the recipient's code once. ID failure stops/holds with reason; clearance enables a distinct later session.
- [ ] Check assisted identity before private PIN setup and recipient opening. Require two eligible independent non-household staff before cash; payer cannot act as recipient.
- [ ] Atomically recheck current versions/date/list/session/code/recusal/checker/ID and save unique handover, consumption, audit and intent. Preserve original opening entry and current handover session entry separately. Accept no amount field and perform no RPC inside the transaction.
- [ ] Recover unknown acknowledgements through GET before safe replay; never automatically repeat cash, offer offline payout or pay again after receipt.

Acceptance: separate clients/different keys produce one receipt/event/intent; dropped committed acknowledgements recover. Exercise input/account/session/challenge races and preserved attempts after unrelated amendments. A same-day distinct session after clearance is allowed; stopped attempts are never reused. Field/photo-ID requirements hold; secrets do not leak and bad-check replay does not increment twice.

### T11 — Private answers/timeouts/grievances/challenges — 28h

Depends on T10; covers AC-18 and AC-20–AC-22. Owns outcomes, cases, deadlines and private forms; tests in `test_outcomes.py` and `test_cases.py`.

- [ ] Append post-handover initial/late/revised answers and neutral 72-hour outcomes. Eligible independent checking continues after closure; payer access is denied.
- [ ] Save adverse answer, unique linked case/reopening, audit and intent atomically. Preserve human resolutions; full answers do not auto-close or repay. Pre-handover reports have a stable transaction target without fake outcomes.
- [ ] Keep resident challenges/reporters private. Serialize pre-cash reversal versus post-cash evidence; allow no arbitrary reversal.
- [ ] Distinguish handover and latest full/adverse/waiting/unconfirmed totals. Payer/barangay receive no private outcome/case signals.

Acceptance: race timeout against answer; only handed-over transactions reach the 72-hour outcome. Late/revised answers after closure work. Adverse→resolve→full→adverse retains one case and reopens history without restoring payability. Missing checker before cash holds; after cash it triggers follow-up. Former payer remains barred from checking.

### T12 — Read-only Auditor/private inspections/legacy — 24h

Depends on T11; covers AC-03 and AC-22–AC-24. Owns Auditor views, private access and legacy verification; tests in `test_audit_privacy.py` and `test_legacy.py`.

- [ ] Show documented funding/workflow/outcome exceptions and per-officer figures with clear denominators; these are review flags, not fraud verdicts.
- [ ] Provide exact-version evidence timelines and current reads. Privately log specific ID/photo opens before serving; logging failure blocks disclosure. Auditor has no mutation/retry/mark/note action.
- [ ] Complete the direct JSON/file/material/replay/error/history projection matrix, excluding private outcomes/cases/inspection selectors from restricted roles.
- [ ] Offer exact read-only legacy import with pinned original protocol/deployment. Never derive pivot eligibility, fabricated observed references or latest-deployment substitution.

Acceptance: Auditor reads change only S12; Field Office cannot see selectors. Redacted material is never presented as the original hash preimage. Import is idempotent, old coverage is labelled and missing evidence is not green. Independent verification matches without a signing key.

### T13 — Full fresh evaluation/faults/restoration — 32h

Depends on T12; covers AC-01, AC-04, AC-19, AC-25 and AC-26. Owns fixtures, command-line evaluation and backup/restore; tests in `test_mvp_journeys.py`, `test_recovery.py` and browser journeys.

- [ ] Seed two disasters, multiple barangays, multiple actors per role and recused/staffless/no-ID cases. Use actual invented PDF/photos and DFC identifiers; full-journey evaluation starts from reference records only.
- [ ] Complete own-device and assisted editable journeys through real APIs, anchors and independent reads. Exception scenarios use the same services, not a presenter state engine.
- [ ] Isolate signing/nonce/database/acknowledgement/RPC/stale/timer failures. Recover overdue work after restart and label accelerated business time while retaining actual chain references.
- [ ] Restore database, exact files and manifests consistently with checksums. Seed idempotently; reset retires the namespace and preserves history. Never discard an unknown nonce or pretend a lost chain was restored.

Acceptance: every criterion passes; restart/restore retains originals, state and pointers against surviving chain state. Same-address node reset is explicit deployment loss with separate old history. Browser and human checks at 390px/1440px cover actor selection, editable forms and understandable recovery errors.

### T14 — Full verification/status docs/handoff — 16h

Depends on T13; covers AC-01–AC-26. Owns current product/system/guides/README/CONTRIBUTING/AGENTS status documentation and validation evidence.

- [ ] Run backend/PostgreSQL/contract/protocol/worker/browser/typecheck/build checks and fix in-scope failures. Remove ignored type errors as the functional UI lands.
- [ ] Check generated schema/API/TypeScript/ABI/protocol against ERD/PRD. Record actual pass/fail/unrun results without reusing historical claims.
- [ ] Reconcile implemented/simulated/Pending runtime, routes, API, chain and setup docs; preserve ideation and the real-use boundary.
- [ ] Declare completion only against PRD's measurable criteria. Commit, push and public deployment require separate authorization.

Acceptance: no unmapped or failing requirement remains; both fresh journeys and real independent proof succeed; public contents reveal no private outcome label. Operational readiness remains Pending.

## 5. Requirement traceability

PRD criterion normative; tests expand it, none claimed passed. ERD S1–S13 matrix covers persisted records. Audit/projection/intent applies every command, not final cleanup.

| PRD | Tasks | Mandatory acceptance |
|---|---|---|
| AC-01 | T05,T13,T14 | Fresh edited own-device/assisted full journey/restart. |
| AC-02 | T01,T02,T05 | No login/multiple active claimed actors/stored scope/injection denied/impersonation possible-labelled. |
| AC-03 | T02,T05,T06,T10,T11,T12 | All-role JSON/binary/material/history/error/replay/delayed actor-switch matrix. |
| AC-04 | T03,T05,T13 | Missing/mutated raw originals/real extraction/manual/version/restore. |
| AC-05 | T05 | Duplicate/words/override/correction types/concurrent complete pair/independent anchors. |
| AC-06 | T05,T08 | Exact authority/no cash deduction/deferred zero/incomplete approved subtotal/awaiting/excess warns. |
| AC-07 | T02,T06 | Nomination/position/activation/deactivation/stable identity-relink/helper recusal. |
| AC-08 | T06,T10 | Residence/dispute/review/no-ID field+photo/DSWD relink not recovery. |
| AC-09 | T06 | Explicit basis/coverage/duration/closure/release not intake/existing review. |
| AC-10 | T07 | Negative/staffless/all-barred/no-response/unsent exact signed-fallback/send-timeout once. |
| AC-11 | T07,T08 | Five checks/fuzzy/missing/phone3-4/flags only/human-bulk-recusal/ID simulation. |
| AC-12 | T07,T08 | Fresh referral after closure/late pre-final recheck/final refusal/one new-info resubmission. |
| AC-13 | T08 | Documentary modes/scalars/null/rounding/overflow/no overrides/default ceiling. |
| AC-14 | T08,T12 | Cumulative/current own-anchor publish/RPC-stale race/resident projection vs whole proof. |
| AC-15 | T08,T09,T10 | Unpaid hold-expiry-notice-list+session/unrelated preserved/paid lock-difference. |
| AC-16 | T09 | DSWD lifecycle/date/current/schedule-not-publication/simulated failure/no-contact/follow-up. |
| AC-17 | T10 | Recipient code/open-expiry-stop-clearance/same transaction/distinct later same-day session. |
| AC-18 | T10,T11 | ID/PIN/two eligible independent actors/late checker/absence before-vs-after cash. |
| AC-19 | T10,T13 | Two-client keys/committed ACK GET-replay/new repeat denied/no amount/offline. |
| AC-20 | T11 | Handed-only72h/timer-answer/late-revised/partitioned latest/no repayment. |
| AC-21 | T11 | One case/history-reopening/full-not-close/private pre-cash report/challenge-cash. |
| AC-22 | T02,T04,T05,T11,T12 | Atomic failure/every typed audit/private access before serving/no shared inspection. |
| AC-23 | T01,T03,T04,T12 | Entire actual inventory/raw coverage/signed fund links/no extra anchor/secrets/public adverse label. |
| AC-24 | T03,T04,T12 | Actual five results/historical-current/no-key independent pinned verifier. |
| AC-25 | T02,T04,T10,T13 | Signature-nonce-kill-revert-conflict-reset/restart-overdue/stale and change/challenge/cash races. |
| AC-26 | T01,T09,T13,T14 | Multiple synthetic actors/disasters/barangays/repeatable restore/labels/no operational readiness. |

## 6. Verification and future local handoff

Future instructions only. Read root scripts; Windows `python`/`npm.cmd`. Existing `python backend/test_backend.py`, `npm.cmd --prefix contracts test`. Frontend typecheck currently Unix path; implementation adds package-local `tsc --noEmit`. New files enable `python -m unittest discover -s backend/tests -v`, real protocol/worker/contract integration, API type generation, frontend strict typecheck/build/browser. PostgreSQL and actual chain required; SQLite/canned success cannot stand in.

Approved setup supported runtimes/ports/new DB/migrations/deliberate local registry registration. Startup connects pinned deployment, no automatic seed/drop/reset/deploy; services separate or owned hidden PowerShell processes, actual independent health states. Secrets never printed; synthetic inputs only. Faults isolated8001/8555/test DB/owned processes, not evaluation or other services. Reset/restore verifies resolved absolute targets inside explicitly named runtime/workspace, no computed cross-shell destructive command/module deletion. DB backup cannot recover destroyed chain.

Independent material only fully allowed originals/canonical bytes/deployment, no signer. Whole list/submission DSWD/Auditor; household own receipt/outcome; payer permitted receipt; checker answer ack only. Redaction not unchanged hash. Formal report export/Merkle resident inclusion deferred.

## 7. Estimate and risks

| Task | Hours |
|---|---:|
| T01 |10|
| T02 |32|
| T03 |28|
| T04 |36|
| T05 |24|
| T06 |28|
| T07 |32|
| T08 |40|
| T09 |28|
| T10 |40|
| T11 |28|
| T12 |24|
| T13 |32|
| T14 |16|
| **Baseline** |**398**|
| **25% integration** |**99.5**|
| **Planning budget** |**497.5**|

The prior 284h estimate becomes 398h (+114h), covering relational/versioned identity and membership, projection checks, evidence restoration, publication/code/session races and full functional completion from reference seeds. With allowance, this is approximately 12–13 engineer-weeks at 40h/week, excluding approval/tooling/integration waits. It is a planning estimate, not a delivery guarantee.

Critical path decisions/model/context→files/protocol/registry→recoverable real anchors→funds→registry/intake/claims→amount/publication→sessions→recipient/cash→outcomes/cases→Auditor→fault/restore/full checks. UI paired with functional API stage. Risks backend/shared fail-open drift, signed transaction/DB/ACK uncertainty/lost deployment, stale/fact/session races, file-DB orphan/missing evidence, many views with impersonable actors, unverified institutional originals/inputs, metadata correlation/missing tooling. Constraints/locking/pinning/tests address evaluation; auth/privacy/funding/SMS/retention/governance remain Pending.

## 8. Consolidated execution approvals and real-use gate

Documents reviewable now; no approval question blocks documentation. **Before later implementation**, obtain applicable repository decisions together once. Full scope/no-login/claimed actors/real core/synthetic evaluation already instructed; do not ask again.

| Approval | Concrete proposed scope/repository reason |
|---|---|
| A1 backend | Confirm FastAPI main sole runtime, preserve/freeze legacy/read import, shared fallback named repair. AGENTS target before editing either. If server.py chosen, revise owners/dependencies first. |
| A2 schema | Approve ERD typed/deferred/uniqueness/secret/audit/work/grants/new local PostgreSQL migrations, no original SQLite/institutional mutation. Ask-first schema. |
| A3 dependencies | Listed packages/tooling/exact supported locks/security refresh at execution, no provider/cloud/auth/Merkle/broker implied. Ask-first dependency. |
| A4 compatibility/contract | Concrete ADR canonical format/vectors/namespace/corrections/public metadata/separate ABI-storage-functions, original receipt/contract unchanged and both tested. Compatibility decision record required. |
| Local scope | Later implementation authorizes deliberate approved local registry setup/generation. AGENTS separate approval applies non-local deployment; public network excluded. |

Before real household data: authenticated identity/sign-in/secure sessions/authenticated authorization/recovery; institutional lawful processing/resident disclosure/exact FACED/signature/retention policy; tested storage/backup RPO-RTO/incident response; actual feasible notice SMS/cost; independent staff/ID/cash/site/activation; network/RPC/key custody/public metadata assessment. No institution/provider/host approval invented. Different assistance unit/signatory/financial workflow requires PRD/ERD/plan revision.

Planning self-review **not product validation**: each AC criterion/task/test and persisted ERD mapping, FK/scope/type/state interfaces, absent-input/history/projection, correction pair/once-only consumption/private inspection/randomized common outcomes, uncertain send/stale candidate/timer/challenge races reviewed. Actual tests/completion future. No permission to commit/push/delete modules/change legacy receipt/deploy publicly.
