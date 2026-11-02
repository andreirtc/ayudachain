# Finals demo runbook

14 October 2026. Run from the repository root. Use invented records only. The software records a synthetic cash handover; no money moves. **Do not run reset commands, replace manifests, restart a surviving chain, or point tests at a shared demonstration database.**

## Tonight's operator handoff

The lab selected during finals preparation is recorded in [readiness](FINALIST_READINESS.md). Current loopback URLs: `http://127.0.0.1:3000/mvp`, API `http://127.0.0.1:8000/docs`. Existing Node is `/home/ralphandreicastillo326/.config/nvm/versions/node/v24.18.0/bin/node`; the locked interpreter is `.venv/bin/python`. PostgreSQL 17.11 is extracted in `.runtime/finals/pg-tools`, with the newly owned cluster in `.runtime/finals/postgres`. This Linux/Python 3.13 setup differs from historical Windows/Python 3.14/PostgreSQL 18 validation; today's results are recorded separately.

Keep the laptop powered and the chain process alive. Hardhat history is volatile. Stopping/restarting the application alone is safe when the pinned chain survives. Losing the chain must be reported as lost/unreachable; a new deployment cannot verify old records.

## Preflight before any install/start

```bash
git status --short --branch
git worktree list
ss -ltnp
export PATH=/home/ralphandreicastillo326/.config/nvm/versions/node/v24.18.0/bin:$PATH
node --version
.venv/bin/python --version
```

Inspect `.env.mvp`, database availability and manifest **existence** privately; never print configuration contents or keys. Occupied ports belong to existing services until ownership is established. Do not kill by port or run broad `pkill`. Do not run the legacy root `npm start`; it starts a different stack.

For a genuinely new checkout only, install the existing locks, without adding/changing dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-mvp.lock
npm --prefix contracts ci
npm --prefix frontend ci
npm --prefix contracts run compile
node frontend/node_modules/@playwright/test/cli.js install chromium
```

On Windows use `.venv/Scripts/python.exe` and supported Node 22/24. Do not overwrite an existing virtual environment or run npm ci against someone else's running frontend. Existing locks retain contract development-tool advisories. No force audit upgrade tonight.

## Local database and isolated lab

PostgreSQL must already be available. Tonight's extracted binaries need their library directory:

```bash
export MVP_PG_BIN="$PWD/.runtime/finals/pg-tools/usr/lib/postgresql/17/bin"
export LD_LIBRARY_PATH="$PWD/.runtime/finals/pg-tools/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
```

If this owned cluster already exists and is stopped, inspect its status before starting it:

```bash
"$MVP_PG_BIN/pg_ctl" -D .runtime/finals/postgres status
"$MVP_PG_BIN/pg_ctl" -D .runtime/finals/postgres -l .runtime/finals/postgres.log -o '-h 127.0.0.1 -p 55432 -k /tmp' start
```

Never run initdb on an existing directory. For another machine, follow [local operation](../guides/local-mvp.md) using its own installation. Do not install server packages over an existing cluster solely for this demo.

To create a **new** test/evaluation lab, preserving all existing databases and originals:

```bash
MVP_RPC_URL=http://127.0.0.1:8547 .venv/bin/python docs/finals/create_isolated_lab.py
```

The helper creates random, separately named evaluation/test databases and a new mode-0600 ignored configuration, with unique manifests/original paths and a private replay key. It never drops, resets, migrates or seeds a database. Select the printed path, not this illustrative placeholder:

```bash
export MVP_CONFIG_FILE="$PWD/.runtime/finals/labs/PRINTED_ID/lab.env"
```

Keep that file private and retain it with the lab. If creation fails, retain any new database for inspection; the helper does not perform destructive cleanup. Existing inherited `MVP_*` overrides take precedence over a configuration file: use a fresh shell or explicitly reconcile known operator overrides before selecting another lab.

## Start actual chain and application

For this resumed rehearsal the separately owned new chain is8547. Earlier8545/8546histories are unavailable; their databases/manifests remain preserved. Do not launch a replacement over their pinned deployments. For a genuinely new isolated node only, after checking8547is free:

```bash
npm --prefix contracts run node -- --hostname 127.0.0.1 --port 8547
```

This keeps the chain independent of application restarts. Do not redirect Hardhat's full startup output into presentation materials: it contains public local development account keys, which must remain local. The supervisor supplies the local-only signer after local checks; no public RPC is allowed.

In the lab-configured terminal:

```bash
.venv/bin/python -m backend.scripts.local_mvp serve
```

For the selected **new absent manifest only**, this deploys an actual local registry, migrates the approved schema, seeds reference actors/disasters and starts API, scheduler, worker and frontend. It refuses a lost existing deployment. Check `.runtime/supervised/` privately if preparation fails. The finals POSIX port probe permits closed connections in TIME_WAIT while still refusing live listeners.

Read `/api/v1/health`, but do not call its HTTP 200 proof of blockchain health: it reports chain/storage `not_checked`. Demonstrate a fresh integrity read on a real saved commitment.

Owned application stop (keeps separately started chain and PostgreSQL alive):

```bash
.venv/bin/python -m backend.scripts.local_mvp stop
```

## Test sequence without resetting data

Run tests in a **new isolated lab**. The browser journey requires an empty household registry and now refuses execution unless explicitly opted in; it no longer calls `reset_mvp`. Run the journey first, then other browser files. A failed partial journey is retained: create another lab to rerun from the beginning.

```bash
MVP_BROWSER_FRESH_RUN=1 npm --prefix frontend run test:mvp -- tests/journey.spec.ts
npm --prefix frontend run test:mvp -- --grep-invert 'five roles use edited original-backed forms'
npm --prefix frontend run typecheck
npm --prefix contracts test
.venv/bin/python backend/test_backend.py
```

For backend domain/fault/recovery tests, use a separate node on 8555 and the selected test manifest. Never reset either node. Start it only when its port is free:

```bash
npm --prefix contracts run node -- --hostname 127.0.0.1 --port 8555
```

Deploy a fault manifest **once at a new path**, matching the lab's `MVP_TEST_DEPLOYMENT_MANIFEST`. In a separate terminal use the exact supported Node executable and temporary loopback RPC/manifest overrides:

```bash
MVP_RPC_URL=http://127.0.0.1:8555 MVP_DEPLOYMENT_MANIFEST="$PWD/.runtime/finals/labs/PRINTED_ID/fault-deployment.json" node contracts/scripts/deploy_evidence.js
.venv/bin/python -m unittest discover -s backend/tests -v
```

Backend tests create owned random schemas in the explicit test database; fault/recovery suites must run sequentially. Their deliberately disposable node-loss cases own their own extra chain and never reset the evaluator's chain. Preserve all manifests after node loss. Correct the PostgreSQL tool/library PATH before backup tests. Do not claim one green full run by adding separate reruns to an earlier failing run.

Stop the owned frontend/API supervisor before `npm --prefix frontend run build`; then restart with the same configuration and surviving chain. A build and dev server must not share `.next` concurrently. Build checks TypeScript; ESLint is explicitly skipped by existing configuration.

## Three-minute stage walkthrough

Preload the real saved lab before the pitch. Avoid entering the entire administrative journey live in three minutes. The [genuine workflow video](VIDEO.md) and test evidence demonstrate the full path; stage inspection shows the resulting records and one fresh check.

| Time | Open / action | Spoken point |
|---|---|---|
| 0:00–0:25 | `/mvp`, DSWD Funding ledger; open the actual release original | “A human confirms the funding evidence. This balance is recorded authority, not a cash-account certification.” |
| 0:25–0:50 | DSWD Claims; open the demonstrated household/thread/decision | “Barangay responses and automatic flags inform a recorded human decision.” |
| 0:50–1:10 | Amounts and lists; show documentary inputs/current list | “The household amount comes from a recorded rule; the list waits for its own chain confirmation.” |
| 1:10–1:45 | Beneficiary Authorization & receipt, then recorded payer/session facts | “This handover was recorded once. We will not repay it to create a second demonstration.” |
| 1:45–2:10 | Beneficiary private answer or DSWD private case | “Recipient report and recorded handover remain separate.” |
| 2:10–3:00 | Auditor Evidence & integrity; click **Check now** on the actual handover proof | “This is a fresh local-chain comparison. A match proves committed evidence continuity, not cash delivery.” |

Use All workspaces to move roles. The Account panel selects another actor of the same role. Always confirm disaster and actor before opening a direct record. Role changes are demonstration convenience, not authentication. Do not put synthetic PINs/codes in slides or reuse them as real credentials.

## Full editable journey / rehearsal

Use the exact form order in [the current evaluation guide](../guides/demo-script.md), **omitting its reset instruction**. The fresh lab already has reference-only actors/disasters.

1. DSWD: upload an invented release PDF, inspect extraction, edit/confirm fields and save; separately upload operation basis and open intake for the chosen barangay.
2. Beneficiary: register invented household and optional private ID/photo, then submit damage/category.
3. Two eligible Barangay actors respond; Punong uploads an invented council resolution and submits fixed threads. If using a fallback route, label it and let the scheduler save its actual exception snapshot.
4. Independent DSWD reviewer examines current check/flags, acknowledges review and decides. Supply invented documentary wage/day inputs; prepare the cumulative list and wait for actual publication.
5. DSWD schedules today in the selected business clock, named members, site and eligible cash staff; opens the session.
6. Beneficiary opens a current attempt, keeps its one-time code; payer compares the actual saved synthetic head photo/ID and records the handover through the review dialog. Reload the receipt; never repeat cash.
7. Recipient privately answers. For the no-phone rehearsal, use a separate household with field-check evidence, privately established PIN and distinct assigned payer/checker. The helper cannot endorse; the payer cannot record the exit answer.
8. Auditor inspects original/version history and performs a fresh check. Optional independent verification uses exact authorized material and original bytes with `contracts/scripts/verify_evidence.js`; never expose the private envelope on the projector.

## Fallbacks that preserve the claim

| Failure | Do / say |
|---|---|
| Frontend unavailable | Use captured actual application screenshots or genuine workflow video with capture date; label recorded evidence. Do not call a screenshot a live test. |
| API/database unavailable | Do not save or repeat cash. Explain state cannot currently be confirmed; use recorded evidence. Restore services under the same configuration. |
| Chain unavailable | Show Chain unreachable. Funding/handover records remain; list publication waits where required. Never create a fake transaction or replace an old pin. |
| Missing/mismatched evidence | Show unavailable/mismatch and explain investigation. Never substitute a sample file and call it verified. |
| Lost handover response | Read the same transaction and receipt before safe request replay. No second physical payout. |
| QR unsupported/denied | Type the same opaque transaction reference. QR is optional lookup, not identity or authorization. |
| No independent checker | Hold assisted payout; escalate staffing. Never select the payer twice. |
| PIN lost / code hidden | PIN recovery is pending. A lost unused code must expire before a permitted new attempt. No bypass. |
| Canva unavailable | Use the local pitch script/replacement slide outline; original deck remains unchanged. |

Never “fix” a failure by weakening review, budgets, eligibility, codes, hashes or history. Record it in [progress](PROGRESS_LOG.md) and [readiness](FINALIST_READINESS.md).

## Current capture/video artifacts

See [actual screenshot gallery](SCREENSHOTS.md) and [video provenance/playback instructions](VIDEO.md). Capture scripts require a completed actual two-handover lab and refuse a nonmatching current check. Reproduce with `node docs/finals/capture_evidence.cjs`; each invocation creates a new capture directory. `MVP_RECORD_VIDEO=1` records the full journey. No mock data or fabricated integrity result is supplied by either capture path.
