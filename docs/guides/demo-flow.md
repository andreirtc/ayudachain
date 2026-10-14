# Demo flow: one household, end to end

A single walk-through of the local MVP: one household's claim goes from barangay response to DSWD decision, amount, published list, cash handover, recipient answer and audit. It uses the fictional sample residents, so every person here is invented. Business changes go through the normal commands; National ID checks and notice SMS remain labelled simulations, chain reads are actual, and nothing here is real-household readiness.

Status: written from the current screen code and seeded data. The individual steps have backend test coverage, but this exact click path has not been verified end to end in a browser; wording of confirmation dialogs may differ slightly.

## Before you start

1. Start the stack as in [local operation](local-mvp.md), then load the sample data with a fresh namespace:

   ```powershell
   .venv/Scripts/python -m backend.scripts.reset_mvp --with-sample-households
   ```

   This retires the current run (history is retained) and seeds 10 households per barangay, residence approvals, open intake and sample claim responses. Restart the API afterwards so it uses the new deployment. Do not run the Playwright journey spec before a demo; it resets the run and removes this data.

2. Make three small PDFs to upload (any PDF or PNG works; these are synthetic):

   ```powershell
   .venv/Scripts/python -c "from pathlib import Path; from backend.scripts.synthetic_evidence import synthetic_pdf as p; d=Path('.runtime/demo-files'); d.mkdir(parents=True,exist_ok=True); [(d/n).write_bytes(p(t)) for n,t in {'1-council-resolution-silong.pdf':'COUNCIL RESOLUTION\nSynthetic demo resolution of the Silong barangay council.','2-wage-basis.pdf':'WAGE BASIS\nSynthetic documented daily wage PHP 435.','3-partially-damaged-days.pdf':'CATEGORY DAYS\nSynthetic documented days for Partially damaged: 10.'}.items()]"
   ```

   Uploads start as soon as a file is chosen and report "Original saved; digital signature not validated."

3. Open http://127.0.0.1:3000/mvp and choose a role. To change account inside a role, use the account menu at the top right and its **Account** dropdown. There is no sign-in. Account links of the form `/mvp/<role>?account=<id>` open a specific account, but account ids change on every reset; read them from `/api/v1/actors/catalogue`.

## Accounts

| Role | Account | Used for |
|---|---|---|
| Barangay Officer, Barangay Secretary (Silong) | Felicidad Ramos | residence approval; she has already endorsed Teodoro's claim |
| Barangay Officer, Punong Barangay (Silong) | Eduardo Salazar | second endorsement and sending the claim to DSWD |
| DSWD Officer | Lourdes Villanueva | decision, amount, publication, sessions |
| Disbursing Officer | Benito Castillo | payer; handover |
| Disbursing Officer | Dolores Mercado | second assigned cash officer |
| Disbursing Officer | Arnel Soriano | independent checker |
| Beneficiary | Teodoro Mendoza | recipient: code and private answer |
| Auditor | Carmela Aquino | inspection and verification |

The Barangay dropdown lists names and positions but not the barangay. Confirm the sidebar label reads Silong. Spare accounts: Ricardo Navarro (DSWD), Victor Estrada (Auditor), and Nestor Ocampo and Gloria Tolentino (Sapa).

## The flow

The household is Teodoro Mendoza, Purok 1, Calle Rizal, Silong. His claim (Partially damaged, flooded ground floor) is waiting for the barangay with one endorsement from Felicidad Ramos.

1. **Residence approval** (Felicidad Ramos, **Households**)
   1. Click the **Lorna Fernandez** row. Her registration opens below the table.
   2. Type a basis in **Basis for approving residence**, click **Approve residence**, then confirm.
   3. Switch to Eduardo Salazar and open the same row. He cannot approve it, because he helped register that household.

2. **Barangay response and batch** (Eduardo Salazar, **Claim responses**)
   1. Click the **Teodoro Mendoza** row.
   2. Choose **Endorse**, tick the residence-and-affectedness attestation, click **Append response**, then **Record response**.
   3. Tick the **Send to DSWD** box on Teodoro's row, upload `1-council-resolution-silong.pdf` under **Council resolution original**, and click **Submit selected claims**.
   4. Teodoro's claim moves to History as "Awaiting DSWD review".

3. **DSWD decision** (Lourdes Villanueva, **Claim review**)
   1. Under **Household to review**, pick **Teodoro Mendoza** and read the flags. A flag is a reason to look, not a fraud finding.
   2. Choose **Approve**, set **Final category** to **Partially damaged**, enter a **Decision reason**, and tick "I reviewed this current check…".
   3. Click **Save human decision**, then **Record decision**.

4. **Amount** (Lourdes Villanueva, **Amounts & approved lists**)
   1. Open **Record an amount basis**, mode wage formula.
   2. **Documented daily wage (PHP)** `435`; upload `2-wage-basis.pdf` as **Wage basis original**.
   3. Under **Partially damaged**, **Documented days** `10`; upload `3-partially-damaged-days.pdf`.
   4. Click **Save immutable input version**. Teodoro's entitlement should read ₱3,300 (75% of 435 rounded up to ₱330, times 10 days).

5. **Publish the list** (Lourdes Villanueva, same page)
   1. Under **Publish an approved list**, pick **Silong**, click **Prepare list for publication**, then **Prepare publication request**.
   2. Click **Refresh publication** until the list shows Published. It waits for the actual chain anchor, so allow up to about 40 seconds.
   3. As Eduardo Salazar, open **Approved list**: Teodoro appears with name, zone and category and no amount.

6. **Schedule and open** (Lourdes Villanueva, **Payout sessions**)
   1. Under **Schedule a payout session**, pick the published list under **Current published list** and tick **Teodoro** under payable members.
   2. Set **Session Manila date** to today's date and **Site** to `Silong Barangay Hall`.
   3. Tick two **Cash staff** (Benito Castillo, Dolores Mercado) and one **Independent follow-up staff** (Arnel Soriano).
   4. Click **Schedule selected members**, then **Open today’s cash session**.

7. **Recipient code** (Teodoro Mendoza, **Authorization & receipt**)
   1. Leave **Recipient path** on **Own device** and click **Open payout authorization**.
   2. Click **Reveal code in this view** and note the one-time code. Keep the page open; the code expires in ten minutes and is shown once.

8. **Cash handover** (Benito Castillo, **Cash handover**)
   1. Select Teodoro's transaction and click **Open household head photo**.
   2. Under **Compare person and accepted photo ID**, set the result to pass, enter an **Accepted photo ID type** (for example "Driver's license"), tick "I compared the person with the accepted photo ID", and click **Save ID comparison**.
   3. Enter the code in **Recipient payout code** and choose Arnel Soriano under **Independent assigned checker**.
   4. Click **Record cash handover** and confirm. Record it once; after a lost response, read the saved receipt before retrying.

9. **Close the session** (Lourdes Villanueva, **Payout sessions**): click **Close cash session**.

10. **Recipient answer** (Teodoro Mendoza, **Private reports**)
    1. Under **Recipient’s private answer**, choose **Received the full amount**.
    2. Click **Save private receipt answer**.

11. **Audit** (Carmela Aquino, Auditor)
    1. Open **Verify**, find the proofs and click **Check now**. A match shows the saved content is unchanged; it does not prove the original was genuine or that cash reached the household.
    2. Open **Inspect** and **Records** to read the append-only histories. Auditor inspections write only to the private access log.

## Notes

- Step order matters: the session cannot open until a list is published, the amount is recorded and the session date is today (Manila time); the code in step 7 needs the open session.
- Approving only Teodoro's claim keeps the published list to one household. Other sample claims stay with the barangay or DSWD, so you can approve more for a longer list.
- The same flow can start earlier or branch: **Households** also lets an independent officer approve the other pending assisted registrations (Bernardo Torres in Silong; Maribel Galang and Domingo Tabora in Sapa, by a Sapa officer); a not-endorsed claim shows the split-response case (Efren Castillo, Imelda Navarro).
- The older [repeatable evaluation procedure](demo-script.md) covers the wider range of paths, including assisted payouts and fallback snapshots.
