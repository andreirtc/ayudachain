# Read-only staff audit and demo completion

DSWD and Auditor can open /audit. GET /api/audit-workspace returns private batch accounting in exact centavos, per-area remaining allocations, household review flags, open concern counts, saved payout anchor states and recipient acknowledgement facts. Audit is read-only, with no payout/review/concern mutation controls for Auditor. Other roles and public requests are denied. Raw anchor envelopes and deployment pins are never returned.

The shared Tonal components connect the workspace to exact household records, concerns and receipt checks. Historical confirmation is an earlier observation, and the audit response explicitly marks current proof as NOT_CHECKED. Check receipt uses the existing live verifier. General audit descriptions remain local history and are labelled accordingly. The API limits payout/event details to the latest 200 rows and supplies total counts; complete permitted history remains available in existing payout/audit-trail endpoints.

The accepted demo sequence now has backend support for payout desk checks, own-household and assisted concerns, retained DSWD replies and office audit inspection, on top of existing registration, CSV, review, lists, arrangements, payouts, receipt snapshots, anchors and acknowledgements. This finishes demo feature wiring; the next visual iteration can reshape these screens around the groupmate's Tonal reference without inventing endpoints.

Validation is intentionally focused at the user's request: three desk checks, four concern journeys, two audit checks, one combined desktop/phone browser scenario, independent TypeScript and one isolated production build. Broad legacy browser/API/contract suites are not rerun. No receipt protocol, contract or anchor worker change is introduced. The browser fixture labels the chain unavailable and does not claim live-chain confirmation.

Non-demo release work stays open: funding/allocation and historical recovery, offline sync, physical camera scanning, a guided tamper playground, general audit anchoring, account administration, dependency upgrades and deployment. The updated [demo script](demo-script.md) describes actual supported behavior. Original data, chain, port 3000 and retained builds are preserved.

## Recorded result

On 2026-10-14 all nine focused backend checks passed (desk 3, concerns 4, audit 2), independent TypeScript passed and the isolated production build passed. The combined authenticated demo passed on desktop1440x900 and phone390x844 (2 browser cases). Screenshots were inspected and retained under tmp/ayudachain-demo-backend-validation, covering assisted concerns, saved payouts, staff audit and household concerns. Temporary services stopped after the run. Browser emulation is not physical-device or human design approval.
