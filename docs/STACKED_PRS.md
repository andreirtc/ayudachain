# AyudaChain stacked PR workflow

## First PR: planning and design requirements

Branch: BinkzBooze/ayudachain-project-overview-explainer
Base: main
Scope: docs/TODO.md and this workflow. This is the first PR in the stack. It records the requested work and UI preferences; implementation items remain unchecked.

All data and money are fictional. Local blockchain or public testnet only. Each later PR must implement correct behavior without real citizen data, real payments, or mainnet transactions.

## Working through the stack

Create one follow-up branch and PR for one bounded task at a time. Base that branch on the previous PR branch, and select the previous PR branch as its GitHub base. This keeps each review diff limited to the new task. Commit updates to the checklist alongside the implementation and validation evidence.

Example sequence:

1. Planning PR: this branch -> main.
2. Local startup and baseline checks: BinkzBooze/ayudachain-01-local-baseline -> this branch.
3. Select and consolidate the backend: a new branch -> the baseline branch.
4. Subsequent accounting, eligibility, anchoring, data/permissions, and frontend tasks: each new branch -> the immediately preceding branch.

The checklist sections define the order, not a requirement to put a whole section into a single PR. Split a large section into several small PRs. Do not create empty future PRs. Every PR should contain one reviewable task with a concrete result.

## Review notes

- Put the previous PR link, task scope, validation, and remaining limitations in each PR description.
- Groupmates can review all open PRs independently using their individual diffs, but merge the stack from oldest to newest.
- If an earlier PR changes after review, propagate that change to descendants before merging them. Prefer ordinary merges when possible; do not rewrite published history or force-push without explicit authorization.
- When a predecessor merges, retarget its immediate successor to main and update that branch against main. Confirm that its diff contains only the intended task, especially after squash merges. Repeat as the stack merges.
- If using squash merges, do not assume retargeting alone removes all parent changes. Inspect the diff and cleanly transfer the successor task onto the updated base if necessary, preserving backups and coordinating with reviewers.
- Each implementation PR must include relevant checks. Documentation-only PRs need content/diff review; do not claim runtime tests passed when they were not run.

## UI direction

The detailed UI requirements and external references are in docs/TODO.md. Judge comprehension, clear user tasks, fewer visible elements, concise natural copy without em dashes, and a simple landing page take priority over displaying technical complexity. Visible success and verification claims must remain truthful.
