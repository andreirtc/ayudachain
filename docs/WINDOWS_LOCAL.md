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
```

`backend/server.py` uses only the Python standard library. `backend/requirements.txt` is for the separate FastAPI app and is not needed for this guide.

## Configuration

There is no `.env.example` yet. The defaults below work for the local chain, so no configuration is needed. To override them, set them in the window that runs the service.

| Variable | Used by | Default |
| --- | --- | --- |
| `POLYGON_RPC_URL` | backend | `http://127.0.0.1:8545` |
| `POLYGON_PRIVATE_KEY` | backend | Hardhat test account #0 (public, local only) |
| `CONTRACT_ADDRESS` | backend | `0x5FbDB2315678afecb367f032d93F642f64180aa3` |
| `NEXT_PUBLIC_API_URL` | frontend | `http://<page host>:8000` |

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
python server.py 8000
```

If `backend/ayudachain.db` is missing or empty, the server creates it with the Typhoon Salinlahi demo batch. Check it with `curl.exe http://127.0.0.1:8000/api/dashboard`.

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

## Reset

The Hardhat chain keeps everything in memory, so stopping it erases all anchored records. The SQLite database keeps its records, including transaction hashes that no longer exist on the new chain. Always reset both together.

1. Stop the frontend, backend, and chain.
2. Delete the database: `Remove-Item backend/ayudachain.db`
3. Start the chain, deploy the contract, then start the backend and frontend as above.

The dashboard's demo reset button (`POST /api/demo/reset`) only reseeds the database. It does not reset the chain, so the chain keeps records from earlier runs. Use the full reset above when you need the two to match.

## Tests

```powershell
npm --prefix contracts test
python backend/test_backend.py
cd frontend; npx tsc --noEmit
```

Run the contract tests from the repository as shown (or from `contracts/`). Running `npx hardhat test` from the repository root fails with HH1 because no Hardhat project is found there. The root `npm test` and `npm run typecheck` scripts use `python3` and `./node_modules/.bin/tsc`, which may not work in PowerShell.

## Known gaps

- If the chain is not running when the backend creates or records data, the backend currently stores a generated placeholder hash instead of failing. Section 4 of [TODO.md](TODO.md) tracks removing this.
- There is no single Windows start script yet.
