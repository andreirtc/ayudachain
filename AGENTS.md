# AGENTS.md

Rules for any AI agent working in this repository, whoever is driving it. A human maintainer's direct instruction outranks this file; this file outranks an agent's defaults.

AyudaChain is a tamper-evident trail for Philippine disaster-relief payouts: private records off-chain, receipt hashes anchored on-chain, public verification. Its whole value is that a "verified" result can be trusted. Treat every change through that lens.

## Screen storytelling plan handoff

At the start of a new agent session on this branch, read [the screen storytelling implementation plan](docs/implementation/2026-10-13-screen-storytelling-plan.md) and briefly link it in your first user-facing response so the maintainer knows to review it. Before changing MVP navigation, dashboards, screen copy or transaction flows, use the plan alongside the current PRD and user flow, and check which phases are already implemented. The plan is proposed work; reading this handoff does not authorize implementation. Follow the user's requested scope and any subsequent explicit implementation authorization.

## Integrity invariants

These hold in every change. If a task seems to require breaking one, stop and ask the maintainer.

1. **Fail closed.** A record is reported as verified only when a hash was read from the chain and matched. Chain unreachable, record absent, or anchoring failed are each reported as their own explicit state.
2. **Real or labelled.** A transaction hash, on-chain hash, or verification result shown to a user comes from the chain. Anything simulated is produced by a clearly named demo path and labelled as simulated in the UI and the API response.
3. **Humans decide.** Duplicate and anomaly detection flags records for review. Approval, rejection and deletion are human actions recorded in `audit_events`.
4. **Audit trail is append-only.** Every state change to a batch, allocation, beneficiary or distribution writes an `audit_events` row. Existing rows are never edited or deleted. MVP evaluation reset retires the namespace and retains history.
5. **Personal data stays off-chain.** Only opaque IDs, amounts and hashes go on-chain. Names, contact numbers and receipt contents stay in the database.
6. **Synthetic data only.** Seeds, fixtures, tests and docs use invented people and `DFC-2026-XXXX` style identifiers.
7. **Docs match code.** A feature is described as implemented only if it is. Mark simulated or planned features as such in the README and docs in the same change that touches them.

## Known state (read before trusting the code)

The five-role MVP is implemented for local synthetic evaluation. Authentication and real-household readiness remain Pending. Current validation and unresolved tooling limitations are recorded in `docs/implementation/validation.md`.

- `backend/app/main.py` is the authoritative FastAPI/PostgreSQL MVP backend, explicitly approved by the maintainer. The legacy `backend/server.py` and SQLite stay separate, preserved and receive no MVP dual writes.
- Chain verification fails closed in the MVP and the repaired legacy adapter. `/verify` contains no fabricated fraud/hash controls. The original receipt hasher and original contract/artifacts remain unchanged.
- `/mvp` uses multiple selectable claimed/unverified actors and a stored-scope identity-resolution boundary. Anyone can impersonate another active actor. These are workflow rules and projections, not secure authorization, operational privacy or authenticated accountability. There is no sign-in gate.
- National ID checks, notice SMS and any accelerated business clock are explicitly labelled simulations. Signatures are `not_validated`. Core records, originals, calculations, handovers, chain submissions/reads and recovery are actual.
- Offline payout is unavailable. Retained legacy screens are separate historical interfaces; their old offline toggle is not a queue or an MVP capability.
- The maintainer approved the PRD/ERD schema and local migrations, the plan's dependencies, the separate versioned protocol/registry and local deployment through scripts. See the accepted compatibility ADR. Changes beyond that approved scope still require discussion.
- The public Hardhat development key is local-only. No public-network deployment is authorized.

## Working rules

- **Scope.** Do what the task asks. Report unrelated problems you find instead of fixing them in the same change.
- **Ask first** before: adding a dependency, changing the database schema, changing the contract's storage or public functions, changing the receipt hash payload in `hasher.py`, deleting a module, or deploying to any network other than the local node.
- **Hash payload and contract are compatibility surfaces.** Changing either invalidates previously anchored records. Such a change needs a decision record in `docs/adr/` and updated tests on both sides.
- **Tests.** Behaviour changes come with a test that fails without the change. Run the suites for the layers you touched and report the real result, including failures and anything you could not run.
- **Secrets.** Keep real keys and RPC credentials in ignored `.env` or `.env.mvp` configuration. Never print, commit or paste them.
- **Git.** Branch from `main`; follow the branch naming and commit format in `CONTRIBUTING.md`. Commit and push only when the user asks. Leave other people's branches, stashes and worktrees alone.
- **Generated files.** `shared/contracts/AyudaChainRegistry.json` and `backend/app/blockchain/AyudaChainRegistry.json` are written by `contracts/scripts/deploy.js`. Regenerate them by deploying; do not hand-edit.

## Environment gotchas

Commands live in the root `package.json`; read it rather than this file. What it does not tell you:

- Root scripts call `python3`. On Windows use `python` (for example `python backend/test_backend.py`).
- `start_ayudachain.sh` depends on `/proc` and `pkill`, so it works on Linux and WSL only. Elsewhere start the three services separately as described in `CONTRIBUTING.md`.
- Contract tests and the frontend typecheck need `npm ci` in `contracts/` and `frontend/` first.
- The MVP uses the PostgreSQL durable worker and pinned evidence registry; the legacy backend uses `contracts/scripts/blockchain_client.js`. Both need actual local-chain tooling. See `docs/guides/local-mvp.md` for setup, migrations, supervision, isolated fault tests and recovery.
- Ports: frontend 3000, backend 8000, chain 8545; isolated fault node 8555; owned local PostgreSQL 55432. Use supported Node 22/24, not system Node 25. Stop the owned frontend tree before npm ci on Windows.

## Where the context lives

Read the document that matches your task before designing or changing behaviour. If a listed file is absent it has not been written yet: say so and ask, rather than inferring requirements from the code.

| When you are... | Read |
|---|---|
| Deciding what to build, or whether something is in scope | `docs/product/prd.md` |
| Checking what the redesign has settled and what is still open | `docs/product-ideation/decisions-2026-10-08.md` |
| Discussing or extending the redesign's roles | `docs/product-ideation/roles/<role>.md` |
| Discussing the DSWD Officer's funds screens, or needing the audit rules behind them | `docs/product-ideation/drafts/` |
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

`docs/product/prd.md` and `docs/system/erd.md` are the approved normative MVP requirements/model. Current sitemap, user flow and system documents describe implemented behavior. The implementation ledger and validation report record actual outcomes. Original product/system guides are preserved under `docs/legacy-documentation/`.

`docs/product-ideation/` is historical discussion, preserved unchanged. The maintainer explicitly authorized implementing the complete five-role journey using the 2026-10-10 plan, PRD and ERD. This does not authorize unrelated Proposed/Default/Later ideas or future integrations. New behavior outside the approved scope requires a new decision; do not silently turn historical proposals into requirements.
