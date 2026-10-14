# GitHub triage and safe consolidation

Read-only snapshots: 14 October 2026, initially approximately 01:25, refreshed at 02:35, then PR #39 follow-up at 2026-10-14T08:16+08:00 (Asia/Manila). GitHub showed **39 open PRs**, all authored by `BinkzBooze`; #1 ready, #2–#39 draft. Remote refs were fetched for inspection; no local branch tip, PR state or remote history was changed. The stack was still receiving new work during inspection, so recheck before any future action.

## Candidate branches

| Branch | Inspected tip | Useful implementation / disposition |
|---|---|---|
| `main` | `6d92882` | Original prototype. Preserve; not the complete five-role demo. |
| `design-proposal` | `4377db1` + local finals diff | Approved PostgreSQL five-role MVP plus Sea-and-Sun styling. Demo candidate. |
| `feat/five-role-mvp` | `4148db2` | Same substantive backend/contract baseline; later role error recovery (`1644f59`) selectively brought into finals. Includes source-copy/showreel artifacts; do not import indiscriminately. |
| `pivot/ideation` | `0880b27` | Historical process/design references and presentation work. Preserve unchanged. |
| BinkzBooze stack | #1 through #39 | Alternative FastAPI/SQLite, allocation-aware contracts and authenticated synthetic sessions. Independent architecture/product direction; preserve for deliberate comparison. |

`design-proposal` and `feat/five-role-mvp` share `56102c4`; neither complete tip is an ancestor of the other. Their substantive `backend/`, `contracts/`, `shared/` files agree at this snapshot. A future merge still needs inspection because tracked generated/source-copy artifacts and frontend/design histories differ.

## PR disposition matrix

Each #n after #1 depends on #n−1 **as an actual ancestor and PR base** in the inspected snapshot. Similar intent does not make a patch an exact duplicate. “Overlap” below is a semantic comparison, not proof that commits are equivalent. Recommendations are local review guidance; no PR has been closed or merged.

| PR / branch suffix | Depends on | Review recommendation |
|---|---|---|
| [#1](https://github.com/andreirtc/ayudachain/pull/1) `project-overview-explainer` | main | Historical backlog. Preserve as discussion; not the approved MVP requirements. |
| [#2](https://github.com/andreirtc/ayudachain/pull/2) `02-public-landing` | #1 | Separate public landing/routes. Incompatible with current root redirect and MVP route shell. |
| [#3](https://github.com/andreirtc/ayudachain/pull/3) `03-windows-local` | #2 | Useful Windows guidance for its own stack; current MVP supervisor guide supersedes it here. |
| [#4](https://github.com/andreirtc/ayudachain/pull/4) `04-fastapi-backend` | #3 | Alternative FastAPI/SQLite consolidation. Do not replace authoritative PostgreSQL MVP or delete legacy runtime. |
| [#5](https://github.com/andreirtc/ayudachain/pull/5) `05-config` | #4 | Useful truthful status principle; configuration and API shapes differ. |
| [#6](https://github.com/andreirtc/ayudachain/pull/6) `06-centavos` | #5 | Centavo arithmetic exists in MVP. This delta touches legacy hasher; compatibility decision required. |
| [#7](https://github.com/andreirtc/ayudachain/pull/7) `07-allocation-limits` | #6 | Allocation cap plus original registry/artifact changes; conflicts with current authority-ledger model. |
| [#8](https://github.com/andreirtc/ayudachain/pull/8) `08-payout-limits` | #7 | Allocation payout caps and original contract changes; requires explicit financial/model decision. |
| [#9](https://github.com/andreirtc/ayudachain/pull/9) `09-grant-policy` | #8 | Per-batch grant policy differs from documentary disaster input versions; concept overlap. |
| [#10](https://github.com/andreirtc/ayudachain/pull/10) `10-payout-eligibility` | #9 | Eligibility gate overlaps implemented current-version guards; different records/API. |
| [#11](https://github.com/andreirtc/ayudachain/pull/11) `11-one-payout` | #10 | Once-only payout overlaps MVP; original registry changes cannot be transplanted. |
| [#12](https://github.com/andreirtc/ayudachain/pull/12) `12-payout-idempotency` | #11 | Idempotency concept overlaps implemented atomic command replay; SQLite-specific code differs. |
| [#13](https://github.com/andreirtc/ayudachain/pull/13) `13-human-review` | #12 | Human review overlaps implemented claim threads/checks; different model. |
| [#14](https://github.com/andreirtc/ayudachain/pull/14) `14-retain-duplicates` | #13 | Retained duplicates/linked payout guards are useful concepts; compare semantics before adaptation. |
| [#15](https://github.com/andreirtc/ayudachain/pull/15) `15-truthful-verification` | #14 | Truthful chain verification overlaps MVP fail-closed reads; legacy adapter differs. |
| [#16](https://github.com/andreirtc/ayudachain/pull/16) `16-receipt-handoff` | #15 | Exact receipt navigation is useful; current MVP uses opaque transaction/commitment routes. Includes branch compatibility review. |
| [#17](https://github.com/andreirtc/ayudachain/pull/17) `17-truthful-demo-workflow` | #16 | Truthful demo/offline messaging overlaps current MVP. Preserve historical routes separately. |
| [#18](https://github.com/andreirtc/ayudachain/pull/18) `18-demo-sessions` | #17 | Useful authenticated-session implementation on SQLite. MVP still has no authentication; not a drop-in security patch. |
| [#19](https://github.com/andreirtc/ayudachain/pull/19) `19-payout-anchor-recovery` | #18 | Useful SQLite durable payout recovery. MVP has separate PostgreSQL worker, ten proof kinds and pinned registry. |
| [#20](https://github.com/andreirtc/ayudachain/pull/20) `20-registry-review-ux` | #19 | Registration/review UX ideas; old operations components and API differ. |
| [#21](https://github.com/andreirtc/ayudachain/pull/21) `21-typography` | #20 | Historical typography. Superseded within its stack by #32 and conflicts with Open Sans/Source Code Pro here. |
| [#22](https://github.com/andreirtc/ayudachain/pull/22) `22-payout-ux` | #21 | Budget-aware payout UX; current MVP intentionally separates recorded authority from physical cash certification. |
| [#23](https://github.com/andreirtc/ayudachain/pull/23) `23-receipt-ux` | #22 | Exact private receipt presentation ideas; current MVP receipt/proof shape differs. |
| [#24](https://github.com/andreirtc/ayudachain/pull/24) `24-verification-ux` | #23 | Useful live verification failure tests; different receipt protocol/routes. |
| [#25](https://github.com/andreirtc/ayudachain/pull/25) `25-ui-polish` | #24 | Navigation/readability ideas; old operations shell cannot replace five role URLs. |
| [#26](https://github.com/andreirtc/ayudachain/pull/26) `26-household-payout-handoff` | #25 | Exact household-to-payout linking overlaps current scoped queue/record links. |
| [#27](https://github.com/andreirtc/ayudachain/pull/27) `27-auth-destinations` | #26 | Authenticated destination preservation depends on #18; current MVP URLs are navigation only. |
| [#28](https://github.com/andreirtc/ayudachain/pull/28) `28-csv-onboarding` | #27 | CSV onboarding overlaps current staged declaration intake; different atomicity/model. Compare failure semantics. |
| [#29](https://github.com/andreirtc/ayudachain/pull/29) `29-recipient-acknowledgement` | #28 | Synthetic own-recipient acknowledgement differs from current full/less/not-received versioned outcomes/grievances. |
| [#30](https://github.com/andreirtc/ayudachain/pull/30) `30-receipt-snapshots` | #29 | Versioned receipt snapshots are useful; do not substitute v2 legacy payload for evidence-v1 commitments. |
| [#31](https://github.com/andreirtc/ayudachain/pull/31) `31-product-direction` | #30 | Alternative accepted direction for its stack explicitly retains caps/auth. Conflicting scope must be decided, not silently merged. |
| [#32](https://github.com/andreirtc/ayudachain/pull/32) `32-tonal-foundation` | #31 | Tonal foundation/local licensed fonts are useful. Desktop rail/phone nav target another authenticated shell. |
| [#33](https://github.com/andreirtc/ayudachain/pull/33) `33-household-start` | #32 | Beneficiary grounded home is useful reference; implemented against SQLite stack, not this MVP. |
| [#34](https://github.com/andreirtc/ayudachain/pull/34) `34-validated-lists` | #33 | Additive authenticated SQLite frozen staff lists/finalization, retained decisions and stale guards. No independent list anchor; not interchangeable with MVP approved-list publication or PostgreSQL schema. Preserve for comparison, no import tonight. |

| [#35](https://github.com/andreirtc/ayudachain/pull/35) `35-payout-arrangements` | #34 | Scoped collection arrangements for frozen SQLite lists. Useful collection-context UI; not the MVP assigned sessions/notice history. |
| [#36](https://github.com/andreirtc/ayudachain/pull/36) `36-payout-desk` | #35 | Guarded payout desk connected to its allocation/approval APIs. Visual person/amount/check progression reusable; business rules differ. |
| [#37](https://github.com/andreirtc/ayudachain/pull/37) `37-household-concerns` | #36 | Household concerns and staff replies with redaction. Compare with MVP versioned outcomes/grievances; not an interchangeable schema. |
| [#38](https://github.com/andreirtc/ayudachain/pull/38) `38-staff-audit-demo` | #37 | Read-only scoped staff audit and supported-flow guidance on the alternative stack. No replacement for evidence-v1 independent verification. |
| [#39](https://github.com/andreirtc/ayudachain/pull/39) `39-material-frontend` | #38 | Strong Sea-and-Sun layout reference, inline registry review, person/amount/check desk, compact audit and phone next step. Latest `de6dd06` also restores CSV/history/receipt links and fixes appearance/account navigation. Reuse bounded UI ideas; whole-branch adoption would switch API/schema/auth/receipt assumptions. See [detailed review](PR39_REVIEW.md). |

## Consolidation strategy after finals

1. Freeze a named reviewed demo candidate after tests. Tonight leaves changes uncommitted for maintainer review; no branch switching, merge or push is needed. Preserve the current database, files, replay key and exact manifests with their chain.
2. Agree which product is authoritative: documentary authority/entitlement/session model or allocation-capped model. Decide authentication, official procedures and receipt compatibility before designing bridges. Current AGENTS/PRD authorize the PostgreSQL MVP in this worktree; PR #31 explicitly documents a different direction for the other stack.
3. Review the MVP implementation as a separate integration proposal from main. Compare actual APIs/schema/contracts and generated artifacts; avoid accepting an entire artifact-heavy branch solely for screenshots. Preserve original legacy hashing/records.
4. Extract bounded UI ideas or reimplement small behaviors with regressions on the chosen baseline. Role error guidance from `1644f59` is the finals example: selected frontend diff, independent before/after tests, no schema/contract migration. Local fonts from #32 are a possible later portability improvement.
5. If preserving the BinkzBooze stack as the chosen future baseline, review dependencies in order. Do not retarget a late PR to main as if it were independent: it carries all predecessor assumptions. Authors/maintainers should decide any eventual rebase/retargeting; this run changes none.
6. Label exact duplicates only after diff/behavior comparison. Mark obsolete ideas in documentation without deleting their history. Any database/contract/hash change needs explicit discussion, ADR where required, migrations and compatibility tests.
7. Run an isolated complete journey, stale-version/denied-role/once-only/fault tests, production build and desktop/phone checks before any authorized consolidation. Public-network/key/production deployment remains separately gated.

## PR #39 follow-up

On the maintainer’s request, refreshed the remote refs and inspected #35–39, the #39 final source delta, requirements, application/database initialization, layout/navigation/appearance code and its committed desktop/phone screenshots. Snapshot now contains 39 open PRs. #39 is draft `de6dd06966a19ec355eb10b909dcffeab561bd25`, based on #38, with two commits. No branch was checked out or merged and author validation counts are not attributed to this worktree.

## Audit provenance

Inspected PR metadata and changed-file inventories are retained in [github-pr-snapshot.json](evidence/github-pr-snapshot.json). Full API replies and fetch logs remain ignored under `.runtime/finals/`. PR-description test claims belong to their authors; they were not rerun against the alternative stack in this audit. We inspected all open-PR deltas and branch histories; that is not a line-by-line security audit of every branch.

Do not present authenticated accounts, budget caps or v2 receipt snapshots from the alternative stack as shipped on the finals MVP. Likewise, do not present the MVP’s full claim/session/PIN/checker journey as already implemented in the alternative stack.

Final read-only refresh at approximately02:35 found PR#34 and38 remote branches. Its19-file delta, actual ancestor dependency, new service/API/schema and VALIDATED_LISTS documentation were inspected. Author-reported tests were not rerun here. Earlier matrix entries/tips remain unchanged. Snapshot includes all39 open PRs observed at that cutoff; later work may continue.
