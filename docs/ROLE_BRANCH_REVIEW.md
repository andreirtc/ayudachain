# Groupmate role/UI review

Reviewed 2026-10-12 against stack head `5e5c2c41871d08b01100c35b570b17e19bda315b` (PR #15). This is source and compatibility review, not a fresh runtime validation of the groupmate MVP.

## Branch identity

Configured origin is `https://github.com/andreirtc/ayudachain.git`. A fresh `git ls-remote --heads` found no `feat/five-role-map`; `feat/five-role-mvp` points to `56102c46afd4a429ad0a3b47fe57d15e759fd9fe`. Its implementation commit is `151fcf6`, authored by Nanashi, followed by evaluator-decision documentation. No open PR was returned for that head. The user subsequently confirmed this is the workmate's intended branch; `five-role-map` was a typo.

Fetched only for comparison; no checkout, cherry-pick or merge of that branch was applied. The prior provider session was not controlled. The common ancestor is `6d92882dcbc4496645b4379561f457d1504aed53`, before our stack. The branch adds a parallel MVP across 364 changed files, rather than a small role selector patch.

## Useful work to preserve

- `frontend/components/mvp/workspaces.ts` separates Beneficiary, Barangay Officer, DSWD Officer, Disbursing Officer and Auditor. In particular, barangay endorsement, DSWD decisions and cash handover have distinct owners. Our three-role context currently conflates those staff tasks.
- `Workspace.tsx` and `Dashboard.tsx` give each role direct URLs, relevant navigation and a concrete next action. Account/disaster context survives navigation; the mobile menu includes focus, Tab and Escape handling. These patterns are useful, though the staff navigation still needs a comprehension review for density.
- `CsvIntake.tsx` offers template download, row errors, duplicate comparisons, explicit confirmation and uncertain-response recovery. Its scoped `/api/v1/registry/csv/*` endpoints differ from our analyzer and cannot be copied alone.
- `SessionLookup.tsx` and its routes connect scanning/manual references to existing assigned payout controls. This is useful work to validate before rebuilding a scanner. The branch documents mocked decoder tests and no physical-camera validation.
- `IntegrityStatus.tsx` separates current checks from historical matches and expands raw evidence. Payouts and outcomes distinguish recorded handover from a recipient's private answer. Those product distinctions improve the story without claiming a chain hash proves cash delivery.
- Backend command keys, immutable versions, anchor jobs/observations and a pinned deployment offer useful lifecycle work to evaluate before implementing equivalent features again.

## Conflicts and assurance limits

1. **Backend and API replacement.** `backend/app/main.py` becomes the PostgreSQL MVP at `/api/v1`, with `{data, meta}` envelopes and string centavos. Our supported app is SQLite at `/api`, with batch/allocation/beneficiary/distribution models. The new role UI requires its own claims, entitlements, sessions and outcomes API. Copying its components into this stack would produce missing routes and incompatible payloads.
2. **Receipt and contract compatibility.** The new `AyudaChainEvidenceRegistry` uses a separate versioned SHA-256 protocol, random bytes32 references and pinned deployment metadata. Our current receipts use the centavos hasher and allocation-aware `AyudaChainRegistry`. Direct branch comparison shows the groupmate's retained legacy contract lacks our allocation/distribution counters and household/batch payment guard, and its legacy hasher accepts float pesos. Those files were unchanged from the ancestor on their side, so an ordinary merge would retain our changed versions alongside their older adapter assumptions. A clean textual merge would not establish compatibility. Never replace current artifacts or rehash existing receipts as a shortcut.
3. **Review and historical duplicates.** Our explicit duplicate survivor links preserve old IDs, receipts and payouts and enforce payment checks across aliases. The MVP uses versioned registry/claim checks and entitlement guards, not a drop-in equivalent of our retained-duplicate model. A data bridge must explicitly preserve linked identities, decision evidence, payout uniqueness and audit lineage; the current branch does not migrate our stack database.
4. **Roles are not authentication.** `actor.py` resolves a caller-supplied `X-Demo-Actor-ID` to stored roles and scope, and services enforce role/assignment/independence rules. Anyone can select or impersonate an active actor. The UI and API acknowledge this. This is stronger workflow scoping than browser hiding alone, but it does not complete our backend authentication/privacy backlog.
5. **Entry and instructions differ.** Their `/` opens a role directory, whereas our `/` is a public landing page and `/dashboard` is operational. Their `AGENTS.md`/contribution rules describe a PostgreSQL MVP and branching from main; our authorized workflow is the existing PR stack. Preserve the public entry and resolve instructions deliberately before any integration.

A read-only three-way `git merge-tree` found conflict markers in `CONTRIBUTING.md`, `README.md`, `backend/app/config.py`, `backend/app/database.py`, `backend/app/main.py`, `backend/app/services/blockchain.py`, `frontend/app/layout.tsx` and `frontend/app/page.tsx`. The moved verification route and shared styles also require semantic review. No conflict resolution was applied.

## Integration approach

1. Branch identity is confirmed. Settle product direction after isolated runtime validation. The five-role model is a useful design reference, not authorization to replace the supported stack.
2. Preserve both implementations. If adopting the complete MVP is desired, first run it in an isolated checkout with its own PostgreSQL, evidence files, ports and local-chain deployment. Do not use our database or original chain. Re-run its claimed journeys and fault tests; its validation ledger records chain-dependent gaps and stopped worker/chain, not fresh passing evidence here.
3. For incremental adoption, bring forward one supported user journey per stacked PR. Start with concise next actions and exact receipt links; retain `/` and current endpoints. Only expose new role tasks once they have connected APIs and documented ownership. Reuse their role map rather than inventing a second five-role model.
4. Treat PostgreSQL, immutable evidence and the worker as a separate migration decision with a compatibility ADR and data bridge. Acceptance must cover exact money, budget limits, eligibility, retained duplicate aliases, review history, idempotent uncertain retries and all four current verification outcomes before cutover.

The current stack has a stronger corrected baseline than main, but remains a collection of open PRs. This MVP may cover several planned workflows; it does not make either implementation nearly finished or integrated.
