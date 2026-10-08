# Decisions: design session of 2026-10-08

**Status: ideation record.** This logs what the maintainer decided while rethinking AyudaChain around the real DSWD process. The overall picture is not final and nothing here is built. Detail lives in the role files; this file is the index of what was settled, what was only recommended, and what is still open.

Each line is marked **Decided** (the maintainer said so), **Recommended** (advised, not explicitly confirmed), or **Open**.

## 1. Repository and process

| # | Decision | Status |
|---|---|---|
| 1.1 | Improve the existing codebase; do not restart from scratch | Recommended |
| 1.2 | `AGENTS.md` at the repo root governs AI agents; `CLAUDE.md` imports it | Decided |
| 1.3 | Docs are organised as `docs/product/` (the existing product), `docs/product-ideation/` (this redesign), `docs/system/`, `docs/guides/` and `docs/adr/`, with lowercase kebab-case filenames | Decided |
| 1.4 | `docs/product/sitemap.md` and `user-flow.md` describe the code as it runs today, including where the UI claims more than the code does | Decided |
| 1.5 | Agents build nothing from `docs/product-ideation/` until the maintainer says a part is ready | Recommended |
| 1.6 | Which backend to keep (standard-library server or FastAPI) | Open |

## 2. What the real process is

These are findings that corrected earlier assumptions. They were checked against DSWD, the wage board, the disaster law and the government news agency, except where noted.

| # | Finding |
|---|---|
| 2.1 | The Commission on Audit is an independent constitutional body. Its auditors review after the fact, and take no part in budgeting, allocating, approving or paying. It is not the top of the hierarchy |
| 2.2 | For DSWD emergency cash aid, the list travels up from the barangay and the money travels down from DSWD. They meet at the DSWD regional Field Office. Corrected later the same day: reports show the formal list is compiled by the city or municipal social welfare office and signed by the mayor before it reaches DSWD. The design leaves that municipal step out (13.17) |
| 2.3 | The barangay receives no cash budget. It identifies and vouches for families. DSWD's own disbursing officers pay families, or an e-wallet does |
| 2.4 | Relief goods are different: DSWD sets the food pack contents and hands packs to the local government, and barangay officials distribute them |
| 2.5 | The cash amount per family is a formula: 75% of the region's daily minimum wage, rounded up to the nearest ₱10, times a number of days. The days are agreed with the local government per operation and depend on how badly the family was affected |
| 2.6 | The funding needed for an area is derived from its validated list. Nobody allocates a lump sum to a barangay |
| 2.7 | Documented corruption concentrates in who gets onto the list, splitting one family's aid, and cuts collected from families after they are paid. Altering the payout record afterwards, the scenario the README leads with, has little evidence behind it |
| 2.8 | Budget reaches a Field Office through a release order (authority to spend) and a notice to the government bank (the cash). Real documents carry several signatories with roles, a mix of handwritten and digital signatures, and sometimes errors |

Not verified: the exact Central Office bureau names, the day counts per damage category in the current circular, and which DSWD dataset list validation would use. On the last point, see 14.2 and the "To verify" list in [roles/dswd-officer.md](roles/dswd-officer.md).

## 3. Scope

| # | Decision | Status |
|---|---|---|
| 3.1 | AyudaChain is scoped to one DSWD Field Office | Decided |
| 3.2 | Declaring a disaster is out of scope. Disasters come from a seeded list | Decided |
| 3.3 | Cash aid only. Relief goods are a separate chain and are not covered | Recommended |
| 3.4 | DSWD pays families directly. The mode where funds are transferred to a local government to pay out is not covered | Open |
| 3.5 | AyudaChain is the shared record every party reads and writes, in place of reports passed between offices | Decided |
| 3.6 | The Commission on Audit officer sees everything | Decided |

## 4. Version 1

| # | Decision | Status |
|---|---|---|
| 4.1 | Version 1 has two roles: the DSWD Officer, with its funds capabilities only, and a read-only auditor | Decided |
| 4.2 | The DSWD Officer is the top role in version 1 | Decided |
| 4.3 | A second person approving budget entries is designed for and switched off | Decided |
| 4.4 | Sign-in is deferred | Decided |
| 4.5 | What happens to the existing beneficiary, payout and verify pages while their roles are undesigned: remove them, keep them as a labelled legacy demo, or widen version 1 | Open |
| 4.6 | Fix the fail-open verification and fabricated transaction hashes as part of version 1 | Recommended |

## 5. DSWD Officer

Detail: [roles/dswd-officer.md](roles/dswd-officer.md). This role was called the Finance Officer until 5.9.

| # | Decision | Status |
|---|---|---|
| 5.1 | Records each fund release per disaster: how much, for what, for which area. Does not set the amount | Decided |
| 5.2 | Every entry needs an uploaded source document, hashed and anchored | Decided |
| 5.3 | Fields are read from the document automatically and only prefill the form; the officer confirms before saving | Decided |
| 5.4 | The ledger is append-only; a correction adds a reversing entry | Decided |
| 5.5 | Screens: disaster tabs, ledger, record a release, entry detail, correct an entry | Decided |
| 5.6 | Can see who has received cash assistance | Decided |
| 5.7 | Never handles the beneficiary list or a family's amount | Reversed by 5.9 for the list. The role still never types a family's amount |
| 5.8 | Later: certify funds, grant cash advances, track liquidation, record returns, export reports | Recommended |
| 5.9 | The Finance Officer and the planned DSWD validator are one role, the DSWD Officer, to simplify scope. Its capabilities stay grouped as funds and beneficiary list so they can be split later | Decided |
| 5.10 | DSWD Officer accounts are seeded. Managing DSWD staff accounts is out of scope | Decided |
| 5.11 | The disbursing officer stays a separate role, so one account cannot approve a claim and also hand over its cash | Decided |

## 6. Auditor

Detail: [roles/auditor.md](roles/auditor.md).

| # | Decision | Status |
|---|---|---|
| 6.1 | A read-only auditor view ships in version 1 | Decided |
| 6.2 | The auditor belongs to the Commission on Audit, outside the Field Office, and changes no record | Decided |
| 6.3 | Their main screen is an exceptions list produced by automatic checks, plus an evidence view per entry. They can also browse the full ledger | Decided |
| 6.4 | Raising audit observations that the Field Office must answer | Later, Recommended |
| 6.5 | Version 1 has six exceptions: not anchored, document mismatch, corrected, amount overridden, words and figures disagree, duplicate document | Decided |
| 6.6 | After version 1 the same list takes the flags produced by the other roles, and every grievance | Decided |
| 6.7 | "Sees everything" includes personal data. ID numbers and photos show only on opening a record, and each view is logged | Decided |
| 6.8 | The auditor can re-run the integrity check on any entry. Export is Later | Decided |
| 6.9 | The auditor writes nothing in version 1. Marks and notes arrive with audit observations | Decided |
| 6.10 | An access log records what the auditor viewed. It is not shown to the Field Office | Decided |
| 6.11 | The auditor's account is seeded and covers the one Field Office | Decided |

## 7. Beneficiary

Detail: [roles/beneficiary.md](roles/beneficiary.md). This role is not in version 1.

| # | Decision | Status |
|---|---|---|
| 7.1 | Beneficiaries register themselves through AyudaChain | Decided |
| 7.2 | Registration has two stages: a household registry at any time, then a claim per disaster | Decided |
| 7.3 | The barangay sends or endorses the list through AyudaChain | Decided |
| 7.4 | DSWD validates the list against its own data | Decided |
| 7.5 | The approved list is shown to the barangay's own residents, as a control against false entries | Decided |
| 7.6 | The beneficiary sees their approved amount beforehand, through AyudaChain | Decided |
| 7.7 | Identification: the National ID first, or another government photo ID; the officer compares the person with the photo | Decided |
| 7.8 | How beneficiaries sign in is on hold. A one-time code by text and a PIN are possibilities only. Google sign-in is deferred | On hold; was Decided |
| 7.9 | The DSWD Officer validates the list (5.9). The earlier recommendation of a separate role was not taken | Decided |

## 8. The payout transaction

| # | Decision | Status |
|---|---|---|
| 8.1 | A payout is a two-party transaction with its own ID: the recipient opens it, the officer confirms it and hands over the cash, the recipient closes it | Decided |
| 8.2 | The officer checks a valid ID before proceeding | Decided |
| 8.3 | The officer cannot mark the cash as handed over without a one-time code from the recipient | Decided |
| 8.4 | The transaction code is separate from the sign-in secret, is generated when the transaction is opened, and is never sent in advance | Decided |
| 8.5 | The officer types no amount; it is computed and shown to the recipient | Decided |
| 8.6 | One transaction per entitlement; a paid household cannot open another | Decided |
| 8.7 | The server enforces the order of steps | Decided |
| 8.8 | Closing answers are received in full, received less, and not received | Decided |
| 8.9 | A transaction that is never closed becomes "unconfirmed" and is neutral, not held against the recipient | Decided |
| 8.10 | The recipient is notified that a payout is happening and opens the transaction after signing in; they scan nothing | Decided |
| 8.11 | The officer is responsible for a working connection at the site; there is no offline mode | Decided |
| 8.12 | A recipient with no phone confirms with both an ID check and a PIN on the officer's device | Decided |
| 8.13 | Assisted payouts get an exit check by a second staff member. Staffing it is DSWD's matter, outside the software | Decided |
| 8.14 | A recipient with a basic phone does everything by text | Recommended |
| 8.15 | The DSWD Officer and disbursing officer can see who has been paid. The barangay sees progress counts only: approved, paid, remaining | Decided; narrowed for the barangay by 13.14 |

## 9. Deferred by the maintainer

- A representative claiming for the household head.
- Google sign-in.
- Second-person approval of budget entries.
- Sign-in as a whole, for version 1.
- How beneficiaries sign in (7.8).
- How a Barangay Officer's email is verified (13.4).

## 10. Open questions

1. What happens to the legacy pages in version 1 (4.5).
2. Closed: the DSWD Officer validates the list (7.9).
3. Closed: the barangay sees progress counts only (13.14).
4. Six defaults for the beneficiary role that were proposed and not yet accepted: whether a registration with no ID waits for a field check, how many households may share a phone number, what residents see on the approved list, who may change a category, how long before a transaction becomes unconfirmed, and who re-links a lost phone. They are listed in [roles/beneficiary.md](roles/beneficiary.md).
5. Closed: all five roles now have a role file.
6. Whether to cover the fund-transfer-to-local-government mode (3.4).
7. Which backend to keep (1.6).
8. Whether to model the municipal step between the barangay and the Field Office (13.17).

## 11. What the design does not solve

Recorded so that AyudaChain is not presented as doing more than it does.

- A real, resident person listed as a favour passes every check. The endorsing Barangay Officer becomes accountable; the system cannot know the truth.
- A cut taken from a family after they leave the payout site cannot be detected. The private "received less" answer and a grievance route to the Field Office are the only handles on it.
- One DSWD Officer account can record the money, set the amount inputs and approve who receives it. The merge in 5.9 removes a separation of duties a real Field Office keeps.
- No outside data says who was affected by a disaster. The automatic checks find duplicates; whether a household was affected rests on the Barangay Officer's attestation.
- Version 1 by itself addresses none of the documented corruption points. It establishes the document-backed, append-only pattern the later controls reuse.

## 12. Key sources

- [Republic Act No. 10121, disaster risk reduction law](https://www.officialgazette.gov.ph/2010/05/27/republic-act-no-10121/)
- [DSWD MC No. 24 s. 2025, emergency cash transfer guidelines](https://batasnatin.com/laws/mc-mc-no-24-s-2025)
- [DSWD: emergency cash transfer rollout](https://www.dswd.gov.ph/dswd-prepares-to-rollout-emergency-cash-assistance-for-tino-hit-families/)
- [DSWD: family food pack contents](https://www.dswd.gov.ph/dswd-chief-reiterates-warning-against-tampering-of-family-food-packs/)
- [National Wages and Productivity Commission: Region V](https://nwpc.dole.gov.ph/region-v/)
- [DILG: barangay officials charged over 2020 subsidy distribution](https://www.dilg.gov.ph/news/DILG-397-barangay-officials-facing-criminal-charges-for-anomalous-SAP-distribution-a-total-of-663-under-investigation/NC-2020-1199)
- [PNA: DSWD probes cash aid cut by Iloilo village officials](https://www.pna.gov.ph/articles/1263152)
- [COA Circular 97-002 on cash advances](https://rgao.upm.edu.ph/media/2023/10/COA-C97-002-Cash-Advances-2-months-cash-flow.pdf)
- [DBM: fund transfers to operating units](https://jur.ph/law/summary/fund-transfers-for-operating-units)
- [PSA: offline verification of the National ID](https://psa.gov.ph/content/psa-unveils-philsys-check-philid-verification-system)
- [PSA: DSWD to use the National ID for its programs](https://psa.gov.ph/content/dswd-use-philsys-delivery-4ps-aics-and-other-programs)
- [DepEd Caraga RM No. 0364 s. 2026, a real release memorandum](https://caraga.deped.gov.ph/publications/issuances/rm-no-0364-s-2026-sub-allotment-release-order-sub-aro-for-special-needs-education-program/pdf)
- [SunStar Davao: who compiles and signs the list](https://www.sunstar.com.ph/davao/dswd-davao-posts-68-ect-completion-rate)
- [SunStar Cebu: DSWD tells LGUs to verify "bloated" lists](https://www.sunstar.com.ph/cebu/dswd-tells-lgus-to-verify-bloated-lists)
- [DSWD Legal Service opinion LO 2024-045](https://batasnatin.com/laws/lo-lo-2024-045)
- [Bacolod City: payout in batches](https://bacolodcity.gov.ph/mayor-gasataya-thanks-dswd-for-immediate-release-of-financial-aid-for-bacolod-typhoon-hit-families/)
- [Negros Now Daily: discrepancies referred back to the LGU](https://negrosnowdaily.com/?p=39803)

## 13. Barangay Officer

Detail: [roles/barangay-officer.md](roles/barangay-officer.md). Settled in a second session on 2026-10-08. This role is not in version 1. It is numbered 13 so that earlier references keep their numbers.

| # | Decision | Status |
|---|---|---|
| 13.1 | The "barangay endorser" is renamed Barangay Officer. It shares only its name with the role in the running code | Decided |
| 13.2 | Each officer is a named person with their own account, tied to one barangay | Decided |
| 13.3 | Anyone the Punong Barangay nominates and a DSWD Officer approves can hold it. The account records their position | Decided |
| 13.4 | Officers sign in with an email for now. Verification is decided later | Decided |
| 13.5 | The officer responds to each claim individually, attesting that the household lives in the barangay and was affected | Decided |
| 13.6 | The officer cannot block a claim. One that is not endorsed still reaches DSWD with a required reason | Decided |
| 13.7 | The officer confirms or disputes the stated category. The DSWD Officer decides it | Decided |
| 13.8 | The officer may register a household on its behalf. It is flagged, and that officer cannot respond to the claim | Decided |
| 13.9 | An officer cannot respond to a claim from their own household; another officer does. For other relatives the officer ticks a declaration and the claim is flagged | Decided |
| 13.10 | A barangay needs two officers to endorse. A claim where every officer is barred goes up marked "no eligible endorser" | Decided |
| 13.11 | The Field Office sets an endorsement window per disaster. A claim with no response goes up marked "no barangay response" | Decided |
| 13.12 | Responses are never edited. A change is a reply attached to the entry it answers, allowed until the DSWD Officer decides the claim | Decided |
| 13.13 | Any officer responds to claims; only the Punong Barangay's account sends a batch, with the council resolution uploaded and hashed. Several batches per disaster are allowed, and each is anchored | Decided |
| 13.14 | The officer sees payout progress as counts only, not names. Narrows 8.15 | Decided |
| 13.15 | The officer has no step in the payout transaction, and sees no grievance or list challenge | Decided |
| 13.16 | The DSWD Officer can refer a claim back; the officer must answer. Late claims go into a later batch until the Field Office closes claims | Decided |
| 13.17 | The batch goes straight from the barangay to the Field Office. The municipal step in the real process is left out and recorded as a known gap | Decided |
| 13.18 | The household sees the response, the reason and the officer's name. The DSWD Officer and the auditor see figures per officer as flags for review | Decided |
| 13.19 | The role is built later, with the Beneficiary role | Decided |

## 14. DSWD Officer: beneficiary list

Detail: [roles/dswd-officer.md](roles/dswd-officer.md). Settled in a third session on 2026-10-08. None of this is in version 1.

| # | Decision | Status |
|---|---|---|
| 14.1 | Every DSWD Officer handles every barangay under the Field Office, from one shared queue | Decided |
| 14.2 | Validation is five duplicate checks on data AyudaChain holds, including near-matches on names and addresses. The National ID check is a simulated, labelled stand-in. Matching across regions is out of scope | Decided |
| 14.3 | Checks raise flags and never decide a claim | Decided |
| 14.4 | The checks are a plain script, called "automatic checks" and not AI. A model, with Jev from TypeSafe AI as the named candidate, is recorded as Later | Decided |
| 14.5 | A claim is approved, declined with a reason, or referred back. The household is told the outcome and the reason | Decided |
| 14.6 | Claims may be approved in bulk only where each is endorsed, unflagged and has an undisputed category | Decided |
| 14.7 | A declined household may submit again once while claims are open. A formal appeal stays deferred | Decided |
| 14.8 | The officer publishes the approved list per barangay as an anchored snapshot. Later batches produce new versions | Decided |
| 14.9 | A challenge before the payout can reverse an approval, with a reason. After the payout it becomes a note for the auditor | Decided |
| 14.10 | The officer records the amount inputs per disaster, each with its document. This confirms capability 9, which was Proposed | Decided |
| 14.11 | A disaster uses one of two modes: the wage formula, or a fixed amount per category | Decided |
| 14.12 | The inputs lock when the first approved list is published. A later change recalculates every unpaid entitlement and notifies the household; paid ones are untouched and the difference is listed | Decided |
| 14.13 | The same officer may enter the inputs and approve claims. The inputs are shown to the auditor and to households | Decided |
| 14.14 | The approved total is shown beside the remaining balance. Exceeding it warns and does not block | Decided |
| 14.15 | An officer cannot decide a claim from their own household | Decided |
| 14.16 | Grievances are a list with a status and notes. The auditor sees all; the barangay sees none | Decided |
| 14.17 | Each claim decision stores who made it and an empty "confirmed by", as 4.3 does for budget entries | Decided |
| 14.18 | The household registry and claim are meant to match DSWD's FACED form. Its fields are still to be read | Decided |

## 15. Disbursing Officer

Detail: [roles/disbursing-officer.md](roles/disbursing-officer.md). Settled in a fourth session on 2026-10-08. This role is not in version 1. The payout steps themselves are in section 8.

| # | Decision | Status |
|---|---|---|
| 15.1 | A named DSWD staff member with an email sign-in. A DSWD Officer creates and deactivates the account | Decided |
| 15.2 | A DSWD Officer sets up a payout session: one disaster, one barangay, one date, with named disbursing officers. An officer acts only on that session's approved list, while it is open | Decided |
| 15.3 | The officer sees the head's name, photo, ID type, category and computed amount, and nothing else about the household | Decided |
| 15.4 | When the ID check fails the officer stops the transaction with a reason. The entitlement stands and a DSWD Officer reviews it | Decided |
| 15.5 | The exit check on an assisted payout is done by another disbursing officer on the same session. It is not a separate role | Decided |
| 15.6 | An officer cannot pay their own household | Decided |
| 15.7 | A handover cannot be undone. The officer may add a note | Decided |
| 15.8 | Cash carried out and brought back is not recorded yet. It waits for cash advances and liquidation. The session shows a computed total paid | Decided |
