# AyudaChain — ito muna ang basahin

Ito ang natural Taglish reading pack para sa team. Familiar English terms ang gamit natin kapag mas malinaw: request, review, payout, records, database at blockchain. Hindi ito bagong product specification. Pareho ang facts at limitations sa detailed English guides.

**Need SDGs for slides?** Read [SDG alignment and spoken answers](SDG_ALIGNMENT.md). Main:SDG16; supporting:SDG1/10.

## Kung 15 minutes lang ang meron ka

1. Basahin ang explanation sa ibaba, tapos [PROJECT_EXPLAINED](PROJECT_EXPLAINED.md).
2. Aralin ang five-minute sheet at top-20 sa [JUDGES_QA](JUDGES_QA.md).
3. Sundan ang [DEMO_RUNBOOK](DEMO_RUNBOOK.md) para hindi maligaw sa demo.
4. Basahin nang malakas ang [PITCH_SCRIPT](PITCH_SCRIPT.md).
5. I-check ang [FINALIST_READINESS](FINALIST_READINESS.md) bago magbanggit ng test results.

Para sa slides: [PITCH_SLIDE_CORRECTIONS](PITCH_SLIDE_CORRECTIONS.md). Para sa branches at PRs: [GITHUB_TRIAGE](GITHUB_TRIAGE.md). [Detailed English reading pack](../START_HERE.md).

## Ano ba talaga ang AyudaChain?

“AyudaChain connects the records behind disaster cash assistance. Makikita ang funding document, household request, human decision, calculation ng amount, recorded payout at report ng recipient. May fingerprint ang selected records sa blockchain para ma-check kung match pa ang saved evidence.”

Hindi app ang nagbibigay ng cash. Tao pa rin ang nagre-review at nag-aabot. Hindi rin proof ng honesty ang blockchain. Ang chine-check nito: pareho pa ba ang committed content at chain record?

## Isang simpleng kuwento

Si **Maria Santos · Demo** ay fictional beneficiary. May damage ang bahay niya sa **Bagyong Luntian · Demo**. Na-register ang pamilya, nag-submit ng request at may barangay responses. Nag-review ang DSWD at nag-record ng decision. May documented inputs para ma-explain ang amount. Inilagay siya sa approved list at payout schedule. Sa venue, kinumpara ang person at accepted photo ID, may authorization, at isang beses ni-record ang handover. Pagkatapos, hiwalay na sinabi ng recipient kung buo, kulang o walang natanggap. Puwedeng buksan ng Auditor ang evidence at mag-check sa actual local blockchain.

Demo names, documents at amounts lang ito. Walang real cash transfer o actual citizen data.

## Tatlong bagay na huwag pagsamahin

| Nakita mo | Ibig sabihin | Hindi nito automatic na napapatunayan |
|---|---|---|
| Recorded payout | May officer na nag-record ng handover | Na physically natanggap ang tamang cash |
| Recipient report | Ito ang sinabi ng recipient | Na independently proven na ang statement |
| Match sa blockchain | Match ang committed evidence sa actual chain read | Na genuine ang document, valid ang identity o totoong naiabot ang cash |

## Bakit limang roles?

- **Mamamayan:** mag-submit ng household information, tingnan ang status/amount/schedule, mag-authorize at mag-report.
- **Barangay Officer:** tumulong sa registration at magbigay ng local response tungkol sa tirahan at epekto ng sakuna.
- **DSWD Officer:** mag-review, mag-record ng funding at amount basis, maghanda ng listahan at schedule.
- **Disbursing Officer:** i-check ang identity at i-record ang authorized cash handover. Puwede siyang DSWD employee; ibang responsibility lang ang pagbabayad kaysa approval.
- **Auditor:** tingnan ang documents, history at exceptions, tapos mag-check ng integrity. Generic reviewer role ito; walang COA integration o official audit certification.

Sa prototype, selectable demo actors ang mga ito. **Wala pang secure sign-in. Puwedeng magpanggap bilang ibang active actor.** Kaya demo records lang ang puwedeng gamitin.

## Ano ang sasabihin kapag may hindi pa implemented?

“Ito ang actual na gumagana locally. Ito ang simulation. Ito ang next requirement bago real citizens.” Mas defensible ito kaysa sabihing complete ang system tapos hindi maipakita.

Actual local uploads, database records, calculations, handover rules at chain reads ang core workflow. **Simulated** ang National ID check, SMS at accelerated demo clock. **Pending** ang authentication, production security/governance at official procedure mapping. **Walang offline payout.**

## Bakit may daily wage?

Reference iyon sa amount calculation, hindi sweldo ni Maria. May DSWD ECT explanation na gumagamit ng regional minimum daily wage at assessed days. Ang demo inputs natin ay invented at hindi current official benefit rate. Sa UI, **Halaga ng ayuda** muna ang kita; optional ang **Paano kinuwenta?**

## Kung kinakabahan sa Q&A

Sagutin muna ang direct question sa isang sentence. Magdagdag ng isang concrete example. Sabihin ang limit kapag relevant. Huwag mag-imbento ng customers, endorsements, savings, gas prices o security guarantees. Nasa [Q&A](JUDGES_QA.md) ang complete reviewer.
