# AyudaChain user guide

AyudaChain is a fictional disaster-relief prototype. Use invented households and simulated payouts only. A matching blockchain receipt hash establishes integrity of the fields currently hashed; it does not establish cash delivery, government affiliation or the identity of a real recipient.

## Sign in and choose a task

The public landing, funding summaries and limited receipt checks do not require sign-in. Private records require a provisioned synthetic account at /sign-in. Account credentials come from local provisioning, not a role dropdown. The server enforces each account's role and scope.

- **DSWD Officer:** review households, register records, analyze CSV and manage fictional funding. Eligibility decisions record the signed-in account. This role cannot record payouts.
- **Barangay Officer:** register and inspect household status within the assigned barangay. Eligibility decisions and private review evidence belong to DSWD.
- **Disbursing Officer:** select an eligible household in the assigned barangay and record its payout. This role cannot approve eligibility or create funding.
- **Beneficiary:** inspect the household linked to the account and its recorded payouts. Other household records are unavailable.
- **Auditor:** inspect private office records and evidence, with no business mutations.

The account banner offers a relevant next action and **Sign out**. Refresh restores the server session. Expired or revoked sessions require sign-in again. Provisioning and permission details are in [DEMO_SESSIONS.md](DEMO_SESSIONS.md).

## Funding summaries

Open /dashboard to inspect stored releases, allocations, recorded payouts and aggregate registry counts. The public activity feed shows funding and allocation events; it excludes household, review and payout narratives. A batch link opens /batch/[id] for its funding and allocation details.

Expand blockchain details for the configured network and contract. These values come from the backend. No dashboard control changes the network. A connection indicator is not evidence that every payout has an anchor. Failed refreshes are visible; older totals should not be treated as newly loaded data.

## Register and review a household

1. Sign in as DSWD or Barangay and open /beneficiaries. Search households or select **Needs review** for pending decisions, including registrations without duplicate flags. **Register a household** accepts a fictional household name and barangay. Barangay accounts use their assigned area; their registrations stay pending for DSWD review. A saved confirmation opens the household's current status.
2. Registration checks for possible duplicate records. A similarity score is a suggestion for human review, not proof of a duplicate.
3. DSWD inspects a household, enters a reason and chooses **Approve household**, **Reject household** or **Keep for review**. The server records the authenticated reviewer, time and prior evidence. Failure retains the reason; a saved review updates eligibility.
4. For a confirmed duplicate, expand **Resolve as a duplicate**, choose another active household in the same batch and select **Mark duplicate and retain history**. The original ID, payouts and decisions remain retained. Under **More registry options**, enable **Include historical duplicates** to inspect those rows. A historical duplicate cannot receive a new payout or ordinary reapproval.
5. DSWD, Auditor and the linked Beneficiary can expand permitted **Review history**. History is local database evidence, not blockchain-protected history.

Expand **Review evidence** for permitted matching scores and saved notes, or **Record references** for household/DAFAC/batch IDs. Approved status still requires Disbursing to check batch, funding and prior payouts; approval alone does not record a payout. Office readers can follow **View payout records**. Disbursing explicitly selects the household on the payout screen.

DSWD can also open **Analyze a CSV** under **More registry options**. Choose a fictional file or explicitly analyze the sample. The analyzer reports possible pairs; it does not import the masterlist. Validation, preview and explicit import remain future work. See [HUMAN_REVIEW.md](HUMAN_REVIEW.md), [RETAINED_DUPLICATES.md](RETAINED_DUPLICATES.md) and [registry UI behavior](REGISTRY_REVIEW_UX.md).

## Record a synthetic payout

1. Sign in as Disbursing and open /distributions. Select an eligible household within the assigned barangay.
2. Check the active batch and fictional grant amount. The API enforces eligibility, the batch maximum, remaining allocation budget and one payout per linked household per batch.
3. Select **Record demo payout**. A recorded payout and a confirmed blockchain anchor are separate facts. Submission errors remain visible; uncertain retries keep the form's request identity during the current page session.
4. Check the separate anchor status. For new payouts, Disbursing can use **Recover anchor** or **Recheck anchor**; this recovers the stored transaction and does not record another payout. After refresh, expand **Anchor status and recovery** on the recorded payout. Older records have no recovery job and remain available for receipt checks.
5. Follow **Check this receipt** to inspect that exact payout. Unknown receipt links show **Receipt not found** and never substitute another payout.

Actual camera QR decoding and a persistent offline queue are not implemented. When the browser reports offline, submission is disabled and no payout is queued. Reconnecting does not submit automatically. The current retry identity is held in memory, not preserved across a page reload.

Older fixtures reuse one sample receipt image/OCR containing another fictional household's details. Scoped accounts do not receive that shared template. A record without a household-specific image shows that limitation and still offers hash verification. Office readers retain access to historical template evidence; stored hashes are unchanged.

## Check receipt integrity

Open /verify or follow a payout's receipt link. The public view exposes receipt references and hash evidence. Authorized accounts can also see their permitted local household and amount context.

- **Receipt hash verified:** an actual successful contract read found a matching anchor.
- **Receipt hash mismatch:** an actual read found a different existing hash. This alone does not identify fraud or an actor.
- **No receipt anchor found:** the contract was read successfully and has no receipt for that reference.
- **Verification unavailable:** a reliable lookup could not be completed. Retry after the configured service recovers.

**Check again** repeats the lookup. Expand technical details for observed hashes and contract information. Names, allocation linkage and raw file contents are not yet all covered by an immutable versioned snapshot. Hashes are not a general guarantee of privacy. New payouts support [durable anchor recovery](PAYOUT_ANCHORS.md). Funding/historical recovery, recipient acknowledgement and an interactive synthetic tampering/restoration screen remain pending. See [TRUTHFUL_VERIFICATION.md](TRUTHFUL_VERIFICATION.md) and [TODO.md](TODO.md).
