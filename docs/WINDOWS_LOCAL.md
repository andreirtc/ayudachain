# Running AyudaChain locally on Windows

All data and money are fictional. This guide uses a local Hardhat chain only.

`start_ayudachain.sh` is written for Linux (it reads `/proc` and uses `pkill`), so on Windows start each service in its own PowerShell window instead. Run every command from the repository root unless a step says otherwise.

## Requirements

- Node.js 20 or later (checked with 24.19)
- Python 3.10 or later (checked with 3.13). On Windows the command is usually `python`, not `python3`.
- `node` must be on `PATH`, because the backend calls `contracts/scripts/blockchain_client.js` to talk to the chain.

Install dependencies once:

```powershell
npm --prefix contracts install
npm --prefix frontend install
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
cd ..
```

## Configuration

Public functionality has local defaults. Private workflows require provisioned synthetic accounts; see [DEMO_SESSIONS.md](DEMO_SESSIONS.md). Existing sessions may use isolated preview ports/database overrides. Inspect the handoff and running processes before starting services; leave another provider's session and original data/chain intact. To override them, copy `backend/.env.example` to `backend/.env` and `frontend/.env.example` to `frontend/.env.local`, or set variables in the window that runs the service. Variables set in the window win over the files. The backend reads all of its settings in `backend/app/config.py`.

- POLYGON_RPC_URL defaults to http://127.0.0.1:8545; POLYGON_PRIVATE_KEY defaults to public Hardhat test account #0 for local use only.
- CONTRACT_ADDRESS and CHAIN_ID default to the retained deployment file in backend/app/blockchain/AyudaChainRegistry.json.
- DATABASE_URL defaults to backend/ayudachain.db. When preserving an older database, choose a new isolated copy/path instead.
- RECEIPTS_DIR defaults to backend/app/data/receipts; use a separate directory for an isolated test/demo.
- CORS_ORIGINS defaults to exact localhost/127.0.0.1 frontend origins on 3000/3001. A wildcard does not authorize login.
- DEMO_ACCOUNTS_FILE defaults to backend/.demo-accounts.json; SESSION_COOKIE_SECURE defaults false only for loopback.
- NEXT_PUBLIC_API_URL defaults to http://<page host>:8000.

Example: `$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:8000"`. Next.js reads `NEXT_PUBLIC_*` values at build time, so rebuild the frontend after changing it.

Never put a real private key in these variables or in a committed file.

## Start

Start the services in this order. The backend records the first fund release on the chain when it creates the demo data, so the chain and contract must be ready first.

**Window 1: local chain**

```powershell
cd contracts
npx hardhat node --hostname 127.0.0.1 --port 8545
```

Wait for `Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/`.

**Window 2: deploy the contract** (once per chain start)

```powershell
npm --prefix contracts run deploy:local
```

On a fresh chain the address is always `0x5FbDB2315678afecb367f032d93F642f64180aa3`. The script rewrites `shared/contracts/AyudaChainRegistry.json` and `backend/app/blockchain/AyudaChainRegistry.json`; only `deployedAt` changes, so don't commit them. Discard the change with:

```powershell
git restore shared/contracts/AyudaChainRegistry.json backend/app/blockchain/AyudaChainRegistry.json
```

**Window 2: backend**

```powershell
cd backend
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

If `backend/ayudachain.db` is missing or empty, the server creates it with the Typhoon Salinlahi demo batch. Check it with `curl.exe http://127.0.0.1:8000/api/dashboard`, or open http://127.0.0.1:8000/docs to try the API.

**Window 3: frontend**

```powershell
cd frontend
npm run build
npm start
```

Use `npm run dev` instead for live reload. Open http://localhost:3000 for the landing page and http://localhost:3000/dashboard for the demo.

## Stop

Press `Ctrl+C` in each window: frontend, backend, then chain.

If a port is still in use (for example, a window was closed while a server was running), find and stop the process:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 3000,8000,8545 -ErrorAction SilentlyContinue |
  Select-Object LocalPort, OwningProcess
Stop-Process -Id <OwningProcess>
```

Check the process name with `Get-Process -Id <OwningProcess>` before stopping it.

## Reset an isolated demo

A stopped Hardhat chain loses in-memory anchors while SQLite retains records. This can make verification unavailable or unanchored; stored transaction references are not proof of current evidence. The API does not generate placeholder hashes or successful verification fallbacks.

POST /api/demo/reset is disabled with 410. Do not delete the original database or reset another provider's chain to obtain a working preview. For a deliberately fresh synthetic demo, stop only its owned services, select a new DATABASE_URL and RECEIPTS_DIR, and use a separate local chain/contract configuration. Keep the originals and previous deployment artifacts. The seed procedure creates data only in the selected empty database.

If an older database uses the former peso format, preserve it and use a compatible isolated copy/new database. Contract changes need deliberate compatibility checks; anchor reconciliation is unfinished.

## Tests

```powershell
npm --prefix contracts test
cd backend; .venv\Scripts\python test_backend.py; .venv\Scripts\python test_api.py; .venv\Scripts\python test_auth.py; cd ..
cd frontend; npx tsc --noEmit; cd ..
```

Run the contract tests from the repository as shown (or from `contracts/`). Running `npx hardhat test` from the repository root fails with HH1 because no Hardhat project is found there. `test_api.py` uses a temporary database and a fake chain, so it does not need the local chain running. The root `npm test` and `npm run typecheck` scripts use `python3` and `./node_modules/.bin/tsc`, which may not work in PowerShell.

## Known gaps

- Failed anchoring records no fabricated transaction hash. Explicit anchor jobs, safe reconciliation and synchronized recovery remain section 4 of [TODO.md](TODO.md).
- There is no single Windows start script yet.
