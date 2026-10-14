# Which AyudaChain should we present?

Recommendation: present the current `design-proposal` finals candidate when the pitch is about an evidence trail from funding to recipient follow-up. Present PR #39 when the team deliberately chooses a narrower authenticated staff registry/payout/receipt product and has rehearsed its own environment. Neither implementation is production-ready. They are separate products in the same repository; do not add their capabilities together in the pitch.

Comparison is against inspected PR #39 head `de6dd06`, based on #38. Current-MVP behavior was exercised locally; PR #39 source and author screenshots/reports were inspected, but its tests were not independently rerun here.

| Judging question | Current finals candidate | PR #39 cumulative stack | Practical implication |
|---|---|---|---|
| Can we demonstrate the original funding evidence being entered and confirmed? | Actual original upload/extraction/manual confirmation, retained corrections and versioned commitments in the UI | Funding/allocation write APIs exist; its validation document states the frontend displays seeded balances/records without authoring forms | Current candidate gives a more complete live evidence-origin story. |
| Can we explain why a household qualifies? | Versioned claim, Barangay attestations/Punong submission, resolution original, exceptions/referral and human DSWD decision | Human registry review/duplicate decisions and finalized staff lists; not the same multi-stage claim/endorsement flow | Current candidate has stronger implemented traceability of this fuller process, at a cost of more steps. |
| Can we show how the household amount was calculated? | Documentary wage/day or fixed-category inputs; computed entitlement; paid amount stays locked | Grant-policy/allocation-aware guards in its different accounting model; not the current documentary input-version workflow | Current candidate better supports the proposed “explain the amount” story. PR #39's budget controls should be acknowledged, not called absent. |
| Is list publication independently witnessed? | Approved-list commitment; publication waits for its own matching chain confirmation | Frozen list/revision hash with stale checks and human finalization; no separate list anchoring call in inspected list service | Current candidate gives blockchain a concrete pre-payout role beyond receipt integrity. |
| Can a household without a phone complete the demonstrated path? | Assisted registration/payment, private PIN, connected staff device and distinct assigned checker; genuine local rehearsal | Staff-assisted registration/concerns exist; it does not implement this PIN/checker/assigned-session pathway | Current candidate demonstrates this specific inclusion safeguard. Neither is offline payout or a general solution for missing ID. |
| What does the recipient say afterward? | Full/less/not-received, versioned private answers, grievance history and separate reporting counts | Own-recipient acknowledgement plus concerns/staff replies | Both listen after payout; current candidate models those three payout outcomes and their case handling explicitly. |
| How broad is the checkable evidence? | Ten commitment kinds and signer-free exact-material/original verification; fresh local checks recorded | Legacy/captured-v2 receipt checks and recovery, with funding/allocation contract controls in its stack | Current candidate supports a broader connected evidence demonstration; this does not make its local chain independently governed. |
| Which has better authentication? | None: active selected actors can be impersonated | Password-authenticated synthetic accounts, scrypt, revocable sessions and request protections in inspected code | PR #39 has a substantial advantage here. Current scopes are workflow checks, not secure authorization. Neither is certified for real citizen data. |
| Which has the clearer interface? | Material 3, real next actions, phone layout, actionable errors; fuller process exposes more tasks | More compact Material shell, inline list/detail registry, grouped payout desk and four-item phone navigation | PR #39 is the stronger visual reference based on inspected screenshots. This is design judgment, not a measured usability study. |
| Which can we safely show immediately? | Freshly rehearsed here, services running, 48redesign captures and a genuine fallback video | Author reports its own validation/preview; not independently launched or rehearsed here | Current candidate has the stronger immediate handoff on this machine. That is not proof PR #39 is less reliable. |

## What our advantage actually is

Our strongest claim is the **connected, document-backed workflow**: “We can show the evidence behind inclusion and the amount, then distinguish the officer's handover record, the recipient's report and an independent integrity check.” More screens, PostgreSQL, more test cases or a private PIN are not advantages by themselves. Human usefulness and a checkable explanation are the advantages we must demonstrate.

PR #39's strengths are **a simpler interface and implemented synthetic-account authentication**. Do not call it merely a cosmetic branch, insecure, fake or broken. Do not claim its stack has no blockchain or no recipient feedback. Its narrower scope may be a better choice if the team can explain and rehearse that product more clearly.

## Changes to the pitch whichever implementation you choose

1. Name the selected branch/product at the start of the team's preparation; use only its actual screenshots, flows and results.
2. Replace “fraud-proof / eliminates corruption” with “makes changes to committed evidence detectable and supports human investigation.”
3. Replace “blockchain proves receipt of cash” with “a fresh check confirms that the committed evidence matches; physical handover and recipient report are separate.”
4. State “local EVM prototype, synthetic records.” Remove any claim of public Polygon deployment, government endorsement or live identity/SMS integration unless separately evidenced.
5. Use accurate identity wording: current candidate has selectable unverified actors; PR #39 has password-authenticated synthetic accounts. Neither proves real identity or official authority.
6. Do not claim offline payout. Manual lookup is an alternative to QR; a connected staff device is still required for the current assisted flow.
7. Keep funding authority, allocated balances and certified available cash distinct. Do not apply one branch's accounting claims to the other.
8. Use a real current check on stage and a labelled recorded fallback if it fails. Never replace an unavailable read with an inferred match.

For the complete19-slide replacement copy, use [PITCH_SLIDE_CORRECTIONS](PITCH_SLIDE_CORRECTIONS.md). Canva access/inspection is cancelled at the team's request; no further access work is needed.

## Suggested team decision

Choose the current candidate for this finals pitch. Use a three-minute saved-record walkthrough rather than all administrative input steps: funding original → decision → computed amount/list → recorded receipt → recipient answer → one fresh integrity check. The local redesign now adapts useful list/detail, grouped payout and phone-navigation patterns, with full desktop task labels referenced from five-role-mvp. It retains our existing API/business rules; PR39 authentication/backend is not imported.

If the team chooses PR #39 instead, rewrite the pitch around authenticated staff review, finalized lists, collection arrangements, guarded payout, captured receipts, acknowledgement/concerns and read-only audit. Remove current-MVP-only claims about original-backed funding entry in the UI, multi-stage claims/endorsements, documentary amount versions, independently anchored list publication, PIN/checker assigned sessions and full/less/not-received outcome handling. Rehearse its own startup and a fresh chain check; our current video/tests do not validate that branch.

## A defensible spoken answer

“We chose the complete evidence workflow for this demonstration. We can trace a documented household decision and amount through recorded handover, recipient feedback and a fresh integrity check. Another branch has a cleaner staff interface and password-authenticated demo accounts, which are useful for the next iteration. We have not combined those implementations, and this demonstration still uses invented data and unverified selectable actors.”

## Inspection sources

Current code: [funds](../../backend/app/services/funds.py), [claims](../../backend/app/services/claims.py), [amounts/lists](../../backend/app/services/entitlements.py), [payouts](../../backend/app/services/payouts.py), [outcomes](../../backend/app/services/outcomes.py), [integrity](../../backend/app/services/integrity.py). Current results: [FINALIST_READINESS](FINALIST_READINESS.md). PR #39 paths, ancestry, author results and scope limits: [PR39_REVIEW](PR39_REVIEW.md), [PR snapshot](evidence/pr39-snapshot.json). Its inspected `backend/app/auth.py` and `services/validated_lists.py` distinguish authentication and list finalization from current-MVP behavior.
