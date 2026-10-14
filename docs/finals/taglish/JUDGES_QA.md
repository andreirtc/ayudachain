# Judges Q&A — natural Taglish reviewer

110 meaningful questions ito, same numbering as the [detailed English masterbook](../JUDGES_QA.md). Basahin muna ang **Short answer**. Gamitin ang explanation/evidence kapag may follow-up. Facts, limits at source references ang basehan; walang invented customer, endorsement, savings o implemented capability. Technical terms stay English kapag mas malinaw. Local synthetic prototype lang ito; wala pang authentication.

## Five-minute emergency study sheet

**Minute1 — Ano ito?** Connected evidence trail para sa disaster cash assistance. Funding document → request → human decision → documented amount → recorded payout → recipient report → integrity check. Software records cash; hindi ito money-transfer service.

**Minute2 — Tatlong facts.** Payout record: may officer na nag-record. Recipient report: ito ang sinabi ng recipient. Blockchain match: match ang committed content sa actual chain read. Walang isa sa tatlo ang automatic proof ng physical delivery o honesty.

**Minute3 — Actual/simulated/pending.** Actual locally ang uploads, persistence, calculations, human workflow at chain reads. Simulated ang National ID, SMS at accelerated clock. Pending ang secure login, real integrations at production readiness. Actors are impersonable; demo data only.

**Minute4 — Inclusion and failure.** Optional QR/manual lookup. Phone optional sa registration; assisted payout uses connected staff device, accepted photo ID, private PIN at distinct checker. Walang offline payout. Lost reply? Read the same receipt; huwag ulitin ang cash.

**Minute5 — Business and ask.** Proposed institutional implementation/training/support; walang beneficiary fee. No validated price/ROI/customer. Hypothetical lang ang finance model. Ask for supervised validation using partner forms/roles/rules and measurable case-tracing/completeness/usability outcomes.

## Top-20 na unahing aralin

1. **Q071:** Walang login; demo actors can be impersonated.
2. **Q041:** Extra witness ang chain; compare signed-log alternative.
3. **Q045:** Match proves content comparison, not physical cash.
4. **Q042:** Local EVM, not public Polygon.
5. **Q081:** Walang offline payout.
6. **Q082:** Read same transaction after uncertain reply.
7. **Q011:** No validated price.
8. **Q013:** People/security/operations costs matter.
9. **Q017:** ROI unmeasured; hypothetical can be negative.
10. **Q021:** No government endorsement.
11. **Q022:** Current official rule mapping incomplete.
12. **Q031:** No mandatory smartphone, but assisted conditions apply.
13. **Q033:** No-ID registration allowed; no-ID payment unavailable.
14. **Q043:** Private content off-chain; metadata risks remain.
15. **Q049:** Local gas units are not peso public fees.
16. **Q063:** Once-only record, not physical enforcement.
17. **Q025:** Flags/responses inform human decision.
18. **Q028:** Funding authority is not certified available cash.
19. **Q102:** Existing government software already exists.
20. **Q110:** Ask for bounded supervised validation, not immediate rollout.

## 110-question bank

### Q001. Sino ang customer?

**Short answer:** Institution ang proposed buyer; household ang service user.

**Paliwanag:** Start sa isang authorized Field Office partner. Program owners, IT, privacy, cash staff at audit have different approval needs.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [Adoption/readiness boundaries](../../guides/local-mvp.md).

**Limit:** Wala pang signed customer o willingness-to-pay study.

**Possible follow-up:** Sino ang may budget at authority?

### Q002. Ano ang ibebenta ninyo?

**Short answer:** Implementation, training, support at operations ang proposed service around open-source software.

**Paliwanag:** I-scope separately ang procedure mapping, secure setup, migration, training, maintenance at incident response. Hindi libre ang lahat dahil open source.

**Evidence:** [MIT license](../../../LICENSE); [Local operations/recovery](../../guides/local-mvp.md).

**Limit:** Proposal pa lang ito, hindi launched service.

**Possible follow-up:** Ano ang responsibility ng agency?

### Q003. Bakit gagamit ang agency?

**Short answer:** Para mas madaling sundan ang evidence behind a decision, amount at recorded payout.

**Paliwanag:** Connect existing records; measure retrieval effort/completeness against their current process. Use actual forms/roles sa supervised pilot.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [Adoption/readiness boundaries](../../guides/local-mvp.md).

**Limit:** Wala pang measured productivity benefit.

**Possible follow-up:** Bakit hindi improve ang existing system?

### Q004. May bayad ba ang mamamayan?

**Short answer:** Walang proposed beneficiary fee o percentage ng ayuda.

**Paliwanag:** Institutional service ang model. Huwag bawasan ang relief amount para sa app fee.

**Evidence:** [MIT license](../../../LICENSE); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Wala pang commercial pricing agreement.

**Possible follow-up:** Sino ang magbabayad ng operations?

### Q005. Ano ang unang adoption step?

**Short answer:** Supervised synthetic workflow validation kasama ang partner.

**Paliwanag:** Agree muna sa users, forms, evidence access at success measures. Security/privacy gates bago actual citizen data.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [DSWD official issuance register](https://www.dswd.gov.ph/issuance/).

**Limit:** Wala pang approved government pilot.

**Possible follow-up:** Sino ang dapat kausapin muna?

### Q006. Sino ang kailangang sumang-ayon?

**Short answer:** Program, frontline staff, IT, privacy, finance at audit stakeholders.

**Paliwanag:** User enthusiasm is useful, pero kailangan ng operating authority, funding, procurement at accountable owner.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [Adoption/readiness boundaries](../../guides/local-mvp.md).

**Limit:** Hindi sapat ang isang supportive official.

**Possible follow-up:** Sino ang puwedeng humarang at bakit?

### Q007. Paano iiwasan ang vendor lock-in?

**Short answer:** Open source at inspectable verification material ang starting point.

**Paliwanag:** Document data export, schema, operating knowledge at key custody. Test kung kayang mag-transition ng ibang operator.

**Evidence:** [Signer-free independent verifier](../../../contracts/scripts/verify_evidence.js); [Accepted evidence compatibility ADR](../../adr/2026-10-10-mvp-evidence-protocol-and-registry.md); [MIT license](../../../LICENSE).

**Limit:** Hindi pa complete ang migration/export product.

**Possible follow-up:** Paano aalis ang agency sa service?

### Q008. Paano kung kulang ang staff?

**Short answer:** Clear task queues at next actions help; hindi puwedeng lampasan ang independent checks.

**Paliwanag:** Assisted payout needs distinct eligible staff. Kapag kulang ang checker, hold/escalate instead of pretending independent ang payer.

**Evidence:** [Scoped task queues](../../../backend/app/routes_queues.py); [Role-specific recovery catalogue](../../../frontend/lib/workflow-errors.ts); [PIN/code/once-only handover service](../../../backend/app/services/payouts.py).

**Limit:** Hindi field-tested ang staffing design.

**Possible follow-up:** Paano kung isang officer lang?

### Q009. Ano ang success metrics?

**Short answer:** Evidence completeness, time to trace a case, review clarity at recovery success.

**Paliwanag:** Measure claims, retrievable originals, current checks, recipient reports at assisted-route failures with clear denominators.

**Evidence:** [Audit projections](../../../backend/app/services/audit_views.py); [Actual local automatic checks](../../../backend/app/services/checks.py).

**Limit:** Walang measured fraud-reduction percentage.

**Possible follow-up:** Anong result ang magpapakitang hindi useful?

### Q010. Kailan puwedeng mag-rollout?

**Short answer:** After agreed workflow, privacy, authentication at recovery gates.

**Paliwanag:** Synthetic validation, hardened staging, then authorized bounded pilot. Expand only after evaluation.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [Local operations/recovery](../../guides/local-mvp.md).

**Limit:** Walang promised national timeline.

**Possible follow-up:** Sino ang mag-sign off?

### Q011. Magkano ang price?

**Short answer:** Wala pang validated selling price; hypothetical lang ang worksheet.

**Paliwanag:** Actual quote needs scope, support hours, document volume, security, hosting, training at procurement terms.

**Evidence:** [Hypothetical model below](#hypothetical-financial-model); [MIT license](../../../LICENSE).

**Limit:** Hindi supplier quote ang sample numbers.

**Possible follow-up:** Paano magiging credible ang price?

### Q012. Paano ang institutional pricing?

**Short answer:** Possible setup fee plus scoped support/operations service.

**Paliwanag:** Separate one-time implementation from recurring service. Specify responsibilities, usage, retention at recovery targets.

**Evidence:** [Hypothetical model below](#hypothetical-financial-model); [Local operations/recovery](../../guides/local-mvp.md).

**Limit:** Walang tested price package.

**Possible follow-up:** Subscription ba o project contract?

### Q013. Ano ang pinakamalaking gastos?

**Short answer:** People, security, operations at training can outweigh infrastructure.

**Paliwanag:** Include compute/DB/files, backups, monitoring, connectivity, travel, support, incident work at governance.

**Evidence:** [Local operations/recovery](../../guides/local-mvp.md); [Hypothetical model below](#hypothetical-financial-model).

**Limit:** Hindi pa fully costed.

**Possible follow-up:** Bakit hindi hosting lang ang budget?

### Q014. Libre ba ang demo?

**Short answer:** Walang purchased infrastructure o public-chain gas sa demonstrated local run.

**Paliwanag:** Existing machine and tools have economic cost. Simulated SMS does not reveal real SMS pricing.

**Evidence:** [Fresh finals readiness](../FINALIST_READINESS.md); [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol).

**Limit:** Local demo cost is not production cost.

**Possible follow-up:** Ano ang babayaran sa pilot?

### Q015. Magkano ang SMS?

**Short answer:** Wala pang real SMS integration o validated provider quote.

**Paliwanag:** Estimate message volume, retry/delivery patterns at dated supplier rates after approval.

**Evidence:** [Labelled simulated notices](../../../backend/app/services/notifications.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Simulated notices lang ngayon.

**Possible follow-up:** Paano kung hindi delivered ang SMS?

### Q016. Paano kinukuwenta ang gas fees?

**Short answer:** Actual gas used times actual effective gas price.

**Paliwanag:** Convert native-token fee to pesos using a dated rate. Include all commitment types, retries at congestion reserve.

**Evidence:** [Measured local gas evidence](../evidence/test-results.md); [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol); [Hypothetical model below](#hypothetical-financial-model).

**Limit:** Walang current peso gas estimate.

**Possible follow-up:** Per household ba ang charge?

### Q017. Ano ang ROI ninyo?

**Short answer:** Unmeasured pa; walang guaranteed savings claim.

**Paliwanag:** Compare observed baseline effort with future effort and full implementation/operations costs. Staff-time value is not automatically cash savings.

**Evidence:** [Hypothetical model below](#hypothetical-financial-model); [Audit projections](../../../backend/app/services/audit_views.py).

**Limit:** Hypothetical model can show negative return.

**Possible follow-up:** Paano ninyo susukatin ang benefit?

### Q018. Paano ang cost per household?

**Short answer:** Total scoped costs divided by clearly defined completed cases.

**Paliwanag:** Define whether denominator is registered, approved, paid or completed follow-up. Include fixed costs, surge and uncompleted cases.

**Evidence:** [Audit projections](../../../backend/app/services/audit_views.py); [Hypothetical model below](#hypothetical-financial-model).

**Limit:** Walang validated unit cost.

**Possible follow-up:** Ano ang denominator ninyo?

### Q019. Paano magiging sustainable?

**Short answer:** Institution-funded implementation/support is the proposed model.

**Paliwanag:** Scope predictable service obligations and test willingness to pay. Beneficiaries should not finance the platform through aid deductions.

**Evidence:** [Hypothetical model below](#hypothetical-financial-model); [MIT license](../../../LICENSE).

**Limit:** Wala pang revenue evidence.

**Possible follow-up:** Paano kapag walang renewal?

### Q020. Guaranteed ba ang budget cap o savings?

**Short answer:** Hindi. Funding authority ledger is not full financial control.

**Paliwanag:** Prototype separates recorded authority, approved amounts and cash arrangements. Advances, returns and liquidation are outside this implementation.

**Evidence:** [Funding/corrections service](../../../backend/app/services/funds.py); [Approved MVP scope and assurance](../../product/prd.md); [Branch/PR triage](../GITHUB_TRIAGE.md).

**Limit:** Hindi certified available cash ang balance.

**Possible follow-up:** Paano kung approvals exceed funding?

### Q021. Official DSWD system ba ito?

**Short answer:** Hindi; local workflow prototype ito.

**Paliwanag:** No endorsement, procurement award o official account integration is claimed. Use the prototype to show a concrete validation proposal.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [DSWD official issuance register](https://www.dswd.gov.ph/issuance/).

**Limit:** Walang government approval.

**Possible follow-up:** May actual partner ba?

### Q022. Exact current ECT rules ba ang gamit?

**Short answer:** Hindi pa certified ang full mapping sa current rules.

**Paliwanag:** Documentary calculation exists. DSWD register lists newer amendments; inaccessible full amendment text means no complete compliance claim.

**Evidence:** [DSWD official issuance register](https://www.dswd.gov.ph/issuance/); [Documentary entitlement calculation](../../../backend/app/services/entitlements.py).

**Limit:** Demo rates/days are synthetic.

**Possible follow-up:** Paano mag-update ng rule safely?

### Q023. Ano ang FACED at mapped ba lahat?

**Short answer:** Relevant official profiling context ito; incomplete ang exact field/procedure mapping.

**Paliwanag:** Prototype uses one household per entitlement. Self-registration is intake, hindi completed official administered profiling.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Hindi FACED-certified.

**Possible follow-up:** Paano ang multiple families sa isang bahay?

### Q024. Bakit DSWD ang funds at review?

**Short answer:** Explicit prototype simplification ito.

**Paliwanag:** Real institutions may separate budget/accounting/approval duties. Recorded provenance helps review, pero needs institutional permission mapping.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [Funding/corrections service](../../../backend/app/services/funds.py).

**Limit:** Walang second-person fund approval here.

**Possible follow-up:** Puwedeng manipulahin ng isang actor?

### Q025. Puwedeng mag-reject ang Barangay?

**Short answer:** Response/opinion ang barangay; DSWD decides eligibility.

**Paliwanag:** Negative response or missing submission remains evidence for human review. Fallback is labelled; hindi fake endorsement.

**Evidence:** [Human claim workflow](../../../backend/app/services/claims.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Prototype routing, hindi universal official rule.

**Possible follow-up:** Paano kung intentionally delayed?

### Q026. Nasaan ang municipal/LGU approval?

**Short answer:** Walang separate municipal role sa direct Field Office prototype.

**Paliwanag:** Five roles are responsibilities, not entire government organization. Map city/municipal social welfare staff and formal signatories with partner.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [DSWD official issuance register](https://www.dswd.gov.ph/issuance/).

**Limit:** Incomplete official organizational mapping.

**Possible follow-up:** Puwede ang C/MSWDO later?

### Q027. Validated ba ang uploaded signatures?

**Short answer:** Hindi; signatures remain not_validated.

**Paliwanag:** Retain original bytes and printed signatory. Hash match does not verify authority, handwriting o certificate trust.

**Evidence:** [Original-file storage/retrieval](../../../backend/app/services/evidence.py); [Authoritative FastAPI API](../../../backend/app/main.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** No legal authenticity conclusion.

**Possible follow-up:** Paano kung forged ang document?

### Q028. Cash available ba ang funding balance?

**Short answer:** Hindi; recorded funding authority iyon.

**Paliwanag:** Release/corrections are saved facts. Supporting documents are not extra counted releases; handover is a different record.

**Evidence:** [Funding/corrections service](../../../backend/app/services/funds.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** No bank, advances, returns/liquidation.

**Possible follow-up:** Paano iko-confirm ang actual cash?

### Q029. Puwede ba direct purchase agad?

**Short answer:** Agency procurement/legal staff must determine the applicable process.

**Paliwanag:** Present scoped need, deliverables and responsibility model. Huwag magpromise ng exemption o shortcut.

**Evidence:** [GPPB RA 12009 and rules](https://www.gppb.gov.ph/new-government-procurement-act-republic-act-no-12009/); [Adoption/readiness boundaries](../../guides/local-mvp.md).

**Limit:** Hindi legal/procurement advice ang prototype.

**Possible follow-up:** Anong procurement route ang legal?

### Q030. Sino ang nag-aayos ng concern?

**Short answer:** DSWD records human review/resolution sa private case workflow.

**Paliwanag:** Earlier reports and responses remain. Changes follow permitted eligibility rules; complaint is not automatic extra payout.

**Evidence:** [Private answers/grievances](../../../backend/app/services/outcomes.py); [Human claim workflow](../../../backend/app/services/claims.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Formal appeals/full external grievance process deferred.

**Possible follow-up:** Paano kung hindi agree ang recipient?

### Q031. Kailangan ba ng smartphone?

**Short answer:** Hindi sa registration; may assisted payment route din.

**Paliwanag:** Connected staff device, private PIN, accepted photo ID and distinct assigned checker apply to the implemented no-phone payout.

**Evidence:** [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [Household/field-check service](../../../backend/app/services/registry.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Walang offline payment.

**Possible follow-up:** Paano kung walang staff device?

### Q032. Mandatory ba ang QR?

**Short answer:** Hindi; manual reference lookup is available.

**Paliwanag:** Both open the same permitted record. Lookup does not verify identity, generate authorization or pay.

**Evidence:** [Optional camera/manual lookup](../../../frontend/components/mvp/SessionLookup.tsx).

**Limit:** Camera support varies by browser.

**Possible follow-up:** Paano kung damaged ang QR?

### Q033. Puwedeng walang ID?

**Short answer:** Puwedeng mag-register/claim, pero payment still needs accepted ID under this prototype.

**Paliwanag:** Field-check and accepted originals must be documented before the relevant assisted steps.

**Evidence:** [Household/field-check service](../../../backend/app/services/registry.py); [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Walang certification-only payout route.

**Possible follow-up:** Paano kung nawala lahat ng ID?

### Q034. Bakit may assisted PIN?

**Short answer:** Recipient authorization safeguard ito sa connected staff device.

**Paliwanag:** Payer cannot simply authorize for the recipient. PIN is separate from current payout code and needs private entry.

**Evidence:** [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Recovery/coercion/inclusion still need work.

**Possible follow-up:** Paano kung nakalimutan ang PIN?

### Q035. Ano ang nakikita ng household?

**Short answer:** Next action, status, amount, schedule, receipt at private report.

**Paliwanag:** Optional calculation explains the basis. Barangay/DSWD responses help explain progress. Registration alone does not approve assistance.

**Evidence:** [Scoped business projections](../../../backend/app/projections.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Not secure real-account privacy yet.

**Possible follow-up:** Puwedeng may helper?

### Q036. Anong language/accessibility support?

**Short answer:** English at natural Taglish, keyboard controls at responsive layouts.

**Paliwanag:** Saved language preference; readable states, labelled controls, 44px phone targets. Specialist fallback text may remain English.

**Evidence:** [Sea-and-Sun design system](../../../DESIGN.md); [Household English/Filipino guidance](../../../frontend/components/mvp/Guidance.tsx); [Fresh finals readiness](../FINALIST_READINESS.md).

**Limit:** No complete accessibility/native-speaker study.

**Possible follow-up:** Paano sa ibang local language?

### Q037. Puwede ba sa NGO?

**Short answer:** Possible future adaptation; hindi shipped generic NGO platform.

**Paliwanag:** Map authority, eligibility, funding documents, privacy and audit requirements. Reuse verifier where useful instead of forcing government-specific flow.

**Evidence:** [MIT license](../../../LICENSE); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Walang NGO adapter/integration.

**Possible follow-up:** Ano ang kailangang baguhin?

### Q038. Public ba lahat ng beneficiaries?

**Short answer:** Hindi; private originals/identity and reports stay off-chain.

**Paliwanag:** Opaque references/hashes and some amounts can still reveal metadata. Full personal disclosure to donors is not the product promise.

**Evidence:** [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol); [NPC privacy assessment guidance](https://privacy.gov.ph/5-pillars-of-compliance-2/); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Off-chain is not automatically secure.

**Possible follow-up:** Paano ang public transparency?

### Q039. Paano mag-report ng kulang/walang cash?

**Short answer:** Recipient can report full, less or not received.

**Paliwanag:** Adverse report opens/reopens a linked private case; earlier answers remain. It does not prove theft or authorize another payout.

**Evidence:** [Private answers/grievances](../../../backend/app/services/outcomes.py); [Scoped business projections](../../../backend/app/projections.py).

**Limit:** No secure identity assurance today.

**Possible follow-up:** Paano kung binago ang answer later?

### Q040. Paano kung may collusion?

**Short answer:** Hindi kayang patunayan ng hashes ang physical truth.

**Paliwanag:** Separate duties, recipient reports, retained evidence and oversight can support investigation. False but consistent input may still match.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [Audit projections](../../../backend/app/services/audit_views.py).

**Limit:** Coercion/collusion remain risks.

**Possible follow-up:** Ano ang actual deterrent?

### Q041. Bakit hindi database lang?

**Short answer:** Database is essential; commitment gives another reference for detecting changes.

**Paliwanag:** Value depends on independent retention/governance. Compare signed logs/timestamping rather than assuming blockchain is always best.

**Evidence:** [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol); [Accepted evidence compatibility ADR](../../adr/2026-10-10-mvp-evidence-protocol-and-registry.md).

**Limit:** Local node is not independent governance.

**Possible follow-up:** Sino ang independent witness?

### Q042. Anong blockchain ang actual?

**Short answer:** Local EVM development chain, chain ID31337.

**Paliwanag:** Actual local deployments/transactions/reads ang demo. Walang public Polygon deployment o purchased gas.

**Evidence:** [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol); [Loopback/Node configuration guard](../../../backend/app/config.py).

**Limit:** Not production decentralized infrastructure.

**Possible follow-up:** Bakit pinili ang EVM?

### Q043. Ano ang nasa chain?

**Short answer:** Selected hashes, opaque references at funding amounts.

**Paliwanag:** Names, contact/ID, receipt contents, secrets and private answers stay in database/files. Metadata risk still exists.

**Evidence:** [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol); [Accepted evidence compatibility ADR](../../adr/2026-10-10-mvp-evidence-protocol-and-registry.md).

**Limit:** Not all events/contents are on-chain.

**Possible follow-up:** Puwede bang ma-link sa tao?

### Q044. Paano ginagawa ang hash?

**Short answer:** Deterministic versioned canonical evidence content ang hini-hash.

**Paliwanag:** Exact payload, domain/version and original-byte references matter. Separate evidence protocol preserves legacy hasher compatibility.

**Evidence:** [Accepted evidence compatibility ADR](../../adr/2026-10-10-mvp-evidence-protocol-and-registry.md); [Independent canonical vectors](../../../shared/protocol/evidence-v1-vectors.json).

**Limit:** Hash match does not authenticate an original.

**Possible follow-up:** Paano kapag nagbago ang format?

### Q045. Ano ang proof ng match?

**Short answer:** Match ang saved committed evidence sa actual chain read.

**Paliwanag:** It checks content continuity for the defined scope. Hindi nito pinapatunayang genuine ang original or physically delivered ang cash.

**Evidence:** [Fresh fail-closed evidence comparison](../../../backend/app/services/integrity.py); [Signer-free independent verifier](../../../contracts/scripts/verify_evidence.js).

**Limit:** Garbage input can still match.

**Possible follow-up:** Bakit may human review pa?

### Q046. Paano ang failure states?

**Short answer:** Distinct ang unreachable chain, absent anchor, mismatch at missing evidence.

**Paliwanag:** Only actual read plus match can show verified. Pending/submitted/historical confirmed is a different state.

**Evidence:** [Fresh fail-closed evidence comparison](../../../backend/app/services/integrity.py); [Fresh finals readiness](../FINALIST_READINESS.md).

**Limit:** No inferred green state during failure.

**Possible follow-up:** Paano kung cached lang ang result?

### Q047. Safe ba ang retries?

**Short answer:** Saved command identity and durable recovery avoid repeating the business action.

**Paliwanag:** Inspect the same transaction after uncertainty. Worker reconciles its saved submission instead of inventing hashes or paying again.

**Evidence:** [Durable signer worker](../../../contracts/scripts/anchor_worker.js); [Consistent backup/restore implementation](../../../backend/scripts/backup_mvp.py).

**Limit:** No offline physical-cash retry policy.

**Possible follow-up:** Paano kung na-double click?

### Q048. Lahat ba ng event may chain fee?

**Short answer:** Hindi; audit events at chain commitments are different records.

**Paliwanag:** Selected evidence versions create commitments. Count the actual mix and correction pairs before budgeting.

**Evidence:** [Accepted evidence compatibility ADR](../../adr/2026-10-10-mvp-evidence-protocol-and-registry.md); [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol).

**Limit:** No blanket per-event fee estimate.

**Possible follow-up:** Ilang writes bawat case?

### Q049. May actual gas measurement ba?

**Short answer:** May local transaction-specific measurements, hindi public peso fees.

**Paliwanag:** Correction pair used555889 gas; example evidence-registry deployment781144. Keep transaction type and provenance with numbers.

**Evidence:** [Measured local gas evidence](../evidence/test-results.md); [Hypothetical model below](#hypothetical-financial-model).

**Limit:** Not average per household.

**Possible follow-up:** Magkano kapag congested?

### Q050. Sino ang may signer/gas?

**Short answer:** Local-only development signer ang demo; institutional custody is future design.

**Paliwanag:** Real keys need approved operator, rotation, funding, monitoring and recovery. Beneficiaries need no wallet.

**Evidence:** [Durable signer worker](../../../contracts/scripts/anchor_worker.js); [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol).

**Limit:** No public signer/governance deployed.

**Possible follow-up:** Paano kung compromised ang key?

### Q051. Ano ang architecture?

**Short answer:** Next.js browser, FastAPI, PostgreSQL/private files, durable worker at EVM registry.

**Paliwanag:** Database transaction records business/audit/intent; worker submits/reconciles chain work. Verification reads pinned deployment.

**Evidence:** [Implemented architecture](../../system/architecture.md); [Atomic command/replay boundary](../../../backend/app/commands.py).

**Limit:** Local prototype topology, no production SLA.

**Possible follow-up:** Ano ang single points of failure?

### Q052. Aling backend ang authoritative?

**Short answer:** backend/app/main.py ang approved MVP backend.

**Paliwanag:** Legacy backend/server.py/SQLite stays separate; no dual writes. Other PR stack assumptions are different.

**Evidence:** [Authoritative FastAPI API](../../../backend/app/main.py); [Implemented architecture](../../system/architecture.md); [Branch/PR triage](../GITHUB_TRIAGE.md).

**Limit:** Do not combine branch capabilities.

**Possible follow-up:** Paano iko-consolidate later?

### Q053. Bakit FastAPI?

**Short answer:** Typed API/domain workflow boundaries fit the approved implementation.

**Paliwanag:** API invokes explicit services and stored role/scope resolution. Framework choice alone is not security proof.

**Evidence:** [Authoritative FastAPI API](../../../backend/app/main.py); [Strict MVP request schemas](../../../backend/app/schemas/mvp.py).

**Limit:** No framework performance superiority measured.

**Possible follow-up:** Paano ang validation/errors?

### Q054. Ano ang ginagawa ng Next.js?

**Short answer:** Role pages, forms, lookup, readable status at responsive navigation.

**Paliwanag:** Client sends real commands and displays server results. UI controls do not establish authenticated identity.

**Evidence:** [Role workspace/selection shell](../../../frontend/components/mvp/Workspace.tsx); [Sea-and-Sun design system](../../../DESIGN.md).

**Limit:** No secure sign-in in this branch.

**Possible follow-up:** Puwedeng direktang tawagin ang API?

### Q055. Paano iiwasan ang stale decisions?

**Short answer:** Revision/current-check boundaries require review of current evidence.

**Paliwanag:** Changed check/claim/comparison resets acknowledgement; stale actions are refused. Earlier versions stay available.

**Evidence:** [Atomic command/replay boundary](../../../backend/app/commands.py); [Human claim workflow](../../../backend/app/services/claims.py); [PIN/code/once-only handover service](../../../backend/app/services/payouts.py).

**Limit:** Not proof of human comprehension.

**Possible follow-up:** Paano kung sabay ang reviewers?

### Q056. Ano ang idempotency key?

**Short answer:** Identifier para ma-recognize ang same command kapag repeated ang request.

**Paliwanag:** Same content can recover the original result; conflicting reuse is refused. Hindi ito permission to repeat physical cash.

**Evidence:** [Atomic command/replay boundary](../../../backend/app/commands.py); [PIN/code/once-only handover service](../../../backend/app/services/payouts.py).

**Limit:** Needs correct client/server handling.

**Possible follow-up:** Paano kung response lost?

### Q057. Bakit separate worker ang blockchain?

**Short answer:** Hindi atomic ang database commit at remote chain submission.

**Paliwanag:** Save durable intent with business history, then submit/reconcile. Database correction can exist while chain work is pending.

**Evidence:** [Implemented architecture](../../system/architecture.md); [Durable signer worker](../../../contracts/scripts/anchor_worker.js).

**Limit:** Pending is not verified.

**Possible follow-up:** Paano kung crash between steps?

### Q058. Paano ipinapaliwanag ang errors?

**Short answer:** Role-specific actionable guidance, with safe fallback for unknown errors.

**Paliwanag:** Explain permitted next step without leaking raw gateway/private details. Uncertain writes tell staff to inspect before retry.

**Evidence:** [Role-specific recovery catalogue](../../../frontend/lib/workflow-errors.ts); [Fresh finals readiness](../FINALIST_READINESS.md).

**Limit:** Not all operational cases field-tested.

**Possible follow-up:** Sino ang may action kapag error?

### Q059. Enough ba ang health200?

**Short answer:** Hindi; health reports chain/storage not_checked.

**Paliwanag:** Check actual permitted records and a fresh integrity read. HTTP availability alone says little about evidence readiness.

**Evidence:** [Authoritative FastAPI API](../../../backend/app/main.py); [Safe demo runbook](../DEMO_RUNBOOK.md).

**Limit:** Not a full dependency health check.

**Possible follow-up:** Ano ang preflight ninyo?

### Q060. Paano ang extraction?

**Short answer:** Extract available PDF text, then human confirms editable fields.

**Paliwanag:** Manual confirmation remains available. Uploaded original bytes are retained and linked; extraction is not authenticity checking.

**Evidence:** [Original-file storage/retrieval](../../../backend/app/services/evidence.py); [Bounded PDF extraction](../../../backend/app/services/extraction.py).

**Limit:** No general OCR/AI guarantee.

**Possible follow-up:** Paano ang scanned PDF?

### Q061. Bakit PostgreSQL?

**Short answer:** Transactions, constraints, relationships and durable job/history storage.

**Paliwanag:** Business state, audit and intent are committed together; explicit migrations follow approved model.

**Evidence:** [PostgreSQL model/guards](../../../backend/app/models/mvp.py); [Approved relational model](../../system/erd.md).

**Limit:** Database choice does not prove scale/security.

**Possible follow-up:** Paano ang backup and restore?

### Q062. Ano ang append-only dito?

**Short answer:** Earlier business evidence and audit history are retained when changes occur.

**Paliwanag:** Corrections/reviews/answers append lineage rather than silently erasing the past. Namespace retirement retains history.

**Evidence:** [PostgreSQL model/guards](../../../backend/app/models/mvp.py); [Atomic command/replay boundary](../../../backend/app/commands.py); [Approved relational model](../../system/erd.md).

**Limit:** Working projections can change; not every row immutable.

**Possible follow-up:** Sino ang DB administrator?

### Q063. Paano once-only ang handover?

**Short answer:** Atomic rules guard entitlement/current authorization and saved handover.

**Paliwanag:** Concurrent requests cannot both consume the same authorized action. Complaint/revised answer never restores payability.

**Evidence:** [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [PostgreSQL model/guards](../../../backend/app/models/mvp.py).

**Limit:** Cannot prevent physical cash outside app.

**Possible follow-up:** May concurrency tests ba?

### Q064. Bakit centavos?

**Short answer:** Exact integer money avoids floating-point rounding errors.

**Paliwanag:** Keep large values exact through database/API/UI formatting. Calculation rules have explicit rounding boundaries.

**Evidence:** [Approved relational model](../../system/erd.md); [Authoritative FastAPI API](../../../backend/app/main.py); [Documentary entitlement calculation](../../../backend/app/services/entitlements.py).

**Limit:** This does not validate the official rate.

**Possible follow-up:** Paano ang huge amounts?

### Q065. Paano itama ang funding error?

**Short answer:** Append linked reversal/replacement with retained original and reason.

**Paliwanag:** Correction pair preserves lineage and selected chain commitment semantics; hindi second independent release.

**Evidence:** [Funding/corrections service](../../../backend/app/services/funds.py); [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol).

**Limit:** Signatures remain unvalidated.

**Possible follow-up:** Paano makita ang original amount?

### Q066. Paano kung nagbago ang rule after payout?

**Short answer:** Paid amount/receipt stays fixed; later difference is informational.

**Paliwanag:** Preserve paid calculation version, later input versions and history. No automatic extra payment/refund.

**Evidence:** [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [Documentary entitlement calculation](../../../backend/app/services/entitlements.py); [Private answers/grievances](../../../backend/app/services/outcomes.py).

**Limit:** Not full financial-adjustment workflow.

**Possible follow-up:** Paano ang unpaid households?

### Q067. Ano ang nasa backup?

**Short answer:** Database, originals, manifests and needed recovery/config material must be planned together.

**Paliwanag:** Restoring DB alone cannot recreate chain history or missing original bytes. Protect secrets and test retrieval.

**Evidence:** [Consistent backup/restore implementation](../../../backend/scripts/backup_mvp.py); [Local operations/recovery](../../guides/local-mvp.md).

**Limit:** No promised recovery SLA.

**Possible follow-up:** May actual restore test ba?

### Q068. Paano kung mawala ang node?

**Short answer:** Old chain history becomes unavailable; do not fabricate recovery.

**Paliwanag:** Preserve DB/manifests and report failed checks. New deployment is a new witness, not verification of old commitments.

**Evidence:** [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol); [Consistent backup/restore implementation](../../../backend/scripts/backup_mvp.py).

**Limit:** Hardhat memory is volatile.

**Possible follow-up:** May retained independent checkpoint ba?

### Q069. Paano ang migrations?

**Short answer:** Explicit approved versioned migrations; no ad hoc schema rewrite.

**Paliwanag:** Apply only in authorized isolated setup, preserving existing histories. Compatibility changes need a decision and tests.

**Evidence:** [PostgreSQL model/guards](../../../backend/app/models/mvp.py); [Local operations/recovery](../../guides/local-mvp.md); [Approved relational model](../../system/erd.md).

**Limit:** No schema change for UI polish.

**Possible follow-up:** Paano kung migration fails?

### Q070. Paano isolated ang tests?

**Short answer:** Separate random databases, manifests, originals and explicit test configuration.

**Paliwanag:** Journey refuses nonempty household registry and never resets it. Partial runs remain; new lab for clean rerun.

**Evidence:** [Safe demo runbook](../DEMO_RUNBOOK.md); [Fresh finals readiness](../FINALIST_READINESS.md).

**Limit:** Test lab is not stage dataset.

**Possible follow-up:** Paano pipili ng tamang lab?

### Q071. May authentication ba ngayon?

**Short answer:** Wala; selectable active actors can be impersonated.

**Paliwanag:** Role URLs/scopes organize workflow but anyone can claim another active identity. Synthetic records only.

**Evidence:** [Authoritative FastAPI API](../../../backend/app/main.py); [Stored actor resolution](../../../backend/app/actor.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Not safe for real citizen data.

**Possible follow-up:** Bakit hindi ninyo muna ginawa ang login?

### Q072. Bakit may role checks kung walang login?

**Short answer:** Useful workflow constraints, pero hindi secure authorization.

**Paliwanag:** Stored role/assignment/scope checks reduce accidental wrong actions in evaluation. Trusted principal binding is still missing.

**Evidence:** [Stored actor resolution](../../../backend/app/actor.py); [Atomic command/replay boundary](../../../backend/app/commands.py).

**Limit:** No authenticated accountability.

**Possible follow-up:** Puwedeng i-bypass ang actor selector?

### Q073. Ano ang production auth requirements?

**Short answer:** Authenticated principals, secure sessions, roles, recovery and accountable provisioning.

**Paliwanag:** Map actual institutional authority; add transport/storage protections, audit and threat-model testing. Login alone is insufficient.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [Stored actor resolution](../../../backend/app/actor.py); [Branch/PR triage](../GITHUB_TRIAGE.md).

**Limit:** Not implemented in this MVP.

**Possible follow-up:** Puwedeng gamitin ang PR39 auth?

### Q074. Plaintext ba ang PIN/code storage?

**Short answer:** Authorization service stores protected representations; secrets stay off-chain.

**Paliwanag:** Separate PIN establishment, current code, expiration and consumption. Avoid projecting codes/logs or reusing demo credentials.

**Evidence:** [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [Accepted evidence compatibility ADR](../../adr/2026-10-10-mvp-evidence-protocol-and-registry.md).

**Limit:** Not full security audit or credential recovery.

**Possible follow-up:** Paano ang brute force/coercion?

### Q075. Compliant na dahil off-chain?

**Short answer:** Hindi; privacy compliance covers much more than storage location.

**Paliwanag:** Need purpose/legal basis, minimization, access, retention, rights, incident handling and institutional privacy review.

**Evidence:** [NPC privacy assessment guidance](https://privacy.gov.ph/5-pillars-of-compliance-2/); [NPC text of Data Privacy Act](https://privacy.gov.ph/data-privacy-act-/); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** No Data Privacy Act certification.

**Possible follow-up:** Sino ang controller/processor?

### Q076. Puwedeng ma-identify gamit ang hashes?

**Short answer:** Possible pa rin through guessing/linkage/metadata.

**Paliwanag:** Opaque IDs reduce direct exposure, not every correlation risk. Review predictable content and disclosure patterns.

**Evidence:** [Accepted evidence compatibility ADR](../../adr/2026-10-10-mvp-evidence-protocol-and-registry.md); [NPC blockchain advisory 2020-032](https://privacy.gov.ph/wp-content/uploads/2020/11/Redacted-Advisory-Opinion-No.-2020-032.pdf).

**Limit:** Hashes are not automatic anonymization.

**Possible follow-up:** Paano ang public verifier privacy?

### Q077. Protected ba ang private files?

**Short answer:** Scoped retrieval/inspection exists, but operational protection is incomplete.

**Paliwanag:** Harden authentication, filesystem/storage access, encryption, transport and retention before real originals.

**Evidence:** [Original-file storage/retrieval](../../../backend/app/services/evidence.py); [Scoped business projections](../../../backend/app/projections.py); [NPC privacy assessment guidance](https://privacy.gov.ph/5-pillars-of-compliance-2/).

**Limit:** Selected actors remain impersonable.

**Possible follow-up:** Puwedeng direct download ang files?

### Q078. Paano kung inspection log fails?

**Short answer:** Fail closed before disclosure under the implemented audit path.

**Paliwanag:** Auditor inspection logs are separate from business audit events. Missing logging is not a reason to quietly expose evidence.

**Evidence:** [Private inspection logging](../../../backend/app/services/access.py); [Audit projections](../../../backend/app/services/audit_views.py).

**Limit:** Not complete production privacy assurance.

**Possible follow-up:** Paano mag-retry safely?

### Q079. Security-audited ba?

**Short answer:** Hindi; functional regressions are not a security certification.

**Paliwanag:** Need threat modelling, auth/storage review, dependency response and independent testing before real data.

**Evidence:** [Fresh finals readiness](../FINALIST_READINESS.md); [MVP validation and test mappings](../../implementation/validation.md).

**Limit:** No penetration-test claim.

**Possible follow-up:** Ano ang highest-risk gap?

### Q080. Puwedeng fake ang payout kahit match?

**Short answer:** Oo; colluding people can record a false but consistent story.

**Paliwanag:** Recipient report, originals, role separation and independent investigation provide additional evidence. Hashing does not observe cash.

**Evidence:** [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [Private answers/grievances](../../../backend/app/services/outcomes.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Cannot prove physical truth.

**Possible follow-up:** Bakit may value pa ang trail?

### Q081. Puwedeng offline payout?

**Short answer:** Hindi available ang offline payout.

**Paliwanag:** Manual reference and assisted access still need connected services. Do not confuse legacy offline toggle with a durable queue.

**Evidence:** [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [Approved MVP scope and assurance](../../product/prd.md); [Safe demo runbook](../DEMO_RUNBOOK.md).

**Limit:** No automatic offline sync.

**Possible follow-up:** Paano sa disaster connectivity?

### Q082. Paano kung naputol during handover?

**Short answer:** Reconnect and read the same saved transaction before retry.

**Paliwanag:** Receipt may already exist kahit lost ang reply. Same-command replay can recover acknowledgement, not authorize physical cash twice.

**Evidence:** [Atomic command/replay boundary](../../../backend/app/commands.py); [PIN/code/once-only handover service](../../../backend/app/services/payouts.py); [Role-specific recovery catalogue](../../../frontend/lib/workflow-errors.ts).

**Limit:** Stop when state is unknown.

**Possible follow-up:** Paano kung matagal ang outage?

### Q083. Paano kung chain lang ang down?

**Short answer:** Show explicit pending/unreachable state, not verified.

**Paliwanag:** Publication gates and later integrity checks must respect actual state. Recovery continues saved submission; no invented chain result.

**Evidence:** [Fresh fail-closed evidence comparison](../../../backend/app/services/integrity.py); [Durable signer worker](../../../contracts/scripts/anchor_worker.js); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** Availability affects workflow progression.

**Possible follow-up:** Puwedeng mag-bypass para matapos?

### Q084. Saan hosted ngayon?

**Short answer:** Local development machine at loopback services.

**Paliwanag:** No public deployment, production network or actual-citizen service is claimed. Other laptops need their own setup or recorded fallback.

**Evidence:** [Safe demo runbook](../DEMO_RUNBOOK.md); [Fresh finals readiness](../FINALIST_READINESS.md).

**Limit:** Local demo is not nationwide access.

**Possible follow-up:** Paano mapapanood sa venue?

### Q085. Puwedeng free serverless lahat?

**Short answer:** Hindi automatically; durable workers, database/files and recovery need explicit support.

**Paliwanag:** Evaluate runtime limits, persistent storage, scheduled work, backups, privacy and total costs before choosing hosting.

**Evidence:** [Implemented architecture](../../system/architecture.md); [Local operations/recovery](../../guides/local-mvp.md).

**Limit:** No validated free-tier architecture.

**Possible follow-up:** Paano ang cold starts/worker lifetime?

### Q086. Anong deployment plan?

**Short answer:** Separate app/API, durable DB/private storage and monitored worker with pinned chain reference.

**Paliwanag:** Select infrastructure based on approved privacy, recovery, workload and governance needs, not branding.

**Evidence:** [Implemented architecture](../../system/architecture.md); [Local operations/recovery](../../guides/local-mvp.md).

**Limit:** No deployed production topology.

**Possible follow-up:** Ano ang minimum secure setup?

### Q087. Paano safe restart?

**Short answer:** Stop/restart only owned app while preserving chain, database and manifests.

**Paliwanag:** Supervisor recovers durable work. Do not kill arbitrary ports or restart surviving Hardhat to tidy the screen.

**Evidence:** [Owned local process supervisor](../../../backend/scripts/local_mvp.py); [Safe demo runbook](../DEMO_RUNBOOK.md); [Fresh finals readiness](../FINALIST_READINESS.md).

**Limit:** Node loss cannot be silently repaired.

**Possible follow-up:** Paano kung stale ownership file?

### Q088. Ano ang RTO/RPO?

**Short answer:** Wala pang committed recovery targets.

**Paliwanag:** Agree acceptable downtime/data loss with institution, then test DB/original/chain recovery together.

**Evidence:** [Consistent backup/restore implementation](../../../backend/scripts/backup_mvp.py); [Local operations/recovery](../../guides/local-mvp.md).

**Limit:** No service-level promise.

**Possible follow-up:** Ano ang acceptable loss sa payout?

### Q089. Sino ang operator?

**Short answer:** Future institution/service agreement must assign ownership and escalation.

**Paliwanag:** Cover monitoring, backups, key custody, incidents, user support and updates. Open source alone does not operate itself.

**Evidence:** [Durable signer worker](../../../contracts/scripts/anchor_worker.js); [Local operations/recovery](../../guides/local-mvp.md); [Hypothetical model below](#hypothetical-financial-model).

**Limit:** No production support contract.

**Possible follow-up:** Sino ang tatawagan kapag down?

### Q090. May wallet/tokens ba ang household?

**Short answer:** Wala; app records cash assistance, not token payment.

**Paliwanag:** No citizen crypto purchase, gas payment or wallet requirement. Blockchain witness is separate from cash handling.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol).

**Limit:** No bank/e-wallet transfer integration.

**Possible follow-up:** Bakit blockchain kung cash?

### Q091. Ano ang actual tests?

**Short answer:** Use the fresh readiness ledger, with exact passes, skips and failures.

**Paliwanag:** Backend/contracts/legacy/browser/build checks have separate scope and dates. Revised UI needs its own current evidence.

**Evidence:** [Fresh finals readiness](../FINALIST_READINESS.md); [MVP validation and test mappings](../../implementation/validation.md).

**Limit:** Do not add reruns into fake green total.

**Possible follow-up:** Ano ang newest completed run?

### Q092. Paano napatunayang fail closed?

**Short answer:** Tests refresh a real match into failed/unavailable state and check that current green result clears.

**Paliwanag:** Missing/incorrect/chain-failure paths cannot synthesize a successful read. Historical checks stay labelled historical.

**Evidence:** [Fresh fail-closed evidence comparison](../../../backend/app/services/integrity.py); [MVP validation and test mappings](../../implementation/validation.md); [Fresh finals readiness](../FINALIST_READINESS.md).

**Limit:** Not complete security/formal proof.

**Possible follow-up:** Paano kung malicious RPC?

### Q093. Paano full journey testing?

**Short answer:** Actual browser forms and original uploads exercise both own-device and assisted paths.

**Paliwanag:** Fresh isolated lab creates real saved calculations, list anchors, handovers and recipient reports. No reset or success fixture for core journey.

**Evidence:** [Actual editable browser journey](../../../frontend/tests/journey.spec.ts); [MVP validation and test mappings](../../implementation/validation.md); [Safe demo runbook](../DEMO_RUNBOOK.md).

**Limit:** Synthetic people/cash only.

**Possible follow-up:** Puwedeng makita ang recording?

### Q094. Physical phones tested ba?

**Short answer:** Viewport emulation ang automated checks; hindi physical-device certification.

**Paliwanag:** Camera fixtures test fallback/lifecycle, not every real handset. Do manual device/network/accessibility testing next.

**Evidence:** [Optional camera/manual lookup](../../../frontend/components/mvp/SessionLookup.tsx); [Fresh finals readiness](../FINALIST_READINESS.md).

**Limit:** No field comprehension study.

**Possible follow-up:** Paano sa low-end Android?

### Q095. Ilang users ang kaya?

**Short answer:** Walang measured production capacity number.

**Paliwanag:** Profile realistic workloads, document sizes, concurrent decisions, worker backlog and read latency before promising scale.

**Evidence:** [Atomic command/replay boundary](../../../backend/app/commands.py); [Implemented architecture](../../system/architecture.md).

**Limit:** No nationwide-load claim.

**Possible follow-up:** Ano ang load-test plan?

### Q096. Ano ang DB bottleneck?

**Short answer:** Locks, scoped projections, originals and concurrent commands need profiling.

**Paliwanag:** Correctness-critical atomic boundaries may serialize work. Measure queries/lock waits before changing constraints.

**Evidence:** [Atomic command/replay boundary](../../../backend/app/commands.py); [Actual local automatic checks](../../../backend/app/services/checks.py).

**Limit:** No measured bottleneck ranking.

**Possible follow-up:** Puwedeng i-shard agad?

### Q097. Paano ang chain throughput?

**Short answer:** Commitment backlog/confirmation delay can slow gates and verification.

**Paliwanag:** Durable jobs preserve intent, but monitor lag and cost. Do not label queued work verified.

**Evidence:** [Durable signer worker](../../../contracts/scripts/anchor_worker.js); [Actual evidence registry](../../../contracts/contracts/AyudaChainEvidenceRegistry.sol).

**Limit:** No finality/throughput SLA.

**Possible follow-up:** Puwedeng batch commitments?

### Q098. Paano crash recovery testing?

**Short answer:** Isolated fault tests interrupt submission/recovery and inspect retained candidates/state.

**Paliwanag:** Preserve exact signed material and reconcile actual chain observations. Never reset evaluator history to fake recovery.

**Evidence:** [Consistent backup/restore implementation](../../../backend/scripts/backup_mvp.py); [Durable signer worker](../../../contracts/scripts/anchor_worker.js); [MVP validation and test mappings](../../implementation/validation.md).

**Limit:** Fault scenarios are bounded.

**Possible follow-up:** Paano kung both DB and node lost?

### Q099. Paano meaningful ang tests?

**Short answer:** Assert safety outcomes at boundaries, not just copy implementation steps.

**Paliwanag:** Concurrency, stale revision, lost replies, exact money, unavailable evidence and role-projection failures matter.

**Evidence:** [Fresh finals readiness](../FINALIST_READINESS.md); [MVP validation and test mappings](../../implementation/validation.md).

**Limit:** Passing tests do not prove all behavior.

**Possible follow-up:** Anong test fails before the fix?

### Q100. Ano ang untested pa?

**Short answer:** Production auth/security, field procedure, physical devices, comprehension and real scale.

**Paliwanag:** Also review governance, signatures, connectivity, recovery objectives and current official rules.

**Evidence:** [Fresh finals readiness](../FINALIST_READINESS.md); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** No real-household readiness.

**Possible follow-up:** Would you release tomorrow?

### Q101. Bakit hindi spreadsheet?

**Short answer:** Connected versions, evidence, once-only records and independent checks are the proposed value.

**Paliwanag:** A good spreadsheet can be cheaper and sufficient. Compare total burden and traceability in a study.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [Implemented architecture](../../system/architecture.md).

**Limit:** No measured competitive ROI.

**Possible follow-up:** Bakit hindi improve ang spreadsheet?

### Q102. May government systems na ba?

**Short answer:** Meron; hindi natin claim na walang existing app.

**Paliwanag:** DSWD XI reported ECT Offline Payout System in2025. Ours has no offline payout; proposed evidence-trail value needs comparative validation.

**Evidence:** [DSWD official issuance register](https://www.dswd.gov.ph/issuance/); [DSWD XI ECT Offline Payout System announcement](https://fo11.dswd.gov.ph/2025/09/%F0%9D%97%97%F0%9D%97%A6%F0%9D%97%AA%F0%9D%97%97-%F0%9D%97%AB%F0%9D%97%9C-%F0%9D%97%A5%F0%9D%97%BC%F0%9D%97%B9%F0%9D%97%B9%F0%9D%98%80-%F0%9D%97%A2%F0%9D%98%82%F0%9D%98%81-%F0%9D%97%98%F0%9D%97%96/); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** No exhaustive market study/integration.

**Possible follow-up:** Aling system ang authoritative?

### Q103. Paano kung may NGO platform na?

**Short answer:** Integration or selected independent witnessing may be better than replacement.

**Paliwanag:** Define record ownership, originals, export and private access. Avoid duplicate identities/inconsistent grant authority.

**Evidence:** [Signer-free independent verifier](../../../contracts/scripts/verify_evidence.js); [Accepted evidence compatibility ADR](../../adr/2026-10-10-mvp-evidence-protocol-and-registry.md); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** No NGO connector shipped.

**Possible follow-up:** Puwedeng verifier lang ang gamitin?

### Q104. Puwedeng AI later?

**Short answer:** Possible review support after validated need, data/privacy and false-positive evaluation.

**Paliwanag:** Current checks are deterministic; humans decide. Learned models need separate evidence and approval.

**Evidence:** [Actual local automatic checks](../../../backend/app/services/checks.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** No learned fraud model implemented.

**Possible follow-up:** Bakit AI sa old marketing?

### Q105. Multiple agencies/regions?

**Short answer:** Not validated as multitenant production service.

**Paliwanag:** Office/run/disaster scopes exist, but cross-region identity/policies/isolation and administration need more design.

**Evidence:** [Approved relational model](../../system/erd.md); [Stored actor resolution](../../../backend/app/actor.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** One Field Office scope now.

**Possible follow-up:** Paano ang duplicate across regions?

### Q106. Goods, tranches, representatives?

**Short answer:** Separate future workflows iyon.

**Paliwanag:** Goods need inventory, tranches need sequencing, representatives need explicit delegated authority. Hindi label change lang.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [PIN/code/once-only handover service](../../../backend/app/services/payouts.py).

**Limit:** Not implemented in current cash MVP.

**Possible follow-up:** Alin ang priority expansion?

### Q107. Official audit findings sa app?

**Short answer:** Hindi; read-only evidence review ang current Auditor.

**Paliwanag:** Inspect originals, versions, exceptions and chain checks. Formal findings/response/export need institutional procedures.

**Evidence:** [Audit projections](../../../backend/app/services/audit_views.py); [Approved MVP scope and assurance](../../product/prd.md).

**Limit:** No COA certification/complete audit.

**Possible follow-up:** Sino ang puwedeng maging Auditor?

### Q108. Bakit dalawang stacks?

**Short answer:** Independent branches developed different product/data/auth assumptions.

**Paliwanag:** Current approved PostgreSQL workflow is broader; PR39 has authenticated synthetic accounts/different accounting model. Reuse compatible UI patterns cautiously.

**Evidence:** [Branch/PR triage](../GITHUB_TRIAGE.md).

**Limit:** Do not combine their claims.

**Possible follow-up:** Alin ang best reference?

### Q109. Ano ang ika-cut sa deadline?

**Short answer:** New features; preserve honest evidence and one rehearsed journey.

**Paliwanag:** Freeze source for validation, use saved records and labelled fallback. Do not trade integrity safeguards for a smoother pitch.

**Evidence:** [Safe demo runbook](../DEMO_RUNBOOK.md); [Fresh finals readiness](../FINALIST_READINESS.md).

**Limit:** No last-minute financial/contract change.

**Possible follow-up:** Ano ang critical must-show?

### Q110. Ano ang ask sa judges?

**Short answer:** Feedback and a supervised workflow-validation partner.

**Paliwanag:** Agree forms/roles/rules and measures: completeness, ease of use and time to trace a case. Then harden before real data.

**Evidence:** [Approved MVP scope and assurance](../../product/prd.md); [Adoption/readiness boundaries](../../guides/local-mvp.md).

**Limit:** Not an instant rollout/customer claim.

**Possible follow-up:** Ano ang next concrete milestone?

## Five complete fictional user journeys

Demo scenarios ito, hindi real citizens, actual agency pilots o official mandated sequence. Current prototype rules ang sinusundan. Secure authentication remains pending.

### 1. May sariling connected device — Maria, DFC-2026-9101

1. DSWD uploads funding original, confirms fields, then separately opens covered intake.
2. Maria registers household/address/members and private ID/photo evidence, then submits damage/category.
3. Eligible Barangay staff respond independently. Punong submits selected responded threads with council-resolution original. Helper/own-household recusal applies.
4. DSWD reviews current checks, flags and responses; records category/decision/reason. Approval alone does not supply missing amount inputs.
5. DSWD records documentary inputs, prepares list, waits for actual matching chain publication, then assigns household/site/date/cash staff and opens session.
6. Maria checks amount, opens a current attempt; payer compares photo ID and presents fixed cash. Maria counts before sharing current code; payer confirms household/amount and records once.
7. Receipt survives reload. Maria separately reports full receipt. Auditor opens originals/history and performs a fresh chain comparison.

**End:** one fixed handover, separate recipient statement, actual integrity result. **Failure:** lost reply means inspect same transaction; unavailable chain means unavailable, never fake match. [Actual journey test](../../../frontend/tests/journey.spec.ts).

### 2. Walang phone at walang ID initially — Rosa, DFC-2026-9102

1. Barangay helper registers household declaration without mandatory phone/ID. Recipient private details use the recipient panel.
2. Helper cannot endorse that household; other eligible officers respond or actual missing-staff/deadline fallback is retained and labelled.
3. DSWD documents field check and accepted photo-ID originals when available. Kung wala pa rin accepted ID, blocked ang payment under this prototype.
4. DSWD decides eligibility, records amount inputs, waits for publication and schedules distinct eligible cash staff.
5. Assigned payer compares identity. Recipient privately establishes6–12digit PIN after the required check, then re-enters it to authorize assisted attempt on a connected staff device.
6. Recipient counts cash and supplies the separate payout code. Payer records one handover with a distinct assigned checker.
7. Checker records private exit answer, possibly after closure. Payer cannot submit their own recipient exit answer. Adverse report opens linked case; Auditor checks history/proof.

**End:** explicit assisted path, one handover, retained follow-up. **Limit:** no general PIN recovery, certification-only payout or offline route. Coercion/staff independence need real operational safeguards. [Payout rules](../../../backend/app/services/payouts.py), [outcomes](../../../backend/app/services/outcomes.py).

### 3. Negative barangay response o missing submission — Ana, DFC-2026-9103

1. Covered open intake accepts household claim, freezes version and starts saved response window.
2. Barangay appends disagreement/reason; hindi iyon DSWD rejection. Missing staff/submission leads to actual labelled scheduler snapshot, preserving responses.
3. DSWD reads frozen comparisons/thread; flag is not automatic rejection. Reviewer may refer a specific question with fresh deadline.
4. Eligible officer appends reply. Timeout routes actual unanswered referral without inventing a response. Existing review can continue after intake closes.
5. DSWD records final decision/reason. If declined, one substantive new-information resubmission is permitted only while intake remains open; full appeals are deferred.
6. If approved, documentary amount → publication → session → identity/authorization → one handover → private report proceeds normally.
7. Auditor inspects deadlines, fallback reason, decision lineage and current commitments.

**End:** inspectable decision, including negative/missing evidence. **Limit:** false consistent attestations can pass; exact official referral/appeal mapping incomplete. [Claims](../../../backend/app/services/claims.py).

### 4. Failed ID check, later clearance, lost reply — DFC-2026-9104

1. Assigned payer records failed comparison/reason; stop/hold applies. No fake authorization or payout result.
2. DSWD reviews and records permitted clearance/evidence. A distinct session created after clearance is required; it can be later the same day.
3. Current authority is checked again. Same transaction/entitlement gets a fresh attempt, not a new payment entitlement.
4. Later actual comparison passes; payer presents fixed cash, recipient supplies current code, final review repeats household/amount.
5. If response disappears after saving, reconnect and GET that transaction. Existing receipt means already recorded; safe same-request replay recovers acknowledgement, not cash twice.
6. Worker reconciles saved submission after interruption; it does not reperform business handover.
7. Recipient report and fresh audit continue with failed/cleared/paid history retained.

**End:** one recorded handover with appended attempts. **Limit:** no offline workaround when state cannot be confirmed. [Commands](../../../backend/app/commands.py), [worker](../../../contracts/scripts/anchor_worker.js).

### 5. Funding typo at kulang na cash report — DFC-2026-9105

1. DSWD compares retained funding original, records linked reasoned reversal/replacement; old entry remains.
2. Selected correction pair is actually committed. Failed/pending anchor stays explicit; no deleted DB correction or invented release.
3. Recipient reports less and actual reported amount. One linked grievance opens/reopens; statement is not automatic theft finding.
4. DSWD records human investigation/resolution. Revised answers/reopening retain history; later full answer does not silently close the case.
5. Later amount basis changes leave paid receipt fixed; difference is informational, no automatic repayment/refund.
6. Auditor inspects permitted ledger lineage, originals, claim/basis/list/payout/case history; access logs precede disclosure.
7. Separate verifier compares authorized exact material/originals against pinned registry. Match/mismatch/absence/unreachable/missing-material remain distinct.

**End:** retained correction, fixed handover, private concern history and checkable evidence. **Limit:** app cannot establish physical truth or issue an official audit finding. [Funds](../../../backend/app/services/funds.py), [independent verifier](../../../contracts/scripts/verify_evidence.js).

## Hypothetical financial model

**Lahat ng peso assumptions dito ay invented classroom scenario. Hindi quote, actual spending, forecast, customer price, procurement estimate o recommended budget.** Palitan ng dated supplier quotes/workload evidence before real offer. Walang beneficiary fee/percentage ng ayuda.

| Monthly item | Invented assumption | Arithmetic |
|---|---|---:|
| Compute/database | Placeholder, not quote | ₱1,500 |
| Private storage | Volume/retention unspecified | ₱500 |
| Backups | Not an SLA | ₱500 |
| Monitoring | Placeholder | ₱500 |
| Support labor | 12h × assumed ₱500 | ₱6,000 |
| Training allocation | 24h × ₱500 ÷6months | ₱2,000 |
| Subtotal | Sum | ₱11,000 |
| Risk reserve | Assumed20% | ₱2,200 |
| Delivery-cost base | Before omitted costs | **₱13,200** |
| Institution fee | Arbitrary scenario input | **₱18,000** |
| Contribution | 18,000−13,200; not net profit | **₱4,800 /26.7%** |

**Hindi priced, kaya hindi zero:** SMS, public gas, site internet/devices/travel, security review/fixes, identity services, legal/procurement/tax/liability, incident surge, governance and migration. Kapag more than₱4,800 ang omitted monthly costs, ubos ang contribution.

Separate illustrative setup:40h×₱500=₱20,000 direct labor versus arbitrary₱30,000 fee. Difference₱10,000 is not proven profit. Huwag i-double-count ito sa training allocation.

**ROI sensitivity:** Assume1,000records/month,8min baseline versus5min future, staff-time value₱250/hour. Scenario saves50hours, valued₱12,500. Against₱18,000 recurring fee, **−₱5,500** before setup/other costs. Walang positive ROI claim. Fee alone requires72saved hours or4.32min per1,000records to break even. Observe real times; wage value is not actual payroll savings unless expenditure changes.

**Gas:** measured local correction pair555,889units; deployment example781,144units. `token fee = gasUsed × effectiveGasPriceWei ÷10^18`; for gwei, `gasUsed × gwei ÷10^9`. Hypothetical30/300/1,000gwei produces0.01667667/0.1667667/0.555889tokens for that correction pair. These are sensitivity inputs, not live market prices. No invented token/PHP rate. Hindi per-household budget ang correction example. [Gas documentation](https://docs.polygon.technology/pos/concepts/transactions/eip-1559), [local measurements](../evidence/test-results.md).

## Ten difficult adversarial questions

1. **“Same laptop ang chain. Nasaan ang independence?”** Local protocol demo lang; approved independent witness/retention/governance is future work. Signed logs may be better if blockchain adds no justified value. Evidence:Q041–042. Follow-up: who is the adversary and independent operator?
2. **“Anyone can be Auditor. Private ba talaga?”** No operational privacy claim today; actor impersonation is known. Synthetic only until authenticated access/storage/transport controls are ready. Evidence:Q071–077. Follow-up: exact trusted principal boundary?
3. **“Puwedeng i-anchor ang forged document.”** Oo. We preserve evidence/version continuity, not authenticity. Human validation/signature trust/oversight remain. Evidence:Q027,045,080. Follow-up: why does retained provenance help investigation?
4. **“Wala kayong complete budget enforcement?”** Correct; recorded authority is not certified cash or full liquidation. Establish authorized external control before real pilot. Do not import other branch's caps by claim. Evidence:Q020,028. Follow-up: who controls available cash?
5. **“Excluding people ang PIN/ID.”** Real limitation. Registration can proceed, but payment still needs current conditions. Validate an authorized inclusive alternative, do not bypass on stage. Evidence:Q031–034. Follow-up: how can recovery be safe?
6. **“Expired code then second payout?”** Fresh attempt cannot repay an already-handed-over entitlement. Read saved receipt after uncertainty. Evidence:Q047,063,082. Follow-up: distinguish request retry from physical cash action.
7. **“Guaranteed lower corruption?”** No. Measure traceability/completeness/response quality; false originals/collusion can remain. Evidence:Q009,040,080. Follow-up: what metric could disprove the value?
8. **“Your finance numbers are made up.”** Yes, explicitly hypothetical. Worksheet shows assumptions/omissions and negative ROI sensitivity, not pricing evidence. Evidence:Q011–020. Follow-up: which quotes and workload observations replace them?
9. **“Existing government system works offline.”** That is a relevant alternative; ours does not. Compare evidence-trail needs and integration before proposing replacement. Evidence:Q102. Follow-up: what authoritative platform should remain?
10. **“Why trust an unfinished hackathon app?”** Judge the bounded prototype against actual code/tests and honest limits. Seek supervised validation, not real-citizen rollout tomorrow. Evidence:Q091–100,110. Follow-up: highest-priority readiness gate?
