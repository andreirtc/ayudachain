# Household registration and review clarity

Bounded frontend follow-up to [PR #19](https://github.com/andreirtc/ayudachain/pull/19), based on `BinkzBooze/ayudachain-19-payout-anchor-recovery`. The existing five authenticated roles and APIs remain authoritative. All records and payouts are synthetic.

## Screen behavior

`/beneficiaries` now presents a household registry with a role-specific purpose, a labeled search and familiar status labels. **Needs review** includes every active pending household, including Barangay registrations without a duplicate or amount flag. Search and status filters stay in place while reviewing records. The same list becomes stacked household rows on phones; no horizontal table scrolling is needed.

DSWD and Barangay can register a household. Barangay remains restricted to its assigned area and new registrations await DSWD review. Registration shows the returned record and a saved confirmation. DSWD registrations without a suggested duplicate can already return approved from the existing API; the screen does not invent a human decision for those records.

The review dialog shows status, the next step and any active flags. Scores, saved evidence, retained history and record references are expandable. It displays actual stored notes rather than inventing matching explanations. DSWD approval, rejection, pending decisions and retained duplicate links still require reasons and record the authenticated reviewer. Duplicate confirmation keeps IDs, payouts, receipts and earlier decisions; the saved message also remains visible after the record becomes historical.

Approved household details explain that Disbursing must still check the batch, funding and previous payouts. Accounts permitted to inspect payouts can open the existing payout screen. That link opens payout records; it does not preselect a household or prove a payout occurred. Barangay receives status guidance without a link to private payout records. The connected browser journey signs into Disbursing and explicitly selects the same household, records one payout and follows its exact receipt link.

CSV analysis and historical rows sit under **More registry options**. CSV analysis starts only on an explicit action, uses a labeled keyboard-accessible file input, and reports inline loading and failure states. It analyzes pairs only; it does not import households or change decisions.

## Feedback and accessibility

- Loading, empty lists, empty searches, refresh errors, registration success and review success are visible. Failed list refreshes hide stale rows until a successful retry. Overlapping loads cannot replace a newer list with an older response.
- Registration names and review reasons survive request failures. In-flight guards prevent repeated clicks; inputs and dialog dismissal are disabled during writes. Browser-reported offline status blocks mutations and analysis. There is no offline queue or automatic reconnect submission.
- Native modal dialogs make the background inert. Initial focus, explicit Tab/Shift+Tab wrapping, Escape when idle and return to the opener are implemented. If a filtered row disappeared, focus returns to the registry heading.
- Phone fields use readable text, controls have at least 44-pixel height, and status uses words as well as color. Search, reasons, locality, file selection and duplicate survivor controls have labels.

These checks establish behavior in automated Edge desktop and phone emulation. They do not establish comprehension by a new viewer, physical-device usability or a full accessibility audit.

## Design references applied

Reviewed on 2026-10-13. [GOV.UK question pages](https://design-system.service.gov.uk/patterns/question-pages/) informed focused task headings, grouped required inputs and avoiding repeated entry. [GOV.UK writing for user interfaces](https://www.gov.uk/service-manual/design/writing-for-user-interfaces) informed direct action labels and concise status/help text. Applying these patterns does not imply government affiliation. Technical evidence stays available without competing with the main household task.

## Validation

Validated on 2026-10-13:

- 26 actual headless Microsoft Edge Playwright cases passed at desktop 1440×900 and phone 390×844. Ten new registry cases cover loading/retry/empty search, input retention, offline and repeated-submit controls, dialog focus, all three ordinary decisions, reviewer attribution, retained duplicates/history/payouts, CSV analysis without import, and the complete registration-to-review-to-payout-to-exact-receipt journey. The existing sixteen session/privacy/payout cases also passed.
- 19 backend authentication/permission regressions passed using `backend/.venv/Scripts/python.exe -m unittest test_auth -q` from `backend`.
- Seven frontend Node receipt-navigation/connectivity checks passed. Independent TypeScript (`tsc --noEmit`), production build and `git diff --check` passed. The build still skips its embedded type/lint checks; independent TypeScript is required.
- Registry, registration, review/history and CSV screenshots were inspected at both sizes. The inspection caught and corrected a desktop action label wrapping. The keyboard test caught and corrected Tab moving from the final control to browser chrome.

Browser tests use `frontend/playwright.config.ts`: temporary DB/accounts/receipts, API 8101 and frontend 3101, with server reuse refused. The API explicitly reports chain unavailability, so these tests assert an unavailable receipt check and do not establish live mining. Live-chain tests were not repeated for this presentation change.

No backend schema, contract, signer, deployment or original database/chain reset is included. Production dependency hardening, CSV import, claim acknowledgement, licensing and other frontend screens remain separate work.
