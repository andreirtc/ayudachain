# AyudaChain, explained nang simple

Companion ito ng [detailed English explanation at technical inventory](../PROJECT_EXPLAINED.md). Code at validated evidence ang basehan, hindi marketing claims.

## Anong problem ang sinusubukang ayusin?

Kapag may tanong na “Bakit ito ang amount na natanggap ng pamilya?”, hindi sapat ang total number. Kailangan makita ang funding document, household information, damage request, review decision, amount basis at payout record. Kailangan ding marinig ang recipient kung ano talaga ang natanggap.

AyudaChain connects those records. May history ng changes at may selected fingerprints sa blockchain para may reference ang integrity check. Hindi nito awtomatikong nahuhuli lahat ng fraud o pinapalitan ang trabaho ng government staff.

## Ano ang ginagawa ng bawat role?

| Role | Actual task sa prototype | Bakit may sarili siyang screen? |
|---|---|---|
| Mamamayan | Registration/request, status, amount, schedule, authorization, receipt at private report | Kailangan malinaw kung ano ang next action, hindi puro technical data |
| Barangay Officer | Assisted registration, local responses, endorsement/submission ayon sa role | May local information sila tungkol sa household at epekto ng sakuna |
| DSWD Officer | Funding evidence, human review, amount inputs, lists, schedules, concerns | Siya ang nagko-connect ng evidence sa decision at payout preparation |
| Disbursing Officer | Assigned session, ID comparison, authorized handover, eligible exit checks | Ang cash action ay kailangang distinct sa approval at recipient statement |
| Auditor | Originals, decisions, exceptions, version history at fresh chain checks | Kailangan ng reviewer na makasunod sa evidence nang walang payment/approval controls |

Responsibilities ito, hindi claim na limang departments ang kailangan. Ang Disbursing Officer ay puwedeng DSWD employee. Ang Auditor ay generic proposed reviewer; COA/internal audit access would depend on actual institutional authority. Walang COA certification o government endorsement.

## Buong journey

1. **Funding:** upload ng original PDF, inspect extracted text, manually confirm/edit ang fields, saka save. Hindi validated digital signature ang printed signatory.
2. **Registration:** household information at optional private details. Puwedeng assisted; hindi mandatory ang phone number sa registration. Registration is not approval.
3. **Request at responses:** household damage/category, supporting documents, barangay responses at formal submission where applicable. Missing responses can take a retained exception/fallback path; hindi ito fake endorsement.
4. **Human review:** DSWD reads current flags, responses at evidence, then records decision/reason. Flags do not automatically reject a household.
5. **Amount:** documented inputs ang basehan. Missing inputs means wala pang final amount. New inputs are versioned; paid amounts stay locked.
6. **List at schedule:** list publication waits for its own matching chain confirmation. DSWD assigns date/site/members/cash staff and opens the session.
7. **Payout:** ID comparison plus current recipient authorization. May final household/amount confirmation bago recorded handover. Once-only ang recorded handover per entitlement.
8. **Report:** buo, kulang o walang natanggap. Private workflow projection ito; hindi secure operational privacy habang walang authentication.
9. **Audit:** originals/history plus actual fresh chain comparison. Separate signer-free verifier can check exact authorized material and originals.

## Paano naka-connect ang technology?

Browser → FastAPI API → PostgreSQL at private original-file storage. Durable jobs handle selected blockchain submissions/recovery. Local EVM registry stores the selected commitments. Verification recomputes/checks the correct material against an actual chain read.

`backend/app/main.py` ang authoritative MVP entry point. Separate legacy system ang `backend/server.py`/SQLite; walang MVP dual writes. Ang ibang PR stack ay may ibang backend/auth/contracts model. Hindi puwedeng idagdag sa pitch ang feature ng ibang branch kung wala rito.

## Ano ang nasa blockchain?

Selected hashes, opaque references at some funding amounts. Names, contact information, photo IDs, receipt contents, PINs/codes at private answers stay off-chain. Pero off-chain does not automatically mean secure: kailangan pa rin ng authentication, access controls, encryption/retention/governance review. May metadata/privacy risks kahit hashes lang ang visible.

## Bakit may blockchain pa kung may database na?

Database ang working store. Ang separately retained commitment ay extra reference kapag kailangang ma-detect kung nabago ang committed content. Useful lang ang independence kung may independent retention/governance. Ang local chain natin ay protocol demonstration; hindi independently operated national infrastructure. Dapat ikumpara sa signed logs/timestamping ang production choice.

## Paano ang QR, code at PIN?

QR at manual reference are lookup options. Hindi sila proof ng identity o payment permission. Optional ang QR. Ang payout code ay short-lived authorization for a current attempt; hindi SMS OTP. Sa implemented no-phone route, connected staff device, privately established PIN at distinct eligible checker ang kailangan. Walang general PIN recovery o no-ID payout route na ipinapangako. Hindi ito official government-mandated PIN/checker policy.

## Ano ang actual, simulated at pending?

| State | Examples |
|---|---|
| Actual locally | Uploads, extraction/manual confirmation, DB persistence, human decisions, calculations, lists, sessions, once-only records, outcomes, actual chain submission/read, recovery |
| Simulated at labelled | National ID check, notice SMS, accelerated business time; demo represents cash without moving real money |
| Pending/unavailable | Secure sign-in, operational privacy, real integrations, validated signatures, public-network governance, offline payout, full advances/returns/liquidation |

Kapag chain unreachable, absent ang commitment o failed ang anchoring, hindi puwedeng tawaging verified. Explicit ang state. Historical confirmation is not a fresh check.

## Real-life fit at adoption

May existing government process at existing software. Ang proposal natin ay i-connect ang records at gawing mas madaling sundan/check ang evidence. Hindi “palitan lahat.” Kailangan ng partner mapping sa actual forms, positions, approvals at applicable current rules. May newer [DSWD issuances](https://www.dswd.gov.ph/issuance/); hindi claimed na fully mapped ang latest ECT requirements.

Sa daily-wage field, reference sa calculation ang ibig sabihin, hindi citizen salary. See [DSWD explanation](https://www.dswd.gov.ph/dswd-insulates-programs-from-politics-adheres-to-guidelines-agency-spox/). Synthetic ang demo amounts at days.

## Business proposal

Institutional implementation, training at support ang proposed service. Walang beneficiary fee o percentage ng relief funds. Wala pang validated selling price, customer contract, measured ROI o financial forecast. Ang [Q&A worksheet](JUDGES_QA.md) ay hypothetical exercise lang.

## UI changes na makikita ngayon

All five roles sa welcome page; full desktop task labels and sidebar; four phone shortcuts plus full menu; one searchable household detail at a time; grouped payout desk; optional advanced audit details. English/Taglish switch sa Settings. Citizen amount at next action muna, optional calculation details pagkatapos. Demo people/places are clearly labelled `· Demo`; walang real citizen records.
