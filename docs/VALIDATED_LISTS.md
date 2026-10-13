# Versioned validated lists

Staff open **Validated lists** from the household registry. DSWD or the assigned Barangay can prepare a version for an active batch/area. Registration and CSV import remain separate intake actions; imported rows stay pending. **Inspect current household** carries the exact reference into the existing scoped review dialog, including retained records. Missing/out-of-scope links never substitute another household.

Preparation saves a private frozen version with every included/excluded household, current status/flags, original reference and retained decision actor/time/reason/evidence. Historical records, unresolved flags, incomplete locality, missing retained approval, unapproved eligibility, explicit staff exclusions and already recorded payouts for linked aliases remain explicit. A prior payout is an operational exclusion, not ineligibility. Missing funding is not an eligibility exclusion. No registry row, receipt hash or old approval is changed/backfilled.

DSWD inspects the version and explicitly confirms a reason to finalize it. An empty included list cannot finalize. Changed records, newly imported rows, changed decisions/grants, inactive batches or new recorded payouts require a fresh version. Finalized originals remain readable with a changed/unavailable-current-record label. List finalization never reserves funds, publishes private households publicly or records/authorizes a cash payout; current payout/budget/alias/idempotency guards stay authoritative.

## Prototype authority and document mapping

The selected synthetic control is one attributable DSWD eligibility decision per included record and one authenticated DSWD finalization of the inspected area version. Barangay preparation is not an eligibility approval. Disbursing reads only its area; Auditor reads without mutation. This maps existing supported roles rather than copying an unverified actor picker or requiring five sequential approvals.

Required prototype evidence is a household reference/name, consistent batch/locality, current approved eligibility without unresolved flags, and the retained human decision. DAFAC references are saved when present, but are not validated identity documents. Existing seed approvals without a retained decision are excluded until staff performs a real prototype review; no official approvals are silently backfilled. Finalization is local staff evidence, not an authenticated government signature, independent anchored audit, genuine document check or comprehensive ECT compliance.

The official ECT sources and their limits are recorded in [PRODUCT_DIRECTION.md](PRODUCT_DIRECTION.md). They inform the validated-list direction. This feature implements a labelled synthetic control, not all institutional approval ownership or documentary alternatives from those circulars. Program-specific documents belong to actual scoped payout instructions; this task does not impose private PINs, short-lived codes, two officers or chain publication gates universally.

## API, durability and privacy

- GET /api/validated-lists and /api/validated-lists/{list_id} are protected staff reads. Barangay/Disbursing see only their area; household accounts cannot inspect full lists. Office decision reasons/evidence and payout references are redacted from those scoped staff projections.
- POST /api/validated-lists/prepare accepts an actor-bound UUID request_id, batch/area and optional explicit exclusions/reasons. Repeated/lost-response requests return the same frozen version; changed data with the same retry identity conflicts. New preparation is explicit.
- POST /api/validated-lists/{list_id}/finalize requires DSWD, consent and a reason. A SQLite writer lock covers current-record reconciliation and finalization. Concurrent/repeated requests retain one actor/time/reason and one audit event.
- Additive validated_lists and list_finalizations tables have update/delete refusal triggers. Privileged database administration can bypass local guards; no chain protection is claimed. Existing tables and hashes are preserved.

The frontend retains failed submission inputs/identities, guards repeat clicks, sends nothing offline, hides failed reads and restores saved versions from the real API. No offline queue or real document/identity integration is implemented. The bounded synthetic list limit is 2000 area records; CSV's separate intake limit remains 200.

## Validation

Validation passed:12 new list API cases,20 authentication and76 business regressions;34 affected existing Edge registry/CSV/authentication cases, followed by all10 new list journeys on the final build at desktop1440x900/phone390x844. Cases include actual CSV import/review, lost-response prepare/finalize retries, stale decisions, role/scope denial, empty/loading/read-error/offline states and keyboard filters. Final light/dark screenshots inspected and retained in tmp/ayudachain-pr34-validation. Frontend Node14, independent TypeScript, isolated production build and diff checks passed. Initial new browser label/navigation/announcer issues were corrected. Tests cover pending CSV-to-review-to-list flow, explicit exclusions, stale decisions/intake, role/area denial, CSRF, concurrent replay, frozen history and preserved linked payout records. Original database/builds/services/artifacts/provider remain preserved; the persistent preview remains stopped.
