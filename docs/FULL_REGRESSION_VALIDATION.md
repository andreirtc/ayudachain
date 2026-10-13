# Full regression validation, 2026-10-14

This pass restores the broader checks previously deferred for speed on the Material frontend branch. It uses invented records, disposable SQLite databases and owned loopback services. The original frontend, database and chain are preserved, along with the two requested comparison previews.

## Fixed behavior

The logo previously opened the public landing page, which displayed a static Sign in header even while the API session remained authenticated. It now opens the household home or staff overview as appropriate. One shared session provider also keeps the account and sign-out control visible when an authenticated user directly visits the public page. Browser checks cover sign-in, logo navigation, reload, public-page visits and explicit logout for every role at both sizes.

The shared appearance control has three labeled choices and dismisses on outside pointer/focus, Escape, selection and navigation. It fits small screens. The account announcement is available to screen readers on phones as well as desktop.

The registry again exposes DSWD CSV import/analysis and staff historical records. Selecting a household focuses its inline detail heading; returning focuses the original row. Payout records again expose search reset, exact references, a return to all permitted records and the receipt dialog's exact verification link. Empty and failed record reads remain distinct. Local Open Sans is now connected to both interface and heading font aliases.

## Results

- All 184 backend tests pass across 12 independently launched suites: accounting/API, authentication, CSV, duplicate/review history, acknowledgement, receipt snapshots, anchor recovery, lists, arrangements, payout desk, concerns and staff audit.
- All 14 frontend Node unit tests and all 21 Solidity contract tests pass.
- Five recovery scenarios pass against a freshly deployed disposable local contract, including lost mined responses, pending transactions, conflicting nonce consumption and lost deployment identity.
- All 140 distinct Playwright cases are covered at desktop 1440x900 and phone 390x844. The complete run passed 137; its three failures were two outdated household-view assertions and one removed phone-menu assertion. Those three pass after correction, with zero retries or skipped cases. The unchanged 137 were not needlessly repeated. Full-run and correction reports are retained separately, with a combined case ledger.
- Eighteen additional browser observations pass against a real disposable chain for legacy and captured version-2 receipts: verified, actual tampering, restoration, immutable capture after registry changes, unanchored and unavailable outcomes. Receipt bytes and canonical snapshot hashes are checked independently.
- Independent TypeScript and the production build pass. Builds now enforce TypeScript errors. ESLint, physical devices, comprehensive accessibility and human design acceptance are not claimed.

Earlier diagnostic failures are retained rather than presented as passing runs. The final browser ledger, full-run/correction JSON, backend suite logs and live-chain browser captures are under `tmp/ayudachain-full-validation/` on the validating machine; temporary artifacts are not versioned. Live UI screenshots were originally produced in an owned `ayudachain-verification-ui-*` temporary directory and copied into that validation folder.

## Repeatable checks

Install the existing locked frontend/contract dependencies and backend requirements using the documented local setup. Node 24 is used for the TypeScript-importing Node tests. From the repository root:

```powershell
npm run test:contracts
python backend/scripts/run_tests.py
npm --prefix frontend run test:unit
npm --prefix frontend run typecheck
node contracts/scripts/test_payout_anchor_live.js
$env:AYUDACHAIN_BUILD_DIR='.next-material-qa'
$env:NEXT_PUBLIC_API_URL='http://127.0.0.1:8000'
npm --prefix frontend run build
npm --prefix frontend run test:e2e
node frontend/tests/live-verification.mjs
```

The backend runner selects its existing `.venv` when present and runs each suite in a fresh process, avoiding global fixture collisions. Playwright starts its own production frontend on3301 and API on8301, refuses occupied ports, and resets only its owned temporary database between cases. The reset route exists only in the test launcher, not the production API. Browser interception forwards actual requests to that API; individual fault tests can still interrupt requests to exercise errors and uncertain responses.

The live browser helper uses3312/8312 and a newly deployed chain on8547, so it does not conflict with either comparison preview. Helpers stop their services afterward. Remove only the owned QA build when finished, and unset task-specific environment variables before ordinary development. Windows uses installed Edge; Linux CI installs Playwright Chromium.

CI is configured for every pull-request base, including stacked PRs, with backend dependencies, every backend suite, frontend unit/type/build/browser checks and both real-chain helpers. This local pass does not claim a remotely executed CI result or a deployment.

## Feature scope

The current frontend connects staff household registration and CSV intake, review/duplicate history, validated lists, payout arrangements, guarded payout recording, receipts, own-recipient acknowledgement, concerns and audit. Other roles expose substantially more than the anonymous navigation. The demo has provisioned accounts; staff household registration does not create login credentials, and public account sign-up is absent.

Funding release and allocation write APIs exist, but the current frontend displays their seeded balances and records without authoring forms. This is an actual interface gap, separate from deferred features without a backend.

The five-role MVP has additional claims/evidence/endorsement journeys, amount calculation, staffed and assigned payout sessions, code/PIN and independent-checker controls, recipient outcome answers and role task queues. Their frontend and backend belong to that separate implementation; they are not hidden pages in this branch. Its selectable actor is also not password authentication. Neither demo proves real identity or physical payment.

The earlier deferrals were choices for the narrower staff-validated-list demo. They do not establish that those capabilities are unnecessary for a broader product. A complete application-to-payment demo would need an agreed claim/intake path, explicit amount rules, assigned operational work and payment-discrepancy follow-up. Public account enrolment, administration/recovery and release hardening also remain separate work. Real SMS, offline synchronization and physical QR scanning need their own implementations and validation if selected.

The next useful product improvement is clearer role home pages with actual tasks, discoverable entry points and meaningful activity/empty states. Agree the expanded journey before porting the MVP's models: its PostgreSQL `/api/v1` API and evidence contract differ from this stack, so copying screens alone cannot deliver the missing capabilities.
