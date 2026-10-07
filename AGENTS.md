# AGENTS.md

Rules for any AI agent working in this repository, whoever is driving it. A human maintainer's direct instruction outranks this file; this file outranks an agent's defaults.

AyudaChain is a tamper-evident trail for Philippine disaster-relief payouts: private records off-chain, receipt hashes anchored on-chain, public verification. Its whole value is that a "verified" result can be trusted. Treat every change through that lens.

## Integrity invariants

These hold in every change. If a task seems to require breaking one, stop and ask the maintainer.

1. **Fail closed.** A record is reported as verified only when a hash was read from the chain and matched. Chain unreachable, record absent, or anchoring failed are each reported as their own explicit state.
2. **Real or labelled.** A transaction hash, on-chain hash, or verification result shown to a user comes from the chain. Anything simulated is produced by a clearly named demo path and labelled as simulated in the UI and the API response.
3. **Humans decide.** Duplicate and anomaly detection flags records for review. Approval, rejection and deletion are human actions recorded in `audit_events`.
4. **Audit trail is append-only.** Every state change to a batch, allocation, beneficiary or distribution writes an `audit_events` row. Existing rows are never edited or deleted outside the demo reset.
5. **Personal data stays off-chain.** Only opaque IDs, amounts and hashes go on-chain. Names, contact numbers and receipt contents stay in the database.
6. **Synthetic data only.** Seeds, fixtures, tests and docs use invented people and `DFC-2026-XXXX` style identifiers.
7. **Docs match code.** A feature is described as implemented only if it is. Mark simulated or planned features as such in the README and docs in the same change that touches them.

## Known state (read before trusting the code)

The current code violates some invariants. These are defects to fix, not patterns to copy.

- `backend/app/services/blockchain.py` fabricates transaction hashes and returns `matched: True` when the chain call fails. Violates 1 and 2.
- `frontend/app/verify/page.tsx` fakes the fraud scenarios with hardcoded hashes on the client. Violates 2.
- Offline mode on the distributions page is a UI toggle; nothing is queued or synced. The README overstates it. Violates 7.
- Roles are a `localStorage` value. The API has no authentication, so role checks in the UI protect nothing.
- Two backends exist. `backend/server.py` (standard library) is the one that runs and is tested. `backend/app/main.py` (FastAPI) with `models/`, `schemas/`, `database.py` and `seed_demo.py` is not run and has drifted. Confirm with the maintainer which one a task targets before editing either; change only that one.
- The private key and contract address defaults in config are the public Hardhat development values. They are safe locally and must never be used on a public network.

## Working rules

- **Scope.** Do what the task asks. Report unrelated problems you find instead of fixing them in the same change.
- **Ask first** before: adding a dependency, changing the database schema, changing the contract's storage or public functions, changing the receipt hash payload in `hasher.py`, deleting a module, or deploying to any network other than the local node.
- **Hash payload and contract are compatibility surfaces.** Changing either invalidates previously anchored records. Such a change needs a decision record in `docs/adr/` and updated tests on both sides.
- **Tests.** Behaviour changes come with a test that fails without the change. Run the suites for the layers you touched and report the real result, including failures and anything you could not run.
- **Secrets.** Keep real keys and RPC credentials in `.env`, which is ignored. Never print, commit or paste them.
- **Git.** Branch from `main`; follow the branch naming and commit format in `CONTRIBUTING.md`. Commit and push only when the user asks. Leave other people's branches, stashes and worktrees alone.
- **Generated files.** `shared/contracts/AyudaChainRegistry.json` and `backend/app/blockchain/AyudaChainRegistry.json` are written by `contracts/scripts/deploy.js`. Regenerate them by deploying; do not hand-edit.

## Environment gotchas

Commands live in the root `package.json`; read it rather than this file. What it does not tell you:

- Root scripts call `python3`. On Windows use `python` (for example `python backend/test_backend.py`).
- `start_ayudachain.sh` depends on `/proc` and `pkill`, so it works on Linux and WSL only. Elsewhere start the three services separately as described in `CONTRIBUTING.md`.
- Contract tests and the frontend typecheck need `npm ci` in `contracts/` and `frontend/` first.
- The backend reaches the chain by spawning `node contracts/scripts/blockchain_client.js`, which needs compiled artifacts (`npm run compile:contracts`) and a running node on port 8545.
- Ports: frontend 3000, backend 8000, chain 8545.

## Where the context lives

Read the document that matches your task before designing or changing behaviour. If a listed file is absent it has not been written yet: say so and ask, rather than inferring requirements from the code.

| When you are... | Read |
|---|---|
| Deciding what to build, or whether something is in scope | `docs/product/prd.md` |
| Checking what the redesign has settled and what is still open | `docs/product-ideation/decisions-2026-10-08.md` |
| Discussing or extending the redesign's roles | `docs/product-ideation/roles/<role>.md` |
| Discussing Finance Officer screens, or needing the audit rules behind that role | `docs/product-ideation/drafts/` |
| Adding or moving a page or route in the code as it is today | `docs/product/sitemap.md` |
| Changing a screen's steps or permissions in the code as it is today | `docs/product/user-flow.md` |
| Moving data between frontend, backend, chain or files | `docs/system/dfd.md` |
| Touching tables, columns or relationships | `docs/system/erd.md` |
| Orienting on the overall design | `docs/system/architecture.md` |
| Changing an endpoint or its payload | `docs/system/api-contract.md` |
| Changing the contract or how it is called | `docs/system/blockchain-spec.md` |
| Checking why a past decision was made, or recording a new one | `docs/adr/` |

When code and a context document disagree, flag the conflict to the maintainer. Update the document in the same change as the behaviour it describes.

## Current product and ideation

Two folders describe two different things. Know which one you are reading.

- **`docs/product/` is the existing product.** `sitemap.md` and `user-flow.md` describe the code as it runs today, with three roles (Public Citizen, Barangay Officer, Auditor) and one hardcoded disaster.
- **`docs/product-ideation/` is a redesign still being worked out.** It reorganises the product around a DSWD Field Office, with roles that would replace the current three. The whole picture is not final.

Treat ideation as context, not as a specification. Build nothing from it until the maintainer says a part is ready to build, even where an item is marked **Decided**: that tag records what was settled in discussion, and later discussion may still change it. The other tags (**Proposed**, **Default**, **Later**) and anything under open points are less settled still.

A disagreement between an ideation file and the current code is expected and is not a conflict to flag. When a task touches behaviour the ideation would change, mention it to the maintainer so new work does not head the opposite way.
