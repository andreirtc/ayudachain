# Evaluator demo deployment handoff

Prepared 2026-10-12. Source baseline: commit `151fcf6` on `feat/five-role-mvp`, pushed to `https://github.com/andreirtc/ayudachain`. This document records a proposed deployment approach, not a completed deployment or a settled architecture.

Follow-up preparation is recorded in the [deployment plan](evaluator-deployment-plan.md) and [provider research](evaluator-deployment-research.md). The plan's [pending-decision register](evaluator-deployment-plan.md#pending-decisions) is the current record of unresolved maintainer choices. Committing and pushing these documents is authorized; deployment decisions remain Pending.

## Objective and next-agent instruction

Deploy a remotely accessible AyudaChain demo for evaluators using synthetic records, preferably within free-tier allowances. Evaluators should complete the actual five-role workflow, upload invented evidence, perform a once-only payout and inspect real chain commitments. Keep claimed actor selection and simulation labels explicit.

**Improve the deployment approach before implementing it.** Treat the services below as candidates. Find a simpler, more reliable or less expensive way to host the complete system if one exists. Compare at least the proposed VM approach and one credible alternative. Prefer fewer infrastructure components and smaller code changes when they preserve integrity and the evaluator experience. Check current official provider documentation; distinguish verified support from assumptions and test the assumptions that decide the architecture.

Evaluate total requirements rather than whether the homepage loads: continuous processing, database permissions and locks, private original bytes, blockchain history across restarts, access protection, cold starts, regional latency, account eligibility, quota exhaustion, recovery, and operator workload. Compare recurring free allowances with time-limited credits. State account/card/domain requirements and possible charges. Avoid architectures that rely on artificial traffic to defeat provider sleep policies.

Produce a concrete deployment plan, prepare its configuration and regression coverage, and resolve the decision points below with the maintainer before actions that require new authorization. The user requested this handoff; this document does not itself authorize paid resources, dependency/schema changes or deployment to a public blockchain. Continue independently with inspection, research and reversible preparation that existing instructions authorize.

## Read first

- `AGENTS.md`: scope, approval boundaries, append-only audits, synthetic data, fail-closed chain verification and Git rules.
- `docs/product/prd.md` and `docs/system/erd.md`: approved workflow/model.
- `docs/guides/local-mvp.md`: provisioning, supervision, pinned deployments, backup and recovery. Some prose predates the commit and stopped-node state; inspect runtime before following startup instructions.
- `docs/implementation/bring-forward-usability.md` and `docs/implementation/validation.md`: delivered features and actual validation limits.
- `docs/adr/2026-10-10-mvp-evidence-protocol-and-registry.md`: protocol/deployment compatibility.
- `docs/system/api-contract.md` and `CONTRIBUTING.md`: API and repository conventions.

Workspace used for the implementation: `C:/Users/Yushin/orca/workspaces/ayudachain/mvp-full`. The `main-2` checkout was reference material; preserve it. Temporary `.tmp/` helpers and `.impeccable/` review artifacts remain local and were excluded from the commit. Runtime configuration, database, originals and manifests are ignored and are not supplied by a Git clone.

## Verified implementation state

The authoritative backend is FastAPI/PostgreSQL in `backend/app/main.py`. Legacy SQLite code stays separate. The frontend is Next.js with five dedicated role workspaces. The evidence registry and actual chain worker use Node/Hardhat. Authentication remains Pending: anyone with demo access can select and impersonate an active actor. Access protection around the demo limits who enters; it does not authenticate the claimed workflow actors.

The seven usability additions are implemented: scoped queues, frozen duplicate review, Filipino guidance, operations table, contextual evidence, staged CSV intake and QR/manual session lookup. Filipino copy has not received native-speaker review. National ID and SMS are labelled simulations; signatures are `not_validated`.

Recorded usability validation: 21 backend tests, 12 browser tests, the existing workspace regression, TypeScript and production build passed. ESLint was skipped by existing build configuration. Five existing chain-dependent checks/review cases errored with `chain_unreachable`; current published-session lookup, advanced operations totals and full chain-backed journeys still need fresh validation. Physical camera decoding was not tested.

At the last runtime inspection, frontend 3000, API 8000 and PostgreSQL 55432 were listening on loopback. Chain ports 8545/8555 were absent. Inspect again; process IDs and readiness are not durable facts. A health reply reports chain/storage as `not_checked`, so HTTP health alone is not deployment acceptance.

## Candidate services and checked limits

Provider facts below were checked against official sources on 2026-10-12. Recheck before provisioning and verify the actual account's allowances.

| Requirement | Candidate | Verified allowance or constraint | Application implication |
|---|---|---|---|
| Frontend | Vercel Hobby | Free plan restricted to personal, noncommercial use | Verify evaluator project eligibility; configure the Next.js build and API routing. |
| Database | Neon Free | 1 GB Postgres storage and 100 CU-hours/project/month; 6-hour instant restore window | Preserve grants and use direct connections initially. This is a quota, not unlimited continuous database compute. |
| API and continuous processes | Oracle Cloud Always Free VM | ARM allocation equivalent to 2 OCPUs/12 GB RAM; 200 GB combined boot/block storage | Candidate for FastAPI, Node worker and Python scheduler. Verify ARM/runtime compatibility and available home-region capacity. Idle instances may be reclaimed. |
| Private files | VM disk | Fits existing filesystem interface | Maintain separate backups. Does not make Hardhat state persistent. |
| Alternative private files | Neon Object Storage or Cloudflare R2 | Neon: 5 GB/project; R2 Standard: 10 GB-month, 1M Class A and 10M Class B operations/month, free egress | Requires a storage adapter, verified access boundaries, exact-byte hashing and backup coverage. R2 requires subscription checkout and bills usage outside included allowances. |
| Public testnet RPC | Alchemy Free | 30M compute units/month, 15 requests/second; Sepolia endpoints | RPC access does not fund gas or execute our worker. Obtain test ETH and approve a new testnet deployment path. |
| Evaluator access | Cloudflare Access Free | Up to 50 users | Protect both frontend and API; verify that the origin cannot bypass protection. Domain/account prerequisites need confirmation. |

Render Free sleeps after 15 minutes of inbound inactivity and loses local files on restart/redeploy/sleep. It has no persistent disks or free dedicated background-worker tier. Koyeb Free sleeps after one hour, has no persistent volumes and cannot be a Worker Service. These can host a redesigned request-driven API, but they are weak fits for our existing continuous processes and volatile blockchain node. Do not describe them as unchanged full-stack deployments.

## Code-specific blockers

| Area | Inspect | Required preparation |
|---|---|---|
| Browser API URL | `frontend/lib/api.ts`, `frontend/lib/mvp-client.ts` | Current fallback is `http://<browser hostname>:8000`. Set a real HTTPS API URL before building or add a same-origin proxy. Public URL variables contain no secrets. |
| Monorepo build | `frontend/package.json`, lockfiles, root `package.json` | Frontend has `ayudachain: file:..`. Verify Vercel project root/build context can access the parent package. Test clean installs/builds from the deployed layout. |
| CORS/access | `backend/app/main.py` | Existing allowed origins are localhost only. Use explicit deployed origins or a proxy; ensure evaluator protection covers API and original downloads. |
| Hosted database | `backend/app/config.py`, `contracts/scripts/anchor_worker.js` | Current supervisor configuration and worker reject non-loopback databases. Add explicit hosted-demo validation with TLS while preserving local-only defaults and blockchain restrictions. |
| Database permissions | `backend/app/database.py`, `backend/scripts/setup_mvp.py` | Preserve `mvp_runtime`, `mvp_worker`, `mvp_inspection`, grants and `SET ROLE` permissions. Adapt local-admin provisioning to Neon. Do not deploy ordinary services with unrestricted migration-owner permissions. |
| Connection pooling | `backend/app/database.py`, `contracts/scripts/anchor_worker.js` | Worker uses session `SET ROLE`, `SET search_path` and session advisory locks. Use a direct Neon connection for worker/migrations/backup. API pooling requires an explicit review of session settings and role boundaries before enabling transaction pooling. |
| Files | `backend/app/services/evidence.py` | Current private originals use filesystem writes, exclusive creation and exact-byte hashes; PDF extraction runs a subprocess. Choose a persistent volume or implement a tested private object-storage adapter. |
| Jobs | `backend/app/scheduler.py`, `contracts/scripts/anchor_worker.js` | Both poll every two seconds. Provide supervision and retain durable job state. Consider bounded/request-driven processing only after proving timeout, once-only handover and nonce/recovery behavior. |
| Chain | `contracts/scripts/lib/local_config.js`, `deploy_evidence.js`, read/check scripts | Loopback RPC, chain ID 31337 and local confirmation policy are intentional. Testnet support needs explicit configuration, dedicated signer, pinned manifests, confirmation/reorg handling and an ADR as applicable. |
| Backup | `backend/scripts/backup_mvp.py` | Local tooling assumes local database creation/restore and a surviving pinned chain. Adapt and test hosted restoration; a Neon branch/restore does not restore files or blockchain state. |

Our API accepts evidence up to 10 MiB. Vercel Functions have a 4.5 MB request/response payload limit, so placing the API or large-file proxy there requires a separate upload/download strategy. FastAPI itself is supported on Vercel, but it becomes a function with bounded invocation duration; that does not host the current infinite worker/scheduler loops unchanged.

Neon's 100 CU-hours cover approximately 400 active hours at 0.25 CU. Continuous two-second polling can keep compute awake and consume the allowance before a full month. For scheduled evaluation, explicitly start/stop processing with clear pending-state behavior. For unattended hosting, design and validate a quota-compatible processing approach; merely increasing polling from two seconds to another interval below the idle timeout will not necessarily permit scale-to-zero.

## Blockchain decision

**Private chain:** run existing Hardhat on the VM for supervised sessions. Keep RPC and the local signing key private. Hardhat state is volatile even on a persistent VM disk; node loss must remain explicit. Never remap old pins or present newly deployed chain data as verification of old records. Define restart/recovery expectations before presenting this as an unattended demo.

**Public testnet:** investigate a currently supported EVM testnet through Alchemy or another verified free RPC provider. Use a new dedicated signer and a separate pinned deployment/namespace; keep historical local evidence intact. Label the network as testnet. Test RPC throttling, unavailable gas, delayed mining, uncertain submissions and confirmation/reorg policy. The existing public Hardhat key is local-only. AGENTS.md requires discussion before any nonlocal network deployment; research is not authorization to deploy a contract.

**Better alternative:** investigate a private EVM with durable state if it reduces operational risk without requiring a public testnet. Establish compatibility and crash recovery experimentally. Adding tooling/dependencies or changing protocol/contract surfaces follows existing approval rules.

## Proposed starting architecture and pending decisions

Starting candidate: Vercel frontend; Neon database; one Oracle VM for FastAPI, worker, scheduler and private original files. Keep the chain private for supervised evaluations initially. This minimizes backend restructuring, subject to VM availability, platform compatibility and defined chain recovery.

The starting candidate has not been selected. Subsequent research recommends one VM conditionally for supervised sessions; that is also a proposal. The following choices are **Pending**, with details and dependent work in the [decision register](evaluator-deployment-plan.md#pending-decisions):

- **D-01:** Evaluation access, schedule, concurrency and availability.
- **D-02:** Existing accounts/domain, payment verification and evaluator access.
- **D-03:** Spending ceiling and paid fallback acceptance.
- **D-04:** Chain network, retained history and restart/recovery guarantees.
- **D-05:** Fresh synthetic dataset or retained-data migration with originals, replay key and exact deployment provenance.
- **D-06:** Final hosting architecture, provider/region and new access/chain tooling.

Ask only for decisions that block progress; continue independent preparation while awaiting answers. Do not assume cloud account access or credentials exist. Keep secret values in ignored configuration/provider secret stores and never include them in the handoff or browser variables.

## Execution and acceptance

1. Inspect the baseline and resolve code/document disagreements. Verify current pricing, eligibility, capacity, runtime versions and account access. Present the comparison and select the deployment architecture with reasons.
2. Record the hosted-demo decision and boundaries. Prepare repeatable provisioning/build/service configuration, explicit migrations/grants, HTTPS routing and restricted evaluator access. Preserve current integrity invariants and local development behavior.
3. Add meaningful regressions for configuration, role permissions, file access and any job/storage changes. Run touched-layer suites and a clean deployment build. Report real failures and unrun checks.
4. Provision authorized resources, keep secrets private, use a fresh deployment identity where needed and retain historical pins. Verify a deployment restart without lost files or misleading chain results.
5. Exercise all five roles remotely: registration, original upload, claim, independent review, entitlement calculation/publication, assigned session, authorization, once-only handover, private answer and Auditor evidence verification. Test lost reply/retry and concurrent handover. Verify a real chain read before claiming Verified.
6. Test unreachable chain, missing/mismatched evidence, former-actor responses, private outcome restrictions and authorized original reads. Validate HTTPS camera behavior on an actual supported device and manual fallback.
7. Verify backup/restore, process restart, quota/cold-start behavior and access-gate bypass resistance. Give evaluators synthetic-only instructions and clear shared-state guidance.
8. Deliver working URLs, deployment commit, exact check results, remaining limits, operator start/stop/recovery commands and teardown/cost controls. Commit/push further changes only under the user's applicable authorization; do not infer future authorization from the already completed baseline push.

Acceptance requires a complete working remote journey with honest failure states. A successful frontend build, HTTP health response or static screenshot is insufficient.

## Official sources

- [Vercel Hobby eligibility](https://vercel.com/docs/plans/hobby), [FastAPI runtime](https://vercel.com/docs/frameworks/backend/fastapi), [function limits](https://vercel.com/docs/functions/limitations).
- [Neon October 2026 free-tier update](https://neon.com/blog/neon-free-plan-1-gb-per-project), [roles](https://github.com/neondatabase/website/blob/main/content/docs/manage/roles.md), [direct versus pooled connections](https://github.com/neondatabase/website/blob/main/content/docs/connect/connection-pooling.md).
- [Oracle Always Free resources, capacity and reclamation](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm).
- [Cloudflare R2 pricing](https://developers.cloudflare.com/r2/pricing/), [subscription prerequisites](https://developers.cloudflare.com/r2/get-started/), [Access/free plan](https://www.cloudflare.com/plans/).
- [Alchemy pricing](https://www.alchemy.com/pricing), [Sepolia RPC](https://www.alchemy.com/rpc/ethereum-sepolia).
- [Render Free limits](https://render.com/docs/free), [Koyeb Free instance limits](https://www.koyeb.com/docs/reference/instances).
