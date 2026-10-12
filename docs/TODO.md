# AyudaChain implementation backlog

All beneficiary records, receipts, balances, and payouts must remain synthetic. No real citizen data, real money, mainnet transactions, or payment-provider integration. Local blockchain or public testnet only.

PR workflow: see [STACKED_PRS.md](STACKED_PRS.md). This planning session is the first PR; each follow-up task gets its own branch and PR based on the previous branch.

Status: unchecked items are planned, not implemented. Work through one numbered item at a time. First establish a runnable baseline; then backend/contracts correctness; then frontend workflow and usability.

The shared hackathon blueprint and confirmed workmate `feat/five-role-mvp` were compared with PR #16 on 2026-10-12. See [BLUEPRINT_COMPARISON.md](BLUEPRINT_COMPARISON.md) for selected ideas, contradictions and remaining integration gates. Keep the corrected accounting and historical proofs; evaluate the five-role journeys and durable evidence implementation before rebuilding equivalents. Preserve this stacked workflow rather than restarting from the blueprint's older #14 baseline.

## 0. Runnable baseline
- [x] Install dependencies and run local blockchain, backend, and frontend; verify dashboard and all routes via HTTP. Browser visual/interactivity review remains pending.
- [x] Document Windows startup and shutdown, environment setup, and database/blockchain reset together. See [WINDOWS_LOCAL.md](WINDOWS_LOCAL.md); validated with a full reset on 2026-10-12.
- [x] Run existing tests and separate TypeScript checking (build currently ignores type errors); record baseline failures. Contract tests: 9 passing. Backend tests: 8 passing. Separate frontend TypeScript check passes. See [landing-page validation](PUBLIC_LANDING.md).

## 1. Select and consolidate the backend
- [x] Choose one supported API implementation: server.py versus FastAPI app/main.py; reconcile DAFAC/schema/endpoint differences and remove ambiguity in docs. Chose FastAPI (2026-10-12); ported CSV, delete, payout checks, and `dafac_id`; removed server.py; added `backend/test_api.py`.
- [x] Load configuration consistently; make frontend API URL and backend blockchain status authoritative. Choose local SQLite for development; decide hosted persistence when deploying. Done 2026-10-12: `backend/app/config.py`, `.env.example` files, truthful chain status in API and UI, receipt URLs use the API base. SQLite stays for development; hosted persistence is decided in section 7.

## 2. Correct fictional fund accounting
- [x] Use integer centavos (or exact decimals) consistently in database, API, hashing, and contract integration. Done 2026-10-12: stored and sent to the contract as integer centavos; API accepts pesos with at most two decimals and returns `amount` plus `amount_centavos`; receipt hash format unchanged.
- [x] Validate positive releases/allocations, known batches/barangays, and allocation totals <= released funds. Done 2026-10-12: backend checks plus contract `allocatedAmount` limit.
- [x] Link distributions to their barangay allocation; prevent distributions exceeding remaining allocation/batch budgets. Enforce applicable limits in contracts too. Done 2026-10-12: one allocation per barangay per batch; payouts store `allocation_id`; backend and contract reject payouts beyond the allocation's remaining amount.
- [x] Store per-batch grant policy rather than hardcoded amounts; label demo amounts as fictional, without unsupported statutory claims. Done 2026-10-12: `standard_grant` and `max_grant` per batch; payout page reads them; "statutory" and "official" wording removed there. Narrative copy elsewhere is part of section 6.

## 3. Eligibility, review, and duplicate payouts
- [x] Require approved eligible beneficiary status, active batch, and consistent beneficiary/batch/barangay/allocation relationships before payout. Done 2026-10-12: payouts need `VERIFIED` + `APPROVED`, an `ACTIVE` batch, a matching batch, and the barangay's allocation (batch/allocation checks from #8).
- [x] Define one payout per household per batch; enforce database uniqueness and transaction-safe checks under concurrent requests. Done 2026-10-12: unique (batch, beneficiary) constraint, record written before anchoring, in-process lock, and contract `beneficiaryPaid` check.
- [x] Add idempotency keys, robust IDs, and safe retries; return the existing result for repeated submissions. Done 2026-10-12: durable unique retry keys and request fingerprints, server UUID payout IDs, 200 replay/409 conflict, database commit before anchor submission, and retained form retry identity. SQLite upgrade preserves existing payouts. See [PAYOUT_RETRIES.md](PAYOUT_RETRIES.md).
- [x] Keep potential duplicate matches as human review decisions, with reason, actor, and timestamp; correctly update flag/status after review. Done 2026-10-12: validated human decisions with required reason and demo reviewer, UTC decision history/evidence snapshots, consistent approved/rejected/pending states, resolved active flags, and a connected review form/history. See [HUMAN_REVIEW.md](HUMAN_REVIEW.md).
- [x] Replace destructive duplicate deletion with historical status/linking that preserves prior payouts and receipts. Done 2026-10-12: reviewed duplicate links retain original IDs, payouts, receipts, and decisions; historical records remain readable; delete routes are disabled; payout eligibility checks include linked aliases and serialize with review/link changes in SQLite. See [RETAINED_DUPLICATES.md](RETAINED_DUPLICATES.md).

## 4. Truthful blockchain anchoring and verification
- [x] Remove fabricated transaction hashes and successful verification fallbacks; distinguish unavailable, unanchored, mismatch, and verified outcomes. Done 2026-10-12: service/seeder/UI no longer invent evidence; strict contract reads return four explicit states; chain/contract checks and mined transaction receipts are required. Verified all states against an isolated local chain. See [TRUTHFUL_VERIFICATION.md](TRUTHFUL_VERIFICATION.md).
- [ ] Separate payout recorded state from anchor pending/submitted/confirmed/failed; record receipt confirmation and support safe retry/reconciliation.
- [ ] Recover consistently when database writes or blockchain operations fail; handle restarted local chains and synchronized demo reset without contradictory records.
- [ ] Use an immutable versioned receipt snapshot covering intended household identity, batch, amount, allocation, and receipt contents; retain deterministic hashing.
- [ ] Replace hardcoded fraud UI outcomes with actual synthetic record tampering and backend/contract verification; test restoration. Old hardcoded scenario controls were removed on 2026-10-12; an interactive tampering/restoration workflow is still pending.
- [ ] Protect and anchor relevant audit history; accurately describe which logs are local versus blockchain-protected.

## 5. Connected data and permissions
- [ ] Connect CSV validation -> preview -> duplicate review -> explicit import -> beneficiary registry; detect matches against existing records and provide row errors.
- [ ] Enforce permissions on backend endpoints using synthetic demo accounts; prevent browser role selection alone authorizing privileged writes.
- [ ] Make public responses appropriately limited; keep detailed household/contact records in staff views even with synthetic fixtures.
- [ ] Add explicit simulated recipient acknowledgement and payout lifecycle; communicate that receipt integrity cannot prove physical cash delivery.

## 6. Frontend workflow and features
- [ ] Apply the UI design priorities below, including a simple landing page, less copy, focused screens, and natural wording without em dashes.
- [ ] Reflect authoritative budgets, eligibility, API validation errors, payout state, and anchor state; remove misleading success/network labels and hardcoded summary assumptions.
  - [x] Remove mock offline queue/camera controls and unsupported claims from the demo shell/payout screen; show actual browser connectivity, preserve API errors and keep receipt evidence distinct from recorded payouts. See [TRUTHFUL_DEMO_WORKFLOW.md](TRUTHFUL_DEMO_WORKFLOW.md). Full authoritative anchor lifecycle and remaining screens still need follow-up.
- [ ] Make network controls truthful: read actual configured network/contract, or implement real authorized configuration; keep technical settings outside ordinary citizen/field-worker flows.
  - [x] Remove cosmetic dashboard network/address editors and show expandable backend-reported configuration, with visible refresh failures. Authorized network reconfiguration is not a product capability.
- [ ] Implement real QR decoding for synthetic DAFAC cards; retain clearly labeled sample selection as a demo convenience.
- [ ] Implement persistent offline queue/cached required data, reconnect sync, retries, and conflict handling; clearly distinguish queued payouts from confirmed anchors.
- [ ] Make registration, review, payout, and citizen verification a connected understandable journey; preserve useful existing styling.
  - [x] Connect a recorded payout to its exact receipt check; reject unknown receipt links without substituting another household's receipt. See [RECEIPT_HANDOFF.md](RECEIPT_HANDOFF.md). The wider journey and browser QA remain open.
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

## Truthful verification preview

Updated 2026-10-12: http://127.0.0.1:3001/verify uses the copied synthetic database and a separate current-contract local chain at http://127.0.0.1:8546 (chain 31337). Six copied receipts were anchored with real local test transactions and verified. The original provider pane, database, and older chain on 8545 remain unchanged. That older contract has an incompatible receipt getter and now correctly produces unavailable verification instead of fallback success. Automatic chain recovery/reconciliation remains pending. See [TRUTHFUL_VERIFICATION.md](TRUTHFUL_VERIFICATION.md).
