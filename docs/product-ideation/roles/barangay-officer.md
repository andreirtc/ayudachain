# Role: Barangay Officer

**Status: ideation, not built, and not part of version 1.** The overall product picture is not final, so this may still change. Capabilities settled in the design session of 2026-10-08. For what the app does today, read [the current user flow](../../product/user-flow.md).

Each item is marked **Decided** (confirmed by the maintainer) or **To verify** (depends on a fact not yet checked with DSWD).

**Decided, process session of 2026-10-09.** [The end-to-end process](../process.md) settles handoffs, state transitions and exceptions across all five roles. Its additions are indexed in decisions section 16; none is permission to build.

This role was first called the "barangay endorser". It shares only its name with the `Barangay Officer` role in the running code, which reviews and deletes beneficiaries and confirms payouts. The redesigned role does none of those.

## Who this is

A person nominated by the Punong Barangay and approved by a [DSWD Officer](dswd-officer.md). The role is not tied to one position: the Punong Barangay, a kagawad, the secretary or a health worker can hold it. The account records the person's actual position.

The Barangay Officer answers one question: **does this household live here, and was it affected by this disaster?** The officer gives an opinion on each claim. DSWD decides.

The role ships with the [Beneficiary](beneficiary.md) role, since each is useless without the other.

## Account

| Rule | Status |
|---|---|
| Each officer is a named person with their own account, tied to one barangay | Decided |
| A barangay may have several officers. Each sees only their own barangay | Decided |
| A barangay needs at least two active officers before it can endorse | Decided |
| A DSWD Officer approves and deactivates accounts | Decided |
| DSWD enters the Punong Barangay's documented nomination, including the initial accounts; nominator, entered-by and approver are recorded separately | Decided |
| A deactivated account can do nothing further. Its past responses stay on record under its name | Decided |
| The officer signs in with an email for now. How the email is verified is decided later | Decided |
| The same person may also hold a beneficiary record | Decided |

## Capabilities

| # | Capability | Status |
|---|---|---|
| 1 | Respond to each claim from their barangay individually: endorsed or not endorsed | Decided |
| 2 | Confirm or dispute the damage category the household stated. The DSWD Officer decides the category | Decided |
| 3 | Register a household on its behalf when it cannot do so itself (an assisted registration) | Decided |
| 4 | Send a batch of responded claims to DSWD. Only the Punong Barangay's account can send | Decided |
| 5 | Answer a claim that the DSWD Officer refers back | Decided |
| 6 | Add a withdrawal or reversal to an earlier response, as a reply on the claim | Decided |
| 7 | See DSWD's decision on each claim from their barangay | Decided |
| 8 | See the approved list as residents see it | Decided |
| 9 | See payout progress as counts: approved, paid, remaining | Decided |

## Endorsement

- **The attestation is fixed.** Endorsing states two facts: the household lives in this barangay, and it was affected by this disaster. The officer does not vouch for identity; the ID check covers that. Decided.
- **The category opinion is recorded separately** from the attestation. Decided.
- **Endorsing needs nothing beyond the attestation.** Not endorsing, or disputing the category, needs a written reason. A photo is optional in every case. Decided.
- **The officer cannot block a claim.** A claim that is not endorsed still reaches DSWD, marked "not endorsed" with its reason. Decided.
- **The officer cannot stall a claim.** The Field Office sets a response duration per disaster; every submitted claim starts its own deadline. At expiry the system forwards it with "no barangay response" where applicable. Responded claims with no signed submission are forwarded with a distinct missing-submission flag and their actual responses. Decided.
- **A declared barangay is unconfirmed at registration.** The residence attestation or a documented DSWD check establishes residence; self-declaration is not permission to read a residents' list. DSWD opens claim intake explicitly for selected barangays. Decided.
- **Late claims are still taken,** into a later batch, until the Field Office closes claims for that disaster. Decided.

## Conflicts of interest

| Situation | Rule | Status |
|---|---|---|
| A claim from the officer's own household | The officer cannot respond to it. Another officer does | Decided |
| A claim from a relative outside the household | The officer may respond, and must tick a "related to this household" declaration. The claim is flagged for the DSWD Officer | Decided |
| A claim the officer registered on the household's behalf | The officer cannot respond to it. Another officer does | Decided |
| Every active officer is barred from a claim | The claim goes to DSWD marked "no eligible endorser". This applies per claim, whatever the number of officers | Decided |

## Responses are a thread

```
Claim
└─ Response: endorsed (Officer A)
   └─ Reply: withdrawn, with reason (Officer A)
      └─ Reply: referred back, with question (DSWD Officer)
         └─ Reply: answer, with reason (Officer B)
```

- **Nothing is edited.** A change is a new entry attached to the one it answers, like a reply to an email. Decided.
- **The officer can reply until a final approval or decline.** A referral keeps the thread open; a permitted resubmission creates a new version/thread without editing the decline. Decided.
- **A referred-back claim gets a fresh deadline.** No answer returns to DSWD with an explicit missing-response result. Existing referrals/review continue after intake closes; closure bars new claims/resubmissions. Decided.

## Sending a batch

- **Any officer responds to claims; only the Punong Barangay's account sends.** This mirrors the real signature on a barangay's list. It is the one action where the officer's position matters. Decided.
- **The barangay council's resolution is uploaded with the batch** and hashed. Decided.
- **A batch is a fixed snapshot** of the claims responded to, with the sender's name and the time. Its hash is anchored on-chain. Decided.
- **Several batches per disaster are allowed.** Decided.
- **An unavailable endorser or missing sender cannot veto delivery.** Fewer than two active officers or all officers being barred routes the claim as "no eligible endorser", with the staffing/conflict reason. Deadline forwarding is a clearly labelled system snapshot, separately hashed/anchored, with no invented council resolution or Punong Barangay signature. Decided.
- **Submitted snapshots never change.** Later replies remain in the thread and are considered by DSWD against their own versions; they do not overwrite the batch. Failed batch/fallback anchoring is explicit and retried without withholding the claim from DSWD. Decided.

In practice lists are not sent once: payouts run in batches, missed names are added in later rounds, and late submission is a reported cause of families being left out.

## What the officer sees of a claim

| Shown | Not shown |
|---|---|
| Household head's name | ID number |
| Household members' names | Photo |
| Address and zone | Phone number |
| Stated category | Computed amount |
| The household's description of the damage and damage evidence | |

## What the household sees

The household is told the response (endorsed or not endorsed), the category opinion, required reasons and the officer's name. An official acting in an official capacity is named, and the household needs the reason to challenge it with DSWD. Decided.

**Photo means identity photo in the restriction above.** Relevant damage evidence is visible to the barangay; identity photos, ID numbers and contact details are not. Uploaded evidence lives in the shared private off-chain store. Decided.

**The residents' approved list** is name, zone and category, with no amount, ID or phone, available only after residence confirmation. The officer sees the same list; payout progress remains aggregate counts. "Paid" counts recorded handovers, not proof of full receipt, and reveals no private closing answers or grievance. Decided.

## Oversight

The DSWD Officer and the auditor see figures per officer:

- share of claims not endorsed
- category disputes, and how many the DSWD Officer overturned
- assisted registrations
- relative declarations
- missed deadlines

These are flags for a person to review. Nothing is penalised automatically. Decided.

## What the Barangay Officer cannot do

- Approve or reject a claim, or make a category final.
- Stop a claim from reaching DSWD, by refusing or by not responding.
- Respond to a claim from their own household, or one they registered.
- Edit or delete a response.
- See who has been paid, or when. They see counts only.
- Take any step in a payout transaction.
- See a grievance, or who challenged an entry on the approved list.
- Re-link a household's account to a new phone.
- See or change any amount.

## What this role's controls do not solve

- **A real resident listed as a favour** passes every check. The endorsing officer is named and accountable; the system cannot know the truth.
- **Officers who agree among themselves.** Handing a conflicted claim to another officer only helps if that officer is independent.
- **Pressure applied in person.** An officer can lean on a household outside the software, for example over a "not endorsed" response the household would otherwise challenge.

## To verify with DSWD

- **The municipal step.** Reports show the formal list is compiled by the city or municipal social welfare office, endorsed by the local disaster office and signed by the mayor. This design sends the barangay's batch straight to the Field Office and leaves the municipal step out. Recorded as a known gap.
- **Exact institutional alignment.** Official MC24 s2025 was read first-hand in the process session and supports direct barangay proposals with Chairperson signature/resolution subject to Field Office validation. This app's claim-batch and nomination mechanisms remain product choices; the real formal signatories/municipal processing are not fully modelled. See [the research and outside boundaries](../process.md#research-used-in-this-decision).
- **Whether a barangay with fewer than two willing officers is realistic,** and what happens there today.

## Data held

| Group | Fields |
|---|---|
| Account | Name, position, barangay, email, who nominated and who approved, active or deactivated |
| Per response | Claim, officer, endorsed or not endorsed, category opinion, reason, optional photo, relative declaration, time, the entry it replies to |
| Per batch | Barangay, disaster, sender, time, claim/response versions, council resolution and its hash; system intake snapshots separately labelled without a barangay sender |
| On-chain | Signed-batch/resolution hashes and separately labelled system fallback hashes, with opaque references. No names; see the [consolidated inventory](../process.md#consolidated-commitments) |

## Sources

- [SunStar Davao: DSWD-Davao posts 68% ECT completion rate](https://www.sunstar.com.ph/davao/dswd-davao-posts-68-ect-completion-rate)
- [SunStar Cebu: DSWD tells LGUs to verify "bloated" lists](https://www.sunstar.com.ph/cebu/dswd-tells-lgus-to-verify-bloated-lists)
- [DSWD Legal Service opinion LO 2024-045](https://batasnatin.com/laws/lo-lo-2024-045)
- [DSWD MC No. 24 s. 2025, emergency cash transfer guidelines](https://batasnatin.com/laws/mc-mc-no-24-s-2025)
- [Bacolod City: payout for typhoon-hit families](https://bacolodcity.gov.ph/mayor-gasataya-thanks-dswd-for-immediate-release-of-financial-aid-for-bacolod-typhoon-hit-families/)
- [Negros Now Daily: 126,930 Negrenses receive ECT assistance](https://negrosnowdaily.com/?p=39803)
