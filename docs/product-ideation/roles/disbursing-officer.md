# Role: Disbursing Officer

**Status: ideation, not built, and not part of version 1.** The overall product picture is not final, so this may still change. Capabilities settled in the design sessions of 2026-10-08. For what the app does today, read [the current user flow](../../product/user-flow.md).

Each item is marked **Decided** (confirmed by the maintainer) or **Later** (agreed in principle, not designed).

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

A DSWD Officer sets up a payout session: one disaster, one barangay, one date, and the disbursing officers assigned to it.

- **An officer can act only on households on their session's approved list.** Decided.
- **An officer can act only while the session is open.** Decided.
- **The session shows a computed total of what was paid.** Nobody types it. Decided.

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
- **Stopping a transaction does not cancel the entitlement.** It goes to a DSWD Officer to review, and the household can be paid in a later session. Decided.
- **Nothing is undone.** The officer cannot reverse "handed over". The recipient's closing answer and the grievance route are the correction. Decided.
- **The exit check is done by another disbursing officer on the same session,** never the one who paid. It is not a separate role. Decided.
- **An officer cannot pay their own household.** Another officer on the session does. Decided.
- **Using the assisted path for a recipient with a registered phone needs a recorded reason.** Proposed in the Beneficiary role.
- **The officer is responsible for a working connection at the site.** There is no offline mode. Decided.

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
- Pay a household outside their session, or after it closes.
- Mark cash as handed over without the recipient's code.
- Close a transaction on the recipient's behalf, except the exit check on another officer's assisted payout.
- Reverse a handover.
- Pay their own household.
- See or handle a grievance.

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
| Per session | Disaster, barangay, date, assigned officers, open or closed, computed total paid |
| Per transaction | Officer, session, time of each step, confirmation path, stop reason, notes, exit checker |
| On-chain | Hashes only. No names |
