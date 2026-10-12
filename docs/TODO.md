# AyudaChain implementation backlog

All beneficiary records, receipts, balances, and payouts must remain synthetic. No real citizen data, real money, mainnet transactions, or payment-provider integration. Local blockchain or public testnet only.

PR workflow: see [STACKED_PRS.md](STACKED_PRS.md). This planning session is the first PR; each follow-up task gets its own branch and PR based on the previous branch.

Status: unchecked items are planned, not implemented. Work through one numbered item at a time. First establish a runnable baseline; then backend/contracts correctness; then frontend workflow and usability.

## 0. Runnable baseline
- [x] Install dependencies and run local blockchain, backend, and frontend; verify dashboard and all routes via HTTP. Browser visual/interactivity review remains pending.
- [x] Document Windows startup and shutdown, environment setup, and database/blockchain reset together. See [WINDOWS_LOCAL.md](WINDOWS_LOCAL.md); validated with a full reset on 2026-10-12.
- [x] Run existing tests and separate TypeScript checking (build currently ignores type errors); record baseline failures. Contract tests: 9 passing. Backend tests: 8 passing. Separate frontend TypeScript check passes. See [landing-page validation](PUBLIC_LANDING.md).

## 1. Select and consolidate the backend
- [x] Choose one supported API implementation: server.py versus FastAPI app/main.py; reconcile DAFAC/schema/endpoint differences and remove ambiguity in docs. Chose FastAPI (2026-10-12); ported CSV, delete, payout checks, and `dafac_id`; removed server.py; added `backend/test_api.py`.
- [ ] Load configuration consistently; make frontend API URL and backend blockchain status authoritative. Choose local SQLite for development; decide hosted persistence when deploying.

## 2. Correct fictional fund accounting
- [ ] Use integer centavos (or exact decimals) consistently in database, API, hashing, and contract integration.
- [ ] Validate positive releases/allocations, known batches/barangays, and allocation totals <= released funds.
- [ ] Link distributions to their barangay allocation; prevent distributions exceeding remaining allocation/batch budgets. Enforce applicable limits in contracts too.
- [ ] Store per-batch grant policy rather than hardcoded amounts; label demo amounts as fictional, without unsupported statutory claims.

## 3. Eligibility, review, and duplicate payouts
- [ ] Require approved eligible beneficiary status, active batch, and consistent beneficiary/batch/barangay/allocation relationships before payout.
- [ ] Define one payout per household per batch; enforce database uniqueness and transaction-safe checks under concurrent requests.
- [ ] Add idempotency keys, robust IDs, and safe retries; return the existing result for repeated submissions.
- [ ] Keep potential duplicate matches as human review decisions, with reason, actor, and timestamp; correctly update flag/status after review.
- [ ] Replace destructive duplicate deletion with historical status/linking that preserves prior payouts and receipts.

## 4. Truthful blockchain anchoring and verification
- [ ] Remove fabricated transaction hashes and successful verification fallbacks; distinguish unavailable, unanchored, mismatch, and verified outcomes.
- [ ] Separate payout recorded state from anchor pending/submitted/confirmed/failed; record receipt confirmation and support safe retry/reconciliation.
- [ ] Recover consistently when database writes or blockchain operations fail; handle restarted local chains and synchronized demo reset without contradictory records.
- [ ] Use an immutable versioned receipt snapshot covering intended household identity, batch, amount, allocation, and receipt contents; retain deterministic hashing.
- [ ] Replace hardcoded fraud UI outcomes with actual synthetic record tampering and backend/contract verification; test restoration.
- [ ] Protect and anchor relevant audit history; accurately describe which logs are local versus blockchain-protected.

## 5. Connected data and permissions
- [ ] Connect CSV validation -> preview -> duplicate review -> explicit import -> beneficiary registry; detect matches against existing records and provide row errors.
- [ ] Enforce permissions on backend endpoints using synthetic demo accounts; prevent browser role selection alone authorizing privileged writes.
- [ ] Make public responses appropriately limited; keep detailed household/contact records in staff views even with synthetic fixtures.
- [ ] Add explicit simulated recipient acknowledgement and payout lifecycle; communicate that receipt integrity cannot prove physical cash delivery.

## 6. Frontend workflow and features
- [ ] Apply the UI design priorities below, including a simple landing page, less copy, focused screens, and natural wording without em dashes.
- [ ] Reflect authoritative budgets, eligibility, API validation errors, payout state, and anchor state; remove misleading success/network labels and hardcoded summary assumptions.
- [ ] Make network controls truthful: read actual configured network/contract, or implement real authorized configuration; keep technical settings outside ordinary citizen/field-worker flows.
- [ ] Implement real QR decoding for synthetic DAFAC cards; retain clearly labeled sample selection as a demo convenience.
- [ ] Implement persistent offline queue/cached required data, reconnect sync, retries, and conflict handling; clearly distinguish queued payouts from confirmed anchors.
- [ ] Make registration, review, payout, and citizen verification a connected understandable journey; preserve useful existing styling.
- [ ] Test mobile layouts, readable text, touch targets, keyboard/focus accessibility, loading/empty/error states, and prevention of accidental repeat submissions.

## 7. Verification and deployment
- [ ] Review dependency audit findings and upgrade vulnerable dependencies, including the installed Next.js version, before shared deployment.
- [ ] Add meaningful API/integration tests for over-allocation, exhausted funds, ineligible beneficiaries, cross-batch requests, retries/concurrency, chain outages, missing anchors, receipt tampering, CSV import, permissions, and retained history.
- [ ] Run contract tests, backend tests, frontend typecheck/build, and browser walkthrough after relevant changes; stop ignoring build type failures.
- [ ] Choose shared demo deployment: frontend can use Vercel; backend requires suitable runtime and persistent SQLite storage or migrated PostgreSQL. Configure HTTPS API URL/CORS and testnet configuration.
- [ ] Update README/user guide to match implemented behavior; clearly identify synthetic data, simulated payments, and genuinely unfinished features.

## UI design priorities requested by the user

Recorded 2026-10-12. These requirements guide all frontend work in section 6. Product clarity, useful workflows, and immediate understanding by judges take priority over showcasing technical complexity. Backend correctness still underpins every visible claim. This is a backlog update, not a completed redesign.

- [ ] Reduce unnecessary text: remove repeated explanations, redundant bilingual duplication, jargon, promotional claims, and instructions that obvious labels already communicate. Keep essential eligibility, privacy, error, and confirmation information.
- [ ] Show only a few meaningful elements per screen or viewport. Give each task screen one clear purpose and primary action; use whitespace and hierarchy to reduce fatigue. Keep related inputs together when useful rather than enforcing an arbitrary element count or adding needless clicks.
- [ ] Use progressive disclosure for secondary details, historical records, receipt hashes, contract addresses, and advanced settings. Important errors and transaction states must remain visible.
- [ ] Write natural, concise UI copy. Remove em dashes from authored product text, formulaic AI-style phrasing, exaggerated claims, and unnecessary decorative emoji. Use direct action labels and familiar terms. This punctuation preference comes from the user, not a claim that punctuation proves AI authorship.
- [x] Add a proper public landing page distinct from the operational dashboard. Explain what AyudaChain does, who it helps, and the problem it addresses in simple language, without requiring blockchain knowledge.
- [ ] Give the landing page a short outcome-focused headline, one brief explanation, one primary entry action, and a compact visual journey from fund release to household receipt. Show an understandable example of the benefit and a clear synthetic-demo label; avoid a wall of feature cards or technical badges.
- [ ] Make the project story understandable through actual interactions: follow a fictional household, review a possible duplicate, record its payout, and see whether its receipt remains unchanged. Keep the story truthful about what the system proves and what is simulated.
- [ ] Separate citizen, field-worker, and auditor tasks. Offer understandable navigation and useful defaults; show each role relevant actions and information.
- [ ] Use consistent typography, spacing, components, and restrained status colors. Make text readable on phones and controls easy to tap. Never rely on color or icons alone to communicate state.
- [ ] Improve feedback: clear loading, empty, success, error, offline, pending-anchor, and retry states; actionable errors near the relevant control; retain user input after failure.
- [ ] Support keyboard navigation, visible focus, accessible labels, and readable contrast. Avoid attention-grabbing motion that distracts from the main task.
- [ ] Validate storytelling with a short comprehension check: after a brief first look, a new viewer should be able to describe the problem, intended users, benefit, and next action without a presenter explaining the page. Treat this as a project-specific design check, not a published usability threshold.
- [ ] Review external guidance during redesign and record which recommendations apply to each screen. Measure usefulness through comprehension and successful tasks rather than the number of features or technical terms shown.

### External design references

These references inform implementation; the specific landing-page structure and writing preferences above are project decisions.

- [Nielsen Norman Group: Aesthetic and Minimalist Design](https://www.nngroup.com/articles/aesthetic-minimalist-design/) supports keeping interfaces focused on relevant information and reducing competing content.
- [Nielsen Norman Group: Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) supports showing essential options first and revealing advanced details when needed.
- [GOV.UK Design System: Question pages](https://design-system.service.gov.uk/patterns/question-pages/) offers focused task-page patterns. Apply the principle thoughtfully; it does not mean every dashboard must contain only one element.
- [GOV.UK Service Manual: Writing for user interfaces](https://www.gov.uk/service-manual/design/writing-for-user-interfaces) supports concise, scannable labels and help text.
- [GOV.UK: Government Design Principles](https://www.gov.uk/guidance/government-design-principles) provides guidance on starting with user needs, making services understandable, and iterating.

## Current preview session
Started 2026-10-12. Node 24 / Python 3.13. Frontend: http://127.0.0.1:3000. Backend: http://127.0.0.1:8000. Local blockchain: http://127.0.0.1:8545 (chain 31337). Contract deployed locally; SQLite seeded with 24 fictional beneficiaries and five sample payout records. Dashboard, beneficiaries, distributions, verify, and batch routes return HTTP 200; backend health and receipt verification respond successfully against Local EVM. No in-app browser is available for visual/interactivity inspection. Baseline tests were subsequently run: 9 contract tests and 8 backend tests pass; separate TypeScript checking passes. No real funds or real citizen data involved.

## Public landing page follow-up

The public landing page is implemented at `/`, with the existing operational dashboard moved to `/dashboard`. See [PUBLIC_LANDING.md](PUBLIC_LANDING.md) for scope, validation, and pending visual/comprehension checks. This bounded task was selected ahead of backend changes because the landing page does not consume APIs or display live success/verification states. The remaining operational UI work still depends on backend correctness.
