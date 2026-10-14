# AyudaChain local synthetic MVP

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

The integration suite requires the distinct fault node on 8555 and its manifest; the browser suite requires the running MVP. Browser full-journey evaluation explicitly retires the old namespace and deploys a new local registry before creating reference seeds. It preserves previous records and originals. Follow [evaluation instructions](docs/guides/demo-script.md). Actual results and all 26 requirement mappings are in [validation](docs/implementation/validation.md).

The authoritative design is [PRD](docs/product/prd.md), [ERD](docs/system/erd.md), and the [14-stage plan](docs/product-ideation/plans/2026-10-10-mvp-implementation-plan.md). [Compatibility ADR](docs/adr/2026-10-10-mvp-evidence-protocol-and-registry.md) defines the separate evidence protocol. Historical ideation is unchanged.

Legacy standard-library/SQLite code, the original receipt hasher, original contract and generated artifacts are retained without dual writes. /legacy-home preserves the old interface; other retained legacy screens need the separate legacy server and do not implement MVP workflows. /verify offers honest frozen legacy verification through the MVP read boundary. Missing original deployment/evidence is explicit, never green.

Offline handover, real SMS, live National ID integration, general PIN recovery, authenticated accounts, operational public-network/key governance, liquidation/advances/returns and cryptographic signature validation remain Pending or deferred. Advanced and returned funds are outside the current MVP and are omitted from the funds interface; recorded handovers do not reduce the received funding balance. Frontend lock audit is clean; retained Hardhat 2/toolbox development tooling has unresolved advisories. Real-household readiness conditions are documented in [local operation](docs/guides/local-mvp.md); this implementation is not ready for real household records.

The redesigned MVP uses responsive task queues, household progress, amount-basis explanations, searchable review/proof records and document previews. [Routes](docs/product/sitemap.md), [user flow](docs/product/user-flow.md) and [design system](DESIGN.md) describe the delivered surface. See the redesign section in [validation](docs/implementation/validation.md) for fresh checks and current runtime limitations.

## Design proposal: Tonal (Material 3, Sea and Sun)

The visual layer of the "Tonal" design was brought forward from `design-proposal` to `/mvp`, preserving this branch's role-specific workflow error recovery, and the [screen storytelling plan](docs/implementation/2026-10-13-screen-storytelling-plan.md) was then implemented on top of it. The full reference design is in [docs/design/tonal-design-reference.html](docs/design/tonal-design-reference.html); open it in a browser. Its palette switcher previews all three palettes, but only **Sea and Sun** is used in the app. [DESIGN.md](DESIGN.md) records what the code implements. The reference's additional layouts and interactions are implemented as described under screen storytelling below, except where the plan chose different Filipino-first labels.

### Implemented

- **Sea and Sun palette:** every `/mvp` colour is a Material 3 role token in `frontend/app/mvp.css`, with no hard-coded hex values in component rules. Both light and dark schemes are included.
- **Light / Dark / Device theme toggle** (`ThemeToggle.tsx`): in the workspace top bar and the `/mvp` header. The choice is remembered in the browser and applied before first paint.
- **Logo:** `public/logo.svg`, rendered by `components/mvp/Logo.tsx` in the drawer and on the directory page. The favicon is `app/icon.svg`, a copy of the same file. The retained legacy screens keep their original PNG logos.
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

### Screen storytelling: implemented and still pending

The [screen storytelling plan](docs/implementation/2026-10-13-screen-storytelling-plan.md) is implemented in software across all five phases and checked by automated tests; the [execution checklist](docs/implementation/screen-storytelling-progress.md) links the evidence. The plan's four beneficiary destinations and Filipino-first copy take precedence over the reference's sample labels.

| Area | Status |
|---|---|
| Safe status and next-action mapping (`Storytelling.ts`) | Implemented; 26 pure regression cases |
| Phone bottom navigation (at most four destinations per role), drawer at 760-1023px, labelled rail from 1024px | Implemented for the Beneficiary and all four staff roles |
| Filipino-first Beneficiary experience with saved English option | Implemented; **translations are drafts pending native-speaker review** |
| Review dialogs, specific saved results and snackbar | Implemented for registration, applications, decisions, responses, ID comparison, handover, publication and case actions |
| Segmented choices (recipient path, decisions, endorsement, identity result) | Implemented as native radio groups |
| Case flag banners | Implemented; they prompt inspection and never declare fraud |
| Integrity rows and Auditor result chips | Implemented; chips filter only records loaded and checked in the view |
| Disbursing tablet layout | Implemented; independent exit checks remain a separate task |
| List and detail panes (claims, payout records, integrity) | Implemented from 1024px |
| Barangay Assisted registration action | Implemented as a secondary link to the existing flow; the Auditor has no create action |
| Other palettes (Bayanihan Teal, Indigo and Mango) | Out of scope; only Sea and Sun is shipped |
| Legacy screens | Unchanged; out of scope |
| **Native Filipino review, five-participant comprehension test, physical phone/tablet/camera checks** | **Pending; they need humans and devices** ([checklist](docs/implementation/storytelling-human-validation.md)) |
| Colour-contrast measurement | Pending; not measured |

### Validation

- **Typecheck:** passed (`tsc --noEmit`, exit 0) on supported Node 22.
- **Production build:** passed in an isolated source copy using the installed locked dependencies, with the running development app untouched. The existing build configuration skips ESLint.
- **Browser checks:** the real form-driven journey passed (own-device and no-phone assisted payouts, actual chain-backed publication and handover, actual current integrity match). The automated suites passed with two exceptions that were fixed and rerun: three older tests and one more asserted raw API codes that the committed error-recovery work replaced with plain-language guidance, so their assertions were updated, and a re-selected payout transaction lost its detail, which is fixed with a regression test. A saved English choice also caused a hydration mismatch, fixed with a regression test. See [validation](docs/implementation/validation.md) for counts and for the one run that was interrupted.
- **Layout matrix:** 42 automated cases passed (five roles at 390px and 1440px in light and dark and in English and Filipino, plus the 759/760/1023/1024px shell transitions): no horizontal overflow, page errors, text under 13px or touch targets under 44px.
- **Limits:** no single uninterrupted run covers every test; a local runtime interruption left one anchor job awaiting reconciliation, so the chain-backed runtime has to be recovered before another chain-backed run (see validation). Authentication and real-household readiness remain Pending.

The earlier proposed completion prompt is kept in [docs/design/implement-missing-design.md](docs/design/implement-missing-design.md) as a historical supporting checklist.

## Five-role usability additions

The workspaces now include scoped search/task queues, frozen duplicate comparisons, English/Filipino step guidance, barangay operations tables, contextual proof checks, staged CSV registration for Barangay and DSWD staff (Beneficiaries use the household form) and native QR/manual session lookup. See [delivered behavior and limitations](docs/implementation/bring-forward-usability.md) and [validation](docs/implementation/validation.md). CSV templates cover head-only no-ID declarations; private completion follows normal workflows. Camera scanning requires browser BarcodeDetector support; manual lookup remains available. These are synthetic evaluation workflows with claimed/unverified accounts, not authenticated production privacy.
