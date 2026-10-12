# Investigation log

Started 2026-10-08 Asia/Manila. Expert evaluation with synthetic role-play; no real-user research.

- Initial branch `main-2`, HEAD `6d92882dcbc4496645b4379561f457d1504aed53`. Existing changes and per-file digests: initial-state.json. No branch switch, commit or stash performed.
- Disposable snapshot: `C:\Users\Yushin\AppData\Local\Temp\ayudachain-investigation-ba4heaqr`. Secrets, databases, dependencies and build output excluded. Tests, deployment manifests and synthetic database mutations run here.
- Required PRD, DFD and ERD absent; ADR directory contains only .gitkeep. Requested authoritative context and pilot owner; redesign assumptions remain provisional pending input.
- Read AGENTS.md: no nested AGENTS.md found. Preserve all integrity invariants; no backend or product edits.
- Disposable snapshot npm ci succeeded for frontend (47 packages; audit reported 4 vulnerabilities) and contracts (640 packages; 58 reported). No audit fix run. Versions: Node 25.4.0, npm 11.7.0, Python 3.14.5; Hardhat reports unsupported Node version.
- Existing checks: backend 8/8 passed; contracts 9/9 passed and compiled Solidity; independent frontend typecheck exit 0; production build exit 0. First harness instances hit Windows stdout encoding errors after saving successful underlying results; harness corrected, no product change, no repeat needed.
- Local deploy wrote generated manifests ONLY in snapshot; services owned by investigation recorded in snapshot/investigation-processes.json. Active backend is server.py, not FastAPI.
- Root browser walkthrough: all five desktop/mobile routes; citizen registration; officer rejection; seeded/custom malformed-header CSV analysis; simulated scanner; normal payout while offline toggle enabled; broken receipt preview; real local hash match; both scripted fraud demonstrations. Raw browser bodies/network/screenshots saved alongside this log. No field participants or measured task timings.
- API baseline probes: public registry and contact/review data exposed without auth; blank name auto-approved; arbitrary review status accepted; rejected/flagged records paid; tiny batch overallocated/distributed; nonexistent batch payout saved and falsely verified; two concurrent requests saved two payouts for same beneficiary; sequential duplicate retry rejected; malformed JSON/nonnumeric amount close connection. Full request/response evidence in api-probes-baseline.json.

- Completed tamper, reverse-order failure, concurrency, lost-response, real browser-offline, real chain/backend outage, chain restart, anonymous deletion and citizen repeat-reset checks. 59 root screenshots/body snapshots. Independent source tracks account for all 73 initial first-party files; A/B browser and primary-source artifacts saved.
- Chain success followed by DB ID collision left an orphan chain assertion and a leaked DB lock; restart was necessary. RPC failure and absent anchors falsely verify. Fresh chain restart retained database but no matching chain record. Citizen repeat demo reset erased audit IDs and replaced genuine tx hashes with nonexistent hashes after duplicate-ID reverts.
- Harness correction: first reset sampled during seeding and used wrong audit URL; recovery-and-reset.json labels that limitation. Second reset awaited HTTP200, used correct endpoint/role, and independent transaction lookup.

- Final audit found two concurrently added finance-officer drafts outside initial inventory. All original73 source hashes still matched; no product code changed. Fully read both, captured additional-context-state.json, extended coverage75, asked whether drafts define intended next scope, and integrated finance-first Direction D plus E15 draft critique. Draft claims remain provisional, not authoritative external rules.
- Root browsers and owned backend/frontend/chain stopped; independent detector helper already stopped. Final gate re-audits additions and links.

- Final coverage follow-up: reopened only snapshot backend/frontend, exercised browser Back on unsubmitted payout draft (BEN-0004/2000 → Verify → Back reset BEN-0001/5000); no payout posted. O19 and60th screenshot saved; both owned services/browser stopped again. Chain remained stopped. Updated E12 and limitations; no unsupported back-navigation claim.

- Maintainer responded: hackathon only; intended body DSWD for disaster-relief funds; no pilot operator or authority; finance-first alternative under consideration. Saved maintainer-context.md and revised all main artifacts to distinguish truthful synthetic demo priorities H1–H4 from conditional future pilot requirements. No product behavior changed; scope remains investigation/redesign proposal.

- Completion gate passed after maintainer context and independent final review:75/75 source areas covered,60 root+16 independent screenshots, all main local links/anchors resolve, all original73 file hashes and both concurrent draft hashes unchanged, git HEAD/branch/status preserved, no owned lab listeners. All four artifacts written; no product implementation/commit/push/issues or public deployment. Remaining institutional/field/production checks explicitly unverified future work.
