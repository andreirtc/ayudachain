# Sign-in destinations and ended sessions

Bounded follow-up to [PR #26](https://github.com/andreirtc/ayudachain/pull/26). Anonymous household links previously lost their exact selection when sign-in returned to the role's default page. Sign-in now carries a validated local return destination through the session gate, desktop/phone navigation, account banner and public receipt details.

## Connected behavior

A link to /distributions?beneficiary_id=... returns to that same household after authentication, including encoded references. A link to /verify?distribution_id=... returns to that exact receipt. The verifier remains public with reference-only evidence; signing in adds only the context permitted to that account. A failed sign-in retains the account input and intended destination for retry. Passwords remain form state, are cleared after success, and are never written to URLs or browser persistence.

Direct /sign-in keeps existing defaults: Disbursing opens payouts, Beneficiary opens the own-household starting point at /household, and other roles open the registry. Return destinations do not authorize anything. Barangay payout links show the existing explicit role-denied view with a household-registry next step. Missing or out-of-scope household/receipt links show the existing unavailable/not-found view without substituting another record.

Supported return routes are /lists, /household, /beneficiaries, /distributions, /verify, /dashboard and /batch/<reference>. Only the household query on registry/payouts, list_id on lists and the receipt query on verification are accepted, with one parameter each. External/protocol-relative/script URLs, backslashes, control characters, malformed escapes, fragments, path normalization, unknown routes/query keys, duplicate parameters and sign-in loops fall back to the role default. The return destination is encoded in the sign-in URL; no hidden browser storage is used.

## Session and privacy boundary

401 responses clear the frontend account and remount private content. Public API reads can legitimately succeed after expiry or revocation, so responses also expose X-AyudaChain-Session (active or ended). An ended response clears existing private context even when public verification succeeds. Server role, CSRF, record scopes and public projections are unchanged. No receipt/hash/schema/contract change is included.

Session refresh hides private page content while authentication is checked. Account transitions and ended sessions discard forms and saved page results; authentication never stores or automatically replays payout/review/registration submissions. Request generations reject late session/expiry responses belonging to an earlier account. The client learns server revocation/expiry on an API response or page/session reload; this is not push revocation or a background polling service. Already downloaded files remain outside that clearing boundary.

## Validation

All 80 isolated real Edge cases passed at desktop 1440×900 and phone 390×844 on the final production build. Sixteen new cases cover exact household links (including encoded IDs), failed sign-in/reload/keyboard retries, exact receipts from the banner and receipt card, real API session revocation and reauthentication, discarded payout form state/no automatic submissions, different-account household/receipt scope, explicit Barangay denial, hostile/ambiguous destinations and all role defaults. Browser authentication uses provisioned synthetic accounts and real API cookies; revocation uses an independent actual logout request. Backend tests separately expire stored sessions and verify the successful public response remains redacted while reporting the ended session.

All 20 authenticated API permission/session tests, 76 business API regressions, 14 frontend Node checks, independent TypeScript, isolated production build and diff checks passed. The existing embedded build type/lint checks remain skipped; independent TypeScript was run. Existing dependency advisories remain before shared hosting. Desktop/phone screenshots were inspected and ten saved under tmp/ayudachain-pr27-validation. An existing registry test now targets the current status badge so retained review history does not make its assertion ambiguous.

To repeat: run backend/test_auth.py and backend/test_api.py with backend/.venv/Scripts/python.exe. From frontend, run node --test tests/*.test.mjs and node node_modules/typescript/bin/tsc --noEmit. Set AYUDACHAIN_BUILD_DIR=.next-handoff-qa, run node node_modules/next/dist/bin/next build, then node node_modules/@playwright/test/cli.js test in the same environment. Restore only inspected Next-generated next-env.d.ts/tsconfig.json changes afterward.

The fixture uses real synthetic provisioned accounts, an isolated system-temp database/receipts and an explicitly unavailable chain. It refuses occupied API8101/frontend3101 ports and stops its own services. The persistent preview remains stopped; original database, frontend3000, chain8545, builds and deployment artifacts are preserved. No new mining, physical-phone or full accessibility audit is claimed.
