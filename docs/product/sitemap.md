# Current routes

| Route | Runtime / scope |
|---|---|
| / | Redirect to /mvp |
| /mvp | Concise directory linking to the five workspaces |
| /mvp/beneficiary | Household overview, registration, claims, own amount basis, appointment, authorization/receipt and private reports |
| /mvp/barangay-officer | Own-barangay response queue, endorsements and batches, assisted registration, restricted residents’ lists and aggregate payout counts |
| /mvp/dswd-officer | Funding, intake, registry/staff, claim review, amount inputs/lists, session assignments, payout records, private cases and evidence |
| /mvp/disbursing-officer | Assigned sessions, identity comparison and cash handover, independent assisted exit checks and operational notes |
| /mvp/auditor | Read-only exception register, funding and payout records, originals, histories and current integrity checks |
| /verify | Read-only frozen legacy verification with original coverage and actual pinned chain state |
| /legacy-home | Preserved old dashboard component |
| Other legacy routes | Preserved three-role screens requiring the independent standard-library backend; not MVP entry points |

Each workspace opens directly and survives refresh. Its navigation uses nested section URLs: overview (the workspace root), funds, registry, claims, lists, sessions, payouts, outcomes and audit. Only the role’s available sections appear. A forbidden section shows Page unavailable; unknown workspaces return 404.

The role is fixed by its URL. There is no direct role-to-role switch. The AyudaChain logo and the "All workspaces" link at the foot of the navigation return to the /mvp directory, where another workspace can be chosen. This is navigation convenience, not access control. The Account panel contains only active accounts of that role; a different eligible Disbursing Officer account can independently check an assisted payout. Account/disaster context persists in query parameters on nested links and in local browser storage. This is navigation, **not authenticated authorization**: synthetic identities remain unverified and impersonable. Existing server role, assignment, household and office checks still apply.

Residence confirmation is required for the residents’ list. Barangay rows expose frozen household name, zone and damage category, without amounts, contact information, identity documents or private outcomes. Aggregate approved/handed-over/remaining counts are read from stored own-barangay records. Beneficiaries see their own entitlement separately. Selective resident inclusion verification is not provided; fully permitted evidence readers can inspect full commitments.

The original legacy sitemap is archived in ../legacy-documentation/product-sitemap.md. Historical ideation remains unchanged.

## Usability navigation additions

Each role also has a nested `/mvp/<workspace>/queues` page with permitted queue kinds only. Registry/claims/payout links use an opaque `record` query parameter and resolve direct server projections independently of bounded catalogues. Evidence links use `record=<commitment UUID>&history=commitment_id`; supporting history links use approved typed target slots. Account changes discard record/history selectors and reset private action state while retaining the URL role. Safe queue state/barangay/page parameters survive refresh/back/forward; search text stays in actor/disaster/queue-scoped tab session storage. CSV remains inside Registry and scan/manual lookup inside assigned payout work. No cross-role workspace navigation was added.

Finals corrections add no routes. Cash handover review stays within payouts; labelled synthetic evaluation tools stay in the DSWD/Auditor footer. See ../finals/FINALIST_READINESS.md for current validation.
