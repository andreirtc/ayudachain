# AyudaChain finalist pitch

Target: approximately **11–12 minutes**, including a three-minute evidence walkthrough. Rehearse aloud; timing assumes roughly 140–150 spoken words/minute outside the walkthrough. Leave about eight minutes of the 20-minute slot for Q&A and transitions. Bracketed directions are not spoken. All household stories and amounts below are explicitly invented examples.

## 0:00–0:55 — Open with the household

[Title. Pause.]

Imagine an invented household whose roof has been damaged by a typhoon. They are told they qualify for assistance. Their name appears on a list. A staff member records a payout. Later, someone asks a simple question: did the household receive the correct amount?

There may be a funding document, a beneficiary list, a payout record and a receipt. But each answers a different question. A total on a dashboard cannot explain every decision. A signature on a document cannot tell us whether its digital copy changed afterward. And a recorded payout alone cannot tell us what the recipient actually received.

AyudaChain connects those pieces into a trail that people can inspect.

## 0:55–1:45 — Explain the product clearly

AyudaChain is a working local prototype for disaster cash-assistance records. It connects funding evidence, household registration, human review, documented amounts, scheduled payout, recorded handover and recipient follow-up.

Private records and original documents stay off-chain. The blockchain holds fingerprints of selected evidence versions, with opaque references. An independent reviewer can compare today's saved evidence with those commitments.

Our promise is precise: make the basis of the recorded action inspectable, and make changes to committed evidence detectable. We do not promise to prove that every original document is genuine or that cash physically reached a household. Those still require people, procedures and independent checks.

## 1:45–2:45 — Five people and their responsibilities

[Five-role workflow.]

The Beneficiary registers the household, submits a claim and sees the reason for the decision, the amount basis and appointment. A person without a phone can ask for help.

The Barangay Officer helps establish residence and affectedness. That officer gives an opinion; DSWD decides eligibility. An officer who helped register a household cannot endorse that same household.

The DSWD Officer records funding and operation authority, reviews evidence, records the documented calculation inputs and schedules payout staff.

The Disbursing Officer compares the person with the accepted photo ID, presents the calculated cash for counting, and records the authorized handover once.

The Auditor reads the evidence and history and requests a fresh integrity check. The Auditor cannot approve a claim or make a payout.

For this evaluation, accounts are selectable and identities are unverified. That lets us demonstrate the roles, but it is not secure authentication. We use invented records only.

## 2:45–3:35 — Human judgment and understandable amounts

Automatic checks highlight possible duplicates and other recorded exceptions. A flag asks a person to look. It does not declare fraud or reject a household automatically.

Amounts come from documented inputs, not an editable amount box on the payout desk. In our invented example, a daily wage of 435 pesos is multiplied by 75 percent, rounded up to the next ten pesos, then multiplied by fifteen documented days. The resulting amount is 4,950 pesos. The household can see that basis.

This is an example rule in the prototype, not a claim about today's mandated regional rate. Missing inputs remain “awaiting amount.” If an unpaid basis changes, old authorization is invalidated. An already recorded handover keeps its original amount and history.

## 3:35–6:35 — Genuine application walkthrough

[Use the saved real lab and screenshots/video in DEMO_RUNBOOK. Do not attempt the full administrative process on stage. Keep this segment under three minutes.]

Here is the funding record. We uploaded this invented original, the software extracted the available text, and a human confirmed the saved fields. If a value needs correction, the original stays and a reversal and replacement explain the change. This balance records funding authority; it does not certify physical cash availability.

[Open the saved claim and current decision.]

Here is the household claim, the barangay response and DSWD's decision. The original evidence and earlier versions remain available. These checks highlight records for review; the decision belongs to the reviewer.

[Open the amount basis/current published list.]

Here is the recorded calculation and the approved list. Publication waits for that list's own matching blockchain confirmation. A saved request is not automatically a published list.

[Open the actual recorded receipt.]

This is the recorded handover. Before recording, the assigned payer compared identity and the recipient authorized the current attempt with a short-lived code. Our final review repeats the household and fixed amount. The server checks the current rules again and consumes the authorization once. Reloading the receipt does not make the household payable again.

[Show a private answer/case under the permitted actor.]

The recipient's report is separate. “Received in full,” “received less” and “not received” are different outcomes. An adverse answer opens a private case for human handling. It does not silently erase the handover or award another payout.

[Auditor: click a current Check now; wait for the real result.]

This check reads the actual local-chain record. If it matches, we can say the committed evidence still agrees. If the chain cannot be read, the screen says so. We never replace that failed read with an earlier green result.

[If failure: “The current chain read is unavailable. The recorded demonstration shows the earlier workflow, but I cannot claim a live match now.”]

## 6:35–7:40 — Why use a blockchain?

[Private records → fingerprint → independently retained witness.]

A database is essential. It stores private evidence and supports the workflow. But when the same administrator controls both the record and its local history, an outside reviewer needs another reference to detect changes to already committed content.

A blockchain commitment can provide that reference when the chain is retained independently and governed appropriately. The reviewer can recompute the fingerprint and query the pinned deployment without the signing key.

Our prototype demonstrates that mechanism on a local EVM node. It is not yet a public Polygon deployment or an independently governed network. That is a limitation we state clearly. Before rollout, we must compare the operating cost and trust benefit with alternatives such as signed audit logs and external timestamping. We should earn the use of blockchain through the audit requirement.

## 7:40–8:40 — Inclusion, connectivity and privacy

QR is optional. A staff member can type the same transaction reference. Scanning opens a record; it does not prove identity or authorize cash.

A household can register and claim without owning a smartphone or having an ID at registration. The implemented no-phone payout route uses an officer's connected device, private recipient authorization and an independent assigned checker. The prototype still requires accepted photo ID and documented checking before payment. We recognize that this can exclude people whose documents were lost; the proper alternative needs institutional agreement, not an improvised demo bypass.

Offline payout is not available. If connectivity is lost, staff must inspect the saved transaction after recovery before retrying. We do not promise that a disconnected device can safely record cash.

Private information stays off-chain, but that alone does not make us privacy-compliant. Authentication, lawful processing, file security, retention and operational safeguards must be established before real records.

## 8:40–9:35 — A realistic adoption path

[Three gates: validate workflow → harden → supervised pilot.]

Our starting scope is one Field Office workflow. We would first work with authorized program staff and auditors using synthetic examples to check the forms, decisions, evidence and exception routes against their actual procedures.

Next come authenticated accounts, secure hosting and files, independent key custody, tested recovery, privacy assessment and approved operational rules. Only after those gates would we propose a bounded supervised pilot with lawful data handling and independent evaluation.

DSWD, LGUs and NGOs have different authority and reporting requirements. The current application does not claim to model them all. Government adoption requires a sponsor, process agreement, security/privacy review and an appropriate procurement route. We have no signed government customer or institutional endorsement to announce.

## 9:35–10:25 — Business and cost discipline

The repository is open source. A possible sustainable service is institutional implementation, training, support and managed operations under agreed responsibilities. Beneficiaries should not pay to receive aid, and we do not propose taking a percentage of relief funds.

There is no validated selling price or revenue forecast yet. We would price a scoped pilot from documented staff effort, hosting, original storage, backups, monitoring, security, notification delivery and—if a public chain is selected—measured transaction fees.

Gas is not the whole cost. Our local chain uses development funds and costs no purchased token. A public-network estimate needs actual gas use, current fees and an exchange rate, plus transaction volume and retries. We have not purchased infrastructure or deployed publicly for this prototype.

## 10:25–11:20 — What we have and what comes next

[Actual screenshot/evidence, not a fabricated percentage.]

We have implemented original-backed editable forms, the five-role workflow, human review, documented calculations, once-only recorded handover, recipient follow-up, append-only histories and actual local-chain verification and recovery.

We also know what remains: authenticated identity, institutional alignment, real messaging and identity integrations, operational privacy and security, resilient deployment and network governance. The exact fresh test results and any failures are in our readiness report; older test runs are labelled historical.

Our next milestone is a supervised validation partner who can help us test the workflow and agree measurable acceptance criteria: whether records are complete, reviews are understandable, exceptions are resolved, and evidence can be retrieved and checked.

AyudaChain gives relief assistance a trail we can inspect and a verification result we can defend. Every verified result must mean a real comparison. Every uncertainty must stay visible. Thank you.

## Presenter controls

- If running late at minute 6:35, compress blockchain explanation to: “The database holds private records. The chain is a separately checkable fingerprint of committed versions. Our local deployment demonstrates the mechanism; independent governance is still required.”
- Keep the live check honest. Read the displayed result, including failure. Never click handover again on a paid household for effect.
- Refresh [readiness](FINALIST_READINESS.md) immediately before presenting. Quote only completed fresh checks, with their limitations.
- For Q&A, start with the spoken answer in [the defense masterbook](JUDGES_QA.md), then offer the implementation evidence if asked.
