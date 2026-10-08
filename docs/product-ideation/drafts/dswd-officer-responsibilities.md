# DSWD Officer Responsibilities: funds (scratch)

**Status: scratch notes, not a specification.** Nothing here is built. Items marked *unconfirmed* come from general knowledge of Philippine government finance and must be checked with a DSWD Field Office before they go into the PRD.

These notes cover the funds side of the [DSWD Officer](../roles/dswd-officer.md) role, which was first called the Finance Officer. In a real Field Office this work belongs to the Financial Management Division. In AyudaChain's planned hierarchy the DSWD Officer is the top role for the first version. In the real organisation the Regional Director sits above it and approves.

## Already in scope

- **Record the budget received per disaster.** Each release from Central Office is one ledger entry: amount, purpose, covered area, and the source document.
- **Attach the source document** to every entry. An entry without one cannot be saved.

## Responsibilities not yet discussed

| # | Responsibility | What it means | Rule or source |
|---|---|---|---|
| 1 | Certify funds are available | Before a payout round is approved, confirm the disaster's remaining balance covers it | Standard budget and accounting control; *unconfirmed* for the exact DSWD form |
| 2 | Grant cash advances to disbursing officers | Release cash from the disaster's budget to a named Special Disbursing Officer, who then pays families | DSWD designates these officers through the Financial Management Division |
| 3 | Check the officer is bonded | Anyone holding government cash must be covered by a fidelity bond | COA Circular 97-002 |
| 4 | Limit the advance | An advance is capped at two months of need | COA Circular 97-002 |
| 5 | Track liquidation | Each advance must be accounted for: confirmed payouts plus cash returned must equal cash advanced | COA Circular 97-002 |
| 6 | Enforce return of unused cash | Cash unused after two months is returned; nothing stays unliquidated at fiscal year end | COA Circular 97-002 |
| 7 | Record returns of unspent funds | Money coming back from an officer, or going back up to Central Office, is its own ledger entry | *Unconfirmed* for the upward return |
| 8 | Report balances | Periodic figures per disaster to Central Office and to the resident auditor | *Unconfirmed* for report names and frequency |
| 9 | Keep documents for audit | Source documents and liquidation papers stay retrievable for COA's post-audit | General audit requirement |

## Separation of duties to preserve

In a real finance division these are different people. The first version may give them to one role, but the data model should record who did each so they can be split later.

- **Budget:** records the allotment and certifies it is available.
- **Accounting:** checks documents are complete and certifies cash is available.
- **Cash:** releases the money.
- **Approval:** the Regional Director, outside the division.

One person entering and approving the same budget entry is the kind of gap an auditor flags.

## Source documents

| Document | What it proves | Issued by |
|---|---|---|
| Sub-Allotment Release Order (Sub-ARO) | Authority for the Field Office to spend a stated amount for a stated purpose | DSWD Central Office |
| Notice of Transfer of Allocation (NTA) | Cash moved into the Field Office's account at the government bank | DSWD Central Office, as an instruction to the bank |

The Sub-ARO says how much may be spent; the NTA says the cash exists. A ledger entry is strongest when it has both.

## Open questions

1. Who approves a budget entry in the first version: the Regional Director, a second DSWD Officer, or nobody?
2. Does one disaster ever receive funds from more than one source (Quick Response Fund plus donations, for example)?
3. Is "covered area" recorded per release, or once per disaster?
4. Should the direct-to-LGU fund transfer mode be supported, where the LGU pays families instead of DSWD staff?

## Sources

- [DBM: fund transfers to operating units (Sub-ARO, NTA)](https://jur.ph/law/summary/fund-transfers-for-operating-units)
- [DBM National Budget Circular No. 488](https://dev.lawyerly.ph/laws/44542)
- [COA Circular 97-002: cash advances](https://rgao.upm.edu.ph/media/2023/10/COA-C97-002-Cash-Advances-2-months-cash-flow.pdf)
- [COA Circular 2021-006: electronic and digital signatures (as cited by DPWH)](https://www.dpwh.gov.ph/DPWH/sites/default/files/issuances/DMC_057_s2021.pdf)
