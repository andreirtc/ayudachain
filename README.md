# AyudaChain local synthetic MVP

Finals preparation (14 October 2026): see [current readiness and evidence](docs/finals/FINALIST_READINESS.md), [safe demo runbook](docs/finals/DEMO_RUNBOOK.md), [plain-English explanation](docs/finals/PROJECT_EXPLAINED.md) and [judges’ defense masterbook](docs/finals/JUDGES_QA.md). These fresh results are distinct from historical validation.

The implemented five-role workflow runs at **/mvp** with FastAPI, PostgreSQL and an actual local EVM registry. The root page redirects there. Open a dedicated role workspace from the entry page: /mvp/beneficiary, /mvp/barangay-officer, /mvp/dswd-officer, /mvp/disbursing-officer or /mvp/auditor. Each has its own overview, nested navigation and a same-role synthetic Account panel. URLs organize the interface; there is no sign-in gate. Authentication, secure authorization, operational privacy and authenticated accountability remain **Pending**. Use invented households only.

Beneficiaries and Barangay Officers register households and submit claims. Barangay responses and council resolutions or explicit unsigned fallback snapshots reach an independent DSWD reviewer. Documentary wage/category inputs produce exact centavo amounts; only a list's own matching chain confirmation publishes it. DSWD schedules cash staff and members. The recipient authorizes a short-lived attempt; an assigned officer compares the person/photo ID and records cash once. No-phone assistance requires a private PIN and a distinct independent checking officer. Private recipient answers, grievances and resident challenges retain their histories. Auditors inspect exact evidence and current chain reads without business mutation.

This software records physical cash evidence; it does not transfer money. Original uploads, real PDF extraction, editable confirmation, immutable versions, corrections, checks, human decisions, notices, audit records, signed transaction recovery and fresh verification use persistent records. National ID checking and notice SMS are explicitly simulated. Digital signatures are **not_validated**; originals are retained. An accelerated business clock is labelled; chain timestamps and references remain actual.

Start from the repository root with Python 3.14, Node 22 and local PostgreSQL 18 available. Use the locked environments:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r backend/requirements-mvp.lock
npm --prefix contracts ci
npm --prefix frontend ci
.venv/Scripts/python -m backend.scripts.setup_mvp
.venv/Scripts/python -m backend.scripts.local_mvp serve --with-chain
```

PostgreSQL must already be running; setup defaults to the owned loopback cluster on port 55432. Configure its local admin/owner URLs privately when using another installation. Setup creates the databases, purpose-specific roles, approved migrations and ignored **.env.mvp**. Point MVP_NODE to the supported Node executable. The supervisor starts frontend 3000, API 8000, chain 8545, the durable worker and scheduler, using private runtime logs. It refuses occupied ports. With a node already running, omit --with-chain. Existing pinned manifests are checked; lost deployments are refused. See [local operation](docs/guides/local-mvp.md) for configuration, recovery, tests and deployment loss.

```powershell
.venv/Scripts/python -m unittest discover -s backend/tests -v
.venv/Scripts/python backend/test_backend.py
npm --prefix contracts test
npm --prefix frontend run typecheck
npm --prefix frontend run build
npm --prefix frontend run test:mvp
```

The integration suite requires the distinct fault node on 8555 and its manifest; the browser suite requires the running MVP. Browser full-journey evaluation now requires a separately created fresh isolated lab and MVP_BROWSER_FRESH_RUN=1. It refuses a nonempty household registry and never resets the current evaluation. Run the journey before dependent browser cases; retain failed partial labs. Follow [evaluation instructions](docs/guides/demo-script.md). Actual results and all 26 requirement mappings are in [validation](docs/implementation/validation.md).

The authoritative design is [PRD](docs/product/prd.md), [ERD](docs/system/erd.md), and the [14-stage plan](docs/product-ideation/plans/2026-10-10-mvp-implementation-plan.md). [Compatibility ADR](docs/adr/2026-10-10-mvp-evidence-protocol-and-registry.md) defines the separate evidence protocol. Historical ideation is unchanged.

Legacy standard-library/SQLite code, the original receipt hasher, original contract and generated artifacts are retained without dual writes. /legacy-home preserves the old interface; other retained legacy screens need the separate legacy server and do not implement MVP workflows. /verify offers honest frozen legacy verification through the MVP read boundary. Missing original deployment/evidence is explicit, never green.

Offline handover, real SMS, live National ID integration, general PIN recovery, authenticated accounts, operational public-network/key governance, liquidation/advances/returns and cryptographic signature validation remain Pending or deferred. Advanced and returned funds are outside the current MVP and are omitted from the funds interface; recorded handovers do not reduce the received funding balance. Frontend lock audit is clean; retained Hardhat 2/toolbox development tooling has unresolved advisories. Real-household readiness conditions are documented in [local operation](docs/guides/local-mvp.md); this implementation is not ready for real household records.

The redesigned MVP uses responsive task queues, household progress, amount-basis explanations, searchable review/proof records and document previews. [Routes](docs/product/sitemap.md), [user flow](docs/product/user-flow.md) and [design system](DESIGN.md) describe the delivered surface. See the redesign section in [validation](docs/implementation/validation.md) for fresh checks and current runtime limitations.

## Design proposal: Tonal (Material 3, Sea and Sun)

This branch applies the visual layer of the approved "Tonal" design to `/mvp`. The full reference design is in [docs/design/tonal-design-reference.html](docs/design/tonal-design-reference.html); open it in a browser. Its palette switcher previews all three palettes, but only **Sea and Sun** is used in the app. [DESIGN.md](DESIGN.md) records what the code implements.

### Implemented

- **Sea and Sun palette:** every `/mvp` colour is a Material 3 role token in `frontend/app/mvp.css`, with no hard-coded hex values in component rules. Both light and dark schemes are included.
- **Light / Dark / Device theme toggle** (`ThemeToggle.tsx`): in the workspace top bar and the `/mvp` header. The choice is remembered in the browser and applied before first paint.
- **Kubo Link logo:** `components/mvp/Logo.tsx`, used in the drawer and on the directory page. The favicon is `app/icon.svg`.
- **Fonts:** Open Sans for the interface and Source Code Pro for references, loaded with `next/font`. The minimum text size is 13px.
- **Material 3 shapes and states:**
  - pill buttons with outlined secondary buttons;
  - outlined text fields;
  - borderless rounded tonal panels;
  - a tonal navigation drawer with a pill indicator for the current page;
  - a primary-container next-step card;
  - a primary-filled journey stepper.
- **Status:** shown as a glyph and a coloured word, with no filled boxes or pills. There is a new negative tone (cross) for "Does not match", "Chain unreachable", "Anchor absent", "Evidence unavailable", "Not received" and "Stopped".
- **Messages:** error, warning and success messages are banner rows with a glyph and a divider, not tinted boxes.
- **Return to the directory:** the logo and an "All workspaces" link return to `/mvp`. Neither switches role directly; see [sitemap](docs/product/sitemap.md).

### Not yet implemented or missing

| Area | In the reference design | Current app |
|---|---|---|
| Phone navigation | Material 3 bottom navigation bar with at most four destinations per role | Hamburger menu opening the full drawer |
| Desktop navigation | Navigation rail with a floating action button, plus list and detail panes side by side for claims, payouts and integrity | Fixed side drawer; list and detail are separate stacked panels |
| Decisions | Segmented buttons (Approve / Decline / Refer to barangay; Endorse / Do not endorse; Pass after comparison / Fail and hold/stop) | Existing radio buttons and selects |
| Confirmation | "Record this decision?" dialog before an irreversible decision or handover | Cash handover has a native household/amount review dialog with cancel/Escape. Other decisions still save directly; CSV keeps its preview-and-confirm step. |
| Feedback | Snackbar after saving ("Decision recorded for DFC-…", with View) | Inline saved message |
| Flags | Material 3 banner at the top of a case: icon, sentence, text-button actions, divider | Flags appear inside the existing panels |
| Integrity rows | Status rows (glyph, record name, time or action, explanation line) | Existing `IntegrityStatus` layout restyled; same structure as before |
| Floating action button | Role's main create action (for example, Barangay "Assisted registration") | Not present |
| Household screens | Phone-first Home, My claim stepper, payout code screen with a large Source Code Pro code and PIN warning banner, private report screen | Existing screens restyled; same layout as before |
| Disbursing Officer | Tablet layout: photo beside the comparison form, plus a "Handover steps" side panel | Existing stacked form restyled |
| Auditor | Result filter chips above the integrity table | Existing search and select filters |
| Empty states | Icon, title and explanation in an outlined card | Existing empty state restyled |
| Other palettes | Bayanihan Teal and Indigo and Mango | Only Sea and Sun is shipped |
| Legacy screens | Not covered by the design | Unchanged (Tailwind legacy UI); only the favicon is shared |

### Validation status

The starting Tonal branch documented ten browser failures. Finals preparation reproduced the duplicate registration selector and concatenated integrity text, repaired them, integrated the existing role error guidance and fixed transaction reselection/registry loading. The cash-handover review and explicit evaluation-clock disclosure are now connected. [Finalist readiness](docs/finals/FINALIST_READINESS.md) records current completed checks, failed intermediate runs and remaining limits. Do not treat earlier branch results as current evidence.

The prompt for completing the missing parts is in [docs/design/implement-missing-design.md](docs/design/implement-missing-design.md).

## Five-role usability additions

The workspaces now include scoped search/task queues, frozen duplicate comparisons, English/Filipino step guidance, barangay operations tables, contextual proof checks, staged CSV registration and native QR/manual session lookup. See [delivered behavior and limitations](docs/implementation/bring-forward-usability.md) and [validation](docs/implementation/validation.md). CSV templates cover head-only no-ID declarations; private completion follows normal workflows. Camera scanning requires browser BarcodeDetector support; manual lookup remains available. These are synthetic evaluation workflows with claimed/unverified accounts, not authenticated production privacy.
