# Scoped payout arrangements

Staff open **Payout arrangement** from a finalized version on **Validated lists**, or go directly to /arrangements. DSWD or the assigned Barangay publishes one arrangement per finalized list version: collection date, time window, collection site, requirements to bring and the responsible staff name shown to households. Disbursing and Auditor read arrangements in their scope without changing them.

Included households see the current instructions on **My household**: the next step names the collection date, and **Payout and instructions** lists the time, site, requirements and staff contact. An edited arrangement is labelled updated. A cancelled arrangement shows a cancellation notice rather than stale instructions. Households never see staff reasons, account identities, excluded rows or other areas.

## Rules

- Only a finalized, unchanged list version can receive an arrangement. A list whose records changed after finalization needs a fresh version first. Each list version has at most one arrangement.
- Edits and cancellations append a new revision with a required staff reason. Earlier revisions stay readable in **Revision history**. A change based on an older revision is refused, so two staff members cannot silently overwrite each other. A cancelled arrangement stays retained and cannot be reopened; publish on a new finalized version instead.
- When a newer list version is finalized for the same batch and area, the older arrangement is marked superseded. Households stop seeing it, and staff publish instructions for the newer version.
- Collection dates in the past and unreadable text are refused.
- An arrangement never approves a household, reserves funds or authorizes a payout. Eligibility, budget, alias and once-only checks at the payout desk stay authoritative. No SMS or other notification is sent.

## API, durability and privacy

- GET /api/arrangements and /api/arrangements/{arrangement_id} are staff reads. Barangay and Disbursing see only their area. Household accounts are refused.
- GET /api/arrangements/mine returns only current instructions for list versions that include the signed-in household and are not superseded. Staff reasons and identities are omitted.
- POST /api/arrangements (DSWD/Barangay) accepts list_id, an actor-bound UUID request_id and the details. A lost-response retry returns the same arrangement; different details under the same request_id conflict.
- POST /api/arrangements/{arrangement_id}/revisions (DSWD/Barangay) accepts request_id, expected_revision, action EDIT or CANCEL, reason and, for edits, the new details. Retries replay; stale expected revisions return 409.
- Additive payout_arrangements and arrangement_revisions tables have update/delete refusal triggers like validated lists. Writes use the same SQLite writer lock. Each publish, revision and cancellation adds one audit event.

## Validation

9 new backend arrangement tests, the existing 12 list, 20 authentication and 76 business tests, the sign-in destination unit tests and TypeScript passed. 2 new browser journeys passed at desktop 1440x900 and phone 390x844 on an isolated production build, covering publish with a double click, edit with retained history, household instructions without staff notes, cancellation, role denial and missing links.
