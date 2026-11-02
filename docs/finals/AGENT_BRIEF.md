# AyudaChain — Finals-safe engineering handoff
**Date:** 14 October 2026 · **Event:** PUP Main Hackathon 2026, Top 10 Finals  
**Reference branch:** `design-proposal` · **Deadline for presentation materials:** 3:00 AM PHT  
**Scope:** fictional beneficiaries; no real payments, ID records, institutional passwords or production blockchain transactions.

## What matters before the 3:00 AM deadline

1. Review the finished slide deck in `AyudaChain_Professional_Finalist_Deck.pptx` and export/send it as PDF, with the PDF named first in the submission sequence.
2. Validate the opening narrative, the prototype capability slide, and the closing ask. Don't claim live role authentication, real SMS, actual National ID validation, offline cash synchronization, production DSWD affiliation or an active public Polygon deployment.
3. Preserve the working demo branch. A reliable three-minute synthetic demo beats an untested redesign.
4. Optionally include a separate, truthfully labeled mockup explainer video if rendered. Do not call the mockup a recording of the working app.

## 1 — Chromebook preparation (no repo currently cloned)

Use **Linux Terminal**, not the browser developer console. Copy one block at a time:

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/andreirtc/ayudachain.git
cd ayudachain
git fetch origin --prune
git switch -c finals-base origin/design-proposal
git status -sb
```

This is the untouched **reference checkout**. Make a separate checkout for the autonomous agent:

```bash
cd ~/Projects/ayudachain
git worktree add -b finals-agent ../ayudachain-finals-agent finals-base
cd ~/Projects/ayudachain-finals-agent
git status -sb
```

Open `~/Projects/ayudachain-finals-agent` as an **existing local project** in Orca. Pick the installed **Codex** coding agent. The complete first-run prompt is below. Keep `~/Projects/ayudachain` unchanged as the demo/reference fallback.

If you previously cloned or worked on the repo, **do not run the clone or switch commands blindly**; use `pwd && git status -sb` and inspect local changes first.

## 2 — Overnight Codex/Orca prompt (paste in one agent session)

You are the lead full-stack engineer, QA engineer, design-system reviewer, and Git history/PR triage analyst for AyudaChain, a PUP Hackathon 2026 Top 10 finalist. The user needs a defensible prototype in the morning and a deck submitted by 3:00 AM Manila time. Work autonomously **within the isolated `finals-agent` worktree only** as far as your configured permissions permit, with regular written checkpoints. Never silently claim completion. Do not interpret this prompt as permission to spend money or deploy externally.

### Read first and reconcile the actual facts

1. `AGENTS.md`, `PRODUCT.md`, `DESIGN.md`, `README.md`
2. `docs/product/prd.md`, `docs/product/user-flow.md`, `docs/product/sitemap.md`
3. `docs/guides/local-mvp.md`, `docs/guides/demo-script.md`
4. `docs/implementation/validation.md`, `docs/implementation/bring-forward-usability.md`
5. `docs/design/tonal-design-reference.html`, `docs/design/implement-missing-design.md`
6. `docs/implementation/evaluator-deployment-plan.md`
7. The Git history, all remote branches and all existing open PRs.

### Hard safety rules

- Never reset/rewrite the working baseline, DB, retained evidence, chain deployments or originals. Never alter main or close, squash, merge, retarget, rebase, delete or force-push **any published branch or PR** unattended.
- Do not merge `BinkzBooze/...` into `design-proposal` wholesale. The paths are materially divergent: one is an authenticated FastAPI/SQLite implementation with stacked PRs, the other a larger synthetic five-role FastAPI/PostgreSQL implementation with claimed demo actors.
- No real identities, bank transfers, live payment APIs, production keys, public chains, SMS providers, external hosted resources, or added paid services. No fabricated screenshots, benchmark numbers or positive blockchain verification states.
- No contradictory design choices. Respect current Sea and Sun / Tonal components. Preserve component and API contracts, immutability, centavo-level accounting, recipient authorization, and append-only evidence rules.
- Keep user-facing claims truthful: QR scanner depends on browser `BarcodeDetector`; SMS and National ID are simulated; no offline payout, true login gate or public deployment.
- Do not install multi-gigabyte toolchains or start concurrent memory-heavy tests on the Chromebook without checking `free -h` and `df -h /`. Use available test tools and report environment blockers. The Chromebook Linux allocation was previously approximately 6.3 GiB RAM and 18 GiB free disk.

### Phase A — Repo inventory and PR triage

Create `docs/finals/PR_TRIAGE_MATRIX.md` with one row per remote branch and each open PR: branch/PR ID, author, base/head and whether stacked, functionality, test evidence, relevance to `design-proposal`, risk, duplication/conflicts and recommended disposition (`retain`, `review`, `selective port`, `superseded candidate`, `close only after approval`). Record a dependency graph for 02–31 rather than merging individually. Identify actual branch latest commit dates and unmerged scope. Do not change GitHub PR state.

Compare `design-proposal` with `feat/five-role-mvp`, `main`, and `BinkzBooze/ayudachain-30-receipt-snapshots`. Different auth/database/contract designs must be documented as incompatible, not silently combined. Create `docs/finals/INTEGRATION_PLAN.md` recommending a single base and isolated implementation sequence. Cherry-pick only a fix that is unambiguously compatible and regression-tested; otherwise document the candidate only.

### Phase B — Stabilize a reliable demo

Inspect all page entry points and tests. Reproduce the branch's reported browser failures, including 10/37 from design notes. Distinguish pre-existing test expectation problems from real UI regressions. Test a *single supported synthetic journey* end-to-end with actual available services, API responses and chain reads. Do not treat a test passing after a mock as a live-chain success. Save commands, screenshots, server logs, and results to `docs/finals/QA_REPORT.md` and `docs/finals/assets/` where reasonable.

If the required PostgreSQL 18, Python 3.14 or Node 22 runtime is unavailable on this Chromebook, stop short of risky installs; audit statically and prepare the exact Windows/Linux setup and test commands in `docs/finals/DEMO_RUNBOOK.md`. Never discard real data to make test fixtures pass.

### Phase C — UI / UX high-value improvements

Focus on no more than **three** independently testable, low-risk improvements, in this order: (1) role-specific primary action and plain-language next steps; (2) keyboard/screen-reader-safe confirmation and success/error messaging for irreversible decisions; (3) mobile navigation and table overflow. Compare current UI with `docs/design/tonal-design-reference.html`, clearly label intended design versus implementation. Review 390px and 1440px viewports if a real browser is available. No changes to entitlement formulas, API contract, database schema or blockchain anchoring. Avoid new dependencies and broad refactors. Commit each stable change to the isolated branch, but do not push or open a PR without a final summary.

### Phase D — Demo and handoff

Produce:
- `docs/finals/FINALIST_STATUS.md`: implemented / simulated / not delivered, with file paths and tested evidence.
- `docs/finals/DEMO_RUNBOOK.md`: prerequisites, startup, 3-minute click sequence, health checks, exact synthetic fixtures, recovery and fallback.
- `docs/finals/JUDGE_QA.md`: 20 realistic questions/answers about actual service process, choice of blockchain vs database, false matches, accessibility and no-phone options, privacy, security limits, network downtime, real cost drivers, buyer and channel, procurement, NGO expansion, pilot metrics, and unit economics as hypotheses rather than made-up numbers.
- `docs/finals/PR_TRIAGE_MATRIX.md` and `INTEGRATION_PLAN.md` from Phase A.
- `docs/finals/VIDEO_SHOTLIST.md`: real app screenshots/screen recording sequence, no fabricated visuals. If the real MVP cannot launch, the existing `docs/product-ideation/mockup/presentation` renderer may produce an **explicitly labeled mockup explainer**, never call it a live demo.
- `docs/finals/QA_REPORT.md` and a concise terminal summary with blockers, pass/fail tests, changed files, backup pointer and safe next steps.

### Stop criteria and autonomy

Prioritize repeatability and evidence over quantity. Stop adding features after the chosen demo journey is reliable. Do not mark unresolved tests as passed. Leave other provider sessions, existing original databases and PRs unchanged. If waiting for approval, work on independent read-only analysis and documentation instead. Provide an end-of-run summary; do not assume the user will be watching.

## 3 — What a human must check before pitching

- The current demo has real loaded data and no missing API/chain.
- A fresh current blockchain read reports its true state. Do not equate a recorded transaction reference with confirmation.
- The demo person and every payment are explicitly fictional.
- If role accounts are still selectable, clearly state this is a synthetic role walkthrough and not a production login model.
- The current mobile route can be navigated at 390px width without lost primary actions.
- In the slides, mock UI examples are called illustrative design targets, not screen captures of the shipped app.
- The presenter can answer what staff does if a person has no phone, no matching ID, an incorrect name, or no internet.
- No production release or real citizen onboarding is represented as ready.

## 4 — Google/GitHub cleanup after the presentation

After the finals, review `PR_TRIAGE_MATRIX.md` as a team. Choose one integration base, protect `main`, verify CI on a test branch, then gradually incorporate validated compatible improvements. Archive stale branches and close superseded PRs **only with their authors' knowledge and a recorded replacement reference**. Avoid mass close/merge; the branch histories contain distinct business logic and database assumptions.

## 5 — Session continuity

To let the agent run unattended, the Chromebook must remain awake, powered, connected, and your Codex/Orca session must permit non-destructive commands without repeated approval prompts. Avoid closing the laptop or assuming ChromeOS Crostini processes remain active while suspended. Do not promise that a desktop agent can finish after you disconnect; confirm its actual progress in Orca and inspect saved files before using them.
