# Role: Finance Officer

**Status: ideation, not built.** The overall product picture is not final, so this may still change. Capabilities discussed in the design session of 2026-10-08. For what the app does today, read [the current user flow](../../product/user-flow.md). Screen-level detail is in [the Finance Officer flow draft](../drafts/finance-officer-user-flow.md).

Each capability is marked **Decided** (confirmed by the maintainer), **Proposed** (suggested and not objected to), or **Later** (agreed in principle, outside version 1).

## Who this is

A member of the Financial Management Division of a DSWD Field Office (regional). In AyudaChain the Finance Officer is the top role of version 1. In the real organisation the Regional Director sits above and approves; that approval step is designed for and switched off in version 1.

The Finance Officer answers one question: **how much was received for this disaster, for what, and for which area.** The role handles money and never the beneficiary list.

## Capabilities in version 1

| # | Capability | Status |
|---|---|---|
| 1 | Switch between declared disasters. Disasters come from a seeded list; declaring or creating one is out of scope | Decided |
| 2 | Record a fund release for the selected disaster: amount, purpose, covered area, reference number, date, signatories | Decided |
| 3 | Attach the source document to every entry. An entry without a document cannot be saved | Decided |
| 4 | Review fields read automatically from the uploaded document, and confirm or correct each before saving | Decided |
| 5 | Read the ledger for a disaster: every entry, plus totals for received, advanced and remaining | Decided |
| 6 | Correct an entry by adding a reversing entry and a replacement, with a reason. The original stays visible | Decided |
| 7 | Re-check that a stored document still matches its on-chain hash | Decided |

## Rules that bind these capabilities

- **The officer records the budget and does not set it.** The amount comes from Central Office's release.
- **The document is hashed on upload** and the hash, amount and disaster are anchored on-chain. If anchoring fails, the entry is shown as not anchored.
- **Document reading only prefills.** Nothing is saved until the officer confirms it. If the officer overrides a machine-read amount, both values are kept.
- **A words-versus-figures mismatch on the document warns and does not block.** Real documents contain such errors.
- **The same document cannot back two entries.**
- **One document may carry a breakdown.** An entry has a total and optional lines per recipient area.
- **Signatories are a list with roles** (for example, funds available and approved). A digital signature that validates is labelled separately from a name printed on the page; the system never claims to have authenticated a handwritten signature or stamp.
- **The ledger is append-only.** No entry is edited or deleted.
- **Entries count immediately in version 1.** Each still stores who entered it and an empty "approved by", so a second-person approval can be added without migrating data.
- **Covered area is recorded per release.**
- **An integrity check has three outcomes:** matches, does not match, or chain unreachable. Unreachable is never reported as a match.

## Capabilities after version 1

| # | Capability | Status |
|---|---|---|
| 8 | See who has already received cash assistance | Decided |
| 9 | Record the inputs that set each family's amount for a disaster: the regional wage in force and the agreed number of days per category, with the document that fixed them | Proposed |
| 10 | Certify that funds are available before a payout round | Later |
| 11 | Grant a cash advance to a disbursing officer, within the disaster's remaining balance | Later |
| 12 | Track liquidation: each advance must equal confirmed payouts plus cash returned | Later |
| 13 | Record returned and unspent funds | Later |
| 14 | Export a disaster's ledger for Central Office and the auditor | Later |

Background on items 10 to 14, including the audit rules behind them, is in [the Finance Officer responsibilities notes](../drafts/finance-officer-responsibilities.md).

## What the Finance Officer cannot do

- Declare a disaster or create its record.
- Add, endorse, validate or remove a beneficiary, or change a family's category.
- Type or change the amount a family receives. Amounts are computed.
- Record a payout or confirm one on a recipient's behalf.
- Edit or delete a ledger entry.
- Approve their own entries, once approval exists.

## Open points

1. **Who validates the beneficiary list.** The maintainer's sketch gave this to the Finance Officer. The recommendation is a separate DSWD role, so one person does not both approve who is eligible and release the money. Not yet settled.
2. **Who approves budget entries,** and from which version.
3. **Whether to support the mode where funds are transferred to a local government to pay out.** Everything above assumes DSWD pays families directly.
4. **Sign-in is deferred.** Until it exists, nothing here is enforced by the backend, and that gap must be stated wherever version 1 is presented.
