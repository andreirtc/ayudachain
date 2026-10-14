# Local MVP operation and evaluation

Historical Windows setup below describes the original `mvp-full` checkout. For the current Linux `design-proposal` finals worktree and safe isolated labs, use [the finals runbook](../finals/DEMO_RUNBOOK.md). Branch/runtime status must be inspected rather than inferred from this historical setup. FastAPI/PostgreSQL is authoritative; the retained standard-library/SQLite backend is separate. No external service or public-network deployment is required or authorized.

## Locked setup

Validated environment: Python 3.14.5, Node 22.23.3, PostgreSQL 18.6, FastAPI 0.143.0, Next.js 15.5.27 and Hardhat 2.29.1. Node 22/24 are accepted; Node 25 is refused. Direct versions and transitive locks are in `backend/requirements-mvp.txt`, `backend/requirements-mvp.lock` and each npm package/lock pair. Official compatibility references are in the [ADR](../adr/2026-10-10-mvp-evidence-protocol-and-registry.md).

Run from the repository root. Windows commands use `.venv/Scripts/python`; on Linux/macOS use `.venv/bin/python`. Activate the environment before using root npm scripts that call `python`. Put supported Node on PATH before npm commands.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r backend/requirements-mvp.lock
npm --prefix contracts ci
npm --prefix frontend ci
npm --prefix contracts run compile
node frontend/node_modules/@playwright/test/cli.js install chromium
```

PostgreSQL must already be running. This checkout has ignored, owned binaries in `.runtime/tools/pgsql/bin`, a local cluster in `.runtime/postgres`, and Node in `.runtime/tools/node-v22.23.3-win-x64`. These runtime downloads are not tracked source. A fresh checkout needs an official local PostgreSQL installation and supported Node; point the configuration to those executables. Do not reuse an unrelated cluster directory. For a new, empty owned Windows development cluster:

```powershell
New-Item -ItemType Directory -Force .runtime | Out-Null
& .runtime/tools/pgsql/bin/initdb.exe -D .runtime/postgres -U postgres -A trust
& .runtime/tools/pgsql/bin/pg_ctl.exe -D .runtime/postgres -l .runtime/postgres.log -o '-h 127.0.0.1 -p 55432' start
```

The trust configuration is for this loopback synthetic evaluation only. Setup defaults to `postgresql://postgres@127.0.0.1:55432/postgres` for local administration. For another local installation, set `MVP_ADMIN_DATABASE_URL` privately before setup. It creates `ayudachain_mvp`, `ayudachain_mvp_test` and NOLOGIN purpose roles `mvp_runtime`, `mvp_worker`, `mvp_inspection`. Runtime commands use `SET LOCAL ROLE`; this is not authenticated isolation against the local owner.

```powershell
.venv/Scripts/python -m backend.scripts.setup_mvp
```

This explicitly creates/upgrades the approved schema; API startup does not migrate, seed or deploy. Repeat setup preserves business records. `backend/migrations/catalogue.py` applies recorded versions 0001-0007 and constraints without rewriting history. SQL files are reviewable generated representations, not independently ordered manual migration instructions.

Setup creates ignored `.env.mvp` if absent, including a random HMAC replay key. Keep it private and preserve it for replay recovery. Configure `MVP_NODE` to the absolute supported executable; its generated Windows default matches this checkout's owned Node. Configure `MVP_PG_BIN` if PostgreSQL utilities are elsewhere. The principal settings are:

| Setting | Meaning |
|---|---|
| MVP_DATABASE_URL, MVP_OWNER_DATABASE_URL | Local MVP database and explicit migration owner |
| MVP_WORKER_DATABASE_URL, MVP_INSPECTION_DATABASE_URL | Local worker/inspection connections, separate purpose grants |
| MVP_TEST_DATABASE_URL | Explicit `ayudachain_mvp_test`; no evaluation-database fallback |
| MVP_TEST_DEPLOYMENT_MANIFEST | Absolute selected fault-node manifest; defaults to `.runtime/test-deployment.json`. Use a new path after node loss and retain the old manifest. |
| MVP_RPC_URL | Credential-free loopback HTTP, normally 8545; local chain ID 31337 only |
| MVP_NODE, MVP_PG_BIN | Supported local executables |
| MVP_DEPLOYMENT_MANIFEST | Exact retained manifest; default `.runtime/deployment.json` |
| MVP_COMMAND_DIGEST_KEY | Random 64-hex-character replay HMAC key; never print it |
| MVP_SCHEMA, MVP_EVIDENCE_ROOT | Schema and private-original root; defaults public and `.runtime/originals` |
| MVP_CONFIG_FILE | Alternative ignored restore JSON configuration |

## Start and stop

For routine evaluation, start the owned supervisor:

```powershell
.venv/Scripts/python -m backend.scripts.local_mvp serve --with-chain
```

It checks loopback configuration, refuses occupied ports, starts its own chain when requested, deploys a new actual registry only if the selected manifest does not exist, runs explicit migrations/reference seeds, and starts the API, worker, scheduler and frontend. An existing manifest whose deployment was lost is refused; it is never silently remapped. Repeated preparation seeds references idempotently without business fixtures.

For restart/backup evaluation, keep Hardhat in a **separate terminal** so stopping the application does not erase its volatile chain:

```powershell
npm --prefix contracts run node -- --hostname 127.0.0.1
```

Then run `local_mvp serve` without `--with-chain` in another terminal. Inspect the selected checkout before starting; preserve any surviving evaluation node and its pinned manifest. Open [the MVP](http://127.0.0.1:3000/mvp). API documentation is [local OpenAPI](http://127.0.0.1:8000/docs); health is `/api/v1/health`. Choose any active claimed actor and either synthetic disaster. The visible accelerated clock changes business deadlines only.

```powershell
.venv/Scripts/python -m backend.scripts.local_mvp stop
```

Stop uses an owner-token handshake and terminates only owned process trees. Database, originals and manifests remain. Ctrl+C also stops owned children. API/worker/scheduler/frontend exits are restarted with persisted state; a chain exit requires explicit operator recovery. Ignored logs and ownership metadata are in `.runtime/supervised`. On Windows stop the owned frontend before `npm ci`, otherwise loaded native modules can block installation.

For separate service debugging, `local_mvp prepare` checks pins/migrates/seeds without starting services. Run the API with the locked interpreter (`-m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`), scheduler (`-m backend.app.scheduler`), actual worker (`node contracts/scripts/anchor_worker.js`) and frontend (`npm --prefix frontend run dev -- --hostname 127.0.0.1`). The worker requires an ignored `MVP_PRIVATE_KEY` for the actual local operator. The supervisor supplies the public Hardhat development key only after local configuration/deployment checks. Never send it to a public network. Prefer the supervisor for ordinary evaluation.

## Fresh reference-only evaluation and retained history

```powershell
.venv/Scripts/python -m backend.scripts.reset_mvp
```

This explicit action refuses unresolved prepared/submitted/uncertain nonces, deploys a new registry through `deploy_evidence.js`, retires prior namespaces, retains all originals/history/manifests and seeds multiple actors, two disasters, categories and barangays. It creates no household, claim, funding or payout success. Follow [the full form journey](demo-script.md). Business changes use normal services; SMS/National ID and accelerated time remain labelled simulations.

The separate namespace retirement CLI uses the same signer lock and refuses unresolved prepared/submitted/uncertain work. Reconcile the retained signature while its run is active before retirement; a fresh namespace cannot discard ownership of its nonce. Reset retains that guard across deployment, retirement and reference seeding.

If Hardhat was restarted/reset, preserve the old manifest. It identifies a lost deployment, even if the same address is occupied again. Select a new unique manifest path and deliberately create a new local deployment/namespace. Resolve uncertain prior signatures before reset; deployment loss is not permission to sign replacements or repay recorded cash.

Retired actors cannot run ordinary commands. Read old history separately using a retired Auditor:

```powershell
.venv/Scripts/python -m backend.scripts.namespace_mvp catalogue
.venv/Scripts/python -m backend.scripts.namespace_mvp history --actor RETIRED_AUDITOR_UUID
.venv/Scripts/python -m backend.scripts.namespace_mvp history --actor RETIRED_AUDITOR_UUID --commitment COMMITMENT_UUID
.venv/Scripts/python -m backend.scripts.namespace_mvp history --actor RETIRED_AUDITOR_UUID --original EVIDENCE_UUID --output .runtime/old-original.pdf
```

Original export requires a new path; inspection is privately logged. Old matched reads remain historical if the pinned chain is unavailable. Frozen legacy SQLite import is explicit and read-only: `python -m backend.scripts.import_legacy --actor DSWD_UUID --source PATH_TO_SYNTHETIC_SQLITE [--manifest ORIGINAL_LEGACY_MANIFEST]`. Import does not create MVP eligibility or re-anchor legacy data. Without original evidence/deployment, verification is explicitly unavailable.

## Tests and independently recomputed proof

The backend integration suite needs a distinct persistent fault node on **8555**, compiled artifacts, the selected test deployment manifest, and the isolated database created by setup. The selected test manifest is `MVP_TEST_DEPLOYMENT_MANIFEST`, or `.runtime/test-deployment.json` by default. Run the node in another terminal:

```powershell
npm --prefix contracts run node -- --hostname 127.0.0.1 --port 8555
```

Create its manifest once with `deploy_evidence.js` in a separate PowerShell terminal using `MVP_RPC_URL=http://127.0.0.1:8555` and an absolute `MVP_DEPLOYMENT_MANIFEST` pointing to `.runtime/test-deployment.json`. Never overwrite an existing manifest. After fault-node loss, deploy to a new manifest path and set `MVP_TEST_DEPLOYMENT_MANIFEST` to it in ignored `.env.mvp`; the tests consistently use that selected pin. Clear those terminal-only overrides before running the evaluation stack. Contract tests use their own ephemeral Hardhat network; the backend tests use random owned test schemas and real fault-chain transactions.

```powershell
.venv/Scripts/python -m unittest discover -s backend/tests -v
.venv/Scripts/python backend/test_backend.py
npm --prefix contracts test
npm --prefix frontend run typecheck
npm --prefix frontend run build
npm --prefix frontend run test:mvp
```

The browser suite requires all evaluation services on 3000/8000/8545. It creates fresh uploaded files, edits forms and performs real own-device/assisted journeys; it now requires an explicitly selected fresh isolated lab and never resets existing evaluation data. Run the full journey first with MVP_BROWSER_FRESH_RUN=1; it refuses existing households. Fault tests kill/reconcile prepared, broadcast and mined work, exercise a real EVM revert, uncertain nonce/conflict, API restart/lost acknowledgement, concurrent business changes and backup restore. A dedicated owned node tests same-address reset; it never resets the evaluation chain. Results are recorded in [validation](../implementation/validation.md).

An authorized Auditor/DSWD can retrieve `/api/v1/commitments/{id}/material` and the permitted original bytes. Save the exact `canonical_utf8`, `content_hash`, `deployment` and an `originals` array of `{id,path}` for every evidence descriptor to a private JSON file. Pipe it to `node contracts/scripts/verify_evidence.js`; it recomputes exact canonical/original hashes and reads the pinned registry, without database or signing key. This material contains private preimages; resident list columns are not a selective inclusion proof. The backend full-journey test independently checks all ten kinds this way.

## Backup and restore against a surviving chain

Stop application writers/worker/scheduler, keeping the separately started chain alive. Choose a **new** bundle directory within `.runtime/backups`:

```powershell
.venv/Scripts/python -m backend.scripts.backup_mvp backup .runtime/backups/manual-evaluation
.venv/Scripts/python -m backend.scripts.backup_mvp restore .runtime/backups/manual-evaluation --database ayudachain_mvp_restore_a1b2c3d4
```

Backup captures a consistent exported PostgreSQL snapshot, custom dump, exact private originals, pinned manifests, checksums, replay HMAC configuration and actual chain checkpoint. It excludes the signing key. Treat the entire bundle as private. Restore creates a new owned database only, refuses existing targets/corrupted components and checks the surviving chain for unknown post-backup records. It preserves exact manifest paths and durable signed candidate/nonce material; it does not recreate a lost Hardhat chain. Use the returned ignored restore JSON path as `MVP_CONFIG_FILE` in a fresh process, without conflicting environment overrides, then start API and scheduler with the locked Python interpreter. For the Node worker, load the same JSON into its process environment first using the Python launcher below. The worker reads every job's exact pinned manifest, not a replacement deployment. Keep the original database and originals intact. Never restore and pay again without resolving any post-backup chain/business uncertainty.

```powershell
.venv/Scripts/python -c "from backend.app.config import ROOT,load_local_environment; import os,subprocess; load_local_environment(); subprocess.run([os.environ['MVP_NODE'],str(ROOT/'contracts/scripts/anchor_worker.js')],check=True)"
```

Supply the local signer through ignored operator configuration when resuming actual submissions; no signer is embedded in the restore bundle. Do not run the general preparation/seed command against a restore before inspecting its active run and exact deployment.


## Conditions before real household data

Real use remains Pending. Selectable identities are impersonable; workflow scope checks and private projections cannot provide operational privacy or authenticated accountability. Before any real records: establish authenticated principals, secure sessions/authorization/recovery and private-file serving; approve institutional/legal eligibility, FACED mapping, signatures, processing/disclosure/metadata policy and retention; implement reliable notice delivery; secure hosting, backup/restore objectives and key/network custody; validate genuinely independent payer/checker staffing and physical cash/site safeguards; resolve development-tool advisories and repeat deployed-environment validation. Live National ID, government signature validation and selective list-inclusion proof require separately approved integration. Existing originals remain `not_validated`; no hash proves authentic documents or actual cash receipt.
