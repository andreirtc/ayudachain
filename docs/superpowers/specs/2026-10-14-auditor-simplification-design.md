# Auditor workspace simplification — design

Date: 2026-10-14. Status: **Implemented 2026-10-14** (frontend only). Validation results are in `docs/implementation/validation.md`.

## Intent

The maintainer reported that the Auditor workspace has too many sidebar destinations and it is unclear where to look for what. The Auditor should be able to verify and monitor transactions easily.

Agreed in discussion (2026-10-14):

- Scope: three destinations plus a split of the long integrity page. Frontend only, no API, schema, contract or hash change.
- The home screen keeps leading with exceptions ("Records needing inspection"), as in the [screen storytelling plan](../../implementation/2026-10-13-screen-storytelling-plan.md) §5 and the [Auditor role](../../product-ideation/roles/auditor.md).

Success: an Auditor can name where to go for each of the role's four capabilities without hunting. The capabilities are landing on exceptions, browsing the ledger, opening a record's evidence and history, and re-running an integrity check. No currently reachable capability becomes unreachable.

## Unchanged constraints

- The Auditor remains read-only. No create, decide, mark, note or retry control appears.
- Integrity results keep their fail-closed states and current-versus-historical wording. The proof filter chips keep their labels and the "records loaded and checked in this view" scope note.
- Server endpoints, scoping and private inspection logging are unchanged. Opening an original still goes through the logged evidence endpoint.
- The legacy screens and other roles' workspaces are unchanged.

## Current state (baseline)

- `frontend/components/mvp/workspaces.ts` gives the Auditor ten navigation items. Its phone bottom bar shows overview, audit, funds and queues.
- Seven items (funds, claims, registry, lists, sessions, payouts, outcomes) are other roles' work pages in read-only mode.
- Exceptions appear on the dashboard (`Dashboard.tsx`) and again at the top of `Audit.tsx`.
- Funding exceptions (`/funds` entries with `exceptions`) appear only in `Audit.tsx`.
- `Audit.tsx` is one long page: exceptions, record history, chain checks, originals and the full business timeline.
- The overview also renders `Operations` (barangay totals table) inside "Supporting operations and totals".

## Design

### 1. Navigation: Inspect, Records, Verify

| Key | Label | Icon | Purpose |
|---|---|---|---|
| `overview` | Inspect | scan | Exceptions to inspect |
| `queues` | Records | list | Find any record |
| `audit` | Verify | shield | Chain checks, originals, history |

- The Auditor's sidebar and phone bottom bar both show exactly these three, in this order. `staffDestinations.auditor` becomes `['overview','queues','audit']`.
- The seven record sections remain valid routes so deep links, record links and existing tests keep working. They are declared as hidden navigation items, for example `hidden: true` on `NavItem`. Hidden items are excluded from the sidebar and bottom bar but still count as part of the workspace, so the "Page unavailable" guard does not fire.
- On a hidden section:
  - Records carries `aria-current="page"`.
  - The breadcrumb reads `Auditor / Records / <page label>`.
  - A **Back to Records** link sits above the page content. It points to the Records URL with the current `account` and `disaster` and keeps the search state the queue already stores in session storage.
- Hidden-item labels are kept descriptive: Funding ledger, Claim decisions, Household records, Amount and list history, Payout sessions, Recorded handovers, Recipient outcomes.
- Other roles' navigation is not changed.

### 2. Inspect (home, `Dashboard.tsx` Auditor branch)

Keep:

- The heading "Records needing inspection." and its description.
- The primary action to Verify.
- The exception register.
- The handover/recipient-answer summary, which links to Recipient outcomes.

Change:

- **Add funding exceptions to the register.** The Auditor dashboard also reads `/funds?disaster_id=…`. Each entry with a non-empty `exceptions` array becomes a register row. Its title is the release reference, its explanation lists the exception names in readable form, and it links to Verify with `record=<fund id>&history=fund_entry_id`. If the funds read fails, the dashboard shows the existing unavailable state. It never shows an empty "no exceptions" result based on a failed read.
- **Fallback link for a flag with no history slot.** Today such a flag links to the `#exceptions-<kind>` anchor on Audit, which this design removes. It now opens the record page named in `exceptionNames[kind][2]`, without a `record` parameter, because the flag's row id (for example a payout attempt) is not that page's record id.
- **Unsupported history slots fixed.** Grievance and challenge flags previously linked to `grievance_id`/`challenge_id` histories, which the timeline endpoint rejects. They now use the row's `transaction_id` or `handover_id`, or fall back to their record page.
- **Remove** the four-number briefing strip. The register count and outcome summary already carry those numbers.
- **Remove** the "Supporting operations and totals" block for the Auditor; it moves to Records. DSWD and Barangay keep it on their overview.

### 3. Records (`Queue.tsx` for the Auditor, plus `Workspace.tsx`)

- The title is "Records" with the description "Find any record and open its evidence." The other roles keep "Search and task queues".
- The existing queue search, filters, paging and scope text are unchanged.
- An **Other records** row of links appears above the search: Funding ledger, Payout sessions, Recipient outcomes, Amount and list history. These cover records the queue search API does not serve.
- Below the search, a collapsed `<details>` labelled "Office totals by barangay" renders the existing `Operations` component. Its count links already open filtered searches.

### 4. Verify (`Audit.tsx`)

- The page title is "Verify" with the description "Check saved records against the chain, open originals and read history."
- **Selected record panel first.** When `record` and `history` are in the URL, the record's history (or the proof detail for `history=commitment_id`) renders at the top with its current integrity status and a close action. This uses the existing logic, moved up.
- **Three views**, chosen by the `view` URL parameter (`checks` default, `originals`, `history`):
  - *Chain checks*: the existing proof search, filter chips, scope notes, "Check now" and proof detail.
  - *Original files*: the existing originals table and private preview.
  - *Event history*: the existing append-only timeline, latest 20 first, with a "show all" control.
- The view switcher is a labelled group of links or buttons using `aria-current`/`aria-pressed`. Changing view pushes a history entry and keeps `record`, `history`, `proof_filter` and `proof_query`, so browser Back restores the earlier view without issuing a chain check.
- **Remove** the "Exceptions and supporting records" section. Exceptions live on Inspect.
- For the Auditor, Verify no longer reads `/audit/overview` or `/funds`; both exception sources are read on Inspect.
- **DSWD is unaffected.** The DSWD Officer's Evidence & history page uses the same component and keeps its combined layout, exceptions section and reads. The view switcher applies to the Auditor only.

### Error and empty states

- Inspect: failed reads use the existing "Records unavailable" state with retry. "No workflow exceptions recorded" appears only after all reads succeed.
- Verify: the existing load-failure, empty-filter and unavailable-summary states are unchanged in each view.

## Testing

New Playwright tests, each of which fails before the change:

1. The Auditor sidebar and bottom bar each show exactly Inspect, Records and Verify.
2. `/mvp/auditor/claims` still renders the claims page, highlights Records, shows "Back to Records", and that link returns to `/mvp/auditor/queues`.
3. A funding entry with exceptions appears in the Inspect register and links to its funding history on Verify. This uses a mocked-API fixture in the style of `storytelling-integrity.spec.ts`.
4. Verify shows no exceptions section. Switching to Original files and then Event history updates `view`, and browser Back returns to the previous view.
5. Read-only: no Auditor page exposes save, approve, decide, note or retry controls. This extends the existing `workspaces.spec.ts` read-only test.

Existing tests to update for the new labels and destinations: `storytelling-staff-shell.spec.ts`, `workspaces.spec.ts` (sections list and the `/mvp/auditor/audit` check), and the "Evidence and integrity" heading assertions in `verification.spec.ts` and `journey.spec.ts`. Recheck `storytelling-integrity.spec.ts` and `workflow-errors.spec.ts`, which load `/mvp/auditor/audit`, after the change.

Run the frontend typecheck/build and the affected Playwright suites, and report actual results. Chain-backed specs depend on the local stack; record any that cannot run.

## Documentation

In the same change:

- `docs/product/sitemap.md`: the Auditor row and the staff destinations line.
- `docs/product/user-flow.md`: the Auditor section.
- `docs/implementation/validation.md`: actual results.
- Add a short note to the storytelling plan's Auditor section recording that the Auditor destinations changed from four to three.

## Out of scope

- A unified Auditor record-detail view replacing the other roles' pages (the discussed option B).
- Any API addition, such as funds, sessions or outcomes in queue search.
- Audit observations, mark-reviewed, notes and export (Later in the role doc).
- Changes to other roles.
