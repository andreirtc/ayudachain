# Fresh finals test evidence

14 October 2026, Asia/Manila. Source baseline `4377db1`; finals changes are local/uncommitted. Environment: Debian 13, Python 3.13.5, Node 24.18.0, extracted PostgreSQL 17.11, repository npm/Python locks and Playwright Chromium. This is a new Linux validation, separate from earlier Windows results.

## Completed checks and retained failures

| Check | Actual result | Evidence |
|---|---|---|
| Contract + canonical protocol | 23 passed on ephemeral Hardhat | [contracts](contracts-baseline.txt) |
| Backend full suite | 111 tests: 108 passed, 2 errors, 1 Windows-only skip; **failed run**, 581.534s | [full log](backend-full.txt) |
| Backup/restore recheck | Both errored cases passed separately in 36.214s after fixing library PATH; not a green full-run claim | [recheck](recovery-recheck.txt) |
| POSIX port safety | Restart in TIME_WAIT failed before fix; then POSIX test passed, Windows test skipped | [before](port-red.txt), [after](port-green.txt) |
| Retained legacy backend | 8 passed | [legacy](legacy-final.txt) |
| Initial six workspace cases | 6 passed, all five roles and 28 sections at 390/1440px | [baseline](browser-baseline.txt) |
| Error recovery integration | Five selected cases failed before; all 15 guidance regressions passed after | [before](errors-red.txt), [after](errors-green.txt) |
| Cash handover review | Failed before missing dialog; cancel/Escape/focus/confirm passed after | [before](handover-red.txt), [after](ux-green.txt) |
| Current transaction reselection | Detail disappeared before; explicit same-reference reload passes | [before](transaction-reselect-red.txt), [after](transaction-reselect-green.txt) |
| Initial registry read | Premature form/false-empty state reproduced; 17 combined UX/error cases passed with initial gate | [before](registry-loading-red.txt), [after](ux-errors-final.txt) |
| Verification boundary | Real matching chain read rendered concatenated status/time before fix; all five current refresh/switch cases passed later | [before](verification-red.txt), [focused recheck](focused-recheck.txt) |
| Broader browser intermediate | 44 passed, 9 failed; copy/locale expectations, text boundary and missing active-session fixture investigated | [failed run](browser-rest.txt) |
| Focused browser recheck | 11 passed, including CSV retry preservation, queues, new UX and all integrity refresh cases | [recheck](focused-recheck.txt) |
| Late amount history | Editing caused disclosure to close before fix; current regression passes | [before](amount-collapse-red.txt), [after](amount-collapse-green.txt) |

The complete journey has several retained partial failures: duplicate registration text, lost transaction detail, delayed registry read, unmounted evaluation clock and late amount-history collapse. [First failure](journey-red.txt), [receipt failure](journey-green-2.txt), [registry failure](journey-final.txt), [clock failure](journey-selected.txt), [amount failure](journey-complete.txt). No partial run was reset or counted as passed. Final full-journey/build/browser results are recorded below.

## Gas provenance

The fresh contract test printed **555,889 gas units for a funding correction pair**; see the contract log. Fresh `deploy_evidence.js` printed **781,144 gas units for the local evidence-registry deployment**. These are local transaction-specific measurements, not a public fee, network average, per-household cost or purchased gas. No live token price is asserted. The hypothetical model in [Q&A](../JUDGES_QA.md#hypothetical-financial-model) keeps fee-price assumptions separate.

## What the evidence does not establish

Controlled error/dialog/QR fixtures are UI tests and do not supply successful blockchain observations. Real current-match tests query the actual pinned local deployment. Viewport emulation is not a physical-phone/camera test. No production load test, authenticated-security audit, native-speaker/comprehension study, government approval or real cash verification occurred. Fresh build/typecheck outputs and final visual provenance are recorded separately when complete.

## Final runs and recorded artifacts

- [Final full backend](backend-final.txt): **112 completed, 111 passes and one Windows-only skip**, 480.620s. Corrected PostgreSQL runtime library path. This is a new full run, distinct from the earlier error run and focused recovery checks.
- [Complete genuine browser journey](journey-recording.txt): **1 passed in 2.3 minutes**, actual own-device and assisted paths. Original video 135.04s; supported retiming/VP9 encoding produced a 45.166s derivative. Chromium decoded it at 1280×720 with readyState4.
- [Session disclosure before](session-collapse-red.txt) and [after](session-collapse-green.txt): late data no longer collapses a form being edited.
- [Touch-target failure](touch-target-red.txt): mobile dialog control was40px before the44px correction; later browser tests include the44px assertion.
- [Clean receipt-guidance red regression](receipt-next-action-red-clean.txt): paid recipients still saw code/PIN instructions before the completion/follow-up change.
- [53-pass run with artifact collision](browser-final.txt): one trace ENOENT from concurrently reusing a Playwright output directory. Not a passing run; subsequent runs are sequential with unique outputs.
- [54-pass follow-up run](browser-delivery.txt): one now-obsolete Filipino authorization-heading expectation after paid-receipt guidance changed. The language regression now checks registration→claim guidance persistence rather than requiring obsolete payout instructions; language checks remain substantive.

[Actual screenshot provenance](../SCREENSHOTS.md), [genuine workflow video](../VIDEO.md) and [signer-free exact-material match](independent-verification.json) are separate evidence. The latest final browser/build output will be appended when complete.

The next sequential55-case run repeated54 passes and exposed a strict selector in the updated language test (English “Submit a claim” also labels its form). The selector is now scoped to the language-tagged guidance aside. No language assertion or application behavior was removed; final repeat remains pending at this entry.

## Accepted final candidate (2026-10-14T08:19+08:00)

- [Final sequential browser run](browser-accepted.txt): **55 passed in3.2 minutes**. Separate from the full journey; all remaining files, including final receipt guidance, phone controls, CSV, sessions, role scopes and current integrity refresh cases. No concurrent output writers.
- [Final rehearsal](rehearsal-final.txt): **1 passed in1.8 minutes** on a NEW separately named lab. Actual original-backed own-device and assisted handovers, private outcomes and audit. Earlier partial/failed lab histories retained.
- [Independent TypeScript](typecheck-final.txt) and [production build](build-final.txt): exit0 after final source edits, build completed10 pages. ESLint explicitly skipped by existing configuration. Build ran while the owned application was stopped; chain/PostgreSQL survived.
- [Latest screenshots](../SCREENSHOTS.md):32 actual captures,0 page errors/overflow, four current actual handover matches at block 172. Representative desktop, phone receipt and dark integrity images visually reviewed.
- [Signer-free independent verifier](independent-verification.json): actual match at block 172 from authorized saved canonical material and exact originals. No wallet/key supplied. Initial block 108 result retained in [initial result](independent-verification-initial.json).
- [Latest video](../VIDEO.md): genuine passing final rehearsal; original retained alongside a3×derivative. Recorded content is synthetic local evaluation.

No contract/hash/schema/financial-rule change, public deployment, database reset, push, merge or commit occurred. Final services remain loopback-only.

- Offline venue reader: 110 question headings rendered; no page errors/document overflow at 390/1440; final video decoded at 1280×720, 35.416s. ZIP integrity passed and no configuration/database/private-original files were included. All 19 final rehearsal anchor jobs confirmed; runtime health remains explicit about chain/storage not_checked and pending authentication.


## Resumed current reference candidate

62remaining browser cases passed3.7min; separate own-device/assisted clean Demo-profile journey1pass1.6min. Final production build/typecheck passed after the welcome illustration. Current48captures have0page errors/overflow;6fresh local matches are recorded with provenance. Independent signer-free proof matched at block71 on NEW chain8547. Older node histories are unavailable, not silently recreated.

Final5case language follow-up initially had4passes/1failure: the test chose the first alphabetical demo actor (unused Ana), after the journey correctly linked Maria to Maria. Test now explicitly chooses Maria where the presentation profile exists, retaining ordinary fixture fallback; rerun is recorded separately. A startup journey failed ECONNREFUSED before any API/business write; ready-state rerun passed. Pre-pause60pass log has no completion evidence and is not called62passed.

[Final language/navigation rerun](language-review-accepted.txt) passed all5cases after selecting the actually populated Maria demo account. [Current clean journey](journey-review-ready.txt), [final typecheck](typecheck-review.txt), [final production build](build-review.txt), [current48captures](../SCREENSHOTS.md), and signer-free block71match are independent evidence.
