---
name: AyudaChain MVP
description: A clear operational record of disaster cash assistance in one DSWD Field Office.
colors:
  ac-accent: "#146b61"
  action-hover: "#0d574e"
  ac-ink: "#19323f"
  ac-muted: "#5c6d76"
  ac-line: "#dce3e7"
  ac-ground: "#f4f7f8"
  white: "#ffffff"
  rail: "#17323f"
  rail-link: "#c6d8df"
  rail-hover: "#254551"
  rail-active: "#2b505b"
  surface-subtle: "#fafcfc"
  control-border: "#abbcc4"
  secondary-ink: "#244958"
  secondary-border: "#bdcbd1"
  secondary-hover: "#f0f5f5"
  focus: "#238b7e"
  positive-ink: "#23634c"
  positive-ground: "#edf6f0"
  positive-line: "#d6e8dc"
  attention-ink: "#8b5620"
  attention-ground: "#fff6e9"
  attention-line: "#efdebf"
  neutral-ink: "#5a6a75"
  neutral-ground: "#f0f3f5"
  neutral-line: "#e0e6ea"
typography:
  headline:
    fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif'
    fontSize: "31px"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "-0.8px"
  title:
    fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif'
    fontSize: "18px"
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: "-0.25px"
  task-title:
    fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif'
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.5
  body:
    fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif'
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  field:
    fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif'
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif'
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.55
  button:
    fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif'
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.5
  briefing:
    fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, Arial, sans-serif'
    fontSize: "25px"
    fontWeight: 620
    lineHeight: 1.3
    letterSpacing: "-0.5px"
rounded:
  tag: "4px"
  control: "5px"
  panel: "7px"
  popover: "8px"
  circle: "50%"
spacing:
  compact: "8px"
  control-gap: "12px"
  inline: "16px"
  form-gap: "17px"
  compact-panel: "20px"
  section-gap: "23px"
  panel: "24px"
  roomy: "28px"
  page-gutter: "36px"
components:
  button-primary:
    backgroundColor: "{colors.ac-accent}"
    textColor: "{colors.white}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
    textColor: "{colors.white}"
  button-secondary:
    backgroundColor: "{colors.white}"
    textColor: "{colors.secondary-ink}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  button-secondary-hover:
    backgroundColor: "{colors.secondary-hover}"
    textColor: "{colors.secondary-ink}"
  input:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ac-ink}"
    typography: "{typography.field}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
  panel:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ac-ink}"
    rounded: "{rounded.panel}"
    padding: "24px"
  navigation-link:
    backgroundColor: "{colors.rail}"
    textColor: "{colors.rail-link}"
    rounded: "{rounded.control}"
    padding: "12px 14px"
  navigation-active:
    backgroundColor: "{colors.rail-active}"
    textColor: "{colors.white}"
    rounded: "{rounded.control}"
    padding: "12px 14px"
  status-positive:
    backgroundColor: "{colors.positive-ground}"
    textColor: "{colors.positive-ink}"
    rounded: "{rounded.tag}"
    padding: "3px 8px"
  status-attention:
    backgroundColor: "{colors.attention-ground}"
    textColor: "{colors.attention-ink}"
    rounded: "{rounded.tag}"
    padding: "3px 8px"
  status-neutral:
    backgroundColor: "{colors.neutral-ground}"
    textColor: "{colors.neutral-ink}"
    rounded: "{rounded.tag}"
    padding: "3px 8px"
---

# Design System: AyudaChain MVP

## Overview

**Creative North Star: "The Public-Service Workdesk"**

AyudaChain uses a calm, practical interface for following disaster cash assistance. A stable navy rail frames white work surfaces; restrained teal identifies actions. The visual hierarchy gives the current task, its supporting record and its permitted next step priority over decoration.

This document records the implementation of `/mvp` and its five role workspaces as of 11 October 2026. Its sources are `frontend/app/mvp.css`, the directory route, `frontend/components/mvp/`, and the 1440px/390px confirmation captures in `.impeccable/review/final/`. It does not define the retained legacy screens. `PRODUCT.md` supplies the durable commitments to truthful evidence, understandable states and household guidance; surface composition remains in `.impeccable/surface-briefs/mvp.md`.

**Key Characteristics:**

- Stable navigation and persistent account/disaster context.
- Dense staff queues and a shorter, sequential household journey.
- White surfaces, fine dividers and restrained teal actions.
- Written states with consistent line icons.
- Evidence first, with explicit unavailable and not-checked states.

## Colors

The palette combines deep blue-green navigation with cool neutral surfaces. Semantic green, amber and gray communicate recorded states without becoming competing page accents. The frontmatter is the normative color reference.

### Primary

- **Service Teal** (`ac-accent`) marks primary buttons, text actions, selected form accents and key amounts. **Deep Service Teal** (`action-hover`) is the primary hover state.
- **Workdesk Navy** (`rail`) anchors the navigation. **Rail Hover** and **Rail Active** provide distinct tonal feedback; active links also use stronger text and `aria-current="page"`.

### Secondary

- **Recorded Green** (`positive-*`) accompanies explicit positive business states or a current matching integrity result.
- **Review Amber** (`attention-*`) marks holds, stops, adverse answers, mismatch and chain unavailability. It calls for attention; it does not allege fraud.
- **Pending Gray** (`neutral-*`) holds other states, including an unchecked integrity result.

### Neutral

- **Record Ink** (`ac-ink`) is the principal text color; **Context Slate** (`ac-muted`) carries supporting prose.
- **Cool Ground** (`ac-ground`) separates the work area from **White** panels and topbar.
- **Quiet Surface** (`surface-subtle`) provides a small tonal step for the context bar and hover rows.
- **Record Line** (`ac-line`) divides panels, queues and histories. Controls use the stronger `control-border`; secondary actions use their own ink and border tokens.

**The Written State Rule.** Color always accompanies a state name and, for status chips, a check, clock or alert icon. A green business status is not a claim that chain integrity or physical receipt has been proved.

## Typography

The shipped operational stack starts with Segoe UI, followed by platform and Arial fallbacks. Body text, fields and labels share that stack. No font asset is generated or loaded for `/mvp`.

The hierarchy favors sentence case and compact task reading. All numerals use tabular figures. Headings balance text; reference strings and supporting data wrap instead of widening the page.

### Hierarchy

- **Headline**: page titles use the frontmatter headline role; compact/mobile page headings reduce to 28px.
- **Title**: panel headings use the title role; mobile panels reduce to 17px.
- **Task title**: queue entries and subsection headings use the task-title role.
- **Body**: the base is the body role. Most panel paragraphs and input values use the 13px field size; table content is 12px.
- **Label**: field captions and button text are compact, semibold and sentence case.
- **Briefing**: the four-column operational strip uses the briefing role; it reduces to 22px below 1200px and is 23px in the mobile two-column strip.
- **Financial emphasis**: entitlement amounts and outcome totals use 36px; payout amounts use 32px. These are record values with their basis or unit adjacent, rather than a general display style.

The directory currently uses a larger system-font headline (64px desktop, 53px below 1000px, 46px mobile). This is an observed entry-page treatment, not a reusable display identity. The shipped 10–11px badge, table-header and metadata text is recorded as compact secondary detail, not a minimum size for future essential instructions.

**The Plain Task Rule.** Preserve clear size and weight steps, sentence case and direct labels. Do not add decorative eyebrows or a separate typographic voice above task headings.

## Layout

Desktop workspaces use a fixed left rail (238px), a 73px topbar, a separate disaster context bar and a flexible main frame. Main content is centered within a maximum 1560px frame with 36px horizontal gutters. Staff overview grids give the main queue more space than its supporting column; forms stop at 900px. The beneficiary overview stops at 1030px and uses a main journey beside entitlement and appointment evidence. The beneficiary next-action paragraph stops at 58ch.

The directory has a maximum 1200px frame, two unequal columns and a ruled list of five workspaces. These are links to dedicated URLs: `/mvp/beneficiary`, `/mvp/barangay-officer`, `/mvp/dswd-officer`, `/mvp/disbursing-officer` and `/mvp/auditor`. Account selection remains inside the chosen role. Workspace navigation links preserve the selected `account` and `disaster` query context. While the initial catalogue is loading, links retain the requested values from the current URL until the loaded records resolve the eligible account and disaster.

Spacing is measured for work rather than forced onto one mathematical scale. The recurring form gap is 17px, section/grid separation is commonly 23–24px, and normal panel padding is 24px. Below 1200px, page gutters become 25px and panel padding 21px. Reuse these existing roles rather than smoothing away the observed rhythm.

Responsive behavior follows the shipped media queries:

- At 1800px and above, the rail widens to 260px.
- At 1200px and below, the rail narrows to 214px and staff grids tighten.
- At 1000px and below, the main operational/audit grids and beneficiary main grid become one column; supporting panels can still form a two-column row.
- At 760px and below, the rail becomes a 254px off-canvas menu. The main frame fills the viewport, the topbar is 61px, content gutters are 20px, context selection wraps, page actions stack, forms and supporting panels become one column, and briefing totals become two columns.
- Mobile panels use 20px vertical and 17px horizontal padding. Tables retain a 470px minimum width inside their own horizontal scroll region; the page itself must fit the viewport.
- At the mobile breakpoint, buttons and text actions have a minimum 44px height. Input controls already have a 44px minimum height; the compact desktop disaster selector uses 36px.

## Elevation & Depth

Work surfaces are flat: white fill and one-pixel borders establish separation. There are no resting panel shadows. Soft shadows are reserved for a floating account panel, the mobile navigation drawer and the keyboard skip link.

### Shadow Vocabulary

- **Account panel**: `0 12px 28px #15313e18`.
- **Mobile drawer**: `8px 0 30px #18333f22`.
- **Skip link**: `0 3px 12px #19323f25`.

**The Flat Work Surface Rule.** Keep record panels and queue rows flat. Use elevation only for controls that float above the work area.

## Shapes

Controls and rail links have modest control corners; panels use slightly softer panel corners. Compact state chips use tag corners. Account panels use popover corners. Circular avatars, journey markers and numbered handover steps express people or sequence rather than turning every control into a pill.

Fine borders and horizontal rules carry most grouping. The AyudaChain shield mark has its existing rounded-bottom silhouette; ordinary panels do not inherit that brand shape.

## Components

### Buttons and links

Primary actions use service teal and white text; secondary buttons use white, a visible border and secondary ink. Both use 9px vertical and 14px horizontal padding, a 41px minimum desktop height, compact semibold text and an 8px icon gap. Hover changes color without lifting or scaling the control. Disabled buttons use 0.5 opacity and a not-allowed cursor.

Text actions use teal, a small arrow where helpful and an underline on hover with a 4px offset. Their minimum desktop height is 36px; mobile actions follow the 44px rule. The prominent page action is selected from the actual task state.

### Inputs and fields

Fields have white fill, a visible control border and 10px by 12px padding. Captions sit above them with a 7px gap. Textareas start at 96px and resize vertically. Search fields use a real label; placeholders supplement it. File selectors are subdued buttons inside a light field.

All focusable descendants receive a visible 3px teal outline with a 3px offset. The caret and native checked-control accent use service teal. Error, warning and saved-result messages use distinct tinted, bordered regions and explicit text; actions never rely on a tint alone.

### Status chips

The shared status component combines a named state, icon and lightly bordered semantic fill. Positive examples include "Approved" and "Handover recorded"; attention examples include "Held" and "Does not match"; pending examples include "Awaiting DSWD review". Chips use compact padding and tag corners. They are record labels, not interactive filters.

Integrity starts as "Not checked". "Check now" requests the current result; matching content is labelled "Verified" only after that request returns a match. Unreachable chain, missing anchor, unavailable evidence and failed refresh stay explicit. A previous match is accompanied by a warning that it does not establish the current result. Saved submission status is labelled as historical evidence.

### Panels, queues and tables

Panels use white fill, a fine border and flat depth. Their headings pair with a small contextual action or count where needed. Queue rows are separated by rules and lead from the work item to its permitted screen or supporting history.

Tables use sentence-case headers, subtle header fill, compact supporting identifiers and specific row actions. Long names and references wrap within the record cell. Empty queues explain the missing prerequisite or next expected event; failed requests offer retry. Loading text uses `role="status"` and never substitutes invented rows.

### Navigation and context

Rail links use existing Lucide line icons, written labels, hover feedback and an active tonal block. The shared icon helper hides decorative icons from assistive technology. The auditor context includes a written "Read-only" label.

Mobile navigation has a labelled trigger with `aria-expanded` and `aria-controls`, a labelled close action, initial focus on a navigation link, focus wrapping, Escape-to-close and focus return to the trigger. Closed mobile navigation is hidden from focus. A skip link targets a focusable main region.

The account disclosure states: "Synthetic accounts have no sign-in. Selected identities are unverified." Role routes and account selection organize workflow; they do not establish authentication or operational access control.

### Household journey and receipt guidance

The beneficiary overview leads with the next available action, followed by five named journey steps. A household that is already registered but has no claim receives "Submit my claim"; its household page hides the registration form. A thin connecting line joins circular complete, current and pending markers. Entitlement evidence shows the amount with its calculation basis; appointment evidence shows the Manila date and site. Private-report guidance stays adjacent to the household workflow.

The handover workspace uses three explicit steps: compare identity, present the amount, record authorization. Recipient confirmation remains separate from the recorded handover. The receipt code is a functional value, never decorative typography.

### Evidence and histories

Integrity records pair exact material/original actions with current checks. Supporting histories use a simple ruled timeline, readable actions, Manila timestamps and expandable actor/version details. Ordinary reading avoids raw JSON; exact verification material is available in an explicit disclosure.

The footer labels synthetic records and the simulated National ID/SMS paths. It also states that chain reads are actual and signatures are not authenticated. Connectivity loss produces a reconnection instruction; there is no offline payout capability.

### Motion and accessibility

Buttons transition colors in 150ms; directory and rail feedback use 160ms; the mobile drawer uses 180ms ease-out. Motion supports state changes and does not animate record evidence. `prefers-reduced-motion: reduce` removes transitions and animation.

Keep native links, buttons, labels, summaries, selects and tables. Status and error text remains readable independently of color. Live integrity feedback uses polite, atomic announcements. Selection, focus, caret and scrollbars follow the palette. The source contains these mechanisms; this document does not claim a complete WCAG conformance audit.

## Do's and Don'ts

### Do:

- **Do** use the existing operational palette, flat panels and visible control borders.
- **Do** pair each status color with explicit words and an appropriate line icon.
- **Do** select the next action from current API records and preserve account/disaster context in task links, including during initial catalogue loading.
- **Do** keep beneficiary instructions short and sequential, with the amount basis and appointment evidence close by.
- **Do** use Philippine peso formatting and Asia/Manila dates with tabular numerals.
- **Do** label simulated ID/SMS paths and the selected, unverified synthetic account.
- **Do** preserve keyboard focus, retry states, reduced motion and mobile 44px action targets.

### Don't:

- **Don't** show "Verified" from a saved submission state or an earlier successful check.
- **Don't** describe a review flag as fraud, or a recorded handover as proof of recipient-confirmed receipt.
- **Don't** invent records, transaction hashes or empty-state success evidence.
- **Don't** claim sign-in, authenticated identity, operational privacy or offline payout.
- **Don't** turn this scoped system into a redesign rule for retained legacy routes.
- **Don't** introduce generic role tabs, decorative metric cards or an additional icon vocabulary into these workspaces.

## Usability extension (12 October 2026)

Search/task queues use labelled wrapping controls and bounded semantic tables in the existing workdesk palette. Barangay operations use aligned rows with scoped drill-down links; aggregate-only cells are plain text. Duplicate review compares two permitted frozen versions alongside acknowledgment/actions. Language selection controls complete step guidance with a retained English fallback. CSV preview and camera/manual lookup remain task panels within Registry and payouts. Raw proof hashes are expandable beneath readable coverage and comparison. Mobile tables scroll within their panel; controls retain visible focus and touch targets.
