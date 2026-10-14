# Storytelling runtime and validation evidence

Date: 2026-10-14. This records runtime recovery and fresh checks for the authorized [screen storytelling plan](2026-10-13-screen-storytelling-plan.md). It does not establish completion of the presentation phases.

## Inspected baseline

The working tree was inspected before runtime changes. It contained the imported Tonal additions and documentation edits on `feat/five-role-mvp`; none was reverted or committed. The owned Node 22.23.3 frontend on port 3000, separately launched API on port 8000 and retained PostgreSQL cluster on port 55432 were running. Both volatile local Hardhat nodes, on 8545 and 8555, were absent.

The initial current-source TypeScript check passed using the owned supported Node executable:

```powershell
& .runtime/tools/node-v22.23.3-win-x64/node.exe frontend/node_modules/typescript/bin/tsc --noEmit --incremental false --project frontend/tsconfig.json
```

A selected browser baseline began before the runtime restart and was deliberately interrupted when implementation edits began. Eight tests had passed: former-actor delayed-response isolation, both Tonal tests, both beneficiary claim-error language tests and the three staff workflow-guidance cases. This is an interrupted partial run, **not a passing complete baseline**. Output is in ignored `.runtime/storytelling-baseline-browser.log`. Subsequent browser runs must use unique output directories to avoid concurrent Playwright artifact collisions.

## Explicit local-chain recovery

Read [local operation](../guides/local-mvp.md), the full plan, repository instructions and existing validation before recovery. Started new separately owned hidden Hardhat process trees using the locked executable and installed dependencies on loopback 8545 and 8555. They remain separate from the application supervisor so stopping/restarting the application does not erase the volatile chain.

After node readiness, `contracts/scripts/check_deployment.js` explicitly failed against the retained evaluation pin. The old manifest identifies a genuinely lost deployment; no successful current check was inferred from old confirmations or from a reused address.

Before namespace retirement, database inspection found **zero prepared, submitted or uncertain jobs**, including retained namespaces. There were 228 confirmed jobs, 50 pending jobs and four mined-unapplied jobs; the four mined-unapplied jobs belonged to retired namespaces. The normal guarded `backend.scripts.reset_mvp` procedure then held the existing signer guard, deployed a new actual local registry, retired the one active namespace through its append-only event and seeded reference actors only. No household, claim, funding, cash or verification success was seeded. All previous records, originals and manifests remain retained.

The newly selected evaluation manifest is ignored `.runtime/evaluation-a0c40eb157944b5794c2a345491218bd.json`. The separately selected fault-node manifest is ignored `.runtime/storytelling-test-deployment-f3dc3565ad9e460d820e3e9e70ea455f.json`; the prior fault manifest was retained. Selection used the existing `MVP_TEST_DEPLOYMENT_MANIFEST` setting in private ignored configuration. No dependency, schema, contract interface or receipt hashing change was made.

Only the verified workspace-owned previous API process tree and frontend process tree were stopped. The documented supervisor was started hidden without `--with-chain`, checked the actual evaluation deployment, ran explicit idempotent setup/reference seeding and restored API, worker, scheduler and frontend. PostgreSQL was preserved throughout.

Runtime logs are ignored `.runtime/storytelling-chain-8545.log`, `.runtime/storytelling-chain-8555.log`, `.runtime/storytelling-supervisor.log` and matching error logs. Hardhat logs contain development credentials and must not be shared or committed.

After recovery, API `/api/v1/health` and frontend `/mvp` both returned HTTP 200. Ports 3000, 8000, 8545, 8555 and 55432 were listening. The new active namespace had zero households; 16 prior namespaces remained retired/readable separately. Those counts describe this checkpoint, before subsequent form-driven browser validation.

The usable local app is [http://127.0.0.1:3000/mvp](http://127.0.0.1:3000/mvp), with [OpenAPI](http://127.0.0.1:8000/docs). Services now follow the documented loopback supervisor procedure. `python -m backend.scripts.local_mvp stop` stops owned application children while the separately started chains survive. This app remains local synthetic evaluation with impersonable claimed actors.

## Fresh validation checkpoints

| Check | Actual result | Evidence |
|---|---|---|
| Initial TypeScript | Passed before storytelling edits | Command above; no compiler diagnostics |
| Selected browser baseline | Interrupted after eight passes; incomplete | `.runtime/storytelling-baseline-browser.log` |
| Retained evaluation deployment after node restart | Failed, deployment unavailable | Explicit `check_deployment.js` exit 1 |
| Guarded new namespace | Passed; one retired namespace, history retained | Normal reset acknowledgement and owner read |
| Restored service health | HTTP 200 for API and MVP | Actual HTTP reads after supervisor start |
| Isolated actual integrity regression | Passed: one test in 22.726 seconds | `.runtime/storytelling-integrity-baseline.log` |

`python -m unittest backend.tests.test_integrity -v` used an isolated synthetic PostgreSQL test schema and the actual fault-chain pin. It exercised required-anchor-absent, an actual matching chain read, mismatch against changed public links/original bytes, evidence unavailable, unreachable RPC and the retained separately historical confirmed observation. Controlled presentation fixtures do not establish these results. No test implementation or assertion changed.

Native-speaker review, representative participant comprehension and physical-device/camera checks remain human validation. No result is invented here.

## Beneficiary actual browser gate

Updated the existing form-driven `journey.spec.ts` to explicitly preserve an English language preference, inspect household/application review dialogs, choose native recipient-path radios, assert record-specific persistent confirmations and exercise grouped payout-code hiding/revealing. All original backend publication, human decision, independent checker, recorded handover and actual-anchor assertions remain.

The first run failed when the live-development DSWD shell remained in its loading state during source recompilation; the API/catalogue later returned HTTP 200 promptly. Registration, actual claim submission, both barangay responses and formal submission had succeeded. This is a recorded failure, not a passing full journey (`.runtime/storytelling-beneficiary-journey.log`).

The second run completed the own-device path through an actual published list, saved authorization, code Hide/Reveal, actual once-only handover, session closure, private recipient answer and terminal refusal to offer another authorization. It then failed entering assisted registration: the test clicked the disclosure before initial household hydration settled, leaving the native form closed. The test now waits for the registry heading before waiting for network idle and deciding whether to open the form. The failure remains recorded in `.runtime/storytelling-beneficiary-journey-2.log`; no product safeguard changed.

The actual-code journey now disables Playwright traces: a trace records input values and could persist private PINs or once-shown payout codes. The generated second-run trace archive was removed for that reason; the failure log remains. No retained business record, manifest, original or append-only history was removed. Subsequent runs use `.runtime/storytelling-runtime-journey-results-3` and `.runtime/storytelling-beneficiary-journey-3.log`.

The third run again completed the own-device path and then completed assisted registration, real accepted-photo/field-check review, assisted claim and the eligible responder's response. It failed at the synthetic-clock control. Source inspection reproduced an existing mismatch: `EvaluationClock.tsx` existed with the expected control, but no frontend file imported it (also true for the inspected `HEAD` shell/claim source), although the retained browser journey expected it on the claim screen. This must be restored as a clearly labelled, existing secondary synthetic-evaluation capability or explicitly documented as unavailable; the test is not weakened to invent deadline completion.

The existing synthetic clock was then restored by the shell implementer inside the DSWD secondary disclosure (now labelled **Simulated clock**). The fourth actual browser journey passed: **1 test in 2.0 minutes** (`.runtime/storytelling-beneficiary-journey-4.log`). Both own-device and no-phone assisted paths used newly uploaded original evidence and actual API records: household/application review, human claim decisions, documented computed amounts, actual chain-backed list publication, sessions, ID comparison, recipient-controlled private PIN and independent assigned checker, grouped code Hide/Reveal, once-only handovers, session closure, separate private receipt answers and no restored payment.

The browser journey was allowed to complete before staff interaction patterns were extended. A separate actual browser Auditor check then opened the confirmed handover row, clicked **Check now**, observed the actual `/integrity/check` response `match` and verified the current **Verified** label (`.runtime/storytelling-audit-current-check.log`). This supports a current chain assertion rather than relying on saved submission confirmation. The same current-read assertion is now in the retained journey regression for final validation.

## Final-suite preparation

Retained English-focused browser regressions now initialize an English preference only when no preference exists. Language persistence tests therefore retain a user-selected Filipino choice across reload/navigation. Bilingual workflow errors use their actual translated field labels and review buttons; old decision, response, publication, identity and handover selectors now include the explicit review/confirm step and record-specific persistent saved result. The actual handover regression also cancels a review and reads the still-unpaid saved transaction before confirming once.

The original-backed funding test previously expected an unreachable chain regardless of runtime state. The preserved `HEAD` test and historical operation report confirm that assumption came from the stopped-chain baseline. With actual nodes restored, the revised test waits for the new release's actual confirmed proofs, requests current integrity and requires `match`/Verified. A controlled failed subsequent read then must clear current Verified while retaining a labelled earlier match. It accepts neither arbitrary success states nor fabricated observations.

A second inherited setup gap was reproduced: the cash journey closes both paid sessions, while later live scan tests require a scheduled/open assigned session. `SessionLookup` intentionally excludes closed sessions. The test helper now prepares a **third unpaid synthetic household/session** only when no current assigned session exists, using existing API commands, newly uploaded originals, independent responses, a reviewed human decision and an actual chain-published list. It schedules that new unpaid household; it never reopens a paid session or creates another payout for a recorded handover. API-only setup passed (`.runtime/storytelling-lookup-preparation.log`); final browser checks remain necessary.
