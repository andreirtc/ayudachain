# Evaluator deployment preparation

Prepared 2026-10-12 against `151fcf66de6aae6a394b7788b9a5856926507530`. **Draft for the maintainer's decision; no hosted environment has been provisioned.** This supplements the [handoff](evaluator-deployment-handoff.md) and [provider research](evaluator-deployment-research.md). It does not replace the approved PRD, ERD or local evidence ADR.

## Goal, assumptions and recommendation

Give evaluators protected HTTPS access to the complete five-role synthetic workflow, including original uploads, independent review, once-only handover and an actual matching read from the pinned chain. Claimed actors remain impersonable; simulated ID/SMS/clock and unvalidated signatures remain explicit. A working homepage or database health response does not meet acceptance.

Session schedule, concurrency, existing accounts/domain, card acceptance, spending ceiling and data/history requirements remain [pending decisions](#pending-decisions). The recommendation below assumes supervised sessions and a **new synthetic hosted dataset**, while preserving the current local dataset and deployment pins. These are planning assumptions, not authorization to expose services, spend money, install new tooling or discard history.

**First choice for that assumption: one VM running the existing stack and PostgreSQL, with one protected public hostname.** Keep API, frontend, database and chain listeners on loopback. Route browser API requests directly to FastAPI through the same ingress as the frontend. Keep filesystem originals and current database/worker semantics. Use a production Next server and independent process supervision; retain Hardhat as a separately operated session chain.

Oracle Always Free is the first provider to check if card verification and home-region capacity are acceptable. A fixed-price VM with an explicit approved spending ceiling is the fallback if free capacity is unavailable. Account eligibility, actual regional capacity, latency and Linux/ARM compatibility are not proven here. Source details and alternatives are in the research note.

| Approach | Application impact | Principal tradeoff | Decision |
|---|---|---|---|
| One VM + local PostgreSQL + private originals + protected ingress | Retains loopback configuration, purpose grants, session locks and exact-byte storage; deployment configuration supplies the public API URL | Operator owns backups/patches and one failure domain; free VM capacity/reclamation; volatile Hardhat history | Recommended conditionally for supervised sessions |
| Vercel + Neon + VM, as proposed in the handoff | Requires hosted-DB validation in Python and Node, restricted hosted provisioning, direct worker connections and coordinated frontend/API protection | Adds providers while retaining the VM and its chain/originals failure domain; polling consumes Neon compute allowance | Keep as alternative if managed DB/frontend benefits justify those changes |
| Existing operator machine + protected temporary tunnel | Avoids cloud provisioning; needs a same-origin router and verified browser access protection | Operator computer/network must stay available; temporary address and tunnel/session limits; fresh chain readiness still needed | Scheduled-session fallback requiring a complete tunnel/browser probe |

None of these placements makes Hardhat history durable. **Unattended access with verification surviving node/VM restarts requires a separately reviewed chain choice.** Evaluate a durable private EVM or separately authorized testnet against exact pin, receipt/event, nonce and recovery requirements before selecting one. A dump of contract storage alone is not a demonstrated recovery mechanism for this adapter.

## Pending decisions

Owner: the maintainer. Recorded 2026-10-12; all decisions below are **Pending**. The maintainer requested that these choices be documented and that the deployment documents be committed and pushed. That instruction authorizes documentation publication; it does not select an architecture or authorize provisioning, paid resources, new tooling, schema changes or public-blockchain deployment.

| ID | Decision | Status | Information or choice needed | Work that depends on it |
|---|---|---|---|---|
| D-01 | Evaluation access and schedule | Pending | Scheduled supervised sessions or unattended access; evaluation dates, expected concurrent users and availability requirements | Operating schedule, target sizing and availability/recovery acceptance |
| D-02 | Accounts, domain and evaluator access | Pending | Existing provider accounts and domain control; willingness to provide payment details/card verification; intended evaluator access list | Provider eligibility, hostname/access-gate setup and authorized account configuration |
| D-03 | Spending ceiling | Pending | Strictly zero cost or an explicit fixed budget, including domain, backups, taxes and usage; whether a paid VM fallback is acceptable | Provisioning paid resources, subscriptions or chargeable fallback/add-ons |
| D-04 | Chain network and history guarantees | Pending | Private session Hardhat, a tested durable private EVM, or a separately authorized public testnet; required history retention and restart/recovery guarantees | Chain/tooling selection, any nonlocal contract deployment and unattended verification acceptance |
| D-05 | Hosted synthetic dataset | Pending | Fresh synthetic reference records or migration of retained synthetic data; required historical evidence availability | Bootstrap/migration procedure preserving database, original bytes, replay key, exact deployment provenance and unresolved submissions together |
| D-06 | Hosting architecture and access tooling | Pending | Select the one-VM recommendation, proposed split stack or tested session-only fallback; confirm provider/region and approve any new connector/router/EVM tooling | Final deployment configuration, source changes where necessary, tooling installation and opening remote access |

Recommendations and example configuration remain proposals until these decisions are recorded. Continue authorized inspection, research and reversible preparation while decisions are pending; do not treat unanswered choices or publication of this plan as approval. Record each eventual choice, its date and any separate authorization before dependent work.

## What the current code establishes

| Evidence | Consequence for deployment |
|---|---|
| `backend/app/config.py` accepts only loopback PostgreSQL and credential-free loopback HTTP RPC, and Node 22/24 | A single machine preserves these defaults; Neon is a behavior change requiring regression coverage |
| `contracts/scripts/anchor_worker.js` separately rejects non-loopback DB hosts; uses session `SET ROLE`, search path and signer advisory lock | Keep a direct local connection and one controlled signer; avoid transaction pooling |
| `backend/app/database.py` uses purpose-specific DSNs and `SET LOCAL ROLE` | Provision restricted login credentials as well as existing purpose grants; ordinary services must not receive migration-owner credentials |
| `setup_mvp.py` defaults to the `postgres` owner and writes `.env.mvp` with Windows-specific Node location when absent | Supply Linux values before setup; inspect and isolate the generated file before any service launch |
| Python configuration and Node `localConfig()` automatically read repository-root `.env.mvp` | A shared root file containing owner or signer secrets defeats per-service environment separation; runtime root file must not contain those values |
| `frontend/lib/api.ts` embeds `NEXT_PUBLIC_API_URL`, otherwise uses browser hostname on HTTP port 8000 | Set the actual HTTPS origin at build time; startup-only configuration is insufficient |
| `backend/app/main.py` CORS allows only local development origins | Same-origin ingress avoids a new CORS policy; a separate API hostname needs an explicit change |
| `routes_evidence.py` and `services/evidence.py` allow at most 10 MiB of original bytes, check signatures and hash exact originals | Route upload/download directly to FastAPI; preserve multipart overhead, actor header, idempotency header and bytes |
| `local_mvp.py` starts Next in development mode, prepares migrations/seeds and may start a volatile chain | Use separate production services; migrations, seeding and deployment remain explicit operator steps |
| `backup_mvp.py` validates a surviving pinned chain and restricts manifests/bundles to the checkout | Keep a stable absolute checkout/runtime path and test recovery there; a database dump alone cannot restore the chain |

The checkout is an existing linked worktree on `feat/five-role-mvp`; local `main` is `6d92882dcbc4496645b4379561f457d1504aed53`, which predates this MVP baseline. The maintainer authorized committing and pushing these deployment documents on this existing branch on 2026-10-12. Before source implementation, create an isolated branch from `main` and explicitly bring forward the reviewed MVP baseline; do not silently build the older `main` application or disturb this worktree. Documentation publication does not authorize future implementation commits or pushes.

## Reviewable deployment configuration

The following are proposed templates, **not installed or cloud-validated configuration**. Replace the example domain and private placeholders after account/architecture selection. `cloudflared` is new operator tooling and needs discussion under the repository's dependency rule before installation. No new Python/npm dependencies, schema change, contract change or hash-payload change is proposed for the one-VM session path.

Keep a stable checkout at `/opt/ayudachain/mvp` and private runtime state inside its ignored `.runtime/`. Backups must also be copied to separately controlled private storage. Do not publish this directory as a static mount. Provision PostgreSQL 18, locked Python 3.14 dependencies and supported Node 22/24 for the selected VM architecture; verify native wheels and npm optional native packages there.

The service separation is:

| Process | Start command from the checkout | Private environment | Restart policy |
|---|---|---|---|
| API | `.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000` | Runtime + inspection DSNs, schema, originals root, replay key, Node and RPC; no signer/owner | Restart on failure; unavailable chain remains an explicit API result |
| Scheduler | `.venv/bin/python -m backend.app.scheduler` | Runtime DSN, schema, replay key; no signer/owner | Restart on failure; persisted deadlines catch up under existing rules |
| Anchor worker | `/usr/bin/node contracts/scripts/anchor_worker.js` | Worker DSN, schema, RPC, local signer, pinned manifest; no owner | Restart on failure; jobs reconcile persisted submissions |
| Frontend | `/usr/bin/node node_modules/next/dist/bin/next start --hostname 127.0.0.1 --port 3000` from `frontend/` | Production mode; public URL already compiled | Restart on failure |
| Hardhat | `/usr/bin/node node_modules/hardhat/internal/cli/cli.js node --hostname 127.0.0.1 --port 8545` from `contracts/` | Local development network only | **No automatic restart/redeployment after node loss** |
| Tunnel | Approved `cloudflared` binary with private tunnel configuration | Connector credential and Access validation configuration; no app/database secrets | Restart on failure; failure removes remote access |

Use dedicated OS service accounts and root-readable systemd `EnvironmentFile` files under `/etc/ayudachain/`. Separate worker signer access from API/frontend, and provide only the original-file permissions each process needs. Do not run the general local supervisor as a hosted service: it combines startup preparation with owner credentials and runs a development frontend.

Example API/scheduler shared settings, with private credentials supplied separately:

```dotenv
MVP_DATABASE_URL=postgresql://mvp_api_login:REPLACE_WITH_URL_ENCODED_PASSWORD@127.0.0.1:55432/ayudachain_mvp
MVP_SCHEMA=public
MVP_EVIDENCE_ROOT=/opt/ayudachain/mvp/.runtime/originals
MVP_NODE=/usr/bin/node
MVP_RPC_URL=http://127.0.0.1:8545
MVP_COMMAND_DIGEST_KEY=REPLACE_WITH_64_HEX_CHAR_PRIVATE_KEY
```

The API additionally receives `MVP_INSPECTION_DATABASE_URL` for a restricted inspection login. Worker configuration receives `MVP_WORKER_DATABASE_URL`, its local signer and a unique absolute `MVP_DEPLOYMENT_MANIFEST`. Owner/admin DSNs belong only to root-controlled provisioning/backup sessions. Keep root `.env.mvp` absent during service runtime, or demonstrate that it contains only settings safe for every process reading it. Setup automatically creates that file: preserve it in private provisioning storage outside the service checkout after extracting the chosen replay key, before enabling services.

Provision ordinary LOGIN roles without superuser, role/database creation or unrestricted owner membership. Grant only their intended existing `mvp_runtime`, `mvp_worker` or `mvp_inspection` purpose role, with `SET ROLE` permitted. Run explicit migration/grant tooling as the provisioning owner, then validate service permissions using the actual restricted DSNs. The worker login must not have general business mutation rights; purpose roles must retain append-only grants. Existing role creation/grants alone do not prove credential isolation.

Build configuration uses a full source checkout, including the parent `package.json` needed by both `file:..` references:

```sh
export NEXT_PUBLIC_API_URL=https://demo.example.com
export NEXT_TELEMETRY_DISABLED=1
npm --prefix contracts ci
npm --prefix frontend ci
npm --prefix frontend run typecheck
npm --prefix frontend run build
```

`NEXT_PUBLIC_API_URL` contains the origin only; the existing MVP client adds `/api/v1`. It contains no secret. Next.js inlines public variables during build; its [self-hosting documentation](https://nextjs.org/docs/app/guides/self-hosting) supports using a production Node server. Actual DNS/hostname changes therefore require rebuilding and revalidating browser requests.

Proposed named-tunnel ingress routing, preserving the path and validating Access on each application rule:

```yaml
tunnel: REPLACE_WITH_TUNNEL_UUID
credentials-file: /etc/ayudachain/private-tunnel.json
ingress:
  - hostname: demo.example.com
    path: ^/api/v1(/.*)?$
    service: http://127.0.0.1:8000
    originRequest:
      access:
        required: true
        teamName: REPLACE_WITH_ACCESS_TEAM_NAME
        audTag:
          - REPLACE_WITH_ACCESS_APPLICATION_AUDIENCE
  - hostname: demo.example.com
    service: http://127.0.0.1:3000
    originRequest:
      access:
        required: true
        teamName: REPLACE_WITH_ACCESS_TEAM_NAME
        audTag:
          - REPLACE_WITH_ACCESS_APPLICATION_AUDIENCE
  - service: http_status:404
```

Before use, create one Access application covering the entire hostname, restrict it to named evaluator emails, and replace the validation placeholders with its team name and correct audience. The 2026.10.0 connector's [ingress implementation](https://github.com/cloudflare/cloudflared/blob/2026.10.0/ingress/ingress.go) constructs its JWT middleware from each rule's Access block; global defaults alone do not establish enforcement. Validate the pinned installed connector's configuration and every route, not just `/mvp`. Do not expose a second hostname or public ports for API, chain, PostgreSQL, originals, Next or backup directories. Keep provider firewalls closed except approved restricted administration; the tunnel uses outbound connections. YAML parsing does not demonstrate token enforcement.

Forward `X-Demo-Actor-ID` and `Idempotency-Key` unchanged. Keep API and original responses uncached, without CDN rules that override `Cache-Control: no-store`. Browser HTTPS must terminate at the protected ingress. A temporary tunnel is a different preparation path: its single origin needs a tested router/Next rewrite, and email OTP behavior must pass a real multi-page browser session, asset loads and uploads before use.

## Ordered work after decisions

1. **Set the evaluation contract.** Confirm dates, concurrent evaluators, supervised/unattended expectation, chain-history guarantees, budget, accounts/card/domain and fresh-versus-retained data. Select the architecture and record the hosted boundary in a new decision record without rewriting the accepted local ADR.
2. **Prove the selected target.** Verify the actual account's free allowance and capacity before provisioning. Run locked installs/builds on its OS/architecture, check private file fsync/exclusive-write behavior and PDF subprocess extraction, and measure an actual remote upload and API read from evaluator locations. A Windows build does not establish ARM support.
3. **Prepare repeatable configuration.** Create reviewed systemd units and separate private environment templates, ingress/token-validation configuration, restricted DB role provisioning, explicit bootstrap and operator commands. Add no automatic migration, seed/reset or replacement pin to service restart. Installing the connector or selecting another EVM needs maintainer authorization first.
4. **Bootstrap an authorized fresh VM privately.** Migrate the approved schema, apply grants, compile the registry, start a loopback node, create a unique manifest through `deploy_evidence.js`, check it, then seed only synthetic references. Preserve generated artifact provenance. Do not copy local runtime credentials, claimed private data or historical manifests into a new chain and call it migration.
5. **Validate before opening access.** Run target-layer checks and the acceptance cases below against controlled synthetic data. Provisioning success, HTTP health and historical test results are separate evidence. Retain exact command results and classify unrun/failed checks.
6. **Open the authorized protected endpoint.** Test an invited evaluator, an uninvited user and origin bypass, including API/original endpoints and unknown routes. Give evaluators clear synthetic-only/shared-state/session instructions. Keep claimed actor labels explicit after the outer access gate.
7. **Operate and recover deliberately.** Back up quiesced application state while the pinned chain survives; retain database, originals, replay key and exact manifests together. Test application-service restart without restarting Hardhat. Node or VM restart is declared chain loss for this path, not restoration of old evidence. Any new session chain/namespace is a separate deliberate operation with prior uncertainty resolved; retain old history and pins.
8. **Publish acceptance evidence and cost controls.** Record URLs, commit, exact tests, known limits, operator start/stop/recovery/teardown instructions, storage/backup checks and quota usage. Commit/push only if requested. Paid fallback requires a concrete approved ceiling before creating resources.

## Regression and remote acceptance coverage

There are no application behavior changes in this preparation, so no new behavior tests are claimed. Implement the following meaningful regressions with any selected configuration/routing/provisioning change; a table is **planned coverage**, not passing evidence.

| Boundary | Required failure/result | Test placement / execution |
|---|---|---|
| Configuration | Public RPC stays rejected; unsupported Node and missing DB remain explicit; selected public API origin reaches `/api/v1` over HTTPS | Preserve `backend/tests/test_preflight.py`; add configuration regressions only for introduced behavior |
| Service credentials | Runtime cannot edit/delete immutable audit/history; worker cannot approve/pay; inspection cannot mutate business records; ordinary logins cannot become owner | Real PostgreSQL tests with the intended LOGIN roles; verify raw credentials as well as `SET ROLE` |
| Ingress/access | Invited user completes all API calls; no credential gives Access refusal; wrong audience rejected; all public-origin bypasses refused | Real protected browser and direct HTTP probes, including original download and unknown paths |
| Files | 10 MiB valid original uploads/downloads byte-identically; oversize rejected; unauthorized actor denied; missing/corrupted original explicit | Extend/run evidence privacy/integrity tests through actual ingress; verify multipart overhead and private storage |
| Browser actor context | Delayed former-actor reply cannot populate new view; scoped queues, outcomes and originals remain role-appropriate | Existing actor-switch, verification and evidence privacy coverage through hosted URLs |
| Five-role workflow | Registration -> upload -> claim -> independent review -> calculation/publication -> assigned session -> authorization -> once-only handover -> private answer -> Auditor proof | Complete real API/browser journey with actual pinned chain, including assisted path |
| Payout/recovery | Lost response/idempotent retry and concurrent handover yield one recorded handover and unchanged paid amounts | Existing payout/journey races and actual worker fault coverage, sequential on a separate fault node/database |
| Verification | Actual current match is Verified; mismatch, absent, unreachable, evidence missing/corrupt and lost deployment are explicit | Existing integrity/protocol tests plus signer-free independent proof; never infer from receipt/health/history alone |
| Process lifecycle | API/worker/scheduler/Next restart retains DB/files/replay and recovers jobs; Hardhat loss cannot replace pins or claim historical match | Real owned-process restart/fault probes; node-loss scenario on an isolated deployment |
| Backup/restore | Exact originals/manifests/key and DB restore against surviving chain; lost chain fails explicitly | Existing backup/checkpoint/restore tests adapted only if selected storage/layout changes |
| Camera/manual lookup | Physical supported device decodes over HTTPS; denial/no decoder/manual reference work | Actual hardware acceptance; mocked browser decoding does not prove device support |
| Provider limits | Recovery, cold start if applicable, quota exhaustion, reboot/idle reclamation and maintenance expectations disclosed | Account metrics/operator drill; do not manufacture traffic to avoid sleep/reclamation |

For current full-layer checks use [CONTRIBUTING](../../CONTRIBUTING.md) and [local setup](../guides/local-mvp.md). The 8555 fault node and a separate test database are prerequisites; run fault suites sequentially. Existing browser reset steps retain history but modify the evaluation namespace: use a separate validation deployment, not an active evaluator session.

## Preparation evidence and limits

- Inspected actual baseline and source boundaries. Current listeners are loopback 3000, 8000 and 55432. Chain 8545 and fault chain 8555 are absent. No service was stopped, reset or redeployed for this preparation.
- Live `/api/v1/health` reports database ready, chain/storage `not_checked`, claimed/unverified actors, pending authentication, simulated business clock/ID/SMS and unvalidated signatures. This is not chain acceptance.
- Existing preflight suite: **4 passed in 0.023 seconds**, including public-RPC rejection, missing-PostgreSQL rejection, unsupported Node and repeatable local configuration.
- A clean `git archive HEAD` probe contains tracked source only, without current `.env.mvp`, runtime pins or installed modules. Frontend and contract locked installs passed using Node `v22.23.3` on Windows. Frontend TypeScript and production build both exited 0; all nine static pages generated. Existing build configuration skips ESLint, so lint is not claimed. The build used the illustrative `https://demo.example.com` API origin; that domain was not provisioned or contacted as an application endpoint.
- Clean-layout contract/protocol suite: **23 passed in 4 seconds**, using the test runner's own ephemeral network. This did not start/reset either persistent evaluation/fault node and is not hosted-chain acceptance.
- Local probe outputs are retained under `.tmp/evaluator-clean-build-41706d6d812e43168cfeb0eb0b980d76/`: `probe.json`, `contracts-probe.json` and per-command logs. They are operator artifacts, not source fixtures or remote deployment evidence. The successful full-source build establishes that `file:..` can work in this layout; a Vercel-specific root/build context is still untested.
- Linux/ARM, VM capacity, protected external requests, restricted hosted login provisioning, storage/chain recovery, five-role hosted workflow, physical camera and billing/account controls have **not** been validated. WSL is not installed on this machine; no cloud credentials or account access are assumed.

Provider facts belong to the cited research note. This draft describes proposed work only; implemented local behavior and earlier validation remain documented in the handoff and validation ledger.
