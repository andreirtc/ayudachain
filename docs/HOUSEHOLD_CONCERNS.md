# Household concerns and staff assistance

Households can report and follow up a concern at /concerns, reached from household home. Concerns cover details, eligibility, payout/amount, arrangements or other issues. The API always binds a household submission to its signed-in account. A missing linked registry row can still report a concern for an existing batch. Staff first register other missing synthetic households rather than invent an identity.

Barangay and Disbursing staff can record an assisted concern for their own area; DSWD can record one for any household. The record retains the actual staff account and STAFF_ASSISTED source. This does not require household credentials or impersonate a household statement. The payout desk carries the exact household to the concern form. Unknown links select no substitute.

DSWD can reply and set Open, In review or Resolved with a household-visible message and separate internal reason. Replies append immutable SQLite revisions, preserve previous text and refuse stale saves. Durable request identities make uncertain-response retries safe. Households never receive staff reasons; DSWD and read-only Auditor can inspect them. Other staff see only concerns in their assigned area. No public endpoint exposes concern content.

Concerns never change eligibility, allocations, payouts, receipts or recipient acknowledgements. Resolve refers to the concern workflow; it is not proof of payment, reversal or an eligibility decision. All data remains synthetic, with no SMS or outside provider.

Validation: four focused authenticated journeys cover intake/replay, unchanged business records, staff reply/private reasons/stale saves, assisted actor and role/area scopes, CSRF, invalid fields, immutable retention and missing own records. TypeScript passes. Final build and a short browser walkthrough are recorded with the successor audit/demo delivery.
