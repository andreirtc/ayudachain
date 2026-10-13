# Implemented five-role journey

Open the role’s dedicated workspace from /mvp, then use its task navigation. The default account is an active synthetic account within that role; the Account panel selects another account of the same role. Disaster and account context survive nested navigation and refresh. No sign-in or authenticated role boundary is claimed. Every confirmation uses an editable form and actual saved originals; no presenter state supplies success.

1. DSWD uploads a release and reviews actual extraction/manual fields, confirmed amount, printed signatories and covered areas. Confirmation records once; correction appends a complete reversal/replacement pair. Saving funding does not open intake.
2. DSWD explicitly opens an operation using a basis original, barangay coverage and response duration.
3. The Beneficiary or helper registers a household and members with a separate contact link. No-ID registration is allowed; an assisted helper is barred from endorsing it. DSWD reviews residence, identity, facts or contact relink with reasons and preserved versions.
4. The household or Barangay submits damage/category evidence. Independent Barangay responses inform review. Punong Barangay submits responded threads with an actual council resolution. Staff shortage or persisted deadline yields a labelled unsigned exception snapshot with exact responses; negative and unsent threads reach DSWD.
5. DSWD reviews all flags and responds with approval, decline, referral or later category correction. Flags never decide. Missing independent reviewers hold/escalate. Referral starts a fresh window; one new-information declined resubmission is allowed during open intake.
6. Documentary wage/days or fixed-category originals determine amounts. Null remains awaiting amount. A cumulative frozen list is queued and publishes only after its own actual matching anchor and current-version check.
7. DSWD schedules payable members, Manila date/site and eligible cash/follow-up assignments. Notice intent/results are persistent and linkless. SMS is labelled simulated; no-contact and failure are visible.
8. The household opens its current eligible attempt and receives a code once. No-phone assistance first requires actual ID comparison and a privately established hashed PIN; the recipient re-enters that PIN to authorize. Cash needs a distinct independent assigned checker.
9. The assigned payer compares the person/photo ID, presents the fixed calculated cash for counting and records handover using the recipient's code. Concurrent requests consume it once. GET/replay recovers an unknown acknowledgement. Failed ID stops/holds; DSWD clearance permits a distinct session created later, including later the same day.
10. The recipient privately answers after handover, or an eligible independent assisted checker records the answer after closure. The payer cannot record their own exit answer. At 72 business hours without an answer, one neutral unconfirmed outcome is appended. Late/revised answers preserve history and never restore payability.
11. Adverse answers open/reopen one linked grievance. DSWD human review/resolution remains in private history; a full answer does not close it automatically. Resident challenges reverse an approval only before cash; after cash they retain evidence without another payment/refund.
12. Auditor reviews denominators/exceptions, versions, originals and current proofs. Private inspection writes a separate access log and creates no business action.

Unpaid basis/category changes hold and invalidate attempts; revised publication plus affected session update is required. Unrelated list additions preserve unchanged codes. Paid amounts, receipts and entitlement versions remain fixed, with calculable differences informational only.

Failed comparison before assisted PIN setup records only a stopped refusal: no recipient authorization or payout code is created. DSWD can clear that refusal for a distinct later session using the same transaction. Current chain checks display checking or unavailable during a failed refresh; any earlier successful check remains timestamped and explicitly historical.

Offline handover is unavailable. No general login/PIN recovery is provided. All households must be invented; current actor selection is unverified. See [evaluation](../guides/demo-script.md) and [scope/visibility requirements](prd.md).

## Workflow errors and recovery

**Local implementation; publication pending.** This section describes uncommitted frontend changes in the reviewed working tree. The documentation-only handoff does not make this behavior available in a fresh checkout. See the linked implementation record for scope and recorded checks.

MVP screens translate API rejection codes into plain-language explanations and next actions for the selected role, using the English/Filipino guidance preference. For example, closed or uncovered intake directs a Beneficiary to ask Barangay/DSWD to check the selected disaster and coverage; a DSWD Officer is directed to Households & intake and the documented opening steps if intake has not yet been opened. Messages do not imply that closed intake can be reopened or its saved coverage silently changed.

Existing claims direct users to the current thread. Stale reviews require refresh and review of the current evidence/flags. Missing amounts/publication, staff assignments, identity checks and recipient authorization name the responsible officer and required step. Payers are explicitly told not to hand over cash again after an existing handover or a lost handover response. A connection loss during a write leaves success uncertain: read the saved record before retrying. Read-only searches, previews, lookup and integrity checks do not claim a business action may have been saved.

Unavailable records remain indistinguishable from records outside the selected account's scope. Private lookup does not reveal whether a transaction exists. Unknown API errors and non-JSON gateway replies get safe recovery messages rather than internal codes/traces. API status/code, permissions, once-only handover and fail-closed integrity rules remain authoritative. Cancelled requests remain silent so former-account replies cannot become recovery guidance in the new view. Filipino copy still requires native-speaker review. See [implementation and checks](../implementation/role-error-guidance.md).

## Workspace presentation

Beneficiaries start with a household timeline, their next action, own entitlement and documented calculation, appointment, receipt and private help. Barangay Officers start with their scoped response queue and aggregate payout counts. DSWD Officers see outstanding human decisions, sessions and separate recipient outcomes; completed claims stay out of the pending queue. Disbursing Officers see assigned sessions and the compare/present/authorize steps. Auditors see linked exception groups and supporting histories, with handovers separated from recipient-confirmed outcomes.

Forms and original-document previews use the existing API commands, revision checks and idempotency keys. Long registration, amount and session forms are expandable; saved history remains accessible. Failed required dashboard/evidence reads display an unavailable state with retry, rather than empty counts. A chain check replaces any previous current result while checking; only an actual matching read shows Verified. Earlier matches remain explicitly historical. Dates use Manila time and money uses exact peso/centavo formatting.

Mobile navigation supports keyboard focus, Escape and return to its trigger; closed navigation is hidden from focus. The interface labels synthetic records and the simulated identity/SMS adapters. Evaluation-clock controls remain an explicitly labelled evaluation tool, separate from operational statuses.

## Usability interaction flow

Use Search & task queues to filter permitted records and open a specific household, claim, transaction or proof. Search/counts run on the server with bounded pages. Overview operations cells open the corresponding permitted filtered queue; Barangay aggregate payout cells remain plain counts. DSWD compares stored duplicate evidence, refreshes changed checks, and acknowledges the current check before deciding; revised evidence clears acknowledgments. Auditor comparison/history stays read-only.

Choose English or Filipino guidance in the context bar; the preference and full step guidance persist across navigation/refresh. Registry CSV follows template → upload → validate/preview → review possible duplicates → explicitly select valid rows → audited registration → per-row outcomes/links. Cancellation before confirmation creates nothing; successful partial rows are retained and identical-file retry recovers them. Templates deliberately omit private identity/contact fields and additional members. Complete those through the ordinary permitted registry workflow.

Assigned Disbursing staff can decode an opaque transaction QR on supported browsers or enter the same reference manually. Unknown/wrong-session references reveal no record. Opening does not compare identity, create a code or record cash. Continue the existing ID, fixed amount, recipient authorization and distinct-checker steps. Proof panels show coverage/current read separately from stored submission state and historical observations. See [delivery details and limits](../implementation/bring-forward-usability.md).
