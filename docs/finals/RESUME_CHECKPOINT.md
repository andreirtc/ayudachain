> Historical pause checkpoint, superseded by the resumed candidate and [Draft PR40](https://github.com/andreirtc/ayudachain/pull/40). For current status read [FINALIST_READINESS](FINALIST_READINESS.md). Do not use the old lab/port instructions below.

# Resume checkpoint — 14 October 2026, 10:11 Asia/Manila

Paused at the maintainer's request to join the team. Work is NOT fully complete. Preserve current uncommitted design-proposal work; no commit/push/merge/public deployment was authorized or performed. Do not reset labs or nodes.

## Latest design feedback — highest priority on resume

The maintainer dislikes the new card-heavy UI and some placements. They want a familiar government work interface: clearer headings, compact tables, standard forms and deliberate placement, fewer decorative dashboard cards. They accepted natural conversational Taglish, rejected formal/literal Filipino and “Ayuda ko”; use “Status ng ayuda” and “Tingnan ang status”. Preserve all five visible roles, assisted/manual access and integrity safeguards. Review the actual current screens before another broad design pass. No government-usability validation is claimed.

## Current implementation

Compact rail/four phone shortcuts/full menu; searchable one-household staff detail; grouped payout desk; optional calculation/audit detail; new five-role welcome; English/Taglish switch; natural Demo seed profile gated MVP_PRESENTATION_DATA=1 for NEW runs only. No schema, contract, hash or financial rule changes.

This turn simplified more interface copy, moved LanguageProvider INSIDE the Workspace Suspense boundary to fix a reproduced hydration/focus failure, and added page-error regressions. Test selectors now target the direct disclosure summary and main-content household control, avoiding legitimate nested-summary/navigation-label ambiguity.

## Current tests — do not inflate results

Original pre-redesign accepted validation: backend111 passed/1Windows skip; contracts23; legacy8; browser55 plus separate fresh journey1; TypeScript/build passed. These are HISTORICAL and do not establish final new UI acceptance.

New plain-Taglish intermediate run:58 passed,4failed in5.0min. Failures: nested summary selector, Pamilya matching nav and select, real hydration/focus issue, and cancelled integrity request during live copy HMR. Retained log: .runtime/finals/plain-taglish-final-browser.log. Fixes applied; source editing stopped before final sequential rerun.

Latest rerun log: .runtime/finals/plain-taglish-accepted-browser.log. At pause, first60 tests had passed; final suite completion was NOT observed. Last tool process session79184 was unavailable on polling. Inspect log/processes before any claim or rerun. Separate earlier wrong-grep run was deliberately interrupted; no journey reset occurred.

Latest final source still needs independent typecheck and production build with owned app STOPPED. Earlier plain-copy typecheck passed before the final copy/provider changes. No final fresh Demo-profile journey/capture/video has been completed.

## Runtime/labs — inspect ownership before acting

Original in-memory8545 chain disappeared; reason unknown. Do not recreate it or claim old proofs current. Incident in LOCAL_CHAIN_INCIDENT.md. New independent loopback chain8546 (original new PID235554) and fault8555/PG55432 should be checked, not assumed alive. Keep all old manifests/history.

During tests the running app was using .runtime/finals/labs/3cb6fc3db148/lab.env (mutation-heavy test lab), supervisor log .runtime/finals/plain-copy-tests-supervisor.log, tool session27207. The selected-lab-path.txt STILL points at .runtime/finals/labs/78a822397963/lab.env, the separate final-presentation lab with natural Demo references and NO full journey yet. This mismatch is recorded here; establish actual process ownership/config before stopping/restarting. Final-presentation-lab-path.txt retains the latter path. Do not test mutation-heavy suites against the intended final presentation lab. Do not print config/keys.

## Documentation

All seven English finals docs and110-question masterbook already exist, plus beginner guide, branch comparison, evidence and offline reader. This turn added role/daily-wage/real-process/adoption explanations and official sources to TEAM_CRASH_COURSE and Q&A; added an honest existing-government-software comparison.

New natural Taglish companions exist in taglish/: START_HERE, PROJECT_EXPLAINED, DEMO_RUNBOOK, GITHUB_TRIAGE, FINALIST_READINESS. They are explanatory companions, linked to detailed originals. Taglish PITCH_SCRIPT, PITCH_SLIDE_CORRECTIONS and JUDGES_QA are NOT YET WRITTEN; links to them are pending, not evidence of completion. Finish all seven companions, including meaningful110-question natural-language reviewer and the requested journey/finance/adversarial/study sections. Original English masterbook remains complete.

The top of START_HERE and FINALIST_READINESS points here because earlier “final checks complete” sections predate the new UI. Current package ZIP and VENUE_READER are STALE, predating redesign/localization and natural Demo records. Do not call them the latest UI packet.

## Exact remaining sequence

1. Inspect actual processes/chain, final browser log and current screens; incorporate government-format/placement feedback.
2. Test any new behavior; complete stable remaining62-case browser suite on test lab. No live source edits during validation.
3. Stop owned app; typecheck/build; restart intended new final lab on surviving8546.
4. Fresh Demo-profile actual journey, genuine recording and pre-code payout captures. Never reset partial runs.
5. Run updated capture_evidence.cjs: English36 plus Taglish12 views; strict actual chain match required. Visually inspect.
6. Run private .runtime/finals/verify_final.py with selected correct config. It now reads configured RPC and retains old verification as independent-verification-pre-redesign.json using exclusive creation. Never overwrite retained evidence. Earlier block172 is historical.
7. Encode/decode new workflow-redesign-original/short files, update VIDEO and sanitized test ledger; preserve older recordings.
8. Refresh operating-state/readiness/runbook/branch comparison and finish natural reading pack. Update package_handoff.py latest capture/video, include TEAM_CRASH_COURSE and Taglish reading sections. Rebuild offline reader/ZIP; link, viewport, decode and secret-exclusion checks.
9. Review diff/check safety/main unchanged. No commit or external writes unless requested.

No final ETA is running while paused. Re-estimate after team feedback on resume. Current proof/UI/software readiness is not equivalent to production readiness; authentication remains absent and actors impersonable.
