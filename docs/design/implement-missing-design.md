# Prompt: implement the rest of the Tonal design

Paste the prompt below into a coding agent (for example, Claude Code) from the repository root on the `design-proposal` branch. It is self-contained. It assumes the agent can read the repository, run the local MVP and run the test suites.

---

## Prompt

You are working on AyudaChain, a tamper-evident record of Philippine disaster cash assistance. The five-role MVP lives at `/mvp` (Next.js frontend in `frontend/`, FastAPI and PostgreSQL backend in `backend/`). Before you change anything, read `AGENTS.md`, `PRODUCT.md`, `DESIGN.md`, `docs/product/sitemap.md`, `docs/product/user-flow.md` and the "Design proposal" section of `README.md`, then follow them.

The visual layer of the approved **Tonal** design (Material 3, **Sea and Sun** palette, Open Sans, Kubo Link logo, light and dark schemes) is already applied. Your job is to implement the parts that are still missing, so the app matches `docs/design/tonal-design-reference.html`. Open that file in a browser and select the **Sea and Sun** palette. Use it as the visual reference for layout, components and wording. It is a design reference, not production code, so do not copy its markup wholesale.

### What to build

Work through these in order. Finish, test and review one item before starting the next.

1. **Confirmation dialog.** Before any irreversible record is saved, show a Material 3 dialog that restates exactly what will be recorded and says it cannot be edited afterwards. Use a native `<dialog>` element with focus trapping, Escape to cancel and focus returned to the trigger. This covers:
   - claim decisions;
   - barangay responses;
   - ID comparison results;
   - cash handovers;
   - list publication.

   The dialog adds a step only. It must not change the request payloads or the API.
2. **Snackbar.** After a successful save, show a snackbar ("Decision recorded for DFC-…") with an optional View action. It uses `role="status"`, does not take focus, auto-dismisses after 5 seconds and can also be dismissed by hand. Keep the existing inline success messages wherever tests or the screen depend on them.
3. **Segmented buttons.** Replace the radio and select controls for single-choice decisions with an accessible Material 3 segmented button, implemented as a radio group with arrow-key navigation:
   - Approve / Decline / Refer to barangay;
   - Endorse / Do not endorse;
   - Pass after comparison / Fail and hold/stop;
   - Own device / No-phone assisted recipient.

   Keep the same form field names and submitted values. When "Fail and hold/stop" is selected, the save button turns into the error style.
4. **Flag banners.** Show duplicate, category and referral flags as a Material 3 banner at the top of the case: an icon in the status colour, a bold sentence, an explanation, text-button actions (for example, "Compare records") and a divider below. Do not use tinted boxes or coloured left edges anywhere.
5. **Integrity status rows.** Restructure `IntegrityStatus` into status rows: a glyph, the record name, the time or a text action on the right, and an explanation line. Keep every existing state and the fail-closed rules: "Verified" appears only after a current chain read matches. Put a space or separate element between the status word and "Checked …" so the text reads "Verified Checked …" rather than "VerifiedChecked …".
6. **Navigation rail and list-detail on desktop.** From 1024px up, replace the fixed drawer with a Material 3 navigation rail: icons with labels and a pill indicator, plus a floating action button for the role's main create action where one exists. On claim review, payout records and integrity, show the list and the selected detail side by side. Keep every current URL, query parameter (`account`, `disaster`, `record`, `history`), role restriction and keyboard behaviour. Keep "All workspaces" and the logo link to `/mvp`.
7. **Bottom navigation bar on phones.** Below 760px, use a Material 3 bottom bar with at most four destinations per role. Choose the four most frequent destinations from `frontend/components/mvp/workspaces.ts`, and keep the other sections reachable from the overview. Write down the chosen four per role in `docs/product/sitemap.md`.
8. **Household screens.** Rebuild these as phone-first screens to match the reference: the beneficiary Home (next-step card first), My claim (stepper with dates and the amount basis), Authorization and receipt, and the private report screen. The payout code uses Source Code Pro at about 34px with spaced groups and a "Hide code" action. The PIN warning is a banner.
9. **Disbursing Officer tablet layout.** Show the photo beside the comparison form, with a "Handover steps" side panel (compare identity, recipient authorises, count and hand over cash, record cash handover) and a "Recorded once only" note line. The amount is shown large in the header.
10. **Auditor filter chips.** Add result filter chips (All, Verified, Does not match, Anchor absent, Chain unreachable, Not checked) above the integrity table, alongside the existing search.
11. **Empty states.** Use an outlined card with an icon, a title and one explanatory sentence.
12. **Barangay floating action button.** Add "Assisted registration" as the Barangay Officer's floating action button. It links to the existing registration flow.

### Constraints you must keep

- Follow the integrity invariants in `AGENTS.md`: fail closed, real or labelled, humans decide, append-only audit, personal data off-chain, synthetic data only, docs match code.
- Do not change the database schema, API payloads, the contract, the receipt hash payload or chain behaviour. This is a presentation change.
- Do not add npm or Python dependencies without asking first. Build components with plain React and CSS on the existing tokens in `frontend/app/mvp.css`. Material Web is a new dependency, so it needs explicit approval.
- Use only the role tokens (`--md-*`, `--st-*`); no hard-coded colours. Every addition must work in light and dark (`data-theme` and `prefers-color-scheme`).
- Accessibility: visible focus, keyboard operation, 44px touch targets on phones, at least 13px text and 4.5:1 text contrast. Status must never rely on colour alone.
- Simulated National ID and SMS paths stay labelled as simulated. The "claimed, unverified account" notice stays visible.
- Update `DESIGN.md`, `docs/product/sitemap.md`, `docs/product/user-flow.md` and the "Not yet implemented" table in `README.md` in the same change as each behaviour you deliver.

### How to verify

1. `npm --prefix frontend run typecheck`
2. `npm --prefix frontend run build` (stop the dev server first)
3. Start the MVP as described in `docs/guides/local-mvp.md`, then run `npm --prefix frontend run test:mvp`. Ten browser tests already fail on this branch: the journey test, its dependants and the "Verified" word-boundary tests listed in `README.md`. Fix the root causes of the ones your work touches. Report the remaining failures honestly, with the output.
4. Check every changed screen at 1440px and 390px, in light and dark. There must be no horizontal page overflow and no console errors.
5. Report what you built, what you changed in the docs and the exact test results. Do not commit or push unless asked.
