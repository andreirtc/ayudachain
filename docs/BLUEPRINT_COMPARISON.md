# Blueprint, PR stack and five-role MVP decisions

Follow-up: [DEMO_SESSIONS.md](DEMO_SESSIONS.md) implements authenticated five-role permissions, limited public responses, disabled HTTP reset and actual headless desktop/phone checks. The comparisons and validation below describe the earlier PR #17 boundary.

Reviewed 2026-10-12. Source: [shared AyudaChain blueprint](https://chatgpt.com/s/t_6accc978bd848191abbdf8a1d3110140), version 1.0, sections 1–20. The public page's full blueprint text was retrieved and read; its downloadable CSV is a separate sandbox attachment and was not obtained. Compared with stack tip `7db0bb4` (PR #16) and confirmed workmate branch `feat/five-role-mvp` at `56102c4`. See [source compatibility review](ROLE_BRANCH_REVIEW.md).

## Conclusion

The stack follows the blueprint's correctness direction, but does not satisfy its complete release criteria. PRs #4–#14 establish a supported backend, exact money, budget constraints, eligibility, uniqueness, durable request replay and retained human/duplicate history. PR #15 removes fabricated blockchain evidence; #16 connects a payout to its exact receipt check. All sixteen PRs are still open. Being implemented in the cumulative tip is different from being reviewed and merged into main.

No entire source wins. Keep the stack's financial invariants and historical compatibility, bring forward the MVP's five-role ownership and connected evidence/outcome journeys, and use the blueprint's evidence-based acceptance criteria. Authentication, recovery and a complete browser walkthrough remain release gates. A broader implemented workflow with impersonable actors is not secure authorization, and a shorter plan is not proof of working code.

This comparison supports incremental stacked implementation. It does not authorize replacing the database, modifying old proofs, merging the workmate branch wholesale, deploying services or using real records/funds.

## Roles and independent review

- Blueprint sections 2/10 suggest four role types and allow Auditor duplicate decisions. The MVP separates Beneficiary, Barangay Officer, DSWD Officer, Disbursing Officer and an Auditor who cannot mutate business records. The stack has three selectable browser views; an Auditor can currently submit named review decisions and previously could use the payout form.
- **Choose the MVP's five business roles and independent read-only Auditor as the target.** Public transparency is an unauthenticated surface, not access to another beneficiary's private workspace. A technical administrator should not automatically act as both eligibility reviewer and payer. Future server permissions must reflect those distinctions.
- This task makes the payout form available only in the existing staff demo view and labels selection as unauthenticated. It does not implement five authenticated roles or change existing review endpoints. Removing Auditor review mutations needs a coordinated backend/frontend follow-up with permission tests and history preservation.

## Authentication and privacy

- The blueprint requires authenticated synthetic staff sessions on privileged requests and limited public representations. The MVP resolves a publicly selectable `X-Demo-Actor-ID` to stored scope and assignments; anyone can impersonate an active actor. The stack uses localStorage views and caller-supplied named reviewers, with no secure authorization boundary.
- **Choose authenticated server sessions plus the MVP's stored scope, assignment and independence checks.** A role dropdown or a private-looking page cannot supply identity assurance. All invented fixture data stays synthetic; neither implementation is suitable for real household information.
- Public verification must disclose only the intended receipt proof and public aggregate information. The current detailed registry/receipt endpoints and reset route are not made secure by removing their navigation controls. Authentication and public response separation remain high-priority backend work.

## Financial model and contract responsibilities

- The blueprint follows relief authority/LGU/barangay allocations and requires on-chain budget caps. Our `AyudaChainRegistry` enforces allocation totals, remaining allocation amounts and one household payment per batch. The MVP instead models direct DSWD handovers with documentary funding authority, claims, calculated entitlements and sessions.
- Its `AyudaChainEvidenceRegistry` provides immutable generic evidence and linked funding corrections. It has no allocation ledger or aggregate payout ceiling equivalent to our contract. Evidence anchoring and spending authorization are different responsibilities; calling both designs blockchain-backed does not make them interchangeable.
- **Retain our financial constraints and allocation links.** Reuse documented funding evidence and appended corrections only through an agreed schema/contract bridge. Funding records do not prove site cash availability. Replacing the contract with the MVP registry alone would lose a stated differentiator and require a separate product decision.

## Grant policy and payout workflow

- The stack and blueprint use a configurable fictional per-batch standard/maximum. The MVP uses documentary wage/category-day or fixed-category calculations, with no legacy grant ceiling and no household amount override.
- **Keep the current fictional policy and exact centavos while evaluating documented calculation inputs as an optional policy extension.** Neither invented policy is presented as law or an official entitlement. A future calculation must still fit the aggregate authorized budget; richer calculation evidence does not justify dropping accounting protection.
- The MVP's separation of recorded handover, recipient authorization, independent assisted checking and private recipient answers is stronger product design than treating a saved payout as proof of delivery. Bring these forward with distinct states and retained evidence, rather than copying form screens whose API does not exist in this stack.

## Receipt protocol, current integrity and retries

- The blueprint proposes immutable versioned receipts, protected identity/document commitments and durable pending/submitted/confirmed/failed jobs. The stack has durable payout replay and truthful live chain reads, but no complete anchor lifecycle; its current hash omits names, allocation links and raw receipt bytes. Matching a saved transaction reference is not current verification.
- The MVP already has canonical immutable envelopes, private nonces, raw evidence digests, pinned deployment manifests, durable jobs, signed-submission persistence and observations. Those are valuable implementation references, but depend on its PostgreSQL schema, Node worker and separate protocol/contract. Fresh fault/journey validation remains necessary.
- **Use the blueprint's lifecycle requirements and evaluate the MVP's implementation rather than inventing another worker blindly.** Keep existing receipt hashing/ABI readable. Any new receipt format needs an explicit version, cross-language vectors and an additive compatibility decision.
- A frozen evidence check and a check of today's mutable operational record are different. The MVP's `integrity.check_saved` compares saved canonical bytes/originals with the chain; it does not by itself recompute all current business projections. The stack recomputes limited current receipt fields. A future verifier must state the selected covered version and separately detect drift in relevant current fields. Never infer household-name integrity from the existing stack hash.
- Keep VERIFIED, MISMATCH, UNANCHORED and UNAVAILABLE as current proof outcomes. Pending/submitted/failed are separate lifecycle states. A local receipt not found is also distinct from a successful chain read that finds no anchor. Safe reconciliation must check the pinned deployment before resubmission; payout replay must continue returning the original saved result.

## UI clarity, offline behavior and scanning

- The blueprint calls for a concise civic prototype, truthful failure states and deferred offline sync. The MVP has dedicated workspaces, next actions, expandable proof evidence and explicit limitations. The stack's public landing and exact receipt handoff are useful; its operational shell still contained official-government wording, a fixed 94% score, fabricated camera framing and a toggle claiming device queues/batch sync.
- **Keep the public landing, adopt task-focused guidance and remove unsupported capability claims.** Bilingual guidance should help understanding, not duplicate every label; prefer the MVP's explicit language choice as a later connected task. Keep supported routes rather than links to unimplemented workspaces.
- Implemented in this follow-up: simpler navigation, mobile-available demo-view selection with sign-in disclosure, an expandable fictional journey, removal of ordinary-navigation database reset, actual browser connectivity, offline submission rejection, API loading/error/refresh states, manual household selection and truthful sample-template wording. Cosmetic dashboard network/address controls now give way to expandable backend-reported configuration, with refresh failures visible. A browser-reported connection does not establish API or chain availability.
- Actual QR decoding remains pending in this stack. The MVP's decoder/manual session lookup is worth reusing after its session dependencies and physical-camera behavior are validated. No mock scan is represented as a camera capability. There is no persistent offline payout queue or automatic reconnect submission.

## CSV and duplicate history

- The blueprint uses the legacy ten-column beneficiary fixture and requires preview, existing-record comparison, human review and explicit import. The MVP imports a five-column head-only no-ID declaration. Those represent different inputs, not alternate encodings of the same record. The stack's analyzer is not a complete importer.
- **Reuse the staged preview/confirmation pattern, with a documented input adapter and source identifiers.** Preserve source rows, birth dates, unknown values and household/member semantics; never silently fabricate fields or import suspicious duplicates as approved households. Import must not create payout anchors.
- Keep the stack's survivor/alias links and historical payout/review IDs. The MVP's versioned claim checks do not automatically replace our across-alias payout protection. An adapter must demonstrate that history and payment uniqueness survive before integration.

## Git, deployment and timing

- The blueprint starts a common integration branch from #14; our latest cumulative baseline is #16. The workmate's contribution instructions branch from main. **Follow the user's existing stacked workflow**, add each bounded task to the preceding tip, and review/merge oldest first. Do not force-push older PRs to make the comparison disappear.
- Keep local SQLite/current contract as the supported baseline. PostgreSQL is appropriate to evaluate for persistent shared operation, but installing it is not the same as migrating our data. Validate the MVP separately before choosing its architecture as a successor.
- Amoy/hosting/free-tier/model commands in the blueprint are proposals, not current deployments, guaranteed prices or instructions to execute here. The MVP's pinning deliberately supports a local evaluation chain. A testnet/hosting change needs fresh provider checks, supported network/key configuration, authentication, privacy, persistence and a real external workflow test.
- The 24-hour schedule assumes five available developers and a confirmed sprint start. It is not an elapsed-time promise for this session. Do not reset original data/chain to meet a timeline, and do not claim a shared sandbox CSV or an unavailable browser was validated.

## Next bounded work and acceptance

1. Validate the isolated five-role MVP against its retained chain and PostgreSQL before adopting its schema. Record current failures, including any missing deployment/worker, without overwriting pins to obtain green results.
2. Adapt authenticated synthetic identities and server permission tests to the selected architecture; keep Auditor business reads separate from DSWD decisions/payout actions and restrict public responses.
3. Bring forward anchor jobs/reconciliation and additive immutable receipts, preserving current accounting, replay, alias/history and old verification. Cover crash/lost-response/deployment-loss cases.
4. Connect a single household's registration, review, payout and recipient outcome with precise current/lifecycle evidence; then add staged CSV and actual QR lookup.
5. Perform browser/mobile/keyboard, dependency and deployment validation before a release freeze. The guided tamper/restoration demo must change covered synthetic data, demonstrate real mismatch and restore it; it cannot be a scripted label.

The next task's acceptance must name the actual scope. This frontend correction does not close authentication, anchor recovery, immutable identity coverage, imported data or the complete five-role journey.
