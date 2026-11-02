# Paano patakbuhin at i-demo

[Exact technical setup/commands at recovery details](../DEMO_RUNBOOK.md). Ito ang team-friendly guide. Huwag mag-reset ng database, mag-overwrite ng manifest o mag-restart ng surviving chain.

## Bago magsimula

Open `http://127.0.0.1:3000/mvp` sa development machine. Hindi ito public website. Hindi automatic na kasama ang running services kapag kinopya ang ZIP sa ibang laptop.

Piliin ang **Bagyong Luntian · Demo** at tamang demo account. Taglish ang default sa new browser. English is available sa Settings, o open `/mvp?lang=en`. Nakikita ang five roles sa welcome page. Demo navigation ito, hindi login.

Current state at verified results: [readiness](../FINALIST_READINESS.md). Private selected config path: `.runtime/finals/selected-lab-path.txt`. Huwag ipakita ang config contents sa projector o i-upload.

Current new rehearsal chain is on **8547**, database on **55432**, API on **8000**, frontend on **3000**. Nawala ang earlier in-memory chains on8545/8546; preserved ang old DB/manifests/evidence. Hindi recovery ng old deployment ang bagong chain. [Incident record](../LOCAL_CHAIN_INCIDENT.md).

## Three-minute demo gamit ang saved records

| Time | Ipakita | Sabihin |
|---|---|---|
| 0:00–0:25 | DSWD → Funding/Pondo → original release document | “May original document at human-confirmed fields. Recorded authority ito, hindi cash certification.” |
| 0:25–0:50 | DSWD → Review → household request at decision | “May barangay responses, flags at recorded human decision.” |
| 0:50–1:10 | DSWD → Lists → amount basis/current list | “May explanation ang amount at retained versions.” |
| 1:10–1:45 | Mamamayan → Resibo → Maria Santos · Demo | “Recorded once ang handover. Hindi natin uulitin ang payout para lang mag-demo.” |
| 1:45–2:10 | Recipient report o DSWD concern | “Hiwalay na statement ang report ng recipient.” |
| 2:10–3:00 | Auditor → Audit → handover record → I-check ngayon | “Actual fresh read ito sa local chain. Match means match ang committed evidence, hindi automatic proof ng cash delivery.” |

Kapag English ang interface, **Check now** ang button. Laging basahin ang actual result. Huwag sabihing verified habang loading, failed o unreachable.

## Kapag may failure sa stage

- **Hindi nag-load:** subukan ang normal refresh/retry. Huwag mag-clear/reset ng database.
- **Chain unavailable:** sabihin “Hindi available ang live chain check.” Ipakita ang labelled recorded video/screenshots; historical evidence lang iyon.
- **Uncertain payout response:** basahin muna ang same saved transaction/receipt. Huwag mag-abot ulit ng cash o gumawa ng second payout.
- **Walang camera:** type the manual reference. QR is optional and lookup only.
- **Walang internet:** walang offline payout. Staff must stop unsafe payment writes and restore connection. Local services on this laptop can work without public internet only while their own local dependencies remain reachable; that is not an offline field-payment feature.

## Full journey para sa rehearsal

Sa **new isolated reference-only lab** lang ito gawin. Preserve partial failures; create another lab instead of reset.

1. DSWD records funding original/confirmed fields and opens intake with basis document.
2. Register household, with optional phone at registration. Submit damage request.
3. Barangay staff respond; Punong submits selected threads with council resolution where applicable.
4. DSWD reviews current flags/evidence and records decision.
5. Enter documentary amount inputs, prepare list and wait for actual publication.
6. Schedule household/date/site/staff, then open the session.
7. Recipient authorizes; payer compares accepted photo ID. Review household/amount and record once.
8. Recipient submits full/less/no-receipt answer. Assisted route uses separate eligible checker.
9. Auditor opens evidence and runs actual check. Optional signer-free CLI uses authorized exact material/originals privately.

National ID/SMS/accelerated clock are simulations. No real citizen data, real cash o real government approval ang ipinapakita.

## Safe technical commands

Do not reinstall working dependencies. Check `package.json`, supported Node 22/24, `.venv`, listening ports at current ownership first. Exact new-lab deployment and PostgreSQL tool setup are in the [English runbook](../DEMO_RUNBOOK.md).

```bash
export MVP_CONFIG_FILE="$(cat .runtime/finals/selected-lab-path.txt)"
.venv/bin/python -m backend.scripts.local_mvp stop
.venv/bin/python -m backend.scripts.local_mvp serve
```

`stop` is for the owned app processes; keep the separately owned chain and PostgreSQL alive. Do not use broad `pkill`, port-based killing or reset commands. If a pinned deployment is lost, do not recreate it at the old manifest.

Browser journey command — **fresh lab only**, not the prepared stage lab:

```bash
MVP_BROWSER_FRESH_RUN=1 npm --prefix frontend run test:mvp -- tests/journey.spec.ts
npm --prefix frontend run test:mvp -- --grep-invert 'five roles use edited original-backed forms'
```

Stop owned app before production build so dev/build do not share `.next`. Existing build skips ESLint. Hindi test pass ang skipped check.

## Fallback files

[Video](../VIDEO.md) · [Actual screenshots](../SCREENSHOTS.md) · [Exact fresh evidence](../evidence/test-results.md). Recorded actual software on demo data ang video, hindi mockup. Hindi nito pinapatunayang healthy ang services ngayon.
