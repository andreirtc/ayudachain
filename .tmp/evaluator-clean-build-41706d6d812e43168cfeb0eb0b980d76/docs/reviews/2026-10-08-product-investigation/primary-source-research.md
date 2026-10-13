# Primary-source research for AyudaChain

Research date and source access date: **2026-10-08, Asia/Manila**. This is an external-fact investigation, not a legal compliance opinion, an institutional endorsement, or evidence of user adoption. No production code, contracts, dependencies, or GitHub records were changed for this research.

The strongest findings are that a universal statutory ₱5,000 household entitlement is contradicted by official ECT material; DAFAC is a real assistance-monitoring instrument but the repository's `DFC-2026-XXXX` identifiers and QR flow have no demonstrated official integration; and an anchored hash establishes consistency with committed data, not that a real household received its entitlement. The public sources support some actual deduction and duplicate-payment concerns, but do not establish the repository's asserted frequency, particular invented scenarios, or universal audit delay.

## Scope and evidence limits

Reviewed repository claims in `README.md`, `docs/system/architecture.md`, and `docs/system/blockchain-spec.md`, following `AGENTS.md`. `docs/product/prd.md` was absent when this research began. Product demand, target institution, acceptance criteria, and operating requirements therefore remain unvalidated rather than inferred from the demo.

Sources below are official DSWD, COA, National Privacy Commission (NPC), NIST, IETF, Hardhat, Ethereum, and Polygon publications or endpoints. An official press release establishes what the agency reported, not that an allegation was adjudicated. An old manual establishes historical procedure, not necessarily the rule in force today. “No evidence found” means these reviewed sources and targeted searches did not substantiate a claim; it is not proof that no local practice or integration exists.

**Current-rule caveat:** the full DSWD MC 11/2025 ECT guidelines were retrieved and inspected, including the signed date and scanned pages. A later official DSWD MC 12/2026 expressly identifies an amendment, MC 24/2025. The full amendment was not retrieved. The formula and procedures below are therefore attributed to **MC 11/2025 as issued**, and should not be presented as a complete certification of October 2026 operational rules. [DSWD MC 11/2025](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2025/07/MC-No.-11-S-2025.pdf), [DSWD MC 12/2026, p. 5](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2026/05/MC-No.-12-S-2026.pdf)

## Program and entitlement findings

ECT and AICS should not be treated as one universal cash benefit. ECT is post-disaster, unconditional cash assistance for relief and early recovery, with activation conditions including a declared state of calamity and functioning markets. AICS addresses different crisis needs, including medical, burial, transportation, education, food, and other assistance. The selected program and approved assistance determine the relevant workflow. [DSWD ECT program](https://drm.dswd.gov.ph/emergency-cash-transfer/), [DSWD AICS program](https://aics.dswd.gov.ph/aics-program/)

MC 11/2025, VI.C, specifies a daily base of `ceil(0.75 × applicable regional daily minimum wage)` at project-proposal approval, multiplied by assessed days. Its categories distinguish severe and slight impact, with funding-dependent limits of 90 and 45 days respectively and additional rules. VII.A makes a digital beneficiary transaction account the primary modality, with certified direct cash disbursement when digital payment is infeasible. The guidelines assign masterlist endorsement/support to LGUs, validation and implementation responsibilities to DSWD Field Offices, and payment/reporting functions to service providers. FACED and identity or alternative supporting documents inform claimant validation; a family representative may be authorized. These are approved, assessed payments, not an entitlement derived from possession of a card alone. [DSWD MC 11/2025, pp. 9, 12–16, 19–20](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2025/07/MC-No.-11-S-2025.pdf)

Two independent official examples reinforce the distinction: DSWD reported ECT of **₱9,960 per family** in Davao Oriental in March 2024; its October 2025 revised-ECT announcement describes assistance differentiated by disaster impact and family needs. AICS also has different cash and guarantee-letter arrangements, not a universal ₱5,000 award. [DSWD Davao Oriental payout](https://www.dswd.gov.ph/dswd-gives-cash-aid-to-2k-disaster-hit-families-in-davao-oriental/), [DSWD revised ECT announcement](https://www.dswd.gov.ph/dswd-makes-emergency-cash-transfer-more-responsive-to-needs-of-disaster-hit-families/), [DSWD AICS cash-aid announcement](https://www.dswd.gov.ph/dswd-assures-continuous-aid-under-the-aics-program/)

**Product inference:** a ₱5,000 synthetic demo award is possible, but should be named as that demo's award. A production amount needs provenance: program, approving authority, approved proposal or assessment, calculation, and payable amount. Sources do not support a universal statutory ceiling or the general fund-flow assumption that every ECT/AICS payment passes from DSWD through an LGU cashier.

## DAFAC, FACED, identifiers, and QR claims

DAFAC expands to **Disaster Assistance Family Access Card**. DSWD MC 12/2024 enhances it into **Family Assistance Card in Emergencies and Disasters (FACED)**. Its functions include profiling affected families and recording assistance for planning and duplicate-assistance control. The circular provides serial-number and **bar-code** controls, retaining the serial when a card is replaced or updated. Its annex has profile fields and an assistance history recording date, disaster, provider, type, quantity/cost, and acknowledgement. Its family classifications also show why a family is not defined by matching a name or address alone. [DSWD MC 12/2024, pp. 1–2, 9–11 and annex](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/issuances/MCs/MC_2024-012.pdf)

The reviewed circular and blank form do **not** substantiate a mandatory nationwide `DFC-2026-XXXX` format, this repository's issued IDs, or official AyudaChain integration. A bar code described in a circular does not prove that the demo's QR encodes an authorized government card or interoperates with a government registry. This is **no evidence found**, not a finding that DSWD never uses QR codes. Current AICS FAQs reference DAFAC and/or FACED, so implementation may include a transition or local variations requiring confirmation. [DSWD AICS FAQs](https://aics.dswd.gov.ph/about-us/faqs/)

There is an existing official digital workflow to investigate: DSWD Field Office XI reported an **ECT Offline Payout System**, introduced June 9, 2025, supporting validation, updates, payroll and reporting. That publication does not establish a public integration interface or a nationwide requirement to use this system. [DSWD XI offline payout announcement](https://fo11.dswd.gov.ph/2025/09/%F0%9D%97%97%F0%9D%97%A6%F0%9D%97%AA%F0%9D%97%97-%F0%9D%97%AB%F0%9D%97%9C-%F0%9D%97%A5%F0%9D%97%BC%F0%9D%97%B9%F0%9D%97%B9%F0%9D%98%80-%F0%9D%97%A2%F0%9D%98%82%F0%9D%98%81-%F0%9D%97%98%F0%9D%97%96/)

## Payment, liquidation, and audit evidence

The 2022 ECT operations manual describes authorized disbursement, masterlists/payroll, claimant acknowledgement, fund-transfer arrangements, and liquidation. Its model LandBank agreement distinguishes paid/unpaid amounts and calls for a witness and signed payroll after cash receipt. It predates MC 11/2025 and is historical context, not an assertion that all details remain mandatory. This demonstrates that evidence of authorization, identity, actual payment, and remaining funds is broader than a generated receipt hash. [DSWD ECT operations manual, payout/liquidation sections and Annex 6A](https://www.dswd.gov.ph/download/publications/operations_manual_for_the_implementation_of_the_emergency_cash_transfer_ect_during_disasters/02012022_ECT_OM_A4_print_FINAL.pdf)

COA's published cash-examination reference distinguishes liquidation from subsequent auditing. Its older circular includes a 30-day audit period after receipt of the accountant's report and documents; another COA documentary reference ties special-purpose liquidation to completion of its purpose. These provisions are **not** measured current disaster-relief turnaround times. COA's current FAQ points users to Circular 2023-004 for documentary requirements, whose complete text was not inspected here. [COA cash-examination reference, §§5.4–5.8](https://www.coa.gov.ph/wp-content/uploads/ABC-Help/Cash_Examination_Manual/an1.3.5.htm), [COA liquidation reference](https://www.coa.gov.ph/wp-content/uploads/ABC-Help/DRCGT/DRCGT.6.htm), [COA documentary-requirements FAQ](https://www.coa.gov.ph/FAQS/what-are-documentary-requirements-in-the-grant-for-common-government-transactions/)

**Claim assessment:** no primary evidence found for a universal **6–12 month** COA disaster-payout audit delay or for accountability only starting at such an audit. This is not a claim that delays never occur. Payout acknowledgement, cash-advance liquidation, reconciliation, individual audit work, annual audit reporting, and public publication are separate events. The target office must supply actual event timestamps and accepted documentary/export requirements before a delay-reduction claim can be tested. No source inspected establishes that COA accepts an AyudaChain hash in place of prescribed payment and liquidation records.

## Fraud mechanisms and the claim boundary

DSWD reported alleged **post-distribution deductions** from ₱10,000 AICS payments in Iloilo: beneficiaries allegedly retained ₱2,000 after ₱8,000 was taken. In December 2025 it reported filing administrative charges and continuing evidence gathering for criminal action. These are documented agency allegations/actions, not final adjudications or nationwide prevalence estimates. [DSWD November 2025 investigation](https://www.dswd.gov.ph/dswd-condemns-aics-cash-aid-cut-by-iloilo-barangay-officials-vows-immediate-probe/), [DSWD December 2025 charges](https://www.dswd.gov.ph/dswd-chief-files-admin-charges-vs-local-officials-involved-in-aics-corruption/)

DSWD's response to COA's 2022 AICS observations acknowledges duplicate-payment/documentation concerns and also describes circumstances in which repeated aid may address a different crisis. Its earlier PhilSys announcement identifies ghost/duplicate avoidance as an identification-system objective; that announcement establishes neither its nationwide rollout nor the prevalence of ghost claimants. [DSWD AICS documentation response](https://www.dswd.gov.ph/dswd-continues-improvements-in-the-streamlining-of-aics-documentary-requirements/), [DSWD PhilSys announcement](https://old.dswd.gov.ph/dswd-to-use-philsys-for-identification-of-4ps-aics-and-other-program-beneficiaries/)

The README's particular slight-name-change/across-barangay ghost mechanism and its ₱5,000-to-₱2,000 altered-liquidation story were **not externally verified**. Treat them as labelled synthetic threat scenarios. Repeated names, addresses, or assistance are review signals; they do not establish ineligibility or fraud without the relevant family/program/event rules and human assessment.

**Technical inference:** locking the recorded award cannot prevent a cashier from entering a false acknowledgement, paying less cash, or demanding money back after a full payment. Those paths can leave an unchanged, correctly anchored receipt. Independent payout evidence, beneficiary confirmation and grievance handling address a different problem from detecting edits after commitment. MC 11/2025 also includes payout grievance desks and investigation/reporting responsibilities. [DSWD MC 11/2025, pp. 22–23](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2025/07/MC-No.-11-S-2025.pdf)

## Privacy and public transparency

The Data Privacy Act regulates personal-information processing, lawful grounds, sensitive information, security and data-subject rights. Storing names off-chain does not itself settle any of those questions. Section 4(c)'s financial-benefit wording is not a general exemption for every field in an aid database. [RA 10173, §§3–4, 11–13, 16, 20](https://privacy.gov.ph/data-privacy-act-/)

NPC Advisory Opinion 2020-026 explains conditional lawful public disclosure of aid-beneficiary information, including names, amounts and broad location, while requiring attention to purpose and proportionality. It discusses omitting names or using pseudonyms when the purpose can be met that way; an exception or lawful basis does not authorize unnecessary information. Opinion 2020-019 identifies details such as birth date, civil status, religion and government ID as excessive for its SAP publication context. These are contextual opinions, not blanket authorization for all AyudaChain screens, exports or fraud labels. [NPC Opinion 2020-026](https://privacy.gov.ph/wp-content/uploads/2020/10/Redacted-Advisory-Opinion-No.-2020-026.pdf), [NPC Opinion 2020-019](https://privacy.gov.ph/wp-content/uploads/2020/10/Redacted-Advisory-Opinion-No.-2020-019.pdf)

**Product inference:** the controller/DPO should decide and document the audience, purpose, lawful basis, minimum fields, access rules, retention and correction process for each public view and export. Opaque IDs and hashes still warrant linkage analysis when they can be joined to identifiable off-chain records; “off-chain” should not be used as a compliance certificate. A public recipient total, private case file, public verification proof and publicly identifying anomaly accusation have different purposes and risks. This investigation does not determine legal compliance.

## What a blockchain anchor can establish

NIST describes blockchain as tamper-evident/resistant under its operating assumptions and discusses the external-data/oracle problem. A hash match can support “these bytes match the committed bytes.” It does not validate an original assertion about identity, eligibility, physical cash handover, or coercion. Authorized writers can commit false records. Evidence must identify what was committed, by whom, when, and under which independent chain assumptions. [NIST IR 8202, especially §7.3](https://nvlpubs.nist.gov/nistpubs/ir/2018/NIST.IR.8202.pdf)

Hardhat explicitly provides a local development network, with reset and state-manipulation tools. If one operator controls the database, writer key and local node, the chain is not an independent external witness against that operator. A public chain provides different consensus/history assurances, while operator input and a verifier's RPC connection remain trust surfaces. A matching local-chain demo result should state that scope. [Hardhat Network overview](https://v2.hardhat.org/hardhat-network/docs/overview), [Hardhat Network reference](https://v2.hardhat.org/hardhat-network/docs/reference)

The README's “permanent mathematical proof of payout” and the architecture's receipt-authenticity language exceed what the hash alone establishes. A more defensible statement is evidence that a particular receipt representation was committed and has not changed relative to that commitment, with explicit chain identity and unresolved/unavailable states. Genuine identity and payment evidence are separate dependencies.

## Smaller blockchain footprint: conditional alternatives

These are design inferences for investigation, not implemented features or validated institutional preferences.

| Option | Evidence it can support | Main tradeoff to validate |
|---|---|---|
| Signed append-only off-chain records plus independently retained checkpoints/exports | Authorship and changes relative to a checkpoint, subject to key custody and witness independence | Avoids chain transactions; requires a credible external recipient/retainer of checkpoints and reliable source-record availability. No COA acceptance or stakeholder demand established. |
| Periodic public-chain Merkle roots for batches | Inclusion of a retained record hash in a committed batch | Fewer transactions and public per-record fields; adds proof/version retention, an interval before anchoring, correction rules and failure handling. Inclusion does not prove that every eligible household was included. |
| Public-chain transaction per record | Direct per-record commitment lookup | More transactions, public metadata and operational overhead; original-input and cash-payment trust limits remain. |

IETF RFC 9162 specifies Merkle inclusion/consistency proof machinery for certificate-transparency logs. It supplies a technical analogy, not a disaster-payment standard or institutional mandate. A root can make committed data auditable while retaining individual proof material off-chain; losing that material can make verification impractical. [RFC 9162, §§2.1, 4](https://www.rfc-editor.org/rfc/rfc9162.html)

Any change to the receipt encoding or contract interface would need maintainer approval, an ADR and compatibility tests under the repository's instructions. These alternatives can be explored without claiming that blockchain establishes payment truth or that less blockchain necessarily meets an auditor's needs.

## Polygon fee check

For an EIP-1559 transaction, actual fee is `gasUsed × effectiveGasPrice`, converted from wei to POL. For an eligible type-2 transaction, effective price is `min(maxFeePerGas, baseFee + maxPriorityFeePerGas)`. Gas limit is a budget, not measured gas used. POL is Polygon PoS's gas token; Amoy uses test tokens rather than demonstrating a production fiat cost. [Ethereum gas documentation](https://ethereum.org/developers/docs/gas/), [Polygon EIP-1559](https://docs.polygon.technology/pos/concepts/transactions/eip-1559), [Polygon POL](https://docs.polygon.technology/pos/concepts/tokens/pol), [Polygon Remix/network documentation](https://docs.polygon.technology/tools/dApp-development/common-tools/remix/)

The official Gas Station mainnet endpoint was queried at **2026-10-08 02:09:17.308957 +08:00** (2026-10-07 18:09:17.308957 UTC), block **95,127,576**. Its transient response was:

```json
{
  "safeLow": {"maxPriorityFee": 38.173736272, "maxFee": 407.61355002},
  "standard": {"maxPriorityFee": 58.584503399, "maxFee": 428.024317146},
  "fast": {"maxPriorityFee": 78.049065008, "maxFee": 447.488878755},
  "estimatedBaseFee": 246.293209165,
  "blockTime": 1.6666666666666667,
  "blockNumber": 95127576,
  "blockTimestamp": 1791396555
}
```

Fee quantities are **gwei**. Gas Station recommends estimates from recent blocks; this is not an executed AyudaChain transaction receipt. [Official live endpoint](https://gasstation.polygon.technology/v2), [Polygon Gas Station documentation](https://docs.polygon.technology/tools/gas/polygon-gas-station)

Using the repository's 183,265-gas figure only as an illustration, estimated base plus standard priority would give approximately **0.0558734 POL**; its standard max-fee budget at that gas amount would be **0.0784419 POL**. Even at 30 gwei, the arithmetic yields **0.00549795 POL**, not a dollar price. This primary-source research track did not itself benchmark that contract's gas usage, submit a production transaction, or retrieve a POL/fiat conversion. Therefore “less than $0.001 per household” and guaranteed nationwide economic viability are **not certified**. Representative contract receipt measurements, failure/retry volumes, batch size, fee observations and a time-stamped exchange rate are needed for a fiat estimate.

### Parent measurement note — separate local execution evidence

The parent investigation independently read the real local transaction receipt for **DIST-7614**, at **block 12**, and measured **`gasUsed: 183265`**. The preserved evidence records transaction `0xa2e68d4f9276df5d862e9b9cc074f91c371cc10764ef5b02600cd5a9089c33d8`. This corroborates the gas used by **that one local execution**. It does not measure production or Polygon fees, representative gas across execution paths, throughput, or fiat cost. The primary-source research track's scope and the fee caveats above remain applicable. [Parent direct-chain evidence](direct-chain-evidence.json)

## Claim disposition

| Repository claim | Disposition |
|---|---|
| Universal statutory ₱5,000 ECT/AICS amount | **Contradicted** by the official variable ECT calculation and actual ₱9,960 payout; no statutory basis for this universal amount was found. A specific local/demo award could still be ₱5,000. |
| Official DAFAC name | **Supported:** Disaster Assistance Family Access Card. FACED is the newer card identified by MC 12/2024. |
| `DFC-2026-XXXX` and QR demonstrate full official integration | **No evidence found.** The format is suitable as labelled synthetic data, not as demonstrated government interoperability. |
| COA audits universally occur 6–12 months after payout | **No evidence found.** Specific office/event measurements are needed; this does not disprove occasional delays. |
| Deduction/duplicate risks exist | **Supported in bounded official reports.** Specific demo mechanisms, prevalence and automated guilt judgments are unverified. |
| Locking award + matching hash prevents cash withholding or proves payout | **Unsupported technical inference:** recorded bytes and actual cash receipt can diverge without any post-anchor modification. |
| Off-chain personal data means DPA compliance | **Insufficient:** disclosure, lawful processing, security, proportionality and rights still require assessment. |
| Local Hardhat anchor provides independent assurance against its operator | **Unsupported:** node-control assumptions do not provide that independence. |
| 183,265 gas at typical 30 gwei guarantees <$0.001 per household | **Unverified cost claim:** parent evidence corroborates one local execution's gas, not Polygon fees or throughput; no fiat rate obtained and the live fee observation differed materially from 30 gwei. |

## Field validation questions before product requirements are fixed

1. Which office, disaster event and program is the pilot for? Obtain MC 24/2025 and any later applicable issuance, approved proposal and current payment SOP.
2. Who decides eligibility, the family unit and payable amount, and which assessment/approval establishes each decision? How are repeated events, family representatives and legitimate successive aid handled?
3. Who assigns DAFAC/FACED serials? What exact identifier/bar-code/QR payload and validation interface does the target LGU/Field Office use? Is integration authorized, and what existing system would receive/export data?
4. Who actually disburses funds: DSWD SDO, LGU under an agreement, bank, digital payment provider or another entity? Identify fund ownership, handover, reconciliation and refund responsibilities.
5. What evidence establishes actual receipt independently of the clerk's data entry? How do recipients report short payment or post-payout collection without needing a smartphone?
6. What approved review and appeal process distinguishes potential duplicates from permitted assistance? Who can approve, reject or correct, and how is that decision preserved?
7. Ask the target accounting/audit staff for current required documents and accepted exports, plus sampled dates for payout, liquidation, reconciliation, audit and publication. Do they want any cryptographic commitment, and what would they inspect?
8. Ask the controller/DPO which fields each audience may see, the lawful basis, retention and correction requirements, and the linkage risks of public IDs/hashes/amounts. No compliance conclusion should precede that assessment.
9. Who independently retains checkpoints or verifies chain history? Who controls writer keys, node/RPC access, corrections and recovery? Would a signed export or periodic batch root meet the evidenced need?
10. Obtain observed transaction volumes, connectivity gaps, queue/retry behavior, operating support capacity and gas receipts before choosing anchor cadence or claiming deployment economics.

## Source register

All sources were accessed **2026-10-08**. Dates below refer to the document or displayed publication/update date, not a search engine's crawl age. An undated page is marked accordingly. PDF dates were checked in the document where stated; hosting-path dates alone were not treated as publication dates.

| Official source and direct URL | Publication / update date | Scope or access limitation |
|---|---|---|
| [DSWD MC 11/2025: Revised ECT Guidelines](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2025/07/MC-No.-11-S-2025.pdf) | Signed 2025-06-19; certified copy 2025-06-23 | Full PDF inspected; later MC 24/2025 amendment not obtained. |
| [DSWD MC 12/2026: Revised DROMIC Guidelines](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/wp-content/uploads/2026/05/MC-No.-12-S-2026.pdf) | Signed 2026-04-24; certified copy 2026-05-21 | Page 5 corroborates the MC 24/2025 amendment. |
| [DSWD ECT program](https://drm.dswd.gov.ph/emergency-cash-transfer/) | Undated; no update date displayed | Program overview, not a complete current circular. |
| [DSWD AICS program](https://aics.dswd.gov.ph/aics-program/) | Undated; no update date displayed | Program scope. |
| [DSWD AICS FAQs](https://aics.dswd.gov.ph/about-us/faqs/) | Undated; no update date displayed | Current web-listed documents; local transition needs confirmation. |
| [DSWD: Cash aid to 2,000 disaster-hit families in Davao Oriental](https://www.dswd.gov.ph/dswd-gives-cash-aid-to-2k-disaster-hit-families-in-davao-oriental/) | 2024-03-05 | A specific historical payout. |
| [DSWD: ECT more responsive to disaster-hit families](https://www.dswd.gov.ph/dswd-makes-emergency-cash-transfer-more-responsive-to-needs-of-disaster-hit-families/) | Published 2025-10-23; modified 2025-10-28 | Official announcement; does not replace full guidelines. |
| [DSWD: Continuous AICS aid](https://www.dswd.gov.ph/dswd-assures-continuous-aid-under-the-aics-program/) | 2024-11-27 | Historical cash/guarantee-letter announcement. |
| [DSWD MC 12/2024: Institutionalization of FACED](https://dswd-file-assets.s3.ap-southeast-1.amazonaws.com/issuances/MCs/MC_2024-012.pdf) | Signed 2024-04-22 | Full document and blank annex visually inspected. |
| [DSWD XI: ECT Offline Payout System](https://fo11.dswd.gov.ph/2025/09/%F0%9D%97%97%F0%9D%97%A6%F0%9D%97%AA%F0%9D%97%97-%F0%9D%97%AB%F0%9D%97%9C-%F0%9D%97%A5%F0%9D%97%BC%F0%9D%97%B9%F0%9D%97%B9%F0%9D%98%80-%F0%9D%97%A2%F0%9D%98%82%F0%9D%98%81-%F0%9D%97%98%F0%9D%97%96/) | Publication path 2025-09; precise publication day not displayed; introduction date 2025-06-09 in article | Regional announcement; no integration interface inspected. |
| [DSWD ECT Operations Manual, Version 1.0](https://www.dswd.gov.ph/download/publications/operations_manual_for_the_implementation_of_the_emergency_cash_transfer_ect_during_disasters/02012022_ECT_OM_A4_print_FINAL.pdf) | 2022; precise publication day not verified | Historical manual based on earlier ECT rules. |
| [COA Revised Cash Examination Manual, Annex 1.3.5](https://www.coa.gov.ph/wp-content/uploads/ABC-Help/Cash_Examination_Manual/an1.3.5.htm) | Underlying COA Circular 97-002: 1997-02-10; web page undated | Official search-index excerpt inspected; direct access returned 403. Old rule, not observed current duration. |
| [COA documentary reference: Liquidation of Cash Advances](https://www.coa.gov.ph/wp-content/uploads/ABC-Help/DRCGT/DRCGT.6.htm) | Undated legacy web reference | Not treated as a complete current relief-payment checklist. |
| [COA documentary-requirements FAQ](https://www.coa.gov.ph/FAQS/what-are-documentary-requirements-in-the-grant-for-common-government-transactions/) | Undated | References Circular 2023-004; full circular not inspected. FAQ displays an inconsistent year for its date. |
| [DSWD: Investigation of alleged Iloilo AICS deductions](https://www.dswd.gov.ph/dswd-condemns-aics-cash-aid-cut-by-iloilo-barangay-officials-vows-immediate-probe/) | 2025-11-12 | Allegations and proposed investigation, not judgment. |
| [DSWD: Administrative charges over AICS corruption](https://www.dswd.gov.ph/dswd-chief-files-admin-charges-vs-local-officials-involved-in-aics-corruption/) | 2025-12-11 | Filing/evidence-gathering status, not final adjudication. |
| [DSWD: Streamlining AICS documentary requirements](https://www.dswd.gov.ph/dswd-continues-improvements-in-the-streamlining-of-aics-documentary-requirements/) | Published 2023-08-17; modified 2025-12-17 | Agency response to COA 2022 observations. |
| [DSWD: PhilSys identification for 4Ps/AICS](https://old.dswd.gov.ph/dswd-to-use-philsys-for-identification-of-4ps-aics-and-other-program-beneficiaries/) | 2021-09-27 | Announced initiative/pilot; not evidence of completed nationwide deployment. |
| [NPC: RA 10173, Data Privacy Act of 2012](https://privacy.gov.ph/data-privacy-act-/) | Statutory text 2012; page undated | Legal text; this report does not certify compliance. |
| [NPC Advisory Opinion 2020-026](https://privacy.gov.ph/wp-content/uploads/2020/10/Redacted-Advisory-Opinion-No.-2020-026.pdf) | 2020-06-26 | Contextual COVID-era public-disclosure opinion. |
| [NPC Advisory Opinion 2020-019](https://privacy.gov.ph/wp-content/uploads/2020/10/Redacted-Advisory-Opinion-No.-2020-019.pdf) | 2020-04-28 | Contextual SAP beneficiary-list opinion. |
| [NIST IR 8202: Blockchain Technology Overview](https://nvlpubs.nist.gov/nistpubs/ir/2018/NIST.IR.8202.pdf) | 2018-10-03 | General technical trust model. |
| [Hardhat Network overview](https://v2.hardhat.org/hardhat-network/docs/overview) | Undated; no update date displayed | Hardhat v2 developer documentation, matching repository generation. |
| [Hardhat Network reference](https://v2.hardhat.org/hardhat-network/docs/reference) | Undated; no update date displayed | Development-node reset/manipulation capabilities. |
| [IETF RFC 9162: Certificate Transparency Version 2.0](https://www.rfc-editor.org/rfc/rfc9162.html) | 2021-12 | Experimental certificate protocol used only as a technical analogy. |
| [Ethereum: Gas and fees](https://ethereum.org/developers/docs/gas/) | No publication/update date established | Fee mechanics; no fixed fiat fee promise. |
| [Polygon: EIP-1559](https://docs.polygon.technology/pos/concepts/transactions/eip-1559) | Undated; no update date displayed | Polygon fee mechanics. |
| [Polygon: POL](https://docs.polygon.technology/pos/concepts/tokens/pol) | Undated; no update date displayed | Native gas-token information. |
| [Polygon: Remix/network configuration](https://docs.polygon.technology/tools/dApp-development/common-tools/remix/) | Undated; no update date displayed | Amoy/mainnet distinction. |
| [Polygon: Gas Station documentation](https://docs.polygon.technology/tools/gas/polygon-gas-station) | Undated; no update date displayed | Estimation method; sample values not used as live readings. |
| [Polygon mainnet Gas Station API](https://gasstation.polygon.technology/v2) | Live observation 2026-10-08 02:09:17.308957 +08:00 | Transient estimate at block 95,127,576; not an AyudaChain fee receipt. |
