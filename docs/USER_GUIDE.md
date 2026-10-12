# AyudaChain user guide

AyudaChain is a fictional disaster-relief prototype. Use invented households and simulated payouts only. A matching blockchain receipt hash establishes integrity of the fields currently hashed; it does not establish cash delivery, government affiliation or the identity of a real recipient.

## Sign in and choose a task

The public landing, funding summaries and limited receipt checks do not require sign-in. Private records require a provisioned synthetic account at /sign-in. Account credentials come from local provisioning, not a role dropdown. The server enforces each account's role and scope.

- **DSWD Officer:** review households, register records, analyze CSV and manage fictional funding. Eligibility decisions record the signed-in account. This role cannot record payouts.
- **Barangay Officer:** register and inspect household status within the assigned barangay. Eligibility decisions and private review evidence belong to DSWD.
- **Disbursing Officer:** select an eligible household in the assigned barangay and record its payout. This role cannot approve eligibility or create funding.
- **Beneficiary:** inspect the household linked to the account and its recorded payouts. Other household records are unavailable.
- **Auditor:** inspect private office records and evidence, with no business mutations.

Navigation offers tasks relevant to the server-authenticated role. The account banner shows identity, **Sign out**, and a next action when it differs from the current task. On phones, **Menu** supports keyboard navigation and Escape. Refresh restores the server session. Expired or revoked sessions require sign-in again. Provisioning and permission details are in [DEMO_SESSIONS.md](DEMO_SESSIONS.md).

## Funding summaries

Open /dashboard to inspect stored releases, allocations, recorded payouts and aggregate registry counts. **Refresh overview** loads a new snapshot. A recorded payout count is not a verified receipt count. The public activity feed shows funding and allocation events; it excludes household, review and payout narratives. **View batch details** opens /batch/[id] for readable allocation rows and permitted activity. Failed batch loads offer retry and do not substitute another batch.

Expand **Blockchain service details** for the reported network and contract, or batch/allocation references for stored transactions. These values come from the backend; a transaction reference is not current verification. No dashboard control changes the network. Failed refreshes are visible; older totals should not be treated as newly loaded data. Recorded dates display in the browser's local time, interpreting legacy UTC strings correctly. See [shared UI polish](UI_POLISH.md).

## Register and review a household

1. Sign in as DSWD or Barangay and open /beneficiaries. Search households or select **Needs review** for pending decisions, including registrations without duplicate flags. **Register a household** accepts a fictional household name and barangay. Barangay accounts use their assigned area; their registrations stay pending for DSWD review. A saved confirmation opens the household's current status.
2. Registration checks for possible duplicate records. A similarity score is a suggestion for human review, not proof of a duplicate.
3. DSWD inspects a household, enters a reason and chooses **Approve household**, **Reject household** or **Keep for review**. The server records the authenticated reviewer, time and prior evidence. Failure retains the reason; a saved review updates eligibility.
4. For a confirmed duplicate, expand **Resolve as a duplicate**, choose another active household in the same batch and select **Mark duplicate and retain history**. The original ID, payouts and decisions remain retained. Under **More registry options**, enable **Include historical duplicates** to inspect those rows. A historical duplicate cannot receive a new payout or ordinary reapproval.
5. DSWD, Auditor and the linked Beneficiary can expand permitted **Review history**. History is local database evidence, not blockchain-protected history.

Expand **Review evidence** for permitted matching scores and saved notes, or **Record references** for household/DAFAC/batch IDs. Approved status still requires Disbursing to check batch, funding and prior payouts; approval alone does not record a payout. Office readers can follow **View payout records**. Disbursing explicitly selects the household on the payout screen.

DSWD can also open **Analyze a CSV** under **More registry options**. Choose a fictional file or explicitly analyze the sample. The analyzer reports possible pairs; it does not import the masterlist. Validation, preview and explicit import remain future work. See [HUMAN_REVIEW.md](HUMAN_REVIEW.md), [RETAINED_DUPLICATES.md](RETAINED_DUPLICATES.md) and [registry UI behavior](REGISTRY_REVIEW_UX.md).

## Record a synthetic payout

1. Sign in as Disbursing and open /distributions. Choose an eligible household within the assigned barangay. The form starts without a selected household. Other permitted roles inspect payout records without an entry form.
2. Check the active batch, grant limit and remaining recorded allocation. The displayed allocation is a recorded budget, not cash on hand. The API enforces current eligibility, the batch maximum, remaining allocation budget and one payout per linked household per batch.
3. Select **Record demo payout**. A recorded payout and a confirmed blockchain anchor are separate facts. Submission errors remain visible; uncertain retries keep the form's request identity during the current page session.
4. Check the separate anchor status. For new payouts, Disbursing can use **Recover anchor** or **Recheck anchor**; this recovers the stored transaction and does not record another payout. After refresh, expand **Anchor status and recovery** on the recorded payout. Older records have no recovery job and remain available for receipt checks.
5. Follow **Check this receipt** to inspect that exact payout. Unknown receipt links show **Receipt not found** and never substitute another payout. **Record another payout** opens an empty entry form. Readers can search **Recorded payouts**, open their permitted receipts and refresh the list. See [payout UI behavior](UI_PAYOUT.md).

Actual camera QR decoding and a persistent offline queue are not implemented. When the browser reports offline, submission is disabled and no payout is queued. Reconnecting does not submit automatically. The current retry identity is held in memory, not preserved across a page reload.

Older fixtures reuse one sample receipt image/OCR containing another fictional household's details. Scoped accounts do not receive that shared template. A record without a household-specific image shows that limitation and still offers hash verification. Office readers retain access to historical template evidence; stored hashes are unchanged.

**View receipt** opens the exact payout's details in a keyboard-accessible dialog. Its amount and household label come from the permitted local records. Office readers can expand **Saved receipt image** and **Saved extracted text**. A shared template is clearly labeled; image failures offer **Retry image** without losing the reference. **Check this receipt** opens the same record on the verification page. See [receipt UI behavior](UI_RECEIPTS.md).

## Check receipt integrity

Open /verify or follow a payout's receipt link. The public view exposes receipt references and hash evidence. Authorized accounts can also see their permitted local household and amount context.

- **Receipt hash verified:** an actual successful contract read found a matching anchor.
- **Receipt hash mismatch:** an actual read found a different existing hash. This alone does not identify fraud or an actor.
- **No receipt anchor found:** the contract was read successfully and has no receipt for that reference.
- **Verification unavailable:** a reliable lookup could not be completed. Retry after the configured service recovers.

**Check again** repeats the lookup. **Enter a receipt reference** opens a particular recorded payout without substituting another if it is missing. Loading the receipt list and looking up proof have separate retry controls. Offline views label the previous observation and disable new checks; reconnecting does not automatically check again. Expand **Hash comparison and lookup details** for hashes, network/contract information and the server's explanation. Names, allocation linkage and raw file contents are not yet all covered by an immutable versioned snapshot. Hashes are not a general guarantee of privacy. New payouts support [durable anchor recovery](PAYOUT_ANCHORS.md). Funding/historical recovery, recipient acknowledgement and an interactive synthetic tampering/restoration screen remain pending. See [verification UI behavior](UI_VERIFICATION.md), [TRUTHFUL_VERIFICATION.md](TRUTHFUL_VERIFICATION.md) and [TODO.md](TODO.md).
