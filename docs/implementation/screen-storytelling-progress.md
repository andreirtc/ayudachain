# Screen storytelling execution ledger

Authorization: maintainer approved all five phases on 2026-10-14, on `feat/five-role-mvp`, uncommitted. Preserve the imported Tonal baseline and role error guidance. [Approved plan](2026-10-13-screen-storytelling-plan.md).

## Durable requirement checklist

| Phase / requirement | Implementation | Evidence / status |
|---|---|---|
| 1: scoped state, owner, safe action, exact destination; conservative conflicts | Implemented `Storytelling.ts` | 26 state regressions passed; [mapping](storytelling-status-map.md) |
| 1: current/historical/checking/failed integrity meanings | Implemented shared pure mapping | Pure regressions passed; runtime chain integrity 1 passed |
| 2: Filipino default, saved English, four destinations; rail/drawer/bottom bar | Implemented shell | 2 shell regressions passed; broader matrix Pending |
| 2: one truthful dashboard next action, amount/appointment/history | Implemented shared mapping integration | Actual journey gate in progress |
| 3: registration/claim review and preserved input | Implemented review flows | 7 beneficiary fixture regressions passed |
| 3: amount/list/appointment/authorization/concern record context and Back | Implemented direct context | Back and wrong-disaster regressions passed |
| 3: recipient radio controls, code hiding/expiry/PIN distinction | Implemented native radios / in-memory code | 2 payout regressions passed (keyboard, code, interrupted opening) |
| 3: specific persistent results, snackbars, accessible dialogs | Implemented `Review.tsx` | Escape/cancel focus, saved-result persistence passed |
| Beneficiary gate before staff patterns | Passed before staff extension | Actual form-driven journey passed ([runtime](storytelling-runtime.md)); rerun after later fixes passed in 2.3 minutes |
| 4: task dashboards, deliberate staff destinations, list/detail | Implemented | 2 staff-shell cases, 42-case layout matrix, existing workspace suites |
| 4: staff decisions/confirmations/flags/permitted creation | Implemented | 6 staff cases (segmented decisions, review/cancel, case action, publication, flags, Barangay response) |
| 4: Disbursing tablet and independent checking | Implemented | 2 handover cases; actual journey covers independent checker |
| 4: Auditor rows/chips/scope/historical distinction | Implemented | 10 integrity cases; existing verification suite 5 passed |
| 5: typecheck/build/affected suites and full changed journey | Done with limits | Typecheck exit 0; isolated production build exit 0; see chronology for the interrupted full run |
| 5: languages/themes/viewports/breakpoints/focus/overflow | Automated matrix passed; contrast and manual review Pending | 42 cases: 5 roles x 390/1440px x light/dark x English/Filipino, plus 759/760/1023/1024px transitions. Dialog focus/Escape and segmented keys covered by flow/staff cases. Contrast not measured |
| 5: README/DESIGN/sitemap/flow/ledger/plan/validation alignment | Updated 2026-10-14 | This ledger, plan, README, DESIGN, sitemap, user flow and [validation](validation.md) |
| Human: native Filipino review | Pending | Requires a native speaker; no result claimed |
| Human: 4/5 participants understand status and next step within 10s | Pending | Requires participants; no result claimed |
| Human: physical phones/tablets/camera/touch/cash-site checks | Pending | Requires physical devices and humans |

## Assumptions and constraints

- Presentations use existing scoped reads and backend guards. No API, schema, dependency, contract or hashing extensions.
- Known missing or conflicting data blocks affirmative action guidance; unknown money stays unknown.
- Runtime recovered with guarded fresh namespace and new local manifests, retaining old records and pins. [Procedure and actual evidence](storytelling-runtime.md).
- Browser fixtures test presentation only and never establish real verification.
- In-memory input is preserved during review/cancellation/error; cross-route durable drafts are not promised. Actor/disaster changes reset private state.

## Staff destination decision (before shell implementation)

Phone destinations are selected from the role's tasks, at most four; the full secondary drawer remains reachable.

| Role | Phone destinations | Reason |
|---|---|---|
| Barangay | Overview, Claim responses, Households, Approved list | Respond first from a claims table; Households is a read-only census with assisted registration below; the approved list shows no amounts. Formal submission is inside claims and Punong-only. |
| DSWD | Overview, Claim review, Payout sessions, Private cases | Human decisions, scheduling and private recovery; funding, intake, amount/publication and evidence remain secondary links and dashboard prerequisites. |
| Disbursing | My work today, Cash handover, Assigned sessions, Exit checks & notes | Current session/recipient task; independent checker task is visibly separate. |
| Auditor | Overview, Integrity & histories, Funding evidence, Search & task queues | Read-only exception/proof inspection; all other permitted record pages stay in the drawer. No create action. |

## Evidence chronology

- Shell RED: missing Filipino heading and intermediate drawer control. Initial run also encountered parallel Playwright artifact collisions; subsequent runs use unique output directories.
- Payout RED: missing native radio and retry still enabled after uncertain write. Initial green exposed CSS-generated checkmark in accessible name; explicit radio label corrected it, then both tests passed.
- Actual beneficiary journey is being diagnosed before staff extensions. First run failed at a required catalogue load, leaving the workspace Loading; this is not a passing journey.
- Defects found and fixed during the Phase 5 gate, each with a regression test that failed first: (1) a saved English choice caused a hydration mismatch because it was applied before the Suspense boundary hydrated (`SavedLanguage`; test in `storytelling-shell.spec.ts`, failed with the old effect); (2) choosing the already auto-selected payout transaction cleared its detail without reloading it, which hid the authorization form and intermittently failed the journey (`storytelling-payout.spec.ts`). Also fixed two nullable `session` TypeScript errors in `Payouts.tsx`.
- Four older tests (`usability-csv` twice, `usability-guidance-scan`, `usability-queues`) asserted raw API codes in visible alerts. The committed workflow-error recovery deliberately replaced them with guidance, so the assertions now check the guidance and that the raw code is not shown. `WorkflowError` still retains the code for diagnostics (existing test passes).
- Second full-suite run was interrupted by the end of the previous session after 114 of 117 tests: 113 passed, 1 failed (the stale CSV assertion, since fixed and rerun: 2 passed). The three unreached tests were rerun separately: both handover cases passed and the real journey passed on the same application code. There is no single uninterrupted all-green run.
- **Open runtime blocker:** the interruption also stopped PostgreSQL and both local chains. After restoring PostgreSQL and a fresh chain on 8545, the guarded `reset_mvp` correctly refused: one anchor job is in `submitted` state (created 2026-10-14 05:12 +08) and the earlier deployment is lost. It was not edited or bypassed. Resolving it needs a maintainer decision on reconciling that retained signature; until then chain-backed browser runs and the supervisor are unavailable. The API and frontend were started separately without a worker for the fixture and layout checks.

