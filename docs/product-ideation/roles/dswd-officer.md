# Role: DSWD Officer

**Status: ideation, not built.** The overall product picture is not final, so this may still change. Capabilities discussed in the design sessions of 2026-10-08. For what the app does today, read [the current user flow](../../product/user-flow.md). Screen-level detail for the funds capabilities is in [the DSWD Officer flow draft](../drafts/dswd-officer-user-flow.md).

Each capability is marked **Decided** (confirmed by the maintainer), **Proposed** (suggested and not objected to), or **Later** (agreed in principle, outside version 1).

This role was first called the "Finance Officer", with a separate "DSWD validator" planned beside it. The maintainer merged the two to simplify the project's scope. The capabilities stay in two groups, funds and beneficiary list, so they can be split into separate roles later without a redesign.

**Decided, process session of 2026-10-09.** Cross-role handoffs, state transitions and exceptions are settled in [the end-to-end process](../process.md). These remain ideation and do not authorise implementation. The additions below are indexed in decisions section 16.

## Who this is

Someone from a DSWD Field Office (regional). In AyudaChain the DSWD Officer is the top role of version 1. In the real organisation the funds work belongs to the Financial Management Division and the list work to disaster response staff, with the Regional Director above both; that approval step is designed for and switched off in version 1.

The DSWD Officer answers two questions:

- **Funds:** how much was received for this disaster, for what, and for which area.
- **Beneficiary list:** which claims are approved, in which category, and for how much.

DSWD Officer accounts are seeded. Managing DSWD staff accounts is out of scope.

## Funds capabilities in version 1

| # | Capability | Status |
|---|---|---|
| 1 | Switch between declared disasters. Disasters come from a seeded list; declaring or creating one is out of scope | Decided |
| 2 | Record a fund release for the selected disaster: amount, purpose, covered area, reference number, date, signatories | Decided |
| 3 | Attach the source document to every entry. An entry without a document cannot be saved | Decided |
| 4 | Review fields read automatically from the uploaded document, and confirm or correct each before saving | Decided |
| 5 | Read the ledger for a disaster: every entry, plus totals for received, advanced and remaining | Decided |
| 6 | Correct an entry by adding a reversing entry and a replacement, with a reason. The original stays visible | Decided |
| 7 | Re-check that a stored document still matches its on-chain hash | Decided |

## Rules that bind the funds capabilities

- **The officer records the budget and does not set it.** The amount comes from Central Office's release.
- **The document is hashed on upload** and the hash, amount and disaster are anchored on-chain. If anchoring fails, the entry is shown as not anchored.
- **Document reading only prefills.** Nothing is saved until the officer confirms it. If the officer overrides a machine-read amount, both values are kept.
- **A words-versus-figures mismatch on the document warns and does not block.** Real documents contain such errors.
- **The same document cannot back two independent releases.** A linked correction set may reference the original evidence for its reversal and replacement; an amended release needs its new document. The original is not counted twice. Decided; qualifies the earlier document-reuse rule.
- **One document may carry a breakdown.** An entry has a total and optional lines per recipient area.
- **Signatories are a list with roles** (for example, funds available and approved). A digital signature that validates is labelled separately from a name printed on the page; the system never claims to have authenticated a handwritten signature or stamp.
- **The ledger is append-only.** No entry is edited or deleted.
- **Entries count immediately in version 1.** Each still stores who entered it and an empty "approved by", so a second-person approval can be added without migrating data.
- **Covered area is recorded per release.**
- **An integrity check distinguishes:** matches, does not match, required anchor absent, or chain unreachable. Missing off-chain evidence is unavailable, never verified. Unreachable is not proof of either a match or absence. Decided.
- **The ledger balance is recorded funding authority, not certified cash.** Advanced and returns have no feeding entries until those capabilities exist; advanced stays zero. Payout totals are separate and do not silently reduce this ledger. Accounting/Cash provides physical funding outside the software. Decided.

## Funds capabilities after version 1

| # | Capability | Status |
|---|---|---|
| 8 | See who has already received cash assistance | Decided |
| 9 | Record the inputs that set each family's amount for a disaster, with the document that fixed them | Decided |
| 10 | Certify that funds are available before a payout round | Later |
| 11 | Grant a cash advance to a disbursing officer, within the disaster's remaining balance | Later |
| 12 | Track liquidation: Accounting-accepted disbursements plus evidenced returns must equal the advance; recorded handovers and recipient outcomes are separate evidence inputs, with acceptance/exception handling not yet designed | Later |
| 13 | Record returned and unspent funds | Later |
| 14 | Export a disaster's ledger for Central Office and the auditor | Later |

Background on items 10 to 14, including the audit rules behind them, is in [the DSWD Officer responsibilities notes](../drafts/dswd-officer-responsibilities.md).

## The amount inputs

Nobody types a family's amount. It is computed from a few inputs that the officer records once per disaster (capability 9).

| Mode | Inputs | Amount |
|---|---|---|
| Wage formula | The documented applicable regional daily minimum wage, and a number of days per damage category | 75% of the wage, rounded up to the nearest ₱10, times the days |
| Fixed amount | An amount per damage category | That amount |

An invented example of the formula: a wage of ₱435 gives ₱330 a day; 30 days for a totally damaged house gives ₱9,900 and 15 days for a partially damaged one gives ₱4,950.

- **The officer picks one mode per disaster.** Real operations use both: reports from Cebu describe flat amounts of ₱10,000 and ₱5,000. Decided.
- **Every input needs its document,** hashed like a fund release. Decided.
- **The inputs lock when the first approved list for the disaster is published.** A later change is a new entry with its own document. Decided.
- **A change recalculates every unpaid entitlement.** The household is notified of the old and new amount, and both stay in the history. Decided.
- **A change does not touch a paid entitlement.** Any difference is listed for the officer as a shortfall or an overpayment to handle. Decided.
- **The inputs are shown to the auditor, and to each household** as "how your amount was worked out". Decided.
- **Eligibility may be approved before inputs exist.** Its entitlement awaits an amount; missing inputs never mean zero. Publication and payment require a computed amount. Decided.
- **An unpaid change holds the affected entitlement until a revised list is published and its session reference updated.** Prior attempts/codes expire; the recipient reviews the new amount and opens a fresh attempt under the same transaction ID. Handed-over amounts remain fixed, even when receipt is disputed or unconfirmed. Decided.

These inputs set every family's amount, so they are the figures most worth tampering with. The same officer who approves claims may also enter them; see "What this role does not solve".

## Beneficiary list capabilities

None of these are in version 1. They arrive with the [Barangay Officer](barangay-officer.md) and [Beneficiary](beneficiary.md) roles.

| # | Capability | Status |
|---|---|---|
| 15 | Enter the Punong Barangay's documented nomination, including initial accounts; approve and deactivate Barangay Officer accounts, recording nominator and approver separately | Decided |
| 16 | Explicitly open a seeded disaster for selected barangays, record its external authority/basis and endorsement duration, and close claim intake | Decided |
| 17 | Receive signed barangay batches, including not-endorsed responses, and separately labelled system snapshots for no response, no eligible endorser or missing signed submission | Decided |
| 18 | See the result of the automatic checks on each claim | Decided |
| 19 | Decide each claim: approve, decline with a reason, or refer back to the barangay | Decided |
| 20 | Decide the category where the Barangay Officer disputed it | Decided |
| 21 | Approve many claims at once, where each is endorsed, has no flags and has an undisputed category | Decided |
| 22 | Publish the approved list for a barangay | Decided |
| 23 | Review a challenge to an entry on the approved list | Decided |
| 24 | See the approved total beside the disaster's remaining balance | Decided |
| 25 | Keep a list of grievances with a status and notes | Decided |
| 26 | See figures per Barangay Officer, as flags for review | Decided |
| 27 | Create and deactivate a [Disbursing Officer](disbursing-officer.md) account | Decided |
| 28 | Schedule, open, close, cancel or append changes to a payout session: one disaster, one barangay, one date/site, named officers and a published-list version; scheduling triggers the payout notice | Decided |
| 29 | Review a transaction a disbursing officer stopped, so the household can be paid in a later session | Decided |
| 30 | Change a category after approval, with a reason; notify the household, preserve history and expose it to the auditor | Decided |
| 31 | Re-link a household's account after a lost phone, following an ID check, with the action logged; never delegate this to the barangay | Decided |
| 32 | Confirm or resolve a household's residence through a documented check, including independently of an aid claim | Decided |
| 33 | Record a field check for a no-ID household; payment still waits for an accepted government photo ID | Decided |

## Rules that bind the list capabilities

**Who handles what**

- **Every officer handles every barangay** under the Field Office. Several officers share one queue. Assignment can be added later. Decided.
- **An officer cannot decide a claim from their own household.** Another officer does. Decided.
- **If nobody independent is available, the action is held and escalated for staffing.** Assisted sessions need two eligible disbursing officers. No recusal or exit-check bypass exists. Decided.
- **Each decision stores who made it and an empty "confirmed by",** so a second-person check can be switched on later without changing the data. Decided.

**Automatic checks**

- **They are a plain script, and are called "automatic checks".** They are not described as AI anywhere. Decided.
- **A check raises a flag and never decides.** The officer decides every claim. Decided.
- **Five duplicate checks run on data AyudaChain holds:** the same person in two households; the same ID on two registrations; a phone number shared beyond the limit; a household already approved or paid for this disaster; a household already recorded as aided for this disaster in another barangay. Decided.
- **Near-matches count.** Names and addresses are compared with edit-distance and token matching, so "Ma. Santos" and "Maria Santos" are flagged. Decided.
- **The National ID check is a simulated stand-in,** labelled as simulated on screen and in the API response. Decided.
- **The queue is ordered by risk:** a weighted count of flags, riskiest first. Decided.
- **Matching across regions is out of scope.** In practice Central Office repeats the check nationally; AyudaChain covers one Field Office.

**Decisions**

- **The household is told the outcome and the reason.** Decided.
- **A declined household may submit the claim again once,** with new information, while claims for that disaster are open. It goes through the barangay again. A formal appeal is deferred. Decided.
- **Referring back is a reply on the claim with a fresh deadline.** Each submission/referral uses the response duration set for the disaster. Existing claims continue through review/referral after intake closes. Decided.
- **The barangay cannot withhold delivery.** The system forwards no-response/no-eligible-endorser claims and responded claims without a signed submission, preserving the exact exception and any responses. This is a labelled system snapshot, not a fabricated barangay batch. Decided.

**The approved list**

- **It is published per barangay as a fixed snapshot,** with its hash anchored on-chain. Later batches produce a new version; earlier versions stay visible. Decided.
- **Publication waits for a computed entitlement and a confirmed list anchor.** An anchor failure leaves publication pending; retry the unchanged version. Only residence-confirmed residents see their barangay's list: name, zone and category, no amount/ID/phone. Decided.
- **A challenge before recorded handover** can lead the officer to reverse the approval, with a reason, as a new entry. Cancel the unhanded entitlement, expire attempts/codes and publish a successor list. Decided.
- **A challenge after recorded handover** becomes a note for the auditor. The officer cannot undo a payment, including a disputed or unconfirmed one. Decided.

**Funds and grievances**

- **An approved total above the remaining balance warns and does not block.** Blocking belongs to "certify funds" (capability 10). Decided.
- **A grievance has a status: open, under review or closed.** The software records what was done and resolves nothing itself. The auditor sees every grievance; the barangay sees none. Decided.
- **An adverse closing answer creates one linked private grievance.** A later adverse report reopens it, preserving previous answers and resolutions. The paying officer sees neither private answers nor grievances. A later full answer does not automatically close a grievance or authorise a new payment. Decided.
- **Session closure ends cash actions, not follow-up.** Late recipient answers, independent assigned exit checks and notes continue. Stopped transactions require DSWD clearance for a later session, using the same transaction ID with an appended attempt. Decided; narrows decision 15.2.

## Shared evidence and authentication boundary

- **Private off-chain evidence storage.** File references/hashes are linked to records; prior versions stay. Provider, retention and formats are Later. Decided boundary.
- **Phone signup/sign-in is Proposed planning only.** No SMS authentication provider or free-tier feasibility is established. The future five-role process needs authenticated actors; this does not change version 1's deferred sign-in.
- **Payout notices require SMS delivery, separately from authentication.** Scheduling/changes trigger linkless notices; failure is visible and DSWD handles unreachable households operationally. Provider/cost policy is Later. Decided boundary.

## What the DSWD Officer cannot do

- Declare a disaster or create its record.
- Endorse a claim. That is the Barangay Officer's opinion to give.
- Type or change the amount a family receives. Amounts are computed from the inputs.
- Decide a claim from their own household.
- Record a payout or confirm one on a recipient's behalf. The disbursing officer is a separate role.
- Undo a payment.
- Edit or delete a ledger entry, a decision or a published list.
- Approve their own entries, once approval exists.

## What this role does not solve

- **One account can record the money, set the amount inputs and approve who is paid.** Merging the funds and list work removes a separation of duties that a real Field Office keeps. Every action still records which account took it, and the disbursing officer stays a separate role, so one account cannot approve a claim and also hand over its cash.
- **No outside data says who was affected by a disaster.** The checks find duplicates. Whether a household was affected rests on the Barangay Officer's attestation.
- **A script misses what it was not written to catch,** for example a damage description that does not fit the stated category.

## Later

- **A model for the checks a script does badly,** chiefly comparing the free-text damage description with the stated category. Jev, from TypeSafe AI, is the named candidate: it returns typed decisions and scores from structured input. It was in early access behind a waitlist in October 2026, and its speed and cost figures are the company's own. To revisit once the script's misses are known. Any model would only add flags, never clear one or decide a claim, and using one sends household data to a third party.
- **Assigning officers to barangays.**
- **A formal appeal for a declined claim.**

## To verify with DSWD

- **Exact FACED field mapping** (Family Assistance Card in Emergencies and Disasters, formerly DAFAC). MC12 s2024's process clauses were read first-hand in the end-to-end session; a field-by-field mapping is still Proposed. FACED can distinguish independently living families sharing one household; this design deliberately keeps one entitlement per household for simplicity.
- **The exact operational Field Office check set and database access.** Official MC11/MC24 describe validation/deduplication, and MC24 names the Social Registry Office's deduplication role through the DSWD Social Registry. Detailed access and checks for this app still need confirmation; its settled checks remain local to AyudaChain.
- **Access to PSA's National ID verification** (National ID Check and eVerify) for this use. DSWD already uses it for 4Ps.
- **Whether PSA's Community-Based Monitoring System data can confirm a household's address.** Nothing found ties it to disaster validation.
- **The day counts per damage category,** and when a flat amount is used instead of the formula.

## Open points

1. **Who approves budget entries,** and from which version.
2. **The local-government payout mode is Later.** The settled process covers direct DSWD cash payout only.
3. **Sign-in is deferred.** Until it exists, nothing here is enforced by the backend, and that gap must be stated wherever version 1 is presented.
4. **The list screens are not drafted.** The flow draft covers funds only.

## Sources

- [DSWD DRMB: workshop on the Family Access Card in Emergencies and Disasters](https://drmb.dswd.gov.ph/2023/04/dswd-drmb-conducts-workshop-on-family-access-card-in-emergencies-and-disasters/)
- [Official FACED MC12 s2024 and ECT MC11/MC24 findings used in the process session](../process.md#research-used-in-this-decision)
- [PSA: National ID authentication services](https://rssocar.psa.gov.ph/content/national-id-authentication-services)
- [PhilSys: registry to be used to clean DSWD Listahanan](https://philsys.gov.ph/psa-continues-to-secure-philsys-milestones-set-to-use-the-philsys-registry-to-clean-dswd-listahanan/)
- [PNA: Listahanan ends as CBMS takes effect in 2024](https://www.pna.gov.ph/articles/1201622)
- [World Bank: COVID-19 and Social Assistance in the Philippines](https://documents1.worldbank.org/curated/en/099335004082237964/pdf/P17338000c78b50000b7c406e14ddbadab7.pdf)
- [SunStar Cebu: DSWD tells LGUs to verify "bloated" lists](https://www.sunstar.com.ph/cebu/dswd-tells-lgus-to-verify-bloated-lists)
- [TypeSafe AI launches Jev for structured software decisions](https://letsdatascience.com/news/typesafe-ai-launches-jev-decision-model-889a38c0)
