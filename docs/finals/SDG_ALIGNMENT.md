# AyudaChain and the SDGs — slide copy and defense

**Primary: SDG16, Peace, Justice and Strong Institutions — especially target16.6.** Supporting alignment: SDG1/target1.5 and SDG10/target10.2. Optional context: SDG13/target13.1. This is the team's proposed contribution based on implemented mechanisms, not measured SDG impact, UN endorsement or achievement of national indicators.

## Ready-to-paste slide copy

**Primary — SDG16: Strong institutions**
Connected evidence, retained decisions, recipient feedback and independently checkable commitments support accountable disaster-assistance records.

**Supporting — SDG1: No poverty**
Supports traceability of disaster cash-assistance records for affected households.

**Supporting — SDG10: Reduced inequalities**
Assisted access, optional QR/manual lookup and clearer language reduce some digital barriers.

Small footer: **Proposed contribution; field impact not yet measured.** Use three goals prominently rather than covering the slide with unrelated SDG badges.

## Natural Taglish explanation

“Pinaka-direct ang SDG16 dahil accountability ang core ng AyudaChain: may evidence behind decisions, retained history at checkable commitments. Related din sa SDG1 dahil disaster assistance ang context, at SDG10 dahil may assisted access at hindi mandatory ang QR o smartphone sa registration. Prototype alignment ito; wala pa kaming measured poverty reduction o inclusion impact.”

## Why these targets fit

| UN target | Connection to actual code | Limit and possible pilot measure |
|---|---|---|
| **16.6 — accountable/effective/transparent institutions** | [Human decisions](../../backend/app/services/claims.py), [retained history](../../backend/app/commands.py), [fresh integrity checks](../../backend/app/services/integrity.py) | No production accountability while actors are impersonable. Measure evidence completeness/time to trace a case; these are project measures, not official UN indicator substitutes. |
| **1.5 — resilience of vulnerable people to shocks/disasters** | [Documented relief amounts/lists](../../backend/app/services/entitlements.py), [cash handover records](../../backend/app/services/payouts.py) | App records assistance; no proven income/resilience/poverty outcome. Compare traceability/access after an authorized pilot. |
| **10.2 — social/economic/political inclusion** | [Assisted registration](../../backend/app/services/registry.py), [optional manual lookup](../../frontend/components/mvp/SessionLookup.tsx), [English/Taglish](../../frontend/components/mvp/Language.tsx) | No offline payout; accepted-ID/PIN/checker barriers remain. Measure task completion/help needed across approved user groups. |
| **13.1 — resilience/adaptive capacity to climate hazards/disasters** | Disaster-scoped records/sessions and follow-up | Contextual secondary alignment only. No hazard forecasting, climate modelling, prevention or measured climate resilience. |

## Questions judges may ask

**“Why SDG16 instead of only SDG1?”** Accountability/checkable evidence is what the software directly implements. It supports a relief context related to poverty, but the app itself does not create income or prove poverty reduction.

**“Does blockchain satisfy SDG16.5 anti-corruption?”** It can support investigating changes to committed evidence. Do not claim it eliminates corruption/bribery or has measured those UN indicators. False originals and collusion can still pass a hash comparison.

**“How is it inclusive with ID/PIN requirements?”** It removes some barriers through assisted registration, optional phone/QR and clearer language. Payment still has significant current constraints. Field inclusion evaluation and authorized recovery alternatives are future work, not claims of universal access.

**“Can you claim SDG13?”** As a supporting disaster-response context, with explicit limits. Prefer SDG16 as the main story; do not describe the app as climate prediction or prevention technology.

## Official sources checked14October2026

[UN Goal16 and targets16.6/16.7](https://sdgs.un.org/goals/goal16), [UN Goal1 and target1.5](https://sdgs.un.org/goals/goal1), [UN Goal10 and target10.2](https://sdgs.un.org/goals/goal10), [UN Goal13 and target13.1](https://sdgs.un.org/goals/goal13). The mapping from those goals to this app is our stated interpretation; sources define the goals, not endorsement of AyudaChain.
