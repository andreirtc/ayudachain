# Public landing page

Parent: [PR1: planning and UX backlog](https://github.com/andreirtc/ayudachain/pull/1).
Branch: BinkzBooze/ayudachain-02-public-landing.
PR base: BinkzBooze/ayudachain-project-overview-explainer.

## Scope

The public route / explains the relief-record problem, intended users, and next action without an API connection. One Explore demo link opens /dashboard. A fictional Soriano household receipt illustrates why comparing a record against its original proof matters. It is an illustration, not a live verification result.

Operational pages use the (operations) route group so navigation, demo controls, role context, and the existing footer appear only in the application. Batch, beneficiaries, distributions, and verify URLs stay the same. Dashboard navigation and the batch back link point to /dashboard; the brand link returns home.

The page labels synthetic data and simulated payments. Its disclosure explains that record integrity does not establish physical cash delivery and that workflows remain under development. It makes no current network or verification-success claims.

This bounded early UI task has no backend dependency. Backend consolidation and accounting/anchoring fixes remain prerequisites for operational UI changes that show authoritative data or outcomes.

## Applied design guidance

- [NN/g: Aesthetic and Minimalist Design](https://www.nngroup.com/articles/aesthetic-minimalist-design/): prioritize the headline, explanation, receipt example, and primary action; keep operational controls off the first view.
- [NN/g: Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/): use a native details disclosure for the receipt-proof explanation while keeping the demo label visible.
- [GOV.UK: Question pages](https://design-system.service.gov.uk/patterns/question-pages/): provide a clear heading and focused next step. Keep the four-step overview together because it explains one journey.

## Validation

2026-10-12 baseline: 9 contract tests and 8 backend tests pass. Separate frontend TypeScript checking passes before and after implementation. The first contract invocation used the repository root and reported HH1; rerunning from the contracts directory passed. The Windows Python runtime required execution outside the sandbox.

Responsive CSS uses a single-column hero and two-column journey on small screens. The page includes a skip link, semantic headings, an ordered journey, decorative icons hidden from assistive technology, a keyboard-native disclosure, and visible focus indicators. Browser visual/interactivity review and a first-look comprehension check remain pending because no in-app browser is available.

The existing build configuration ignores TypeScript errors; a separate TypeScript check is used. Removing that setting and correcting existing operational verification claims remain in TODO.md.

Production preview checks return HTTP 200 for /, /dashboard, /beneficiaries, /distributions, /verify, and /batch/RELIEF-2026-001. The landing response contains the new headline and excludes the operational pitch banner; application routes retain the operational banner.

The Next.js production build completed successfully and emitted all expected routes.
