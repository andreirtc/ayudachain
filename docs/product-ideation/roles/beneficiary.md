# Role: Beneficiary (Barangay Citizen)

**Status: ideation, not built, and not part of version 1.** The overall product picture is not final, so this may still change. Capabilities discussed in the design session of 2026-10-08. For what the app does today, read [the current user flow](../../product/user-flow.md).

Each item is marked **Decided** (confirmed by the maintainer), **Proposed** (planned or suggested, not settled for implementation), or **Later** (outside the settled process). The former defaults were settled in the process session.

**Decided, process session of 2026-10-09.** [The end-to-end process](../process.md) reconciles the five roles and defines states, exception routes and anchoring. Its additions are indexed in decisions section 16. None is permission to build.

## Who this is

A resident of a barangay whose household may be affected by a declared disaster. The same person is a citizen before a disaster and a beneficiary once their claim is approved.

This role depends on three others: the [Barangay Officer](barangay-officer.md), the [DSWD Officer](dswd-officer.md) and the [Disbursing Officer](disbursing-officer.md). It also requires sign-in, which version 1 defers.

## The route

| Step | What happens | Status |
|---|---|---|
| A. Household registry | The household registers at any time, before any disaster. A Barangay Officer may register it on its behalf; that registration is flagged | Decided |
| B. Claim | DSWD explicitly opens the seeded disaster for selected barangays; the household submits a claim from its declared barangay | Decided |
| C. Endorsement | A named Barangay Officer responds with attestation and category opinion; signed batch or explicit system fallback takes the claim to DSWD | Decided |
| D. Validation | Automatic checks use AyudaChain records and a labelled simulated National ID stand-in; DSWD decides eligibility and final category | Decided; aligns with 14.2 |
| E. Approved list | The household is told its result; an approval may await amount inputs. Publication needs computed amounts and a confirmed list anchor; residence-confirmed residents see their barangay's list | Decided |
| F. Payout notice | DSWD scheduling a session triggers a linkless text with date/site; list publication alone does not announce a payout | Decided |
| G. Payout transaction | Open, presented, handed over | Decided |
| H. Closing | The recipient answers, or the transaction becomes unconfirmed | Decided |
| I. Grievance | An adverse answer/report opens or reopens one linked private grievance for DSWD; no automatic replacement payment | Decided |

## Capabilities

| # | Capability | Status |
|---|---|---|
| 1 | Register their household: identity, household members, address, phone number, sign-in | Decided |
| 2 | Claim for a declared disaster covering their area, stating how they were affected | Decided |
| 3 | See their own status, category and computed amount before the payout, with how the amount was worked out | Decided |
| 4 | See the approved list for their own barangay | Decided |
| 5 | Receive a notice that a payout is taking place | Decided |
| 6 | Open their own payout transaction after signing in | Decided |
| 7 | Reveal the one-time transaction code to the officer, after counting the cash | Decided |
| 8 | Close the transaction with one of three answers: received in full, received less, not received | Decided |
| 9 | Report a shortfall privately, and append a changed closing answer afterwards, including after session closure | Decided |
| 10 | Challenge an entry on their own barangay's approved list privately to DSWD | Decided |

## Identification

| Rule | Status |
|---|---|
| The National ID is the primary identity document. Its digital check is a simulated stand-in, labelled on screen and in the API response; no live PSA verification is claimed | Decided; aligns with 14.2 |
| Another government photo ID is accepted as the alternative | Decided |
| The officer compares the person with the photo on the ID at payout | Decided |
| Registration records identity evidence/check status; photo comparison and any field check are distinguished from simulated National ID verification | Decided |
| A household with no surviving ID may register and claim, flagged; payment waits for a documented DSWD field check and accepted government photo ID | Decided |
| Certification-only payment without that photo ID | Later |

## Sign-in and the transaction code

**Phone signup/sign-in is Proposed planning only.** A one-time code by text and a PIN are possibilities, not a selected authentication mechanism. No provider, integration feasibility or free-tier availability has been established. Authentication remains a prerequisite for the future five-role process, not an implemented capability. The Decided assisted PIN is separate from selecting general phone authentication.

These are two different secrets.

| | Sign-in | Transaction code |
|---|---|---|
| Purpose | Authenticates the account/person | Records recipient authorisation for this payout; physical identity is checked separately |
| How | Proposed planning; provider/method unresolved | Generated only when the recipient opens the transaction/attempt |
| Lifetime | Depends on the authentication method, not yet selected | One attempt, short-lived and consumed at handover |
| Shown to | Nobody | The officer, at handover |

- **No payout code is sent after registration or with a notice.** It does not exist until the recipient opens the transaction. Decided.
- **Sign-in with a Google account is deferred.** Decided.
- **The access card number identifies a household and is not a secret.** It is never enough to sign in.

## The payout transaction

```
Open → Presented → Handed over → Closed: received in full
  │       │                     → Closed: received less   (grievance opened)
  │       │                     → Closed: not received    (grievance opened)
  │       │                     → Unconfirmed             (72 hours after handover)
  └───────┴─ Stopped/expired → cleared/valid new attempt under the same ID

Unconfirmed → late closing answer
Closed answer → appended revised answer; adverse report opens/reopens grievance
```

- **One transaction ID per entitlement, with appended attempts.** DSWD may clear a stopped attempt for a later session; an expired unused attempt can be retried when current eligibility/session rules hold. No recorded handover can be repeated, even if disputed or unconfirmed. Decided; clarifies 8.6 alongside 15.4.
- **The amount is computed by the system** and shown to the recipient beforehand. The officer has no amount field. Decided.
- **If amount inputs/category change before recorded handover,** the entitlement is held, old codes/attempts expire and old/new amounts are reported. DSWD republishes a list and updates affected sessions before the recipient opens again. Handed-over amounts remain fixed; any difference is flagged for human review. Decided.
- **The officer cannot mark "handed over" without the recipient's code.** Decided.
- **The server enforces the order** and which party may make each move. Decided.
- **Unconfirmed is neutral and begins 72 hours after recorded handover without an answer.** A late answer is allowed after session closure; abandoned open/presented attempts expire instead of becoming unconfirmed. Officers and sites are watched by their share of unconfirmed, disputed and assisted payouts. Decided.
- **Adverse answers open one linked private grievance.** New answers preserve the old ones; a later adverse report reopens a closed grievance. A full answer does not automatically close it. DSWD records human resolution; no automatic repayment follows. Decided.

## How the payout is confirmed

Every transaction records which path was used.

| Path | When | How | Status |
|---|---|---|---|
| Full | The recipient has a smartphone | Signs in, opens the transaction, shows the code, closes it on their own device | Decided |
| Text | The recipient has a basic phone | Transaction-by-text and authenticated replies still need a protocol/provider; payout-notice SMS does not establish this | Later |
| Assisted | The recipient has no phone | Both an ID check and their PIN typed on the officer's device | Decided |

- **Assisted payouts get an exit check.** The closing answer is recorded by a second staff account, not the paying officer. Staffing it is DSWD's operational matter. Decided.
- **The assisted PIN is privately established after identity checking and stored hashed.** It is not the transaction code and is never sent by SMS. The exit checker must be another eligible Disbursing Officer assigned to the session, outside the recipient's household; late checks can continue after session closure. Decided.
- **An officer cannot use the assisted path for a recipient with a registered phone** without recording a reason. Proposed.
- **A text is sent to any number on the record after a payout is recorded,** whatever path was used. Proposed.
- **The officer is responsible for a working connection at the site.** There is no offline mode. Decided.
- **Paying officers do not see private closing answers or grievances.** The independent exit checker may receive the answer they record, without grievance-management access. The beneficiary, DSWD and Auditor see the linked outcome and grievance. Decided.

## What the beneficiary cannot do

- Approve their own claim or make their category final.
- Change the amount.
- Open a transaction for another household, or a second one for themselves.
- See other households' identity details, phone numbers or amounts.
- Record that cash was handed over. Only the officer does that.

## Former defaults: settled on 2026-10-09

| # | Question | Decision | Status |
|---|---|---|---|
| 1 | Can a registration with no surviving ID be paid before a field check? | No; it needs a documented DSWD field check and accepted government photo ID | Decided |
| 2 | How many households may share one phone number? | Flag above 3; sharing is not automatically rejected | Decided |
| 3 | What do residents see on the approved list? | Name, zone and category only, after residence confirmation | Decided |
| 4 | Who can change a category after approval? | DSWD, with reason, household notification and Auditor visibility; invalidate affected unpaid authorisations | Decided |
| 5 | How long before an unanswered transaction becomes unconfirmed? | 72 hours after handover; later answers remain possible | Decided |
| 6 | Who re-links an account when a phone is lost? | DSWD after ID check; never the barangay; logged | Decided |

**Residence and privacy: Decided.** The household declares its barangay at registration, initially unconfirmed. Barangay residence attestation or DSWD's documented check confirms it; DSWD can check it without an aid claim. The household receives endorsement, category opinion/reasons and officer name. Damage evidence can reach the barangay, identity photos cannot. All files stay in a private off-chain store. One household entitlement is deliberately retained; FACED's separate-family-within-household support is Later.

## What this role's controls do not solve

- **A real, resident person listed as a favour** passes every check. The endorsing Barangay Officer is accountable; the system cannot know the truth.
- **A cut taken after the family leaves the payout site.** The private "received less" answer and the grievance route are the only handles on it.

## Deferred

- A representative claiming for the household head. The record must separate "who claimed" from "household head" so this can be added.
- Appeals when a claim is declined. Meanwhile a declined household may submit the claim again once, with new information, while claims for that disaster are open.

## To verify with DSWD

- A future live dataset integration. The settled checks use AyudaChain data only, with simulated National ID checking. No unified DSWD database integration is promised.
- Exact FACED field mapping. The official process clauses were read first-hand; app self-registration is intake, not completed official administered profiling. See [the process research](../process.md#research-used-in-this-decision).
- Data Privacy Act requirements for storing ID details and photos, and for showing the approved list.

## Data held

| Group | Fields |
|---|---|
| Identity | Name, birth date, ID type, how identity was proven, photo |
| Household | Members, address, barangay, access card number |
| Contact and sign-in | Phone/account linkage; phone authentication Proposed; assisted PIN stored hashed, never printed/logged |
| Per disaster | Claim, category and evidence, Barangay Officer's response, validation decision and who made it, flags, computed amount |
| Per payout | Transaction ID, appended attempts, officer/session/site, step times, input/list versions, confirmation path, closing-answer history, linked grievance |
| On-chain | Handover/outcome hashes and snapshot commitments with opaque references; no names, ID numbers, photos or secrets. See the [consolidated inventory](../process.md#consolidated-commitments) |
