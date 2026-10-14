# AyudaChain — natural Taglish pitch

Companion ng [complete English11–12minute script](../PITCH_SCRIPT.md). Target11–12minutes including three-minute app walkthrough, pauses at transitions. Rehearse aloud; actual timing depends on speaker pace. Hindi kailangang literal na basahin lahat ng technical details. Bracketed instructions are not spoken. Demo households, documents at amounts are fictional.

## 0:00–1:00 — Simulan sa tanong ng pamilya

[Title.]

Imagine a family na nasira ang bahay dahil sa bagyo. Nagbigay sila ng information, nakita ang pangalan sa listahan, at may officer na nag-record ng payout. Pero pagkatapos, may tanong: bakit ito ang amount? Kumpleto ba ang naibigay? At kung may disagreement, saan makikita ang records?

May funding document, household list, decision, payout record at recipient report. Bawat isa, ibang tanong ang sinasagot. Hindi sapat ang isang total sa dashboard para ma-explain ang buong case. Hindi rin automatic proof ng cash delivery ang isang recorded payout.

AyudaChain connects those records para mas madaling sundan ang assistance at i-review ang evidence behind it.

## 1:00–2:00 — Ano ang product?

AyudaChain is a working local prototype for disaster cash-assistance records. Connected ang funding evidence, household request, human review, documented amount, scheduled payout, recorded handover at recipient follow-up.

Private information at original documents stay outside the blockchain. Selected evidence versions get a digital fingerprint sa chain. Puwedeng i-compare ng reviewer ang saved evidence sa actual chain record.

Ang precise promise namin: makita ang basis ng recorded action, at ma-detect kung hindi na match ang committed evidence. Hindi namin claim na blockchain proves every document is genuine, o na physically natanggap ang cash. Kailangan pa rin ang tao, authorized procedures at independent investigation.

## 2:00–3:00 — Limang roles, malinaw na trabaho

[Five roles.]

Ang Mamamayan registers the household, submits damage information, checks status/amount/schedule, authorizes the current payout attempt at reports what was received. Puwedeng magpatulong; hindi mandatory ang smartphone sa registration.

Ang Barangay Officer gives local responses tungkol sa tirahan at epekto ng sakuna. Opinion at evidence iyon; DSWD makes the final eligibility decision.

Ang DSWD Officer records funding authority, reviews current evidence, documents the amount basis at organizes lists/sessions/staff.

Ang Disbursing Officer compares identity, presents the fixed cash for counting at records the authorized handover once. Puwede siyang DSWD employee, pero different responsibility ang approval at cash handover.

Ang Auditor reads originals, history at exceptions and runs fresh integrity checks. Generic reviewer role ito; hindi COA integration o official audit certification.

Sa current demo, selectable unverified actors ang accounts. Wala pang secure sign-in. Synthetic records only ang ginagamit namin.

## 3:00–4:00 — Human review at amount explanation

Automatic checks flag possible duplicates at exceptions. Flag means kailangan tingnan, hindi automatic rejection o accusation of fraud. Human reviewer records the decision and reason.

Documented inputs ang basehan ng amount. Sa invented example:₱435 daily-wage reference times75percent, rounded up to₱330, times15documented days gives₱4,950. Reference sa assistance calculation iyon, hindi salary ng beneficiary o payment for working. These are synthetic inputs, not today's mandated regional rate.

Kapag kulang ang inputs, awaiting amount ang state. Kapag paid na, fixed ang original paid amount at history; later changes don't create automatic another payout. Sa household screen, amount at next action muna ang makikita. Optional ang calculation explanation.

## 4:00–7:00 — Three-minute actual application walkthrough

[Use saved records. Follow DEMO_RUNBOOK. Huwag mag-input ng whole journey live.]

**Funding:** Ito ang original document at human-confirmed fields. Kung may typo, retained ang original at may linked correction. Recorded funding authority ito, hindi certification ng cash sa desk.

**Review:** Ito ang household request, barangay responses at human decision. Flags support review. May earlier versions para makita kung ano ang basis ng decision.

**Amount/list:** Ito ang documentary calculation at current list. List publication waits for its own matching chain confirmation. Hindi pareho ang saved list at published list.

**Receipt:** Ito ang recorded handover. Nakikita ang household, amount at relevant session facts. Recorded once ito; hindi natin uulitin ang payment para sa demo.

**Recipient report:** Hiwalay ang report ng recipient: buo, kulang o walang natanggap. Adverse report opens a private case, hindi automatic finding of theft o authority for repayment.

**Auditor:** I-check natin ang actual saved handover proof ngayon. [Click I-check ngayon/Check now; wait and read result.] A match means match ang committed evidence sa fresh local-chain read. Hindi proof ng physical cash delivery. Kung unavailable ang read, sabihin iyon at gamitin ang labelled recorded fallback.

## 7:00–8:00 — Inclusion at real-life fit

QR is optional. Puwedeng i-type ang same reference. Lookup is not identity proof o payment authorization.

May assisted registration at no-phone payment route using a connected staff device. Current prototype requires accepted photo ID, privately established PIN at distinct eligible checker for that path. Wala pang general PIN recovery o certification-only payment. Walang offline payout; kapag uncertain ang saved state, stop and inspect the same receipt before retry. Huwag ulitin ang physical cash dahil lang lost ang reply.

Hindi namin hinihiling na palitan agad ang existing government process. We propose connecting records already needed for assistance and testing against a partner's actual forms, roles and rules. May existing government software; integration or a narrower evidence-witness component may be better than replacement.

## 8:00–9:00 — Technical value, with clear boundaries

Next.js/React ang interface. FastAPI ang API, PostgreSQL ang working database, at off-chain files ang original documents. Durable jobs handle selected chain submissions and recovery. Solidity registry ang local EVM witness.

Database pa rin ang essential working store. Ang extra commitment gives another comparison reference beyond the record keeper's own history. Pero local chain is a protocol demonstration, hindi independent institutional governance. Production choice needs independent retention/key control and comparison against signed logs or timestamping.

For deployment, PostgreSQL can stay. Private object storage, hosted app/worker, authenticated accounts, backups and monitoring are proposed next steps. They are a deployment plan, not already operating integrations. National ID, SMS at accelerated demo clock are explicitly simulated.

## 9:00–10:00 — Business at measurement

Proposed model namin is institutional implementation, training and support. Walang beneficiary fee at walang percentage ng relief funds.

Wala pang validated price, contract o ROI study. Our financial worksheet is clearly hypothetical. Kasama ang labor, hosting, storage, backups, support and risk reserve; nakalista rin ang unpriced costs. Sa sample sensitivity, possible pa nga ang negative return. Hindi namin ipapakita iyon bilang forecast o government budget recommendation.

Ang dapat sukatin sa pilot: complete ba ang required evidence, gaano kadaling i-trace ang isang case, malinaw ba ang next action sa staff/citizen, at kaya bang mag-recover safely after failure? Those are testable outcomes. Walang invented corruption-reduction percentage.

## 10:00–11:30 — Readiness and close

[Use only completed current results from FINALIST_READINESS.]

We exercised the actual original-backed forms, own-device and assisted payout paths, separate recipient reports and actual local-chain reads. Browser checks cover role navigation, desktop/phone viewports, error handling and current verification failures. May independent signer-free check of exact authorized material. These are functional prototype results, not production security or physical-device certification.

Before real households, kailangan authenticated access/recovery, privacy/security hardening, approved procedure/current-rule mapping, real integrations at operating governance. Hindi namin itatago ang boundary na iyon. Ang value ng prototype ay concrete at inspectable: puwedeng sundan ang evidence at makita ang truthful failure states.

Our next milestone is a small supervised pilot using a partner's actual forms, roles and rules, after the readiness gates. We are asking for a workflow-validation partner and feedback on the measures that matter.

AyudaChain makes the evidence behind assistance easier to follow. Recorded handover, recipient report and chain match stay separate—para ang result na tinatawag naming verified ay may actual comparison na puwedeng ipakita.

[Pause. Invite questions. Keep remaining slot for Q&A.]
