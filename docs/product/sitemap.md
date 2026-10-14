# Current routes

| Route | Runtime / scope |
|---|---|
| / | Redirect to /mvp |
| /mvp | Concise directory linking to the five workspaces |
| /mvp/beneficiary | Household overview, registration, claims, own amount basis, appointment, authorization/receipt and private reports |
| /mvp/barangay-officer | Own-barangay response queue, endorsements and batches, assisted registration, a household census with residence approval, the restricted approved list and aggregate payout counts |
| /mvp/dswd-officer | Funding, intake, registry/staff, claim review, amount inputs/lists, session assignments, payout records, private cases and evidence |
| /mvp/disbursing-officer | Assigned sessions, identity comparison and cash handover, independent assisted exit checks and operational notes |
| /mvp/auditor | Read-only. Inspect (exception register, including funding exceptions), Records (server search plus links to funding, sessions, outcomes and list history) and Verify (chain checks, originals, event history) |
| /verify | Read-only frozen legacy verification with original coverage and actual pinned chain state |
| /legacy-home | Preserved old dashboard component |
| Other legacy routes | Preserved three-role screens requiring the independent standard-library backend; not MVP entry points |

Each workspace opens directly and survives refresh. Its navigation uses nested section URLs: overview (the workspace root), funds, registry, claims, lists, sessions, payouts, outcomes and audit. Only the role’s available sections appear. A forbidden section shows Page unavailable; unknown workspaces return 404.

The role is fixed by its URL. There is no direct role-to-role switch. The AyudaChain logo and the "All workspaces" link at the foot of the navigation return to the /mvp directory, where another workspace can be chosen. This is navigation convenience, not access control. The Account panel contains only active accounts of that role; a different eligible Disbursing Officer account can independently check an assisted payout. Account/disaster context persists in query parameters on nested links and in local browser storage. This is navigation, **not authenticated authorization**: synthetic identities remain unverified and impersonable. Existing server role, assignment, household and office checks still apply.

Residence confirmation is required for the residents’ list. Barangay rows expose frozen household name, zone and damage category, without amounts, contact information, identity documents or private outcomes. Aggregate approved/handed-over/remaining counts are read from stored own-barangay records. Beneficiaries see their own entitlement separately. Selective resident inclusion verification is not provided; fully permitted evidence readers can inspect full commitments.

The original legacy sitemap is archived in ../legacy-documentation/product-sitemap.md. Historical ideation remains unchanged.

## Usability navigation additions

Each role also has a nested `/mvp/<workspace>/queues` page with permitted queue kinds only. Registry/claims/payout links use an opaque `record` query parameter and resolve direct server projections independently of bounded catalogues. Evidence links use `record=<commitment UUID>&history=commitment_id`; supporting history links use approved typed target slots. Account changes discard record/history selectors and reset private action state while retaining the URL role. Safe queue state/barangay/page parameters survive refresh/back/forward; search text stays in actor/disaster/queue-scoped tab session storage. CSV remains inside Registry and scan/manual lookup inside assigned payout work. No cross-role workspace navigation was added.

## Screen storytelling navigation

**Implemented 2026-10-14 (software-checked; human validation Pending).** Existing URLs, nested section routes, `account`, `disaster`, `record`, `history` and queue-filter parameters remain valid. No route is removed.

Below 760px every workspace shows a labelled bottom bar with at most four destinations. From 760px to 1023px the same destinations are in the keyboard-accessible drawer, and from 1024px a labelled navigation rail shows the full grouped list. The logo and All workspaces return to `/mvp`. Every other permitted section stays reachable from the drawer or rail, and the main frame reserves space so the bar never covers the final action.

| Workspace | Phone destinations (section) |
|---|---|
| Beneficiary (Filipino first, English option) | Ayuda ko / My assistance (overview, appointment, authorization and receipt); Impormasyon namin / Our information (registry); Mga tala / Records (claims, amount and lists, queues); Humingi ng tulong / Ask for help (private reports) |
| Barangay Officer | Barangay overview; Claim responses; Households; Approved list |
| DSWD Officer | Operations overview; Claim review; Payout sessions; Private cases (funding, intake, amounts/lists, payout records, evidence and queues stay in the drawer/rail) |
| Disbursing Officer | My work today; Cash handover; Assigned sessions; Exit checks & notes |
| Auditor | Inspect; Records; Verify. The same three appear in the drawer/rail. Record pages (funding, claims, households, amounts and lists, sessions, handovers, outcomes) keep their URLs; they open from Records or an exception, highlight Records, and show Back to Records. |

Each role’s overview leads with one task: Barangay “Claims needing your response”, DSWD “Work needing your decision”, Disbursing “Find recipient”, Auditor “Records needing inspection”. The Barangay Assisted registration action opens the existing registry flow as a secondary link; the Auditor has no create action. Barangay Claim responses is a table of the barangay’s own claims (open claims, then history); selecting a row opens that claim’s review and Endorse / Not endorse form below it, and the Punong Barangay ticks rows to send. Barangay Households is a census table of every household registered in the barangay, whether or not it has claimed; selecting a row opens the registration (members, address, zone), and an officer who neither lives there nor helped register it can approve its residence with a recorded basis. That confirms residence only, never aid. Barangay Approved list shows DSWD-published entries (name, zone, category) and a count, never amounts. Claims, payout records and integrity use a list beside a detail pane from 1024px and stack below it; Auditor proof selection keeps `record`, `history`, `material` and `proof_filter` in the URL so browser Back restores the earlier selection without issuing a chain check or business command.

The Beneficiary dashboard’s status and single next action come from `frontend/components/mvp/Storytelling.ts`; see the [status and action mapping](../implementation/storytelling-status-map.md).
