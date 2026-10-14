# Understand AyudaChain from zero

Read this before the long technical documents. You do not need to memorize code, blockchain terminology or 110 answers. Learn the story, the three separate facts, the demo order and the short answers below. This guide describes the current `design-proposal` MVP, including its compact role interface. All demonstration people, documents and cash amounts are invented.

## The 30-second explanation to memorize

“AyudaChain helps people follow the evidence behind disaster cash assistance. It connects funding documents, household claims, human decisions, calculated amounts, recorded handovers and recipient feedback. Private information stays in the database and private files. Selected records get a fingerprint on a local blockchain, so a reviewer can check whether the committed evidence still matches. It records assistance; it does not transfer money or prove that cash physically arrived.”

## The problem in ordinary language

Imagine someone asks: “Why did this household receive this amount?” A total payout number cannot answer everything. You need the funding document, household information, damage claim, decision, amount basis, recorded handover and recipient's own report. Those pieces can be difficult to follow when they are separate.

Our prototype connects those pieces and keeps earlier versions. Its value is the explanation and the checkable trail. Avoid saying it eliminates corruption, replaces government judgment or guarantees honest documents.

## One household story

This story is illustrative, not a claim about a real family or an official current benefit.

1. **DSWD records funding evidence.** A worker uploads an invented release document, reviews extracted text and confirms the fields. The funding number records authority; it does not certify that cash is already available at a payout desk.
2. **A household registers and submits a claim.** Maria Santos · Demo says where her household lives, who its members are and what damage occurred. A helper can assist. Registration alone does not approve assistance.
3. **Barangay workers respond; DSWD decides.** Responses and supporting originals inform a human reviewer. Duplicate flags ask for investigation; they do not automatically reject Maria or accuse her of fraud.
4. **The amount is explained.** In the synthetic wage example, 75% of ₱435 is ₱326.25, rounded up to ₱330. Fifteen documented days produce ₱4,950. These are invented inputs, not today's mandated rate. Missing inputs stay “awaiting amount”.
5. **A current list and session are prepared.** The approved list waits for its own matching chain confirmation. DSWD names the households, date, place and staff for a payout session.
6. **The officer records a handover once.** The recipient authorizes the current attempt with a short-lived code. The payer compares identity, presents the fixed cash for counting, checks the final household/amount review and records once. In our demo no real cash moves.
7. **The recipient reports independently.** “Received in full”, “received less” and “not received” are different reports. An adverse report creates a private case; it does not automatically create another payment.
8. **The Auditor checks the evidence.** A fresh read compares the saved evidence fingerprint with the actual pinned local-chain record. A match confirms that comparison; it does not prove the original story or physical delivery was true.

## The three facts you must keep separate

| Fact | What it says | What it cannot establish alone |
|---|---|---|
| Recorded handover | An officer recorded that handover under the workflow | Whether the person physically received the right cash |
| Recipient report | A recipient reported full, less or no receipt | That the statement is independently proven true |
| Current chain match | The committed evidence agrees with an actual fresh chain read | Genuine documents, valid identity, eligibility or physical cash delivery |

If you remember only one technical point, remember this table.

## Five roles: what each person does

| Role | Simple job | Main screen/action |
|---|---|---|
| Mamamayan / Beneficiary | Describe the household and damage, inspect progress/amount, authorize and report receipt | Home shows the next action; My claim, Receipts and Help are phone shortcuts |
| Barangay Officer | Help record households and independently respond about residence/affectedness; Punong submits supporting resolution | Households, Review and Lists |
| DSWD Officer | Record authority, review claims, document amounts, publish lists and schedule staff | Funding, Households, Review, Lists and Sessions |
| Disbursing Officer | Compare identity and record the authorized fixed cash handover once during an assigned session | Sessions and Pay desk |
| Auditor | Inspect decisions, originals, exceptions, history and fresh chain comparisons | Integrity, Funding and Cases; no approval/payment action |

These are different responsibilities. DSWD approval is not a cash handover. Barangay opinion is not DSWD approval. The recipient's report is not the payer's own statement.

**Why would each worker use it?** Barangay staff can find a household and add their local response without maintaining another disconnected list. DSWD staff can see the evidence behind a decision and amount, then organize the payout. The Disbursing Officer records the cash action; that person may also be a DSWD employee, but approval and paying are different responsibilities. The Auditor retrieves originals, versions and exceptions to examine a case and performs a fresh integrity check. The app supplies evidence; the auditor still investigates and exercises judgment.

**Which department is the Auditor from?** This is a generic reviewer role in the prototype. A future authorized user could be an internal audit professional or an external government auditor, depending on institutional access rules. COA is an independent commission, not a DSWD department. DSWD also has internal audit personnel. We have no COA integration, approval or official auditor accounts. Sources: [COA audit scope](https://www.coa.gov.ph/FAQS/what-agencies-can-be-audited-by-coa/), [DSWD internal audit vacancy](https://jobs.dswd.gov.ph/index.php?catid=&id=10476&lyt=list&option=com_jobboard&view=job).

## Does this process already happen in real life?

The broad responsibilities do: identify affected households, check information, authorize assistance, organize payment and examine supporting records afterward. The [DSWD ECT operations manual](https://www.dswd.gov.ph/download/publications/operations_manual_for_the_implementation_of_the_emergency_cash_transfer_ect_during_disasters/02012022_ECT_OM_A4_print_FINAL.pdf) describes DSWD/LGU coordination and beneficiary validation. Current amendments are listed in the [official issuance register](https://www.dswd.gov.ph/issuance/). Our five-role sequence simplifies that setting; it is not a claim that every LGU follows these exact screens or that PINs, checker assignments and blockchain gates are mandated government procedures. Municipal/city social welfare roles and formal signatories need to be mapped with a partner.

**Use this positive, accurate adoption answer:** “AyudaChain connects the records already needed for disaster assistance—from household information and authorized decisions to payout and recipient feedback. Staff can follow the evidence, and reviewers can check whether committed records changed. Our next milestone is a small supervised pilot using a partner's actual forms, roles and rules, measuring record completeness, ease of use and time to trace a case.” This proposes supporting existing responsibilities, rather than claiming the government must adopt our prototype sequence wholesale.

## Why is there a daily wage in a disaster-assistance app?

It is an **amount-calculation reference**, not a question about the beneficiary's salary and not wages paid for working in this app. DSWD has publicly explained ECT amounts using 75% of the regional daily minimum wage and an assessed number of days; ECT is described as unconditional assistance. Sources: [DSWD explanation](https://www.dswd.gov.ph/dswd-insulates-programs-from-politics-adheres-to-guidelines-agency-spox/), [ECT overview](https://drm.dswd.gov.ph/emergency-cash-transfer/).

Our synthetic example applies the prototype's documented rounding/day rule to invented inputs. It is not today's official regional rate or a legal benefits calculation. Newer amendments exist and their full requirements have not been mapped here. The beneficiary sees **Halaga ng ayuda** first; **Paano kinuwenta?** opens the optional explanation. Only staff enter the documentary basis. Say “reference used to work out the amount,” not “your daily salary.”

**Critical limitation:** our demonstration has selectable actors, not secure sign-in. Anyone can impersonate an active actor. These workflow restrictions do not make it safe for real citizens. PR #39 has a different authenticated synthetic-account implementation; do not claim it is already included here.

## The terms, translated

- **Database:** the working store for private household details, decisions and relationships. Ours uses PostgreSQL.
- **Original evidence:** actual uploaded file bytes, stored privately outside the chain. Saving a file does not prove it is genuine.
- **Version/history:** a new recorded change that keeps the earlier facts, rather than silently replacing the trail.
- **Hash/fingerprint:** a calculated value representing exact content. Change the committed content and its fingerprint changes. It is not a scanned fingerprint or a citizen identifier.
- **Commitment/anchor:** saving the selected evidence fingerprint and opaque references on the chain.
- **Blockchain:** the extra reference against which committed evidence is compared. Our current demonstration uses a local EVM process, not public Polygon or independently governed infrastructure.
- **Off-chain:** stored outside the blockchain. Names, IDs, photos, phone numbers, receipt contents, PINs/codes and private answers stay off-chain.
- **Verification:** an actual comparison with a chain read. A saved historical confirmation is not a fresh check.
- **Once-only/idempotency:** the software prevents a repeated recorded handover for the same entitlement and can recognize the same request after an uncertain reply. It cannot physically prevent an officer handing out cash outside the system.
- **QR/manual reference:** two ways to find the same record. Neither identifies the person or authorizes payment.
- **MVP:** the working prototype used to evaluate the process. It still has significant production/security gaps.

## Built, simulated and pending

**Working local mechanisms:** original uploads/extraction and confirmation; household registration/claims; human review; documentary calculations; list publication; assigned sessions; PIN/code workflow; once-only recorded handover; private outcomes/cases; actual local blockchain reads/submissions; retained history and recovery mechanisms.

**Explicit simulations:** National ID checks, SMS notices, accelerated business time when used, and represented physical cash. No handset delivery, national database connection or real payment is proved.

**Before real households:** authenticated accounts/recovery, institutional procedure/privacy/security approval, hardened storage/hosting, validated signatures, real integrations, retained network/key governance and operating support. Offline payout and full advances/returns/liquidation are not implemented.

## How to operate the demo without getting lost

Open `http://127.0.0.1:3000/mvp` on the development machine. Choose the role, then verify the selected disaster and actor. “All workspaces” returns to the role directory. This is demonstration navigation, not login.

Desktop uses a left navigation with full task labels. Phone uses four shortcuts and a top-left menu for all remaining tasks. Settings near the top-right contains theme and English/Taglish. A first visit defaults to Taglish; `?lang=en` or `?lang=fil` explicitly chooses the language, and the choice is remembered in this browser. All five roles are visible on the welcome page. The copy uses ordinary phrases such as “Status ng ayuda,” “Tingnan ang status” and “I-submit ang request.” Specialist terms may remain English; native-speaker and comprehension testing is still needed. Language changes do not change business records.

Staff registry uses a searchable list and one detail pane. On a phone, select the household, inspect it, then use Back to households. DSWD can open the existing review controls; Barangay cannot access those DSWD actions. Search stays in the browser view rather than placing names in the URL.

At the payout desk, keep the household/amount, identity comparison and handover controls together. For a person without a phone, the implemented route uses a connected staff device, privately established recipient PIN and a distinct assigned checker. General PIN recovery and a payment route without accepted photo ID remain limitations.

Never run reset commands, restart a surviving chain, create a second payout to repeat the demonstration, or enter real citizen information. Current lab/node details are in [readiness](FINALIST_READINESS.md). The earlier 8545 node exited; the new isolated rehearsal uses8547 and does not verify the old deployment.

## The three-minute stage demonstration

Use saved genuine records. Entering the whole administration process live will consume the pitch.

1. **Funding:** show one saved original and confirmed fields. Say: “A human confirms the evidence.”
2. **Decision:** show the claim and human review. Say: “Flags inform a decision; they do not make it.”
3. **Amount/list:** show the recorded calculation and current list. Say: “We can explain the amount and version.”
4. **Receipt:** show a recorded handover. Say: “Recorded once; we will not pay again to demonstrate it.”
5. **Recipient:** show a permitted private answer/case. Say: “The recipient's report is separate evidence.”
6. **Auditor:** click Check now and wait. Say exactly what the current result says. If unavailable, say so and use the labelled recorded fallback.

See [DEMO_RUNBOOK](DEMO_RUNBOOK.md) for exact setup, the longer editable journey and fallback instructions. The recorded video shows real local software operating on invented data; it is not a live health check.

## Twenty short spoken answers

| Question | Answer to remember |
|---|---|
| What is it? | A connected, checkable evidence trail for disaster cash assistance. |
| Does it transfer money? | No. It records a cash handover; cash handling stays with authorized people. |
| Why blockchain? | It supplies another reference for detecting changes to already committed evidence. Independent retention/governance is still needed. |
| Why not a database alone? | A database is essential. The extra witness helps when the record keeper's own history should not be the only reference; signed logs are a legitimate alternative to compare. |
| Is it on Polygon? | Our demonstrated chain is a local EVM. No public Polygon deployment is claimed. |
| What does Verified mean? | The committed evidence matched an actual fresh chain read. It does not prove cash delivery. |
| Can someone submit a false document? | Yes. Hashing preserves a submitted record; human authenticity and eligibility checking remain necessary. |
| Is personal data public? | Private contents stay off-chain. Metadata/privacy risks still require assessment and real access protection. |
| Is it secure for real citizens now? | No. This branch has no authentication and uses invented records only. |
| Are the five roles real login accounts? | Here they are selectable unverified actors. PR #39 has a separate synthetic-account sign-in implementation. |
| Must a citizen have a smartphone? | No. Assisted registration/payment exists, but staff still need connectivity and the prototype's ID/PIN/checker conditions apply. |
| Is QR mandatory? | No. The same record can be found by typing its reference. |
| Does it work offline? | Offline payout is unavailable. Stop, reconnect and inspect the same saved transaction before retrying. |
| Does AI approve people? | No. Automatic checks flag possible issues; humans decide. |
| What if an officer pays twice? | The system blocks a second recorded handover for the entitlement; physical misconduct outside it still needs operational oversight. |
| What if the recipient disagrees? | Keep both records, open a private case and investigate. Do not automatically repay or label fraud. |
| What does it cost? | No validated selling price yet. Proposed implementation/training/support must be costed; the finance worksheet is hypothetical. |
| Are gas costs zero? | No purchased gas was used locally. Public fees would depend on actual transactions/network prices; hosting and staff time still cost money. |
| Is DSWD adopting or endorsing it? | No endorsement or adoption is claimed. We are seeking supervised workflow validation. |
| Why choose this over PR #39? | This version demonstrates the fuller evidence journey. PR #39 has a cleaner reference interface and authenticated demo accounts; we are adapting useful UI patterns without pretending the branches are already integrated. |

## What each teammate should learn

Everyone should know the 30-second explanation, three-facts table, current authentication/local-chain limitations and six demo stops. The demo operator additionally rehearses role/context switching and a fresh check. The technical speaker reads the architecture/blockchain/recovery questions. The business speaker reads the pricing/ROI/adoption questions and keeps hypothetical figures labelled.

Do not memorize 110 answers word for word. Read the short answers in [JUDGES_QA](JUDGES_QA.md), especially its top-20 reviewer. When uncertain, say: “That is not implemented/validated in this prototype. Here is what we can show, and here is the next validation step.”

## Study order

1. This crash course: understand the story and boundaries.
2. [PITCH_SCRIPT](PITCH_SCRIPT.md): speak it aloud once, targeting 11–12 minutes.
3. [DEMO_RUNBOOK](DEMO_RUNBOOK.md): rehearse the saved-record walkthrough.
4. [JUDGES_QA](JUDGES_QA.md): top-20 short answers first, full 110-bank as reference.
5. [FINALIST_READINESS](FINALIST_READINESS.md): quote current results and limitations accurately.

The full explanation and source inventory are in [PROJECT_EXPLAINED](PROJECT_EXPLAINED.md). Those deeper notes are backup material, not prerequisites to understand the pitch.
