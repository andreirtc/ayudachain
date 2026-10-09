# Role: Disbursing Officer

**Status: ideation, not built, and not part of version 1.** The overall product picture is not final, so this may still change. Capabilities settled in the design sessions of 2026-10-08. For what the app does today, read [the current user flow](../../product/user-flow.md).

Each item is marked **Decided** (confirmed by the maintainer) or **Later** (agreed in principle, not designed).

**Decided, process session of 2026-10-09.** [The end-to-end process](../process.md) settles cross-role handoffs and states; additions are indexed in decisions section 16. Existing Beneficiary proposals remain explicitly Proposed where noted. Nothing here is permission to build.

## Who this is

A named DSWD staff member who hands cash to approved households at a payout site. The role is separate from the [DSWD Officer](dswd-officer.md), so one account cannot approve a claim and also hand over its cash.

The Disbursing Officer answers one question: **is this the right person, and did they get the cash?** The officer decides nothing about who is eligible or how much they receive.

The payout transaction itself is described from the recipient's side in [the Beneficiary role](beneficiary.md).

## Account

| Rule | Status |
|---|---|
| Each officer is a named person with their own account | Decided |
| A DSWD Officer creates and deactivates the account | Decided |
| The officer signs in with an email for now. Verification is decided later | Decided |

## Payout sessions

A DSWD Officer schedules a payout session: one disaster, one barangay, one date/site, a published approved-list version and the named disbursing officers. Scheduling triggers the linkless payout notice; publishing the list does not. Decided.

- **An officer can act only on households on their session's approved list.** Decided.
- **Cash actions require an open session on its date.** Recipient answers, independent assigned exit checks and notes can continue afterward. Decided; narrows the original restriction in 15.2.
- **DSWD opens, closes, cancels and appends session changes.** Changes notify affected households and expire affected pre-handover attempts/codes; old versions and handovers stay. Decided.
- **The session shows separate computed handover and receipt-outcome totals.** A recorded handover counts once; received in full, disputed and unconfirmed are distinct. Nobody types totals. Decided.
- **Physical cash comes through outside Accounting/Cash arrangements.** Session creation does not create an advance or change the funding ledger; advances/returns/liquidation remain Later. Decided boundary.

## Capabilities

| # | Capability | Status |
|---|---|---|
| 1 | See the households to be paid in a session they are assigned to | Decided |
| 2 | Check the recipient's ID and compare the person with the photo | Decided |
| 3 | Confirm a transaction the recipient has opened | Decided |
| 4 | Mark the cash as handed over, by entering the recipient's one-time code | Decided |
| 5 | Use the assisted path for a recipient with no phone: an ID check and the recipient's PIN on the officer's device | Decided |
| 6 | Record the closing answer for an assisted payout made by another officer (the exit check) | Decided |
| 7 | Stop a transaction, with a required reason, when the ID check fails | Decided |
| 8 | Add a note to a transaction | Decided |
| 9 | See who in the session has been paid | Decided |

## Rules

- **The officer types no amount.** It is computed and shown to both parties. Decided.
- **No code, no handover.** The officer cannot mark cash as handed over without the recipient's one-time code. Decided.
- **The server enforces the order of steps** and which party may make each one. Decided.
- **Stopping a transaction does not cancel the entitlement.** It goes to DSWD for review/clearance and a later session; the recipient opens an appended attempt under the same transaction ID, with a fresh code. Decided; clarifies 8.6 and 15.4.
- **Nothing is undone.** The officer cannot reverse "handed over". The recipient's closing answer and the grievance route are the correction. Decided.
- **The exit check is done by another disbursing officer on the same session,** never the one who paid. It is not a separate role. Decided.
- **An officer cannot pay their own household.** Another officer on the session does. Decided.
- **No independent eligible staff means hold and escalate to DSWD.** Assisted payouts need two eligible officers; the checker is neither payer nor from the recipient's household. A later missing exit check becomes follow-up/unconfirmed, never reversal of cash. Decided.
- **Check current eligibility and amount again at handover.** Changed unpaid inputs/category require a new published list/session update and recipient authorisation; reversal cancels an unhanded entitlement. Prior codes/attempts expire. A handed-over amount cannot be recalculated, including disputed/unconfirmed payouts. Decided.
- **Unconfirmed starts 72 hours after recorded handover with no answer.** Late answers remain possible; unused open/presented attempts expire instead. No outcome makes the entitlement payable again. Decided.
- **Using the assisted path for a recipient with a registered phone needs a recorded reason.** Proposed in the Beneficiary role.
- **The officer is responsible for a working connection at the site.** There is no offline mode. Decided.
- **A lost acknowledgement requires reading the same transaction before retry.** Never assume the handover failed or pay again. Receipt anchoring failure is explicit and retried without another payment. Decided.
- **Private closing answers and grievances are hidden from the paying officer.** The independent exit checker receives only the answer they record and cannot manage the grievance. Decided.

## What the officer sees of a recipient

| Shown | Not shown |
|---|---|
| Household head's name | Phone number |
| Photo | Household members |
| ID type | Other households' details |
| Category | |
| Computed amount | |

## What the Disbursing Officer cannot do

- Approve, decline or change a claim or a category.
- Type or change an amount.
- Pay a household outside their session, after it closes, or under stale/reversed authorisation.
- Mark cash as handed over without the recipient's code.
- Close a transaction on the recipient's behalf, except the exit check on another officer's assisted payout.
- Reverse a handover.
- Pay their own household.
- See the payer's private closing answers or see/handle a grievance.

## What this role's controls do not solve

- **A cut taken from the family after they leave the site.** The private "received less" answer and the grievance route are the only handles on it.
- **An officer and a recipient who agree to a false handover.** The code proves the recipient was present and willing, not that the full cash changed hands.
- **Two officers on a session who cover for each other** on assisted payouts. The exit check only helps if the second officer is independent.

## Later

- **Cash carried out and brought back per session.** This belongs with cash advances and liquidation, which are marked Later for the DSWD Officer (capabilities 11 and 12). Real disbursing officers must be bonded and must account for every advance.

## Data held

| Group | Fields |
|---|---|
| Account | Name, email, who created it, active or deactivated |
| Per session | Disaster, barangay, date/site, assigned officers and list versions, scheduling/change/closure history, separate computed handover/outcome totals |
| Per transaction | ID, appended attempts, officer/session and step times, current input/list references, confirmation path, stop/expiry reason, notes, exit checker; private answers restricted |
| On-chain | Handover-receipt and outcome-event hashes with opaque references. No names, PINs or codes; see the [consolidated inventory](../process.md#consolidated-commitments) |
