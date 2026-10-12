# Receipt verification clarity

Bounded frontend follow-up to [PR #23](https://github.com/andreirtc/ayudachain/pull/23). The existing API still determines VERIFIED, MISMATCH, UNANCHORED and UNAVAILABLE from actual chain reads. No business endpoint, contract or receipt protocol changes are included.

The selected receipt's current outcome is presented before its local receipt details. Each outcome has a familiar title, a distinct explanation and a visible check action. Missing local references remain **Receipt not found**, separately from a successful chain read finding no anchor. Users may choose a receipt or enter its reference; an unknown reference never substitutes another receipt.

Record-loading errors and lookup errors have separate retries. Repeated check clicks are guarded. Late responses cannot replace evidence for a newly selected receipt. Browser-reported offline status disables checks and labels any retained result as an earlier observation; reconnecting does not automatically initiate a lookup. Hashes, network/contract metadata, the server's explanation and anchor timestamp remain expandable. The check's limits on identity, document coverage and cash delivery remain visible.

## Validation on 2026-10-13

- All 48 real Edge desktop/phone browser cases passed, including eight new verification cases for manual references, offline observations, failed lookups, repeated retries, late actual responses and index failures. These ordinary fixtures explicitly report chain unavailability.
- `node tests/live-verification.mjs` from `frontend` passed ten additional actual Edge → FastAPI → local EVM observations: verified, one-centavo mismatch, restoration to verified, genuinely unanchored and unavailable after stopping the owned chain, at desktop 1440×900 and phone 390×844. Public views retained reference-only data. Outcome screenshots were inspected.
- Independent TypeScript, production build and diff checks passed.

The live harness refuses occupied ports 8547/8102/3102. It deploys directly from the compiled test artifact without rewriting retained deployment files, uses a guarded system-temp database/receipts/accounts directory, and stops only its spawned process trees. Its tamper/restore helper refuses non-owned directories. The unanchored case is a deliberately seeded test receipt with a computed compatible hash and no chain transaction. Original databases, provider processes and chains are untouched. A Windows child-output startup issue was fixed by using pipes and explicit RPC readiness before provider creation.

The fixture changes establish test behavior; they do not implement an interactive tampering/restoration product screen. Immutable complete identity/document snapshots, recipient acknowledgement and production infrastructure remain separate work. Automated evidence does not establish new-viewer comprehension.
