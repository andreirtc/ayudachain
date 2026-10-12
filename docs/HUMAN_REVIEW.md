# Human review of household records

Completed 2026-10-12 as the next bounded section 3 task, based on [payout retries, PR #12](https://github.com/andreirtc/ayudachain/pull/12). Data, reviewers, and payouts are synthetic.

## Decisions and eligibility

A similarity match remains a suggestion for human review. The review endpoint accepts three decisions: `VERIFIED` approves the household, `REJECTED` rejects it, and `FLAGGED_FOR_REVIEW` keeps or reopens the review with `PENDING` status. Arbitrary status strings are rejected. Only verified and approved households are eligible for a new payout.

Each decision requires a reason of 1–2000 characters after trimming and one of the named demo reviewers: `demo-officer-01` or `demo-auditor-01`. The server generates a UUID review ID and a UTC timestamp. It saves the prior verification/review status, prior notes, match ID/confidence, and duplicate/anomaly flags before and after the decision. Later decisions append history rather than overwrite earlier decision records.

Approve and reject clear active duplicate/anomaly flags, so resolved households leave the pending-review filter and dashboard flag count. The original match ID and confidence remain visible as historical evidence. Reopening a review restores known duplicate/anomaly signals and blocks a new payout. A review change never modifies or reverses prior payouts, receipt hashes, or blockchain records.

The registry update, decision record, and local `BENEFICIARY_REVIEWED` audit event commit together. SQLite obtains its write lock before reading prior state; concurrent decisions record a consistent sequence even without the process lock. Database failure rolls back all three changes. Startup creates the new history table without deleting existing registry or payout records. Existing automatic/seeded approvals have no invented human reviewer or timestamp.

## Interface

Open [the current preview](http://127.0.0.1:3001/beneficiaries), select an officer or auditor demo view, and inspect a household such as BEN-0007. Choose the demo reviewer, enter the reason, and approve, reject, or keep the record for review. Saving disables the controls and repeated clicks; failure retains the reason and shows an inline error. The updated registry status and pending filter reflect the saved decision.

The household dialog retains original match evidence and provides a collapsible review history with decision, reviewer, time, reason, and matched record. History has loading, empty, error, and retry states. Rejected households are labeled rejected instead of incorrectly appearing as pending review. The dialog scrolls on smaller screens.

The preview backend uses the separate copied synthetic database prepared earlier in this session. Its 24 households and six existing payout records remain present. The original database and original provider pane were not modified or resumed for preview setup.

## Validation

- API suite: 54 tests pass, including actor/reason/time/evidence capture, approval/rejection/pending/reopening, resolved flags, invalid requests, failed commits, preserved payouts, concurrent review history, and additive table creation.
- Backend hashing/entity-resolution suite: 12 tests pass.
- Contract suite: 13 tests pass.
- Separate frontend TypeScript check and production build pass. The existing build still skips embedded type validation/linting; section 7 addresses that configuration.
- Preview health, dashboard, review history, OpenAPI schema, beneficiary page, and referenced JavaScript assets return HTTP 200. Original copied record counts are preserved.
- Visual and interactive browser review remains pending; no browser was available in this session.

## Remaining work

Demo reviewer identity is supplied by the caller and is not authenticated. Role selection only changes the demo interface. Backend permissions belong to section 5. Review history is append-only through these API endpoints, but remains editable by someone with database access; blockchain protection belongs to section 4.

The next section 3 task replaces destructive registry deletion with retained historical status/linking. The table-level delete action still exists until that task; review records have no cascading delete and their history endpoint remains readable after registry deletion. Demo reset still intentionally removes synthetic history with the rest of the dataset. Persistent review idempotency, pagination, and multi-worker coordination between payout eligibility checks and review changes are not introduced by this task.
