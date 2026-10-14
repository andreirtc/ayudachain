---
name: AyudaChain MVP
description: A clear operational record of disaster cash assistance in one DSWD Field Office, set in Material 3 with the Sea and Sun palette.
colors:
  md-primary: "#2b5ea7"
  md-on-primary: "#ffffff"
  md-primary-container: "#d7e2ff"
  md-on-primary-container: "#001a41"
  md-secondary: "#565e71"
  md-secondary-container: "#dae2f9"
  md-on-secondary-container: "#131c2b"
  md-tertiary: "#7a5900"
  md-tertiary-container: "#ffdf9e"
  md-on-tertiary-container: "#261a00"
  md-surface: "#f9f9ff"
  md-surface-container-lowest: "#ffffff"
  md-surface-container-low: "#f3f3fa"
  md-surface-container: "#ededf4"
  md-surface-container-high: "#e7e8ee"
  md-surface-container-highest: "#e2e2e9"
  md-on-surface: "#191c20"
  md-on-surface-variant: "#44474f"
  md-outline: "#74777f"
  md-outline-variant: "#c4c6d0"
  md-error: "#ba1a1a"
  md-on-error: "#ffffff"
  md-error-container: "#ffdad6"
  md-on-error-container: "#410002"
  st-ok: "#1b6b3a"
  st-ok-container: "#c8ecd2"
  st-warn: "#7a4f00"
  st-warn-container: "#ffddb0"
  st-sim: "#6750a4"
typography:
  headline:
    fontFamily: '"Open Sans", Roboto, Arial, sans-serif'
    fontSize: "31px"
    fontWeight: 600
    lineHeight: 1.2
  title:
    fontFamily: '"Open Sans", Roboto, Arial, sans-serif'
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.35
  body:
    fontFamily: '"Open Sans", Roboto, Arial, sans-serif'
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  field:
    fontFamily: '"Open Sans", Roboto, Arial, sans-serif'
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: '"Open Sans", Roboto, Arial, sans-serif'
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.5
  button:
    fontFamily: '"Open Sans", Roboto, Arial, sans-serif'
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.5
  reference:
    fontFamily: '"Source Code Pro", ui-monospace, monospace'
    fontWeight: 500
rounded:
  field: "4px"
  chip: "8px"
  tonal-block: "12px"
  fieldset: "16px"
  button: "20px"
  panel: "24px"
  next-step: "28px"
  nav-indicator: "28px"
  circle: "50%"
components:
  button-primary:
    backgroundColor: "{colors.md-primary}"
    textColor: "{colors.md-on-primary}"
    typography: "{typography.button}"
    rounded: "{rounded.button}"
    padding: "8px 20px"
  button-secondary:
    backgroundColor: "transparent"
    borderColor: "{colors.md-outline}"
    textColor: "{colors.md-primary}"
    typography: "{typography.button}"
    rounded: "{rounded.button}"
    padding: "8px 20px"
  input:
    backgroundColor: "{colors.md-surface-container-lowest}"
    borderColor: "{colors.md-outline}"
    focusBorderColor: "{colors.md-primary}"
    textColor: "{colors.md-on-surface}"
    typography: "{typography.field}"
    rounded: "{rounded.field}"
  panel:
    backgroundColor: "{colors.md-surface-container-low}"
    textColor: "{colors.md-on-surface}"
    rounded: "{rounded.panel}"
    padding: "24px"
  navigation-drawer:
    backgroundColor: "{colors.md-surface-container-low}"
    textColor: "{colors.md-on-surface-variant}"
  navigation-active:
    backgroundColor: "{colors.md-secondary-container}"
    textColor: "{colors.md-on-secondary-container}"
    rounded: "{rounded.nav-indicator}"
  next-step:
    backgroundColor: "{colors.md-primary-container}"
    textColor: "{colors.md-on-primary-container}"
    rounded: "{rounded.next-step}"
  status-positive:
    textColor: "{colors.st-ok}"
  status-negative:
    textColor: "{colors.md-error}"
  status-attention:
    textColor: "{colors.st-warn}"
  status-neutral:
    textColor: "{colors.md-on-surface-variant}"
---

# Design System: AyudaChain MVP

## Overview

**Creative North Star: "Tonal public service"**

AyudaChain follows Material 3, the design language most Android phones in the Philippines already use, so households and field staff meet familiar controls. The Sea and Sun palette pairs a deep sea blue with a sun-gold tertiary colour. Surfaces are tonal rather than bordered or shadowed. The current task, its record and its permitted next step take priority over decoration.

This document records the implementation of `/mvp` and its five role workspaces as of 13 October 2026. Its sources are `frontend/app/mvp.css`, `frontend/app/layout.tsx`, `frontend/app/icon.svg`, `frontend/components/mvp/Logo.tsx` and `frontend/components/mvp/UI.tsx`. It does not define the retained legacy screens, apart from the shared favicon. `PRODUCT.md` supplies the durable commitments to truthful evidence, understandable states and household guidance.

**Key characteristics:**

- A tonal navigation drawer with a pill-shaped active indicator, and persistent account and disaster context.
- Pill-shaped buttons, Material 3 outlined fields and rounded tonal panels.
- Status shown as a glyph and a coloured word, never as a filled box or highlighted pill.
- Evidence first, with explicit unavailable and not-checked states.

## Logo

The mark is **Kubo Link**: a bahay kubo roof (the household) over two linked rings (the checkable record). `LogoMark` in `frontend/components/mvp/Logo.tsx` draws it in `currentColor`. It appears in primary blue beside the Open Sans Bold wordmark in the drawer and on the directory page. `frontend/app/icon.svg` is the favicon: the mark in on-primary-container ink on a primary-container tile. The logo is a concept that has not been registered. It uses no government seal, flag or agency mark.

## Colours

All colours are Material 3 role tokens declared on `.ac-entry,.ac-app` in `mvp.css`. Component rules refer to roles, not hex values. The legacy aliases `--ac-ink`, `--ac-muted`, `--ac-line`, `--ac-accent` and `--ac-ground` point to on-surface, on-surface-variant, outline-variant, primary and surface. Light and dark schemes are implemented. The dark scheme uses the Sea and Sun dark roles (primary `#acc7ff`, surface `#111318`, on-surface `#e2e2e9`, outline `#8e9099`) and dark status colours (success `#8cd8a1`, warning `#f2bc6a`, error `#ffb4ab`). A Light, Dark and System toggle (`ThemeToggle.tsx`) sits in the workspace top bar and the directory header. System follows `prefers-color-scheme`. An explicit choice sets `data-theme` on `<html>` and is remembered in the browser under `ayudachain:theme`. An inline script in `layout.tsx` applies it before first paint.

- **Primary** (sea blue) is used for filled buttons, links, text buttons, focus rings, the logo and completed journey steps. **Primary container** carries the household next-step card.
- **Secondary container** is the active navigation indicator, count chips, date blocks and directory icons.
- **Tertiary container** (sun gold) is used for avatars.
- **Surfaces** step from surface (page) through surface-container-low (drawer, panels) to surface-container-high (account panel).
- **Status colours** are shared and independent of the palette: success green, warning amber, error red and simulated violet. They are used only as text and glyph colour.

Contrast was checked with the WCAG formula. On-primary on primary is 6.4:1. On-surface-variant on surface is 8.9:1. Success, warning and error text on surface-container-low are each at least 5.8:1. The outline is 4.3:1 on surface, which meets the 3:1 requirement for component borders.

**The written state rule.** A state is always a glyph plus its name. A green business status is not a claim that chain integrity or physical receipt has been proved.

## Typography

Open Sans (400, 500, 600, 700) is the interface face. Source Code Pro (500, 600) is used for code, references and the payout code box. Both load through `next/font/google` in `frontend/app/layout.tsx`, exposed as `--font-open-sans` and `--font-source-code-pro`. Headings use weight 600 and sentence case. All numerals use tabular figures.

The minimum text size is 13px. Every 10px, 11px and 12px rule in `mvp.css` was raised to 13px. Form fields use 15px and buttons 14px.

## Layout

Layout is unchanged from the previous implementation. There is a fixed left drawer (238px; 260px from 1800px, 214px below 1200px), a topbar, a disaster context bar and a flexible main frame. At 760px and below, the drawer becomes an off-canvas modal drawer with rounded trailing corners and a shadow. Tables keep their own horizontal scroll. The directory remains a two-column page with a ruled list of the five workspaces.

## Shapes and depth

- **Fields** use 4px corners, following Material 3 outlined text fields.
- **Count chips** use 8px corners. **Date blocks and icon tiles** use 12px.
- **Fieldsets** use 16px corners. **Panels** use 24px. **The next-step card** uses 28px.
- **Buttons** are 40px tall with 20px pill corners. The navigation indicator is a full pill.

Panels have no border and no shadow; tone separates them from the page. Shadows are reserved for the account panel and the mobile drawer.

## Components

### Buttons

The filled primary button has on-primary text and darkens 10% on hover. The default button is outlined, with primary text and a transparent fill. Hover and press use 8% and 12% primary state layers. Disabled buttons use 0.45 opacity.

### Fields

Fields are outlined with a 1px outline. On focus, the outline thickens to 2px in primary. Labels use on-surface-variant. The file selector button is a secondary-container pill.

### Status

`Status` in `UI.tsx` has four tones, each with its own glyph:

- **Positive** uses a check: approved, published, active, received in full, open, verified, handover recorded, confirmed.
- **Negative** uses a cross: stopped, does not match, not received, chain unreachable, anchor absent, evidence unavailable.
- **Attention** uses an alert circle: held, declined, reversed, received less, stale.
- **Neutral** uses a clock: every other state.

The status has no fill, border or padding.

Integrity starts as "Not checked". "Verified" appears only after a current check returns a match.

### Messages

`mvp-error`, `mvp-warning` and `mvp-success` are banner rows on the page surface. Each has a circled glyph (×, ! or ✓) in the status colour, plain on-surface text and a divider underneath. They have no tinted box or coloured edge.

### Navigation

The AyudaChain logo and an "All workspaces" link at the foot of the drawer both go to the `/mvp` directory. Both sit outside the role navigation list, and neither switches role directly.

Drawer links are 14px semibold on-surface-variant text with line icons. Hover uses a state layer. The current page uses the secondary-container pill and `aria-current="page"`. Keyboard handling, focus trapping on mobile, Escape-to-close and the skip link are unchanged.

### Household journey

The next-step card uses primary-container, and its action is a filled pill button. Journey markers are filled primary when complete and primary-container with a primary ring when current.

### Motion and accessibility

Existing transitions are kept, and `prefers-reduced-motion` still removes them. The focus ring is 3px primary with a 2px offset. The source contains these mechanisms; this document does not claim a complete WCAG conformance audit.

## Do's and Don'ts

### Do:

- **Do** use role tokens (`--md-*`, `--st-*`) instead of hex values in component rules.
- **Do** pair each status colour with words and a glyph.
- **Do** keep one filled button per task area. Use outlined buttons for everything else.
- **Do** use Philippine peso formatting and Asia/Manila dates with tabular numerals.
- **Do** label simulated ID and SMS paths, and the selected, unverified synthetic account.

### Don't:

- **Don't** put status in tinted boxes, filled pills or coloured left edges.
- **Don't** show "Verified" from a saved submission state or an earlier check.
- **Don't** describe a review flag as fraud, or a recorded handover as proof of receipt.
- **Don't** invent records, transaction hashes or empty-state success evidence.
- **Don't** claim sign-in, authenticated identity, operational privacy or offline payout.

## Usability extension (12 October 2026)

Search and task queues use labelled, wrapping controls and bounded semantic tables. Barangay operations use aligned rows with scoped drill-down links, and aggregate-only cells are plain text. Duplicate review compares two permitted frozen versions alongside the acknowledgement and actions. The language selector controls complete step guidance, with an English fallback. CSV preview and camera or manual lookup remain task panels within Registry and payouts. Raw proof hashes expand beneath readable coverage and comparison. Mobile tables scroll within their panel, and controls keep visible focus and touch targets.
