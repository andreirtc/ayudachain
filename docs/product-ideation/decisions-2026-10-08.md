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
| 2.2 | For DSWD emergency cash aid, the list travels up from the barangay and the money travels down from DSWD. They meet at the DSWD regional Field Office |
| 2.3 | The barangay receives no cash budget. It identifies and vouches for families. DSWD's own disbursing officers pay families, or an e-wallet does |
| 2.4 | Relief goods are different: DSWD sets the food pack contents and hands packs to the local government, and barangay officials distribute them |
| 2.5 | The cash amount per family is a formula: 75% of the region's daily minimum wage, rounded up to the nearest ₱10, times a number of days. The days are agreed with the local government per operation and depend on how badly the family was affected |
| 2.6 | The funding needed for an area is derived from its validated list. Nobody allocates a lump sum to a barangay |
| 2.7 | Documented corruption concentrates in who gets onto the list, splitting one family's aid, and cuts collected from families after they are paid. Altering the payout record afterwards, the scenario the README leads with, has little evidence behind it |
| 2.8 | Budget reaches a Field Office through a release order (authority to spend) and a notice to the government bank (the cash). Real documents carry several signatories with roles, a mix of handwritten and digital signatures, and sometimes errors |

Not verified: the exact Central Office bureau names, the day counts per damage category in the current circular, and which DSWD dataset list validation would use.

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
| 4.1 | Version 1 has two roles: the Finance Officer and a read-only auditor | Decided |
| 4.2 | The Finance Officer is the top role in version 1 | Decided |
| 4.3 | A second person approving budget entries is designed for and switched off | Decided |
| 4.4 | Sign-in is deferred | Decided |
| 4.5 | What happens to the existing beneficiary, payout and verify pages while their roles are undesigned: remove them, keep them as a labelled legacy demo, or widen version 1 | Open |
| 4.6 | Fix the fail-open verification and fabricated transaction hashes as part of version 1 | Recommended |

## 5. Finance Officer

Detail: [roles/finance-officer.md](roles/finance-officer.md).

| # | Decision | Status |
|---|---|---|
| 5.1 | Records each fund release per disaster: how much, for what, for which area. Does not set the amount | Decided |
| 5.2 | Every entry needs an uploaded source document, hashed and anchored | Decided |
| 5.3 | Fields are read from the document automatically and only prefill the form; the officer confirms before saving | Decided |
| 5.4 | The ledger is append-only; a correction adds a reversing entry | Decided |
| 5.5 | Screens: disaster tabs, ledger, record a release, entry detail, correct an entry | Decided |
| 5.6 | Can see who has received cash assistance | Decided |
| 5.7 | Never handles the beneficiary list or a family's amount | Recommended |
| 5.8 | Later: certify funds, grant cash advances, track liquidation, record returns, export reports | Recommended |

## 6. Auditor

| # | Decision | Status |
|---|---|---|
| 6.1 | A read-only auditor view ships in version 1 | Decided |
| 6.2 | The auditor belongs to the Commission on Audit, outside the Field Office, and changes no record | Decided |
| 6.3 | Their main screen is an exceptions list produced by automatic checks, plus an evidence view per entry | Recommended |
| 6.4 | Raising audit observations that the Field Office must answer | Later, Recommended |

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
| 7.8 | Sign-in is a one-time code by text or a PIN the person sets. Google sign-in is deferred | Decided |
| 7.9 | Which DSWD role validates the list. A role separate from the Finance Officer is recommended | Open |

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
| 8.15 | The barangay, Finance Officer and disbursing officer can see who has been paid | Decided, with a concern recorded below |

## 9. Deferred by the maintainer

- A representative claiming for the household head.
- Google sign-in.
- Second-person approval of budget entries.
- Sign-in as a whole, for version 1.

## 10. Open questions

1. What happens to the legacy pages in version 1 (4.5).
2. Which DSWD role validates the list (7.9).
3. Whether the barangay should see names of who was paid, or only progress counts. Officials collecting a cut after payout is a documented abuse, and a live list of who was paid and when would help them. The maintainer's stated design gives the barangay this view (8.15).
4. Six defaults for the beneficiary role that were proposed and not yet accepted: whether a registration with no ID waits for a field check, how many households may share a phone number, what residents see on the approved list, who may change a category, how long before a transaction becomes unconfirmed, and who re-links a lost phone. They are listed in [roles/beneficiary.md](roles/beneficiary.md).
5. The remaining roles: barangay endorser, DSWD validator, disbursing officer.
6. Whether to cover the fund-transfer-to-local-government mode (3.4).
7. Which backend to keep (1.6).

## 11. What the design does not solve

Recorded so that AyudaChain is not presented as doing more than it does.

- A real, resident person listed as a favour passes every check. The endorser becomes accountable; the system cannot know the truth.
- A cut taken from a family after they leave the payout site cannot be detected. The private "received less" answer and a grievance route to the Field Office are the only handles on it.
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
