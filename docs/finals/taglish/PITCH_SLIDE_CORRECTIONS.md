# Ano ang babaguhin sa19slides?

Hindi na natin ia-access ang Canva, per team instruction. Recommended sequence ito; hindi claimed na inspected ang actual original19slides. [Detailed English correction guide](../PITCH_SLIDE_CORRECTIONS.md). Existing “Under the hood” screenshot was supplied and reviewed; corrections for that specific slide are below.

| Slide | Main point / replacement copy | Visual |
|---|---|---|
| 1 | **AyudaChain — A checkable trail for disaster cash assistance** | Recreated shield/link logo; no government seal |
| 2 | Bakit included? Bakit itong amount? Ano ang payout record? Ano ang recipient report? | One fictional household and four questions |
| 3 | Funding → Request → Human decision → Amount → Payout → Report → Check | One readable flow |
| 4 | Mamamayan, Barangay, DSWD, Disbursing, Auditor | One responsibility per role |
| 5 | Original document → Review fields → Human confirmation | Actual funding crop |
| 6 | **Flags support review. Humans decide.** | Actual claim/review crop; remove AI approval claims |
| 7 | **Synthetic example:**₱435×75%, rounded to₱330×15days=₱4,950 | Arithmetic; not current official benefit rate |
| 8 | Saved list≠published list; matching chain confirmation required | Actual list/version |
| 9 | Date/site, named members/staff, assigned session | Actual session; SMS simulated |
| 10 | Compare ID → Count fixed cash → Authorize → Review → Record once | Genuine handover screen, hide codes |
| 11 | Optional QR, manual lookup, assisted access | Phone crop; connected staff device required |
| 12 | Full / less / not received are separate recipient reports | Actual private concern/outcome |
| 13 | Private database/files → selected fingerprint → chain → fresh comparison | Architecture; label now versus planned |
| 14 | Match checks committed content; not authenticity/cash proof | Actual current check with timestamp |
| 15 | Show exact completed tests and scope | Use current readiness, not “all tests pass” badge |
| 16 | Synthetic evaluation now; auth/privacy/rule/governance gates before real data | Readiness steps, no fake certification |
| 17 | Supervised validation → hardening → authorized bounded pilot | No invented dates/adoption count |
| 18 | Institutional implementation/training/support; no citizen fee | Cost categories; finance assumptions labelled hypothetical |
| 19 | **Every verified result must mean a real comparison.** | Ask for workflow-validation partner |

## Exact correction: “UNDER THE HOOD” screenshot

| Current card | Replace with |
|---|---|
| Frontend: Next.js React PWA | **Next.js · React · Responsive web interface** |
| Backend: FastAPI | **FastAPI (Python) · PostgreSQL · Off-chain document storage** |
| Blockchain: local EVM / Polygon testnet | **Solidity · Hardhat · ethers.js · Local EVM prototype** |
| AI Models: Random Forest / Isolation Forest | Rename **Review Checks** — **Rule-based duplicate/anomaly flags · Human decisions** |
| Access Control: Supabase Auth | Rename **Role Workflows** — **Five selectable demo roles · Authentication pending** |

Footer: **Local prototype · Synthetic records · National ID and SMS simulated.** PWA install/offline behavior, public Polygon deployment, learned fraud models and Supabase Auth are not demonstrated here.

## Paano ilalagay ang deployment plan?

Separate row o backup slide labelled **Proposed deployment**: hosted Next.js/FastAPI/worker; managed or agency-hosted PostgreSQL; private object storage with authorized retrieval/backups; institutional sign-in/RBAC; monitored pinned-chain infrastructure after approved network/governance decision. PostgreSQL is suitable beyond localhost. S3-compatible storage is a proposed option, not integrated today. Supabase Auth can be named only as a proposed option if the team chooses it.

Huwag paghaluin ang implemented prototype at future plan sa same unlabelled technology list. [PostgreSQL](https://www.postgresql.org/about/), [S3 public-access controls](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).

## Claims na dapat tanggalin kahit saang slide

“Fraud-proof,” “blockchain proves cash delivery,” “secure real-user login,” “official government-compliant/endorsed,” “offline payout,” “real SMS/National ID,” “guaranteed savings” at unsupported public-network claims. Replace with actual mechanism and relevant limit. Current candidate does not include PR39 authentication.

Use actual screenshots labelled **Actual local application · Synthetic records ·14Oct2026**. Label mockups as proposed illustrations. One readable crop per task, hindi buong desktop na sobrang liit. New logo is a vector recreation of the supplied mark, not a government certification badge.
