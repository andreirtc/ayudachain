# Payout desk

The Disbursing payout form reads current household approval, active batch, linked-duplicate payout history, fictional grant limits and exact remaining allocation from GET /api/payout-desk/{beneficiary_id}. Failed reads block recording. The selected household and amount stay visible; collection details and individual checks expand on request using the shared Tonal controls.

The latest finalized list and its current collection arrangement provide context only. They do not authorize payment. The existing transactional confirm endpoint rechecks accounting and eligibility and retains once-only payout, replay, immutable receipt and anchor recovery behavior. A saved payout and a household acknowledgement remain distinct from physical cash delivery. No new PIN, impersonation or fabricated document check is introduced. Assisted concerns follow in the next bounded task.

Validation uses three focused authenticated API checks for record/replay, budget and linked aliases, invalid amounts, denied roles and area scope. Types/build and a short combined browser demo are checked after the remaining connected features. The original database, chain and frontend port 3000 are preserved.
