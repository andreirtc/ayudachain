# Role: Auditor

**Status: ideation, not built.** The overall product picture is not final, so this may still change. Capabilities settled in the design sessions of 2026-10-08. For what the app does today, read [the current user flow](../../product/user-flow.md).

Each item is marked **Decided** (confirmed by the maintainer) or **Later** (agreed in principle, outside version 1).

This role shares only its name with the `Auditor / COA` role in the running code, which can review and delete beneficiaries and confirm payouts. The redesigned auditor changes nothing.

## Who this is

An officer of the Commission on Audit. The Commission is an independent constitutional body: its auditors review after the fact and take no part in budgeting, allocating, approving or paying. The auditor sits outside the Field Office and is not above it in any hierarchy.

The auditor answers one question: **does the record hold up?** They read everything and change nothing.

The auditor ships in version 1, alongside the [DSWD Officer](dswd-officer.md)'s funds capabilities.

## Account

| Rule | Status |
|---|---|
| The account is seeded, like DSWD Officer accounts | Decided |
| It covers the one Field Office AyudaChain is scoped to | Decided |
| Sign-in follows version 1, where it is deferred | Decided |

## Capabilities in version 1

| # | Capability | Status |
|---|---|---|
| 1 | Land on the exceptions list for a disaster | Decided |
| 2 | Browse the full ledger for any disaster | Decided |
| 3 | Open any entry to its document, hash, on-chain reference and history | Decided |
| 4 | Re-run the integrity check on any entry | Decided |

## The exceptions list

Automatic checks put an entry on the list. They are a plain script and only point at entries; the auditor judges them.

**In version 1**, six conditions:

| Exception | Meaning |
|---|---|
| Not anchored | The entry was saved and its hash never reached the chain |
| Document mismatch | The stored document no longer matches the on-chain hash |
| Corrected | The entry was reversed and replaced |
| Amount overridden | The officer changed an amount read from the document |
| Words and figures disagree | The document states two different amounts |
| Duplicate document | The same document was offered for a second entry |

**After version 1**, the same list grows as each role is built:

- figures per Barangay Officer: claims not endorsed, category disputes and how many were overturned, assisted registrations, relative declarations, missed deadlines
- claims approved in bulk
- a category changed after approval
- a change to the amount inputs, and the entitlements it recalculated
- an approved total above the remaining balance
- a transaction stopped by a disbursing officer
- assisted, unconfirmed and disputed payouts, per officer and per site
- a challenge raised after a payout
- every grievance

## Rules

- **The auditor changes no record.** There is no approve, reject, edit, mark or note in version 1. Decided.
- **An integrity check has three outcomes:** matches, does not match, or chain unreachable. Unreachable is never reported as a match. Decided.
- **The auditor sees everything, including personal data.** Names and claim details show in lists. ID numbers and photos show only when a specific record is opened. Decided.
- **Each view of an ID number or photo is logged.** Decided.
- **An access log records what the auditor viewed.** It is not shown to the Field Office, so staff cannot tell which entries are under scrutiny. The log is written by the system, not by the auditor. Decided.

## What the auditor cannot do

- Create, correct, approve or delete anything.
- Decide a claim, a category or an amount.
- Take any step in a payout.
- Mark an exception as reviewed, or attach a note, in version 1.

## What this role does not solve

- **The list shows what the checks were written to catch.** A problem no check looks for stays off it, though the full ledger remains browsable.
- **A matching hash proves the document is unchanged since it was anchored,** not that the document was genuine when uploaded.
- **Without sign-in, the role is a selectable setting.** Until sign-in exists, nothing stops anyone from choosing the auditor view, and that gap must be stated wherever version 1 is presented.

## Later

- **Audit observations.** The auditor raises an observation on an entry and the Field Office must answer it. Marking an exception as reviewed, and notes, arrive with this.
- **Export** of a disaster's ledger with each entry's document hash and on-chain reference, shared with the DSWD Officer's export (capability 14 there).

## Data held

| Group | Fields |
|---|---|
| Account | Name, Field Office covered |
| Access log | What was viewed and when, including each view of an ID number or photo |
| Exceptions | Computed from the records. Nothing is stored by the auditor |
