# Implemented MVP API

Base URL: http://127.0.0.1:8000/api/v1. The complete generated contract is [OpenAPI](../../shared/protocol/openapi.json); frontend/lib/mvp-api.generated.ts is generated from it. The original endpoint documentation is retained in ../legacy-documentation/system-api-contract.md.

Select an actor using X-Demo-Actor-ID. Stored current role/office/barangay/household/member links determine rules and projections. Unknown, inactive, system or retired actors are refused on ordinary API routes. Auditor mutation is refused. No authentication is claimed; anyone can select another active actor. General mutation requests use Idempotency-Key and typed current revisions. Injected context/role fields are rejected.

Responses use data and meta. Metadata identifies claimed_unverified, authentication pending, impersonation possible, actual blockchain, business-clock mode, simulated adapters, not_validated signatures and real_data_ready=false. Monetary *_centavos values cross JSON as decimal strings; null means unknown, not zero. Structured errors omit submitted PINs, codes, file selectors and raw database/chain errors. Responses are no-store; CORS is limited to local development origins.

| Group | Implemented routes |
|---|---|
| Evaluation/references | GET health, context, actors/catalogue, disasters, barangays, categories; GET evaluation/status; DSWD POST evaluation/clock |
| Originals | POST evidence multipart file/purpose/prepared_for_actor_id; GET evidence/{id} metadata and evidence/{id}/content original |
| Funding | GET funds (ledger, totals and exceptions); POST funds/releases; POST funds/{id}/corrections |
| Registry/staff/intake | GET registry; POST registry; GET registry/{id}; POST registry/{id}/reviews; GET staff; POST staff/nominations, staff/{id}/status and staff/{id}/member-link; GET intake; POST intake/open and intake/{id}/close |
| Claims | GET/POST claims; GET claims/{id}; POST claim-rounds/{id}/responses and claims/submissions |
| Decisions/amounts/lists | POST claims/{id}/decisions and claims/bulk-approve; GET/POST amount-inputs; GET/POST lists; GET entitlements |
| Sessions/notices | GET barangay/payout-counts; GET/POST sessions; POST sessions/{id}/changes; GET notifications |
| Payout | GET transactions and transactions/{id}; POST sessions/{id}/id-checks, households/{id}/assisted-pin, entitlements/{id}/attempts, transactions/{id}/handover and transactions/{id}/clearances |
| Private follow-up | POST transactions/{id}/outcomes, reports and notes; GET transactions/{id}/private-outcomes and transactions/{id}/notes; GET grievances/challenges; POST grievances/{id}/actions, list-entries/{id}/challenges, challenges/{id}/actions; GET outcome-totals |
| Proofs/Auditor | GET audit/overview, audit/proofs, audit/originals, audit/timeline/{typed-slot}/{id}, audit/own-inspections and commitments/{id}/material; POST integrity/check (read operation); DSWD POST anchor-jobs/{id}/retry |
| Frozen legacy | GET legacy/records, legacy/records/{id}, legacy/records/{id}/integrity |

OpenAPI is authoritative for exact method/path/body spelling; the table groups workflows. Uploads retain original bytes and extraction state; extraction is prefill only. Independent private file and material access is checked separately from list projection access. Attaching an existing original checks its current permitted scope before adding the new link. Replacement uploads retain purpose and private recipient and require permitted predecessor scope; the helper identity panel has a narrow preparation exception without stored-original read access. Funding evidence includes its actual attachment_role, so corrections select the primary source independently of upload order. Amount prefills preserve exact integer centavos.

Success acknowledgements contain typed resource handles and replayed. The payout code is included only in its first successful opening response. Same-key replay never reveals it. Different body with the same key is refused. Stored refusal keys prevent duplicate credential counters or refusal audit records. After a lost handover acknowledgement, GET the transaction before safe replay; never repeat physical cash.

Only the current candidate's own real confirmation publishes a list. Failed supporting anchors remain inspectable without an additional publication prerequisite. Handover accepts no amount, derives the fixed current amount and atomically consumes the code and entitlement. Current input/list/session/date/actor/account/ID/checker rules are checked again at recording.

An ID comparison failure before recipient authorization creates a terminal stopped refusal under the same transaction, with no open event or payout code. DSWD clearance and a distinct later session are required before another comparison and recipient opening. Pending list generations are invalidated for both barangays after a reviewed residence move, and after a paid display-category change; locked cash versions remain unchanged.

Private answers and case histories are available only to the recipient, DSWD and Auditor. An assisted checker can submit the household's answer and receives an acknowledgement; the actual payer is permanently barred. Payer/barangay projections omit private outcome/case selectors and revision signals. Original identity files and exact full envelopes have stricter scope than resident list columns. Every Auditor inspection is logged privately before disclosure; logging outage fails closed.

Auditor officer response figures classify deadlines using the saved claim.respond business-effective audit time, including labelled accelerated evaluation. File/write wall timestamps remain distinct and do not change those historical figures. One response is counted once even when it has multiple linked audit events.

Operational notes are available after closure to assigned officers and independent DSWD. They append without changing outcomes or payment and create no standalone anchor. Disbursing note history contains only that actor's own notes; DSWD/Auditor can inspect the scoped full history. Auditors cannot append.

GET /barangay/payout-counts requires a stored Barangay Officer role and a disaster in the actor’s evaluation run and Field Office. It returns only integer approved, recorded_handover and remaining counts for the actor’s stored barangay. It accepts no client scope override, omits household identifiers, amounts, contacts and private outcomes, and logs the read separately from append-only business events. Cancelled entitlements are excluded. Frontend workspace URLs and Account controls do not change these server rules.

## Usability endpoints

| Method/path | Contract |
|---|---|
| POST /queues/search | Strict body kind, disaster_id, query (max200), state, barangay_id, offset, limit (default25/max50). Server role/scope predicates apply before count/pagination. No private identity/contact payloads; disbursing omits zone/outcomes. Proof catalogue is explicitly office-wide with actual anchor-job state options. |
| GET /operations?disaster_id | DSWD/Auditor per-barangay current claims/entitlements, valid appointments, locked handover amounts and latest outcome totals; Barangay exact own aggregate allowlist. Known amounts plus awaiting count; no cash-availability inference. |
| POST /claims/{id}/recheck | DSWD independent reviewer, expected_revision, Idempotency-Key. Appends the existing check and audit without deciding. Latest-check projection includes algorithm, time, compared/current revision, stale and frozen comparisons; historical missing snapshots unavailable. |
| GET /registry/csv/template | Beneficiary/Barangay/DSWD safe template/limits; only head declaration fields. |
| POST /registry/csv/preview | Strict content body; read-only bounded UTF-8 parser/row errors/scoped duplicate suggestions and saved-row recovery. |
| POST /registry/csv/confirm | Content, preview digest and selected row indices; revalidation then normal per-row registry.register commands with actor/content/row keys. Partial outcomes retain successes; identical upload/retry recovers original resources. |
| POST /sessions/{id}/lookup | Disbursing read-only strict reference body, UUID or ayudachain:transaction:UUID. Current assignment, active membership/version and session/disaster/run/office checks; unknown/wrong-session indistinguishable404. Returns transaction_id only. |
| GET /commitments/{id}/summary | Existing wholly-authorized commitment scope; kind, saved time, actual submission state, opaque covered versions and original descriptors, no raw private preimage. Auditor read logged. |

Integrity check replies now include server checked_at, commitment_id/kind, and observed pinned chain/address/public reference only when available; no synthetic chain metadata. Transaction details include stored disaster_id for correct selected-disaster direct links. See regenerated OpenAPI for exact request/response shape and [limits](../implementation/bring-forward-usability.md).
