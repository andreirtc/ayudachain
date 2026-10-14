# Screen storytelling and usability implementation plan

Date: 2026-10-13.

Status: **Phases 1-5 implemented in software and automatically checked, 2026-10-14; human validation Pending.** The maintainer approved all five phases and the aligned Tonal direction. [The durable checklist](screen-storytelling-progress.md) links the implementation and actual evidence, including limits: no single uninterrupted all-green run, an unresolved local anchor job blocking chain-backed reruns, colour contrast not measured, and native Filipino review, participant comprehension and physical-device checks all Pending.

Confirmed preference: beneficiary screens are **Filipino first, with an English option**. Existing saved language choices should remain respected.

## Goal and governing requirements

Each screen should immediately answer: **Where am I in the process? What do I need to do? What happens afterward?** Design for limited digital experience, small phones and stressful circumstances. Keep the tone respectful and instructions concrete.

Make each role's dashboard the starting point for its work. Give it one visually dominant next action that opens a focused task with the relevant record already selected. Keep detailed records and secondary tools reachable.

Use the [PRD](../product/prd.md), [ERD](../system/erd.md), [current user flow](../product/user-flow.md), [sitemap](../product/sitemap.md) and [repository instructions](../../AGENTS.md) as the governing requirements. This plan changes presentation and task guidance within those requirements. Any needed API, schema or business-rule extension must be identified separately and handled under the repository's approval rules.

Use [DESIGN.md](../../DESIGN.md) for the implemented Tonal visual system and the [Tonal reference](../design/tonal-design-reference.html), with **Sea and Sun** selected, for proposed component and layout treatments. The reference's sample copy, records and layouts do not override the approved workflow or this plan's Filipino-first beneficiary guidance.

Retain fail-closed verification, human decisions, append-only history, role-scoped views and once-only handover. A recorded handover, a recipient's answer and a current integrity check are separate facts. Authentication remains Pending; synthetic evaluation and simulated ID/SMS disclosures must remain visible and accurate.

## Review baseline

The proposal was informed by the current working-tree source and read-only visits to all five live role dashboards on 2026-10-13. The branch contained substantial pre-existing uncommitted UI and documentation work. Reinspect the current implementation before executing a phase.

The site already has role dashboards, a beneficiary timeline, server-scoped queues, record links, bilingual guidance and role-specific error recovery. Build on those capabilities.

Observed friction:

- Beneficiary navigation exposes eight destinations, including technical concepts such as entitlement and authorization.
- Guidance and errors support Filipino, while much of the navigation, dashboard and form copy remains English.
- The beneficiary dashboard repeats its next-action link and gives substantial space to calculation details and appointment history.
- Dashboard next-action selection uses broad conditions, including the presence of a session. A session's existence alone does not establish current payout readiness.
- Several dashboard links open a general section, requiring the user to identify the same record again.
- Staff dashboards combine immediate tasks with extensive operational summaries. Closed sessions can compete with current work.
- Generic saved messages and technical history labels require users to interpret what an action achieved.

These are source and interface observations, not findings from a completed usability study. Existing validation results are recorded in [validation](validation.md). At planning time, the reviewed working tree contained uncommitted error-guidance changes. Those changes were subsequently committed in `1644f59`; see [role error guidance](role-error-guidance.md) for their scope and validation. This does not mark any phase of the storytelling redesign as completed.

### Baseline after the Tonal import

The maintainer subsequently authorized importing the additions from `design-proposal` commit `4377db1`, based on shared commit `56102c4`. The current working tree now includes the Sea and Sun light/dark schemes, remembered Light/Dark/Device choice, Kubo Link logo/favicon, Open Sans and Source Code Pro, tonal panels, pill buttons, outlined fields, glyph-and-word statuses, banner messages and links back to the workspace directory. Retain these additions and the newer workflow-error recovery; do not repeat the visual import as a storytelling task.

The import restyled the existing screens. It did not implement the four beneficiary destinations, complete Filipino copy, accurate shared next-action mapping, connected task flows or the remaining reference layouts. All five phases below therefore remain Pending. Fresh import checks and limits are recorded under **Tonal design import** in [validation](validation.md); the source branch's ten browser failures are historical findings, not the current test baseline.

### Alignment with the design-proposal README

The source README's implemented/missing distinction remains useful. Its missing components are incorporated into this plan as follows; every item below is **Pending**, unless explicitly out of scope. Phase 5 validates all delivered items.

| Source README area | Planned application | Delivery phase |
|---|---|---|
| Phone navigation | Bottom navigation with the four beneficiary destinations in section 1; all existing capabilities remain reachable. Staff have at most four primary destinations, selected from role tasks before implementation rather than assuming usage frequency from the route list. | 2 for beneficiary; 4 for staff |
| Desktop navigation | Labelled Material 3 navigation rail at 1024px and above; preserve context, routes, keyboard access, directory links and the dashboard as the starting point. Claim review, payout records and integrity get list/detail panes where appropriate. | 2 for beneficiary shell; 4 for staff panes |
| Decisions | Accessible segmented radio groups for approval/decline/referral, endorsement, identity pass/fail and recipient path. Preserve existing values, reasons, recusal rules and server guards. | 3 for recipient path; 4 for staff decisions |
| Confirmation | Dialog review before saving claim decisions, barangay responses, ID comparisons, handovers and publication. Describe the exact record and consequence; retain append-only correction/history rules. | 3 for beneficiary review patterns; 4 for staff records |
| Feedback | Snackbar with a specific saved result and optional permitted View action, supported by persistent inline confirmation and the next responsible role. | 3 for beneficiary; 4 for staff |
| Flags | Case-level duplicate/category/referral banner with explanation and permitted actions above a divider. Flags prompt human inspection and never declare fraud. | 4 |
| Integrity rows | Explicit current state, record, check time/action and explanation, with earlier observations separate. Define the states first, then implement the rows. | 1 for mapping; 4 for presentation |
| Floating action button | A labelled create action only where the role permits one. Barangay Assisted registration opens the existing flow; it must not compete with the dashboard's primary response task. No Auditor create action. | 4 |
| Household screens | Phone-first current aid status, dated claim progress, amount basis, appointment, authorization/receipt and private concern, following the same record through each step. | 2 for Home; 3 for task screens |
| Disbursing Officer | Tablet layout keeps selected household, accepted photo ID comparison, fixed amount and handover steps visible together; independent exit checks remain separate. | 4 |
| Auditor | Filter chips for current proof results without treating historic submission confirmation as a current match or unchecked results as verified. | 4 |
| Empty states | Consistent outlined icon/title/explanation treatment with a useful permitted action; waiting, no records and failed reads remain distinct. | 2 for dashboard; 3 and 4 for task screens |
| Other palettes | Bayanihan Teal and Indigo and Mango remain reference-only. Ship Sea and Sun in light/dark. | Out of scope |
| Legacy screens | Preserve the historical interfaces; no legacy redesign or new MVP capability is implied. | Out of scope |

This plan owns implementation order and task behavior. The [completion prompt](../design/implement-missing-design.md) is a supporting checklist, not a second sequence. Align the current README and delivery documents when an item is actually implemented; importing or planning an item does not mark it complete.

## 1. Beneficiary dashboard and navigation

Reduce primary navigation to four destinations:

- **Ayuda ko:** current status, next action, relevant amount and appointment.
- **Impormasyon namin:** household information and permitted corrections.
- **Mga tala:** submitted application, decisions, history and receipt.
- **Humingi ng tulong:** permitted reports and follow-up.

Preserve access to existing capabilities through these destinations and contextual links, including the restricted residents' list and permitted challenges. Keep existing deep links usable while reorganizing navigation; do not remove a route merely to shorten the menu.

Below 760px, use these four labelled destinations in a Tonal bottom bar. At 1024px and above, show the same grouping in a labelled navigation rail; keep an accessible drawer between those breakpoints. Reserve space for the bottom bar so it does not cover forms, focused controls, messages or the final task action. Keep the logo and All workspaces return reachable. Do not substitute the reference's English Home/Claim/Payout/Report labels for the agreed grouping.

Order the dashboard by immediate need: current status, next action, relevant amount or appointment, recent update, optional details. Put calculation breakdowns and older history behind descriptive expandable sections. Keep completed appointments in history rather than presenting them as upcoming work.

Show one prominent CTA. When another role must act, name that role and explain whether the beneficiary needs to do anything. Do not manufacture a task to fill the dashboard.

## 2. Accurate status and next-action mapping

Define the message, responsible role, permitted action and destination for each meaningful state before changing layouts:

- **No household:** offer “Irehistro ang sambahayan.”
- **Registered and eligible to submit:** offer “Mag-apply para sa ayuda.”
- **Intake unavailable:** explain the known intake or coverage issue and where to ask for help. Do not infer the precise cause from an ambiguous response.
- **Under review:** identify Barangay or DSWD as the next responsible party and show actual saved progress.
- **Declined:** show the reason. Offer the existing once-only new-information resubmission only when its rules permit it.
- **Approved, amount pending:** explain that DSWD is completing the documented amount calculation; an unknown amount is not zero.
- **Awaiting publication or appointment:** show the known amount, the pending step and its owner without implying payout readiness.
- **Appointment scheduled:** prioritize its current date, site and preparation instructions.
- **Current payout available:** guide the recipient into the permitted authorization flow after checking current eligibility, session and hold information.
- **Held or stopped:** explain the recorded issue, responsible officer and permitted recovery. Distinguish an expired unused code from a stopped identity comparison.
- **Handover recorded:** ask what the recipient actually received; never offer another payout.
- **Answer recorded:** show the answer and any separate case status. A full answer does not automatically close a case.
- **Required data unavailable:** show an explicit unavailable state and safe refresh action. Do not treat failed reads as empty records or completed steps.

Derive the presentation from current scoped records, not array position, a progress index or optimistic assumptions. If existing responses cannot safely establish an action's availability, document the missing information and use a conservative message until the gap is resolved. Backend guards remain authoritative.

Keep a shared, testable mapping for dashboard, detail and confirmation copy so they describe the same state. Do not turn that mapping into a second business-rule engine.

Include the integrity vocabulary used by the imported glyph-and-word statuses: not checked, checking, match, mismatch, absent anchor, chain unreachable and evidence unavailable. A failed refresh clears the current match while retaining a separately labelled earlier observation. Define how filter chips distinguish these states before changing proof-row layout.

## 3. Filipino-first language

Apply the language preference to the complete beneficiary experience: navigation, headings, buttons, field labels, validation, statuses, loading states and confirmations. Switching languages must preserve the active task and entered values.

Example draft for a claim awaiting DSWD review:

> **Sinusuri ng DSWD ang inyong aplikasyon**
>
> Naisumite na ang inyong aplikasyon. DSWD ang susunod na magsusuri.
>
> Wala ka pang kailangang gawin ngayon.
>
> **Tingnan ang aplikasyon**

Draft vocabulary:

- “Your entitlement” becomes **“Halaga ng ayuda.”**
- “Open payout authorization” becomes **“Kumuha ng payout code,”** with timing and expiry explained before code creation.
- “Private receipt answer” becomes **“Sabihin ang natanggap mo.”**
- “Append private report” becomes **“Ipadala ang iyong concern.”**

Use familiar language and short instructions. Explain necessary program terms near their first use. Have a native Filipino speaker review the copy, then test comprehension with intended users. These examples are drafts, not validated translations. Staff language defaults are outside the confirmed beneficiary preference.

## 4. Connected transaction flows

Use one consistent interaction pattern:

**Dashboard action → focused task → review where needed → saved result → next step.**

Carry the household, claim, session or transaction into the task. Preserve safe account/disaster context, queue filters and browser Back behavior. Reset private task state when the selected actor changes. Keep validation errors beside the relevant fields and retain valid input.

Beneficiary flows:

- **Registration:** household details → members → contact/identity information → review → saved household → claim submission when available. Make clear that registration itself is not an application for aid.
- **Claim:** describe damage → supporting evidence → review → confirmation naming the next responsible role.
- **Payout:** appointment preparation → current authorization step → count cash before sharing the code → recorded handover → private receipt answer. Explain the once-shown code and expiry before generating it; never imply that refreshing reveals a lost code.
- **Concern:** select the relevant permitted record → describe the concern → submit → show the saved report and follow-up state.

Keep the no-phone assisted journey explicit: actual ID comparison, recipient-controlled private PIN entry and an independent eligible checker. Simplifying the screen must preserve the existing separation of duties and code/PIN distinction.

Replace generic “Action saved” messages with the specific confirmed result and what follows. A lost write response leaves success uncertain: read the saved record before retrying. Refreshing or rechecking must not repeat a business action or physical handover.

Use accessible native confirmation dialogs for consequential staff records listed in the alignment table. Restate the selected record, current choice and effect immediately before submission. Cancellation before submission sends no command; confirmation keeps existing revision checks and idempotency handling. Say that the saved event remains in history, with permitted correction through a new event where supported; do not claim every decision is impossible to correct. No dialog, cancellation or retry may imply that cash already handed over has been undone.

A snackbar may announce a confirmed save with `role="status"`, an optional View action and manual dismissal; it must not take focus. It may dismiss after five seconds only because the same result and next step remain readable inline. Never announce a save before acknowledgement or recovery confirms the record, and never offer Undo for an append-only event. Localize beneficiary dialogs, feedback and empty states with the rest of the task.

Publication and anchoring feedback must name the actual saved state. A queued publication request is not a published list or a verified chain result; use the existing current record and matching-anchor rules to describe completion.

For payout codes, use the existing Source Code Pro treatment at about 34px with readable grouping and a Hide code action. Hide/reveal may use only the code already held in the active view; refresh or leaving the view cannot retrieve the once-shown code. Keep code expiry and the distinction from the private PIN explicit, and keep both out of URLs and general browser storage.

Preserve unsaved input within the active multi-step flow. Durable drafts and cross-device recovery require an implemented storage design; do not promise them as part of a presentation-only change. Keep sensitive input and codes out of URLs and general browser storage.

## 5. Staff dashboards and handoffs

### Barangay Officer

Lead with **“Claims needing your response.”** Open the selected claim directly, show the evidence and response needed, then provide a clear route to the next eligible claim. Distinguish claims needing a response, ready for formal submission and already with DSWD.

Show formal batch submission only to an eligible Punong Barangay. Explain recusals and missing independent responders. Preserve aggregate-only payout visibility and the restrictions on amounts, identity documents and private outcomes.

### DSWD Officer

Lead with **“Work needing your decision.”** Group work into setup, claim review, amounts/publication, scheduling and private cases. Surface missing prerequisites with direct links and explain why a task is blocked.

After approval, explain whether the household awaits an amount, publication or scheduling. Keep saving funding and opening intake as distinct actions. Present funding authority separately from physical cash availability. Reuse existing server-scoped queues rather than calculating global task totals from a bounded record catalogue.

### Disbursing Officer

Lead with the current assigned session and **“Find recipient.”** Continue with the selected household: identity comparison → fixed amount and cash-counting instructions → recipient authorization → record handover → result.

Keep household and amount visible throughout. Provide independent exit checks as a separate task for an eligible checker. Move closed sessions to history. On uncertain handover acknowledgement, prioritize reading the recorded transaction and explicitly prevent guidance that encourages repeat cash.

On tablets, place the accepted-ID photo beside the comparison form and a handover instruction panel. Its wording follows the actual sequence: compare identity, present the fixed amount and cash for counting, recipient shares the payout code after counting, hand over cash and record it once. For the no-phone path, show recipient-controlled private PIN entry and the independent checker requirement explicitly. Opening authorization or privately entering the PIN is distinct from revealing the payout code. Do not copy a reference ordering that suggests counting only after sharing the payout code.

### Auditor

Update 2026-10-14: the maintainer approved reducing the Auditor to three destinations (Inspect, Records, Verify) with record pages reachable through Records and exceptions; see the [Auditor simplification design](../superpowers/specs/2026-10-14-auditor-simplification-design.md). This replaces the four Auditor destinations recorded in the sitemap.

Lead with **“Records needing inspection.”** Open each exception directly to its explanation, original evidence, relevant changes and current integrity result. Preserve filters when returning to the list.

Keep the workflow read-only. A flag is a reason to inspect, not a fraud finding. Show current proof results separately from submission history and earlier successful checks. Preserve logged access for sensitive evidence.

Use readable integrity rows with a glyph, record label, current check time or permitted action and explanation. Separate the status word from the Checked text in visible and accessible text; whitespace between JSX elements alone may not produce a word boundary. Include result chips for All, Verified, Does not match, Anchor absent, Chain unreachable, Evidence unavailable and Not checked. Checking and failed-refresh states stay explicit. If filtering is local, label its scope as records loaded/checked in this view; do not present bounded or unchecked data as global verified totals. Document any server data gap separately rather than silently extending the API.

Staff retain search, detailed tables and operational summaries as secondary tools. Prioritize actionable work on the initial dashboard without hiding important exceptions.

Choose and record the at-most-four phone destinations for each staff role before its shell changes. Keep every secondary section reachable and preserve record/queue context across list/detail layouts. Use segmented radio groups with arrow-key navigation and visible labels; a failing identity comparison uses an explicit stop/hold label and error tone, not color alone. Case flags use icons, explanations, permitted text actions and a divider. A Barangay Assisted registration floating action links to the existing flow and preserves assister recusal.

## 6. Visual hierarchy and accessibility

Use descriptive titles, short supporting text and one visually dominant action per task. Make help consistently available. Keep detailed explanations near the decision they support rather than repeating long guidance above every form.

Prioritize readable mobile text, generous touch targets, visible labels, keyboard operation, clear focus and text alongside status colors/icons. Check both Filipino and English for wrapping and overflow. Use descriptive controls instead of icon-only actions for essential tasks.

Keep synthetic-evaluation disclosures persistent and simulated-service labels attached to the relevant result. Explain integrity problems plainly while preserving the distinctions between pending, absent, mismatch, unreachable and unavailable evidence.

Build on the imported Material 3 roles (`--md-*`, `--st-*`), Sea and Sun light/dark schemes, existing fonts and logo. Keep glyph-and-word statuses and divider banners; use outlined empty-state cards without turning unavailable reads into friendly empty success. New components need at least 13px text, 44px phone touch targets and adequate contrast (4.5:1 for ordinary text, 3:1 for large text). Confirm dialogs trap focus, allow Escape before submission and return focus to their trigger. Use existing React/CSS and native elements; Material Web or another dependency requires separate approval.

## 7. Delivery sequence and completion criteria

All five phases were authorized and are implemented; the evidence and its limits are in [the execution checklist](screen-storytelling-progress.md) and [validation](validation.md). The beneficiary journey was validated before staff patterns were extended. Human checks (native Filipino review, five-participant comprehension, physical phones/tablets/camera) remain Pending and are not claimed.

### Phase 1 — Status and action mapping

Inspect `Dashboard.tsx`, `Payouts.tsx`, `Sessions.tsx`, `UI.tsx`, the current API projections and existing workflow-error guidance. Define each state's message, owner, safe action and record destination. Identify missing data explicitly.

Include `IntegrityStatus.tsx` in the state inventory and specify current versus historical proof/filter semantics. Treat the source README's verification-word-boundary failure as a reproduction target, not an assumed current test result. Do not start with the completion prompt's dialogs or navigation before the safe action mapping is defined.

Complete when the mapping covers the states in section 2, resolves conflicting states conservatively and has meaningful regression cases for unsafe or misleading next actions. Presentation rules must agree with the server's existing workflow rules.

### Phase 2 — Beneficiary dashboard and language

Update `workspaces.ts`, `Workspace.tsx`, `Dashboard.tsx`, `Language.tsx`, `Guidance.tsx` and relevant styles. Establish the shared vocabulary and reduce competing actions. Preserve existing route access and safe context handling.

Use the imported Tonal baseline rather than redoing theme/logo/font work. Deliver the four beneficiary destinations in the phone bottom bar and labelled desktop shell, an accurate Home focal action and distinct waiting/empty/unavailable states. Localize the essential shell controls as well as the dashboard, preserving saved theme and language choices.

Complete when the four primary destinations cover existing beneficiary capabilities, the dashboard has an accurate focal action, and essential dashboard/navigation controls work in both languages. Record translation-review status honestly.

### Phase 3 — Beneficiary task flows

Connect `Registry.tsx`, `Claims.tsx`, `Lists.tsx`, `Sessions.tsx`, `Payouts.tsx` and `Outcomes.tsx` through record-specific links and clear result states. Include waiting, declined, held, expired and interrupted flows.

Apply the reference's household layouts only after the corresponding record flow is connected. Include recipient-path segmented controls, code hide/expiry/PIN guidance, specific persistent saved results, optional snackbars and reusable accessible review/confirmation components for Phase 4. Keep amount basis and dated progress available without competing with the next action.

Complete when users can move from dashboard to the relevant task and back without reselecting the same record, losing valid input to a validation error or misunderstanding what was saved. Both own-device and assisted payout journeys must preserve existing safeguards.

### Phase 4 — Staff handoffs

Update role dashboards and their links into `Queue.tsx`, `Operations.tsx`, `Funds.tsx`, claim/session/payout screens and `Audit.tsx`. Separate immediate work from history and supporting totals.

Deliver staff phone destinations, labelled rails, appropriate list/detail panes, permitted floating actions, segmented decisions, consequential-record dialogs, flag banners, Disbursing tablet composition and Auditor integrity rows/filter chips. Reuse Phase 3 components and Phase 1 meanings. Keep human actions, role restrictions, logged evidence access and once-only cash recovery unchanged.

Complete when each role can open a relevant task, perform or inspect its permitted step, understand who acts next and return to the appropriate queue with context intact. Confirm visibility restrictions for each role.

### Phase 5 — Usability, regression checks and documentation

Use synthetic records on phone and desktop viewports. Run meaningful tests for changed behavior, frontend typecheck/build and the affected existing browser suites. Run backend or contract suites if those layers change. Record failures and unavailable checks rather than treating them as passes.

Check Filipino/English at 390px and 1440px in light/dark, plus behavior at the 760px/1024px shell transitions and on tablets. Verify bottom-bar clearance, dialog keyboard/focus/cancellation, segmented radio navigation, persistent feedback after snackbar dismissal, safe code hiding, filter scope and failed-refresh proof states. Retain the import's theme/device-preference and workflow-error regressions. Establish the current browser baseline instead of carrying forward the source README's historical failure count.

Update the sitemap, user flow, implementation ledger and validation report alongside the behavior they describe. Preserve historical ideation. Mark plan phases complete only with links to implementation and actual validation evidence.

Proposed acceptance targets:

- At least four of five representative participants explain the current status and next step within ten seconds without coaching. Treat this as a formative test, not a statistical claim about all users.
- A dashboard task opens the relevant record without requiring a second search.
- Essential beneficiary tasks are usable in Filipino without English-only controls.
- Waiting states identify the responsible role without inventing a completion date.
- Holds, stale appointments, expired codes and existing handovers never suggest an unsafe next action.
- Interrupted handover recovery never encourages a second payment.
- Confirmation restates the selected record and effect, cancellation sends no command, and confirmed saves remain readable after transient feedback disappears.
- Proof filters and rows distinguish current reads, earlier observations and unchecked/unavailable evidence without changing chain behavior.
- Existing role URLs/context and directory return work across rail, drawer, bottom navigation and list/detail transitions; no permitted capability becomes unreachable.
- Keyboard/mobile checks and meaningful changed-behavior regressions pass.

Start with Phase 1 and the beneficiary dashboard. Validate that journey before extending the interaction pattern to staff screens.

## Design references

- [W3C: Make the purpose of your page clear](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o1p01-clear-purpose/) supports descriptive headings and orientation.
- [GOV.UK: Complete multiple tasks](https://design-system.service.gov.uk/patterns/complete-multiple-tasks/) supports communicating task order and completion.
- [GOV.UK: Confirmation pages](https://design-system.service.gov.uk/patterns/confirmation-pages/) supports explaining the saved result and what happens next.

These references inform the interaction design; the repository's approved product requirements determine actual workflow behavior.
