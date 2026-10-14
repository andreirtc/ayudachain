# Storytelling status and safe actions

Date: 2026-10-14. Phase 1 implementation of the [approved storytelling plan](2026-10-13-screen-storytelling-plan.md). The mapping is implemented in `frontend/components/mvp/Storytelling.ts`; consuming screens and full journey validation are recorded separately in the plan and validation report. Translations remain drafts pending native-speaker review.

`beneficiaryStory` describes current scoped saved projections. It never sends commands, awards assistance, creates codes, clears holds, counts cash or establishes chain verification. The existing backend services remain the authority. `storyHref` retains account/disaster/filter context and adds only an opaque record selector.

| Saved state / condition | Message and next responsible role | Safe action / exact destination |
|---|---|---|
| No household, successful reads | Register the household; registration is separate from applying. Beneficiary acts. | Registry registration |
| Registered, no claim, known open intake and included barangay | Describe damage and apply for human review. Beneficiary acts. | Claims submission for the actor's household |
| Closed, uncovered, absent or ambiguous intake | Explain only the known issue; unknown intake/coverage stays unconfirmed. DSWD acts. | Outcomes/help |
| `waiting_barangay` | Saved claim awaits Barangay response; DSWD decides afterward. | Claims `record=<claim>` |
| `awaiting_dswd` | DSWD is reviewing the saved application; do not submit again. | Claims `record=<claim>` |
| `referred` | Barangay response requested. | Claims `record=<claim>` |
| `declined` | Reason comes from `current_decision_id`, never array position. DSWD explains, or the Beneficiary may supply new information when the known once-only allowance is unused and intake is open/covered. | Claims `record=<claim>`; View decision when resubmission availability is unknown or exhausted |
| Approved, missing entitlement or null amount / `awaiting_amount` | DSWD completes documented amount calculation. Unknown amount remains absent, never zero. | Lists/own amount `record=<entitlement>` where known |
| `awaiting_publication` | DSWD publishes the current list with its confirmed anchor. A queued request is not a published list. | Lists/own amount `record=<entitlement>` |
| Known amount, no live appointment | DSWD schedules the current appointment. Closed/cancelled sessions remain history. | Sessions |
| Current scheduled appointment | Show date/site and accepted-photo-ID preparation. Wait for DSWD to open it; no authorization yet. | Sessions `record=<session>` |
| Exact current entitlement version, one matching open session on current Manila date, full transaction, matching amount/status | Open the guarded authorization task at the site; the server checks all requirements again. Beneficiary acts. | Payouts `record=<transaction>` |
| Existing `open`/`presented` authorization | Disbursing Officer acts next. Keep the code private; count cash before sharing it. A refresh cannot retrieve a lost code. | Payouts `record=<transaction>` |
| Saved ordinary unused `expired` attempt and still-current open session | Review a fresh authorization; all existing server checks apply. No cash is implied by expiry. Beneficiary acts. | Payouts `record=<transaction>` |
| Hold or cancellation from either entitlement or transaction | DSWD reviews recorded reasons/decision and session/amount versions. Do not generate a code. | Lists `record=<entitlement>` or Claims `record=<claim>` for reversal |
| Saved `stopped` identity comparison | DSWD reviews the stop. Clearance plus a distinct session created later are required; expiry is different. | Payouts `record=<transaction>` |
| Past open/scheduled date | DSWD reviews the appointment; it is not current cash authorization. | Sessions `record=<session>` |
| Session entry references an older entitlement version | DSWD updates the session; do not authorize against stale amounts. | Sessions `record=<session>` |
| Receipt, entitlement/transaction `handed_over`, or handed-over attempt | Any handover signal blocks another payout even if another projection says payable or held. Recipient answers privately. Chain state cannot restore payment. | Outcomes `record=<transaction>` |
| Answer after handover | Display the actual answer and separate case status. A full answer does not close a case or restore payability. | Outcomes `record=<transaction>` |
| Lost write response | Read saved transaction before any retry; never repeat physical cash. | Refresh current Payouts `record=<transaction>` or refresh records when identity is unknown |
| Failed required read, ambiguous household/claim/entitlement/transaction, inconsistent joins or amount/status, multiple live assignments, unknown state, incomplete transaction detail | Explicitly unavailable. Refresh; do not infer a completed step or readiness. | Refresh records |

The selection uses household/disaster identity and entitlement-version/session-entry joins rather than array position. Live sessions are considered separately from history. Amount, handover, answer, case and proof remain separate facts. Known holds/handovers are conservative even when other reads disagree. No payout permission is derived from a progress index.

## Existing projections and precise gaps

- GET `/intake` already exposes disaster, status and `barangay_ids`; no API extension is needed to establish known opening/coverage. Read failure is unavailable, not closed. Missing/multiple operation data cannot establish submission availability.
- GET `/claims` and `/claims/<id>` already expose `resubmissions` and `current_decision_id`. The frontend Claim type must retain these when displaying resubmission/reason availability. A missing field never grants another submission.
- GET `/entitlements` already exposes household, `current_version_id` and `transaction_id`. Session entries include entitlement version and transaction identity. Retain these for exact links/version checks.
- GET `/transactions` is a summary. It cannot establish absent receipt, current attempt, expiry or stopped identity state. Read the exact `/transactions/<id>` before presenting current authorization. Missing `current_attempt`/`receipt` keys in a summary are unknown, not null.
- The transaction projection does not expose stopped-attempt clearance or the creation ordering of a replacement session. A still-stopped attempt therefore retains conservative recovery guidance even when DSWD has cleared it. The guarded detail task can attempt permitted recovery and the backend establishes its availability; the dashboard cannot promise it.
- The projections do not provide one authoritative server-computed `may_authorize` result covering current input/list/membership, available original identity bytes, staff recusal, registered-phone path, independent checker or PIN-lock policy. The mapping offers navigation into the task, with explicit rechecking language, rather than payment assurance. Actual code creation/handover continue to use the existing server guards.
- The existing context projection does not expose current business time, but GET `/evaluation/status` already provides `business_utc` and `clock_mode` to all actors. The dashboard reads that existing projection, converts its business time to the Manila date supplied as `today`, and retains the simulated-clock disclosure. No API change is needed. The pure mapping also accepts `today` for deterministic tests; absent a supplied date, it uses the browser's Manila date conservatively. Code expiry follows the saved backend attempt state, not a browser countdown or invented expiry event.
- Uncertain write state must be supplied by the consuming view's recovery state, or a confirmed receipt must be read. A fresh empty projection is not proof that a lost handover never occurred.

These are presentation limits within the existing API/schema scope. None requires changing a contract, schema, hash payload or security claim to deliver conservative guidance.

## Current integrity and history

`currentIntegrity` maps only a current check response. `match` means an actual matching read supplied by the integrity request hook; controlled presentation fixtures do not create that fact. Stored submission/anchor history and earlier successful checks are not current checks. Pending/checking/failed refresh always clear the current match while retaining a separately labelled earlier timestamp.

| Current state | Visible meaning / filter |
|---|---|
| `not_checked` | Not checked; no current read. Not checked chip. |
| `checking` | Reading current chain; not verified yet. Explicit row in All/checking state, not Verified. |
| `match` | Committed content matches the chain record. Verified chip only for this current result. |
| `mismatch` | Committed content does not match. Does not match chip; no fraud verdict. |
| `required_anchor_absent` | Required anchor not found after a successful read. Anchor absent chip. |
| `chain_unreachable` | Chain could not be read; not verified. Chain unreachable chip. |
| `evidence_unavailable` | Required evidence unavailable; not verified. Evidence unavailable chip. |
| `refresh_failed` | Current request failed; not verified. Explicit failed-refresh row in All; never collapsed into absent anchor or Verified. |

Filters describe only records loaded/checked in this view, not global totals. All includes checking/failed-refresh. Those states remain explicit even though the agreed chips do not include separate checking/refresh-failed choices. Unknown result vocabulary fails closed as evidence unavailable. Current check time is separate from the status word; earlier match time belongs in a labelled historical observation.

## Requirement and evidence checklist

- [x] Section 2 states have shared message, responsible role, safe action and destination.
- [x] Unknown amounts, ambiguous intake, stopped/expired distinction, stale/historical sessions, inconsistent versions, held state and recorded handover have conservative regressions.
- [x] Lost acknowledgement directs saved-record read; no repeated cash or business command is issued by the mapping.
- [x] Answer/case facts remain separate; a full answer never automatically closes the case.
- [x] Current/historical/unchecked/checking/unreachable/absent/mismatch/evidence-unavailable/failed-refresh semantics and scoped filters are defined and tested.
- [x] Actual backend guards/projections inspected; no API/schema/hash/contract/dependency change.
- [x] Regression RED reproduced: Playwright failed to load missing `Storytelling` before implementation (exit 1).
- [x] GREEN: 26 pure Playwright regression tests passed on Node 22.23.3 (1.0s). Command: `.runtime/tools/node-v22.23.3-win-x64/node.exe frontend/node_modules/@playwright/test/cli.js test storytelling-state.spec.ts --config frontend/playwright.config.ts --output=.runtime/storytelling-state-results`.
- [x] Frontend TypeScript check passed (exit 0) after the initial mapping implementation. Full delivery checks are recorded in the shared validation report after integration.
- [ ] Native Filipino copy review and intended-participant comprehension checks: Pending human validation.
- [ ] Physical-device checks: Pending human validation.

This file establishes mapping evidence. It does not claim a completed browser journey, real chain check, authentication or real-household readiness.

## Phase 4 proof presentation and evidence

Implemented after the parent agent validated the original-backed own-device and no-phone-assisted beneficiary journey. `Audit.tsx` now offers the seven agreed current-result chips, an explicit loaded/checked-view scope, a URL-backed `proof_filter`, record-type/reference search, and a selected proof detail pane. `record`, `history=commitment_id` and `material=1` carry the exact proof into the pane. Browser Back restores the preceding selection/filter without issuing a chain check or business command. The selected pane and list share the same current checks so one read cannot leave contradictory current results. Covered-version summary and exact-material reads use the existing scoped, logged endpoints; originals retain their existing logged content access.

`IntegrityStatus.tsx` uses the Phase 1 current-state mapping, shows an explicit explanation for every state, keeps earlier matching observations separate, and inserts an actual text space before Checked/Sinuri. Recorded coverage and raw check details remain accessible in expandable sections. Current check explanations and essential check/history labels respect the existing language preference. The Auditor remains read-only and has no create action.

The existing `/audit/proofs` response provides a run-wide exact commitment catalogue and saved submission observations, not server-wide current-verification totals. Current-result chips filter only reads loaded/checked in this view. The displayed record count has the same local scope. Checking and failed-refresh remain visible under All and cannot appear under Verified. Historical confirmed submission state never puts an unchecked proof in Verified.

Actual validation on Node 22.23.3:

| Check | Result and limit |
|---|---|
| Chip regression before implementation | RED: the `Current integrity results` group/All button was absent; first test failed and eight did not run under the deliberate fail-fast baseline. |
| Word-boundary regression before implementation | RED reproduced exactly: `VerifiedChecked Oct 14, 2026, 11:00 AM Manila`; the expected `Verified\s+Checked` failed. |
| Mounted actor reset before implementation | Existing safeguard passed (one test, 2.5s); preserved, not claimed as a newly fixed defect. |
| New presentation browser suite | **10 passed (25.0s)**: all result chips/scope, word boundary, failed-refresh invalidation and earlier match, mismatch/absence/unreachable/unavailable distinctions, exact-material selection/filter/Back, mounted actor reset, keyboard chip operation and checking state. Controlled synthetic responses test presentation only, never actual verification. Output: ignored `.runtime/storytelling-integrity-results`. |
| Existing verification browser suite | **5 passed (22.6s)**: actual current matching chain reads on Funds, Amounts/lists, Authorization/handover and Evidence/review, followed by controlled request failure that clears the current match; delayed real-chain response cannot populate a new actor view. Output: ignored `.runtime/storytelling-current-proof-results`. |
| TypeScript | Final frontend `tsc --noEmit --incremental false --project frontend/tsconfig.json` exited 0. |

The first full new presentation run passed three cases, then encountered a navigation timeout while a port-3000 listener was unavailable during development updates. Its verified test process was stopped; the stable rerun above passed all ten. This was not recorded as a clean initial run or attributed to a product defect. Existing verification-suite assertions now inspect current `.ac-integrity-result` rows rather than the whole page: the required Verified chip label is not itself a positive proof result. The real-chain response assertions and fail-closed checks remain intact.

Build, cross-screen viewport/theme checks and broader integrated results belong to the shared delivery validation report. Native-speaker review, participant comprehension and physical devices remain Pending human validation.
