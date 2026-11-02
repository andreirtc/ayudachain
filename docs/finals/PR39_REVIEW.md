# PR #39: practical reuse review

Inspected 14 October 2026 at the maintainer’s request. [PR #39](https://github.com/andreirtc/ayudachain/pull/39), draft, head `de6dd06966a19ec355eb10b909dcffeab561bd25`, based on #38. Metadata is retained in [snapshot](evidence/pr39-snapshot.json). No checkout, merge or installation from this branch was performed.

## Recommendation for the venue

Use the current validated PostgreSQL five-role MVP for the complete funding → registration → review → entitlement → recorded handover → receipt → integrity demonstration. Use #39 as an additional visual reference for the deck and later frontend adaptation. Its design is useful; switching the whole application immediately would replace a tested journey with a different product/API/schema baseline.

The final #39 delta is 71 files, 1,334 additions and 1,583 deletions relative to #38, across two commits. The first introduces the Material layouts; the second restores omitted CSV/history/receipt navigation and fixes appearance/account navigation. The second also touches backend test requirements and launchers, CI and regression configuration. Thus “frontend only” is accurate for the initial layout intention, not a complete file-scope description of the latest cumulative PR.

Compared with committed `4377db1`, the #39 tip differs across **134 frontend files** (7,681 additions/9,609 deletions) and **176 backend/contract/shared files** (6,004 additions/20,230 deletions). Their merge base is original main `6d92882`. These are branch comparison statistics, not a UI-port estimate. Selective screen adaptation is smaller but still requires preserving and retesting MVP workflow guards.

## Reusable work

| Actual source | Useful behavior | Safe adaptation boundary |
|---|---|---|
| `frontend/app/tonal.css` | Sea-and-Sun surfaces, 44px actions, 16px fields, 96px desktop rail and four-item phone bar | Current MVP already shares palette/fonts/focus and now has 44px controls. Its more numerous tasks need explicit overflow/navigation design before replacing its drawer. |
| `frontend/app/(operations)/beneficiaries/page.tsx` | Inline registry list/detail and focus return; CSV/history tools restored | Reimplement against current registry/claims endpoints; preserve current household originals and human-review history. |
| `frontend/app/(operations)/distributions/page.tsx` | Person, amount and checks grouped at payout desk | Keep current session membership, version gates, code, assisted checker, idempotency and final confirmation unchanged. |
| `frontend/app/(operations)/household/page.tsx` | Prominent actual next step and recorded progress | Current MVP also has next-action/progress components. Use presentation hierarchy without implying that a scheduled collection means already paid. |
| `frontend/app/(operations)/audit/page.tsx` | Compact searchable table and attention/history areas | Preserve all ten evidence kinds, current-check states and private-envelope controls; a saved anchor is not a fresh match. |
| `frontend/components/AppearanceMenu.tsx` | Light/dark/device choices; Escape/outside/context dismissal and focus return | Independent interaction idea. Current MVP uses a direct three-button theme control; no menu replacement is required for this demo. |
| `frontend/components/Navbar.tsx`, `workspaceHome.ts` | Actual account home navigation and scoped searches | These depend on its authenticated session context; current MVP selectable actor is explicitly unverified. Do not transplant its authentication wording. |

## Compatibility findings from code

- #39 `backend/app/main.py` imports `app.auth`, SQLAlchemy entity models and alternative services, and installs `authorize_request` as an application dependency. Current MVP uses PostgreSQL actor-resolution rules and different endpoints/records.
- Its `backend/app/database.py` defaults to SQLite and contains startup migrations/protection for its idempotency, duplicate history, receipt snapshots and validated lists. Running it over this worktree’s database is unsafe; no such startup was performed.
- Its final regression document explicitly says funding release/allocation write APIs exist but the current frontend displays seeded records without authoring forms. It also explicitly locates claims/evidence/endorsement, amount calculation, assigned sessions, code/PIN/checker controls, outcome answers and task queues in the separate five-role MVP.
- Version-2 receipt snapshots and allocation-aware original-contract changes come from predecessor PRs. They are different compatibility surfaces from the current separate evidence-v1 registry. An intact #39 checkout carries those predecessor decisions even though its own layout commit does not alter them.
- Frontend package ranges differ: #39 declares Next15.5.5/React19.1.0, this worktree declares Next15.5.27/React19.3.0. Do not overwrite current lockfiles or copy an old build into the current frontend.

## Evidence and limits

I inspected the final source delta, stack ancestry, application/database initialization, package requirements, layout/navigation/theme code, author validation documents and committed registry-desktop/household-phone captures. The screenshots are readable and aligned with the supplied Material reference. They are **author-generated branch screenshots**, not captures from our running finals lab; they must not be presented as this worktree’s implemented UI.

The author reports 184 backend, 14 frontend unit and 21 contract passes, five recovery scenarios and 140 browser cases covered (137 in the full run, three corrected separately), plus 18 live-chain observations. Those results were **not independently rerun here** and are not added to our test counts. The author’s own local preview3101/API8101 belongs to their machine; this report does not claim those addresses are available here.

After finals, select the authoritative product model first, then adapt small components in separate reviewed changes with current-MVP regressions. Preserve all branches/data and original hash/contract compatibility. No automatic whole-stack integration is recommended for the departure window.
