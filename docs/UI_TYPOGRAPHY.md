# Typography direction

The user rejected the previous system-font treatment on 2026-10-13. The blue/slate palette remains the working brand direction. This bounded typography change precedes payout, receipt, verification and remaining UI polish, each in its own stacked PR.

Use Manrope for headings and the wordmark, Source Sans 3 for forms, explanatory copy and records, and monospace only for expanded technical evidence. Headings use restrained weights and readable spacing. The landing headline has less compressed tracking and a calmer scale. Body copy uses tabular figures for aligned amounts.

The pairing is a design choice for a civic relief prototype, not a claim that one typeface guarantees comprehension. [Manrope's official repository](https://github.com/googlefonts/manrope) describes its geometric sans design and peso/Filipino character coverage. [Adobe Source Sans](https://github.com/adobe-fonts/source-sans) is designed for UI environments. The two official variable WOFF2 assets are vendored under `frontend/app/fonts`, with their OFL licenses. Next's local font loader serves them from the app; no runtime Google Fonts request or build-time font download is needed. Together the font files are about 224 KB before HTTP compression.

Research also reviewed [Anthropic's frontend-design guidance](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md), listed on [skills.sh](https://skills.sh/anthropics/skills/frontend-design). Its emphasis on deliberate typography, clear hierarchy and restrained content informed this work. No global skill package or new project dependency was installed.

Validation on 2026-10-13: independent TypeScript, production build and diff check passed. All 26 established Edge desktop/phone journeys passed; the two new typography cases passed after normalizing quoted CSS family names in the assertion. The checks verify that both local font faces load, entry screens fit, and all font requests stay on the application's origin even when external font services are blocked. Landing and sign-in screenshots were inspected. Automated checks and screenshot inspection do not establish preference or new-viewer comprehension.
