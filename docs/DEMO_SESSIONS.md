# Authenticated synthetic sessions

Follow-up: [PAYOUT_ANCHORS.md](PAYOUT_ANCHORS.md) adds Disbursing-only scoped recovery for new payout jobs. Its separate route is covered by role/CSRF checks; public representations remain restricted.

Bounded follow-up to [PR #17](https://github.com/andreirtc/ayudachain/pull/17). This implements password-authenticated synthetic accounts, server permissions and connected sign-in, not the full workmate claims/session/outcomes system. Original receipt hashes, accounting constraints, linked-duplicate history and payout replay semantics remain intact.

## Account and workflow ownership

Accounts are provisioned locally with random passwords, salted scrypt hashes and an assigned role/scope. There are no public default credentials and no account-picker login. Changing browser localStorage, request role fields or `X-Demo-Actor-ID` does not grant access.

- **DSWD:** office registry reads, registrations, CSV analysis, eligibility decisions, retained duplicate links, funding/allocation writes and private audit reads. Cannot record a payout.
- **Barangay:** own-barangay registry/status reads and registrations. New registrations remain pending for DSWD eligibility review, even when no duplicate is suggested. Contact/review notes and match references are redacted. Cannot approve eligibility, inspect review evidence or access named payout records.
- **Disbursing:** own-barangay household/status and payout/receipt reads; can record payouts in that area. Cannot approve eligibility, analyze office CSV or create funding. This is a barangay scope, not the MVP's future per-session staff assignment.
- **Beneficiary:** reads only the household linked to the account, its history and payouts/receipts. No privileged writes. Self-registration, claimant evidence and recipient acknowledgement remain follow-ups.
- **Auditor:** authenticated office-wide private reads; no business mutations, eligibility decisions, payout or reset. Private inspection-access logging remains future work.

The public landing, aggregate funding/batch views, limited receipt index and hash verification remain available without sign-in. Public activity excludes household/review/payout narratives. `/api/public/receipts` returns only distribution and batch references. Public verification redacts `beneficiary_id`; detailed OCR/contact/household records are not exposed there. Scoped accounts cannot read the shared legacy sample image/OCR, which contains another fictional household's details. Stored evidence is preserved and office readers retain inspection access. Existing unsalted receipt hashes and older predictable IDs are preserved for compatibility; this is not a new privacy-preserving commitment protocol.

Review requests require a reason. `reviewed_by` is now optional; the server records the authenticated DSWD account. A supplied different identity returns 403. Existing review rows, including old simulated reviewer labels, are retained without rewriting history. The HTTP reset endpoint returns 410 and performs no reset; deliberately resetting an isolated local dataset remains an operator procedure.

## Session lifecycle

Login returns an opaque HttpOnly, SameSite=Strict cookie. Only its SHA-256 digest, account revision and expiry are stored in the additive `demo_sessions` table. Login rotates/revokes the presented old session. Logout deletes its stored session. Expiry, disabled accounts and changes to passwords/role/scope/name invalidate subsequent private requests. Database/session lookup survives API client recreation; process-local browser role state is not an authority.

Mutation requests require a matching CSRF header, an application header and an allowed Origin when supplied. Login also checks the application header/Origin. Cookies use Secure when configured; insecure sign-in is restricted to loopback origins/hosts. Exact CORS origins replace wildcard authorization. Responses use no-store; validation errors omit submitted inputs, including passwords. Failed login attempts are counted under a lock and limited per client/account in this API process. This limiter is not a distributed production rate limiter.

The frontend keeps CSRF state in memory and restores the session from the server after refresh. `/sign-in` retains account input after an error, disables repeated submits and offers role-relevant destinations after success. Protected pages wait for the session; account changes remount their content, and 401 clears access. Logout removes rendered private content. Browsers can retain files a previously authorized user already downloaded; logout does not erase those copies.

Design references: [OWASP session guidance](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), [OWASP CSRF guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

## Local provisioning and configuration

From the repository root, `backend/.venv/Scripts/python.exe backend/scripts/provision_demo_accounts.py` creates `backend/.demo-accounts.json` and `backend/.demo-login.json`. Both are ignored by git. It generates credentials for the five role types, including four barangay-scoped disbursing accounts and a beneficiary linked to BEN-0004. It refuses to overwrite existing credentials and does not connect to/reset records or the blockchain. Protect these local files; use a private externally configured account file for any later hosted evaluation.

`DEMO_ACCOUNTS_FILE` overrides the hashed account file location. `SESSION_TTL_SECONDS` defaults to 3600 and is bounded to 60–86400. `SESSION_COOKIE_SECURE` defaults false only for the loopback prototype. `CORS_ORIGINS` must name exact frontend origins; `*` does not authorize sign-in. `RECEIPTS_DIR` selects receipt storage and allows tests to isolate files from original receipts. Account provisioning is required for private workflows; a missing/invalid file fails closed with 503. Public functionality does not require credentials.

No generated passwords are committed, printed in chat or included in frontend bundles. The fixed password in test support belongs only to temporary test accounts and is never a production fallback.

## Validation

- Existing API/business suite: 76 passed through real authenticated role-appropriate test clients. Reset occurs explicitly in a temporary fixture, not through an HTTP bypass.
- Session/permission suite: 19 passed, including anonymous/forged role rejection, reviewer binding, CSRF/origin checks, private file and household scope, independent Auditor permissions, rotation/logout/expiry/account changes, redacted public responses, disabled HTTP reset, input redaction and concurrent failed-login counting.
- Backend units: 21 passed. Frontend reference/connectivity tests: seven passed.
- Independent frontend TypeScript and production build passed; the existing build still skips embedded types/lint. Lint is not claimed.
- Headless Playwright 1.64.0 with installed Microsoft Edge: 16 passed at 1440×900 and 390×844. Actual browser requests call the isolated API on 8101, with frontend 3101; responses are not fabricated. Registration failure is exercised by aborting one real network request, then retrying with retained input. Temporary database, account file and receipt directory are used. The chain adapter explicitly returns unavailable, so these browser tests do not establish real mined confirmation or live recovery.
- Browser checks cover sign-in errors/input retention, keyboard movement in the form, viewport overflow on tested pages, DSWD review attribution, scoped Barangay registration without eligibility/evidence controls, persisted sign-in, Auditor read-only UI/API, own-household visibility, logout clearing content, actual browser offline state, payout-to-exact-receipt navigation, missing receipt handling and stored-role forgery. Six screenshots were captured for review/sign-in/payout at both sizes and visually inspected. General modal focus trapping, other browsers and the full five-role claims journey are not claimed.

## Repeat the isolated checks

From the repository root on Windows, run the backend suites with backend/.venv/Scripts/python.exe and the frontend checks from frontend. Browser tests require a prior production build and installed Microsoft Edge; they start/stop only their own ports 8101/3101 and refuse to reuse another service.

```powershell
backend/.venv/Scripts/python.exe backend/test_auth.py
backend/.venv/Scripts/python.exe backend/test_api.py
backend/.venv/Scripts/python.exe backend/test_backend.py
cd frontend
node --test tests/receipt-navigation.test.mjs tests/payout-connection.test.mjs
node node_modules/typescript/bin/tsc --noEmit
node node_modules/next/dist/bin/next build
node node_modules/@playwright/test/cli.js test
```

## Remaining boundaries

This is authenticated access for invented evaluation accounts, not proof of government affiliation, real-household identity or production readiness. Staff recusal/member linkage, independent assisted checking, session assignments, account recovery/administration, distributed rate limiting, institutional privacy/retention and immutable authenticated audit provenance beyond review history remain separate work. Recipient acknowledgement is still unfinished.

Anchor lifecycle/reconciliation, versioned receipt identity/document coverage and public deployment remain pending. Existing Next.js/runtime dependency advisories must be addressed before shared deployment; adding Playwright did not upgrade runtime dependencies. The groupmate branch was not merged or overwritten, and no contract ABI/hash format was changed.
