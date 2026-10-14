# Prompt: implement the rest of the Tonal design

This proposed completion prompt was brought forward from `design-proposal` with its Tonal visual layer. The import does not authorize the remaining work below. Follow the maintainer's requested scope and the screen storytelling plan in `docs/implementation/2026-10-13-screen-storytelling-plan.md`; all storytelling phases remain Pending.

When the maintainer authorizes a completion task, use the prompt below from the current checkout. It assumes the agent can read the repository, run the local MVP and run the test suites.

---

## Prompt

You are working on AyudaChain, a tamper-evident record of Philippine disaster cash assistance. The five-role MVP lives at `/mvp` (Next.js frontend in `frontend/`, FastAPI and PostgreSQL backend in `backend/`). Before you change anything, read `AGENTS.md`, `PRODUCT.md`, `DESIGN.md`, `docs/product/prd.md`, `docs/system/erd.md`, `docs/product/sitemap.md`, `docs/product/user-flow.md`, the "Design proposal" section of `README.md` and `docs/implementation/2026-10-13-screen-storytelling-plan.md`, then follow them.

The imported **Tonal** visual layer (Material 3, **Sea and Sun** palette, Open Sans, Kubo Link logo, light and dark schemes) is already applied. Implement only the phase or tasks the maintainer has authorized. Open `docs/design/tonal-design-reference.html` in a browser and select **Sea and Sun** for component/layout reference. Its sample wording and records do not override the PRD, current workflow or Filipino-first beneficiary plan. Do not copy its markup wholesale or redo the imported theme/logo/font work.

### What to build

Follow the storytelling plan's phase order: **1. safe status/action mapping; 2. beneficiary dashboard and language; 3. beneficiary task flows; 4. staff handoffs; 5. usability and validation.** This numbered list is a component checklist, not execution order. The plan's alignment table assigns each item to its phase. Complete and validate the beneficiary journey before extending the pattern to staff; do not start with dialogs merely because they appear first below.

1. **Confirmation dialog (Phases 3–4).** Before saving consequential staff records, show a Material 3 dialog that restates the selected record, choice and consequence. Explain that the event remains in history, with a new correction event where the existing workflow permits one. Use a native `<dialog>` with focus trapping, Escape to cancel before submission and focus returned to the trigger. This covers:
   - claim decisions;
   - barangay responses;
   - ID comparison results;
   - cash handovers;
   - list publication.

   The dialog adds a review step only. Cancellation before submission sends no command; retain current revisions, permissions and idempotency handling. It must not change request payloads or the API, imply that cancelling reverses cash already handed over, or offer Undo for an append-only record.
2. **Snackbar (Phases 3–4).** After a confirmed save, show a specific result (for example, "Decision recorded for DFC-…") with an optional permitted View action. It uses `role="status"`, does not take focus, dismisses after 5 seconds and can also be dismissed by hand. Keep a persistent inline result and next step after it disappears; do not announce success for a lost write response until the saved record is read. Queued publication/anchoring is not published or verified; describe the actual current state.
3. **Segmented buttons (Phases 3–4).** Replace the radio and select controls for single-choice decisions with an accessible Material 3 segmented button, implemented as a radio group with arrow-key navigation:
   - Approve / Decline / Refer to barangay;
   - Endorse / Do not endorse;
   - Pass after comparison / Fail and hold/stop;
   - Own device / No-phone assisted recipient.

   Keep the same form field names and submitted values. When "Fail and hold/stop" is selected, the save button turns into the error style.
4. **Flag banners (Phase 4).** Show duplicate, category and referral flags at the top of the case: an icon in the status colour, a bold sentence, an explanation, permitted text-button actions (for example, "Compare records") and a divider below. Flags call for human inspection, not a fraud finding. Do not use tinted boxes or coloured left edges for status/flag banners.
5. **Integrity status rows (Phases 1 and 4).** Define current/historical result meanings in Phase 1, then restructure `IntegrityStatus` in Phase 4: glyph, record name, current time/action and explanation. Keep every state and fail closed: "Verified" appears only after a current chain read matches. Failed refresh removes the current match; earlier observations remain separately labelled. Ensure visible and accessible text has a word boundary between the status and "Checked …"; separate JSX elements alone are insufficient. Reproduce any existing text-boundary failure before fixing it.
6. **Navigation rail and list-detail on desktop (Phases 2 and 4).** From 1024px up, use a Material 3 rail with icons, readable labels and a pill indicator. Keep the agreed beneficiary grouping. Staff claim review, payout records and integrity use appropriate list/detail panes; a labelled create action appears only where permitted and useful. Keep the dashboard as the starting point, every route/context parameter (including `account`, `disaster`, `record`, `history` and safe queue state), role restriction, browser Back and keyboard behavior. Keep All workspaces and the logo link to `/mvp`; use an accessible drawer at intermediate widths.
7. **Bottom navigation bar on phones (Phases 2 and 4).** Below 760px, the beneficiary destinations are **Ayuda ko, Impormasyon namin, Mga tala, Humingi ng tulong**, with English translations and saved-language preference respected. For staff, select at most four destinations from actual role tasks before implementation; the route list alone does not establish usage frequency. Keep every secondary section reachable and preserve existing deep links. Reserve clearance for focused controls and final actions. Update `docs/product/sitemap.md` when the navigation is delivered.
8. **Household screens (Phases 2–3).** Put the mapped status and one next action first on Home, then amount/appointment, latest update and optional details. Connect claim progress, amount basis, authorization/receipt and private concern to the selected record. Complete essential Filipino copy with an English option. The payout code uses Source Code Pro at about 34px with readable grouping and Hide code; reveal uses only the code still held in that active view, never a refetch or persisted browser value. Explain expiry, counting cash before sharing the code, and the distinct private PIN.
9. **Disbursing Officer tablet layout (Phase 4).** Show accepted-ID photo beside the comparison form, fixed amount in the header and a handover instruction panel: compare identity, present amount/cash for counting, recipient shares the payout code after counting, hand over and record once. Opening authorization/private PIN entry is distinct from revealing the payout code. Keep no-phone recipient-controlled PIN entry, eligible independent checker and uncertain-handover recovery explicit. Independent exit checks remain a separate eligible-checker task.
10. **Auditor filter chips (Phase 4).** Add All, Verified, Does not match, Anchor absent, Chain unreachable, Evidence unavailable and Not checked alongside existing search. Preserve checking/failed-refresh states. Label local filters as loaded/checked records in this view; historic submission states and unchecked records must not imply current verification or global totals. Record any missing API data separately.
11. **Empty states (Phases 2–4).** Use outlined icon/title/explanation cards with a permitted action where useful. Distinguish waiting, no records and failed required reads.
12. **Barangay floating action button (Phase 4).** Add labelled Assisted registration only within the existing permitted flow, retaining assister recusal. Keep the dashboard's response task dominant; no Auditor create action is added.

### Constraints you must keep

- Follow the integrity invariants in `AGENTS.md`: fail closed, real or labelled, humans decide, append-only audit, personal data off-chain, synthetic data only, docs match code.
- Do not change the database schema, API payloads, the contract, the receipt hash payload or chain behaviour. This is a presentation change.
- Do not add npm or Python dependencies without asking first. Build components with plain React and CSS on the existing tokens in `frontend/app/mvp.css`. Material Web is a new dependency, so it needs explicit approval.
- Use only the role tokens (`--md-*`, `--st-*`); no hard-coded colours. Every addition must work in light and dark (`data-theme` and `prefers-color-scheme`).
- Preserve the agreed Filipino-first beneficiary experience with an English option, saved language/theme choices, valid entered values and record-specific task context. Treat every imported completion item as Pending until implemented and validated.
- Accessibility: visible focus, keyboard operation, 44px touch targets on phones, at least 13px text and 4.5:1 text contrast. Status must never rely on colour alone.
- Simulated National ID and SMS paths stay labelled as simulated. The "claimed, unverified account" notice stays visible.
- Update `DESIGN.md`, `docs/product/sitemap.md`, `docs/product/user-flow.md` and the "Not yet implemented" table in `README.md` in the same change as each behaviour you deliver.

### How to verify

1. `npm --prefix frontend run typecheck`
2. `npm --prefix frontend run build` (stop the dev server first)
3. Start the MVP as described in `docs/guides/local-mvp.md`, then run `npm --prefix frontend run test:mvp`. The original `design-proposal` recorded ten browser failures; these are historical findings, not the current checkout's baseline. Consult `docs/implementation/validation.md`, establish the current results, and fix the root causes of failures your authorized work touches. Report remaining failures honestly, with the output.
4. Check every changed screen at 1440px and 390px, in light/dark and Filipino/English; check tablet composition and transitions at 760px/1024px. Verify bottom-bar clearance, dialog focus/cancellation, segmented keyboard controls, persistent feedback, safe code hiding, proof-filter scope and existing theme/error regressions. There must be no horizontal page overflow or browser exceptions.
5. Report what you built, what you changed in the docs and the exact test results. Do not commit or push unless asked.
