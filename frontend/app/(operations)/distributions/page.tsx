"use client";

import React, { Suspense, useEffect, useRef, useState } from "react";
import { formatRecordedDate } from "@/lib/recordedDate";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { RefreshCw } from "lucide-react";
import {
  fetchDistributions,
  fetchPayoutDesk,
  PayoutDeskCheck,
  fetchBeneficiaries,
  fetchBatches,
  fetchBatchDetail,
  Allocation,
  confirmDistribution,
  DistributionConfirmPayload,
  Distribution,
  Beneficiary,
  ReliefBatch,
  apiUrl,
  formatPeso,
} from "@/lib/api";
import { useChainStatus, chainLabel } from "@/lib/useChainStatus";
import { useRole } from "@/lib/roleContext";
import { receiptVerificationHref } from "@/lib/receiptNavigation";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { submitOnlinePayout } from "@/lib/payoutConnection";
import { recoverPayoutAnchor } from "@/lib/api";
import PayoutAnchorStatus from "@/components/PayoutAnchorStatus";
import RegistryDialog from "@/components/RegistryDialog";
import ReceiptDetails from "@/components/ReceiptDetails";

function DistributionsContent({ requestedId }: { requestedId: string | null }) {
  const router = useRouter();
  const chain = useChainStatus();
  const { role, account } = useRole();
  const browserOnline = useBrowserOnline();
  const [distributions, setDistributions] = useState<Distribution[]>([]);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [batches, setBatches] = useState<ReliefBatch[]>([]);
  const [allocations, setAllocations] = useState<Allocation[]>([]);
  const loadVersion = useRef(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // New Distribution Form State
  const [selectedBenId, setSelectedBenId] = useState(requestedId ?? "");
  const [amountStr, setAmountStr] = useState("");
  const numericAmount = parseFloat(amountStr) || 0;
  const selectedReceipt = "sample_relief_receipt.svg";
  const [step, setStep] = useState<"IDLE" | "SUBMITTING" | "SUCCESS">("IDLE");
  const submitting = useRef(false);
  const pendingSubmission = useRef<{
    key: string;
    payload: DistributionConfirmPayload;
    serialized: string;
  } | null>(null);
  const [desk, setDesk] = useState<{ key:string; result:PayoutDeskCheck|null; error:string|null } | null>(null);
  const deskKey = selectedBenId + ':' + amountStr;
  const deskCurrent = desk?.key === deskKey ? desk : null;
  useEffect(() => {
    let active = true;
    if (role !== 'DISBURSING' || !selectedBenId || !/^\d+(?:\.\d{1,2})?$/.test(amountStr) || Number(amountStr) <= 0 || loading || loadError || !browserOnline) { setDesk(null); return; }
    setDesk(null);
    const timer = setTimeout(() => {
      fetchPayoutDesk(selectedBenId, amountStr).then(result => { if(active) setDesk({key:deskKey,result,error:null}); }).catch(e => { if(active) setDesk({key:deskKey,result:null,error:e instanceof Error ? e.message : 'Payout checks unavailable.'}); });
    }, 180);
    return () => { active = false; clearTimeout(timer); };
  }, [deskKey, role, account?.id, loading, loadError, browserOnline]);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [confirmedResult, setConfirmedResult] = useState<Distribution | null>(
    null,
  );
  const [previewReceipt, setPreviewReceipt] = useState<Distribution | null>(
    null,
  );
  const recovering = useRef(false);
  const [anchorBusy, setAnchorBusy] = useState(false);
  const [anchorError, setAnchorError] = useState<{
    id: string;
    message: string;
  } | null>(null);

  const recoverAnchor = async (id: string) => {
    if (recovering.current || role !== "DISBURSING") return;
    recovering.current = true;
    setAnchorBusy(true);
    setAnchorError(null);
    try {
      const result = await submitOnlinePayout(navigator.onLine, () =>
        recoverPayoutAnchor(id),
      );
      setDistributions((rows) =>
        rows.map((row) => (row.distribution_id === id ? result : row)),
      );
      setConfirmedResult((current) =>
        current?.distribution_id === id ? result : current,
      );
    } catch (e) {
      setAnchorError({
        id,
        message: e instanceof Error ? e.message : "Recovery failed. Try again.",
      });
    } finally {
      recovering.current = false;
      setAnchorBusy(false);
    }
  };

  const loadData = async () => {
    const version = ++loadVersion.current;
    setLoading(true);
    setLoadError(null);
    try {
      const [dList, bList, batchList] = await Promise.all([
        fetchDistributions(),
        fetchBeneficiaries({ include_historical: true }),
        fetchBatches(),
      ]);
      const details =
        role === "DISBURSING"
          ? await Promise.all(
              batchList.map((batch) => fetchBatchDetail(batch.batch_id)),
            )
          : [];
      if (version !== loadVersion.current) return;
      setDistributions(dList);
      setBeneficiaries(bList);
      setBatches(batchList);
      setAllocations(details.flatMap((detail) => detail.allocations));
      setSelectedBenId((current) =>
        bList.some((b) => b.beneficiary_id === current) ? current : "",
      );
    } catch (err) {
      if (version === loadVersion.current)
        setLoadError(
          err instanceof Error
            ? err.message
            : "Payout records could not be loaded.",
        );
    } finally {
      if (version === loadVersion.current) setLoading(false);
    }
  };
  useEffect(() => {
    void loadData();
    return () => {
      loadVersion.current++;
    };
  }, [account?.id]);

  const handleDisburse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBenId || submitting.current) return;
    if (role !== "DISBURSING" || loading || loadError || blockedReason || !deskCurrent?.result?.can_record) {
      setSubmitError(
        "Sign in as a disbursing officer and refresh the household records before recording a payout.",
      );
      return;
    }

    submitting.current = true;
    setSubmitError(null);
    setConfirmedResult(null);
    setStep("SUBMITTING");
    try {
      const payload: DistributionConfirmPayload = {
        beneficiary_id: selectedBenId,
        batch_id: selectedBeneficiaryObj?.batch_id || "",
        amount: numericAmount,
        receipt_filename: selectedReceipt,
      };
      const serialized = JSON.stringify(payload);
      if (pendingSubmission.current?.serialized !== serialized) {
        const bytes = crypto.getRandomValues(new Uint8Array(16));
        const key =
          "payout-" +
          Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join(
            "",
          );
        pendingSubmission.current = { key, payload, serialized };
      }
      const request = pendingSubmission.current;
      const result = await submitOnlinePayout(navigator.onLine, () =>
        confirmDistribution(request.payload, request.key),
      );
      setConfirmedResult(result);
      setStep("SUCCESS");
      await loadData();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : String(err));
      setStep("IDLE");
    } finally {
      submitting.current = false;
    }
  };

  const selectedBeneficiaryObj = beneficiaries.find(
    (b) => b.beneficiary_id === selectedBenId,
  );
  const requestedHousehold = beneficiaries.find(
    (b) => b.beneficiary_id === requestedId,
  );
  const householdUnavailable = requestedId !== null && !requestedHousehold;
  const selectedBatch = batches.find(
    (b) => b.batch_id === selectedBeneficiaryObj?.batch_id,
  );
  const selectedIsApproved =
    selectedBeneficiaryObj?.verification_status === "VERIFIED" &&
    selectedBeneficiaryObj?.review_status === "APPROVED";
  const standardGrant = selectedBatch?.standard_grant ?? 0;
  const maxGrant = selectedBatch?.max_grant ?? 0;

  // Start each household at its batch's standard grant
  useEffect(() => {
    if (selectedBatch) setAmountStr(String(selectedBatch.standard_grant));
  }, [selectedBenId, selectedBatch?.batch_id]);

  const existingPayout = distributions.find(
    (d) =>
      d.beneficiary_id === selectedBenId &&
      d.batch_id === selectedBatch?.batch_id,
  );
  const allocation = allocations.find(
    (a) =>
      a.batch_id === selectedBatch?.batch_id &&
      a.barangay_id === selectedBeneficiaryObj?.barangay_id,
  );
  const spentCentavos = allocation
    ? distributions
        .filter((d) => d.allocation_id === allocation.allocation_id)
        .reduce(
          (sum, d) => sum + (d.amount_centavos ?? Math.round(d.amount * 100)),
          0,
        )
    : 0;
  const remainingCentavos = allocation
    ? (allocation.amount_centavos ?? Math.round(allocation.amount * 100)) -
      spentCentavos
    : 0;
  const amountValid =
    /^\d+(?:\.\d{1,2})?$/.test(amountStr) && numericAmount > 0;
  const blockedReason = !selectedBeneficiaryObj
    ? "Choose a household to begin."
    : selectedBeneficiaryObj.record_status !== "ACTIVE"
      ? "This retained duplicate cannot receive a new payout. Its earlier records remain available."
      : existingPayout
        ? "A payout is already recorded for this household in this batch."
        : !selectedIsApproved
          ? "This household needs DSWD approval before payout."
          : !selectedBatch || selectedBatch.status !== "ACTIVE"
            ? "This household's relief batch is not active."
            : !allocation
              ? "No allocation is recorded for this barangay and batch."
              : !amountValid
                ? "Enter a positive amount with up to two decimal places."
                : numericAmount > maxGrant
                  ? "The amount exceeds this batch's maximum grant."
                  : Math.round(numericAmount * 100) > remainingCentavos
                    ? "The amount exceeds the remaining recorded allocation."
                    : null;
  const query = searchTerm.trim().toLowerCase();
  const filteredPayouts = distributions.filter(
    (d) =>
      (requestedId === null ||
        (!householdUnavailable && d.beneficiary_id === requestedId)) &&
      [
        d.distribution_id,
        d.beneficiary_id,
        beneficiaries.find((b) => b.beneficiary_id === d.beneficiary_id)
          ?.household_name,
      ].some((value) => value?.toLowerCase().includes(query)),
  );
  const deskBlock=blockedReason||deskCurrent?.error||deskCurrent?.result?.checks.find(c=>!c.passed)?.message;
  function resetEntry(){if(requestedId!==null){router.replace('/distributions',{scroll:false});return;}setConfirmedResult(null);setStep('IDLE');setSelectedBenId('');setAmountStr('');setSubmitError(null);pendingSubmission.current=null;}
  return <div className="registry workflow payout-workspace space-y-6">
    <header className="registry-header"><div><p className="registry-eyebrow">{role==='DISBURSING'?'Payout desk':'Recorded assistance'}</p><h1 id="payout-heading" tabIndex={-1}>{role==='DISBURSING'?'Record a demo payout':role==='BENEFICIARY'?'My payouts':'Payout records'}</h1><p className="registry-description">{role==='DISBURSING'?'One household. Check the amount. Keep the receipt.':'Recorded payouts and their exact receipts.'}</p></div><div className="flex flex-wrap gap-2">{requestedId!==null&&<Link className="registry-button registry-text-button" href="/distributions">View all permitted payouts</Link>}<Link className="registry-button" href="/verify">Check receipts</Link><button className="registry-button registry-text-button" disabled={loading} onClick={()=>void loadData()}>Refresh records</button></div></header>
    {loading&&<p role="status">Loading household and payout records...</p>}{loadError&&<div role="alert" className="registry-error">{loadError} Previously loaded records are hidden.<button className="registry-button" onClick={()=>void loadData()}>Retry loading payouts</button></div>}
    {!loading&&!loadError&&householdUnavailable&&<section className="workflow-panel space-y-3"><h2>Household unavailable</h2><p>The linked household is missing or outside your account's records.</p><Link className="registry-button" href="/distributions">Choose another household</Link></section>}
    {role==='DISBURSING'&&!householdUnavailable&&<div className="workflow-columns">
      <section aria-label="Payout entry" className="workflow-panel">
        {browserOnline===false&&<p role="alert" className="registry-notice">Browser is offline. Reconnect to record a payout. Nothing is queued.</p>}
        {confirmedResult&&step==='SUCCESS'?<div className="space-y-5" role="status">
          <p className="registry-approved">Saved to the payout records</p><h2>Payout recorded</h2><p>{beneficiaries.find(b=>b.beneficiary_id===confirmedResult.beneficiary_id)?.household_name||confirmedResult.beneficiary_id}</p><p className="workflow-amount">{formatPeso(confirmedResult.amount)}</p>
          <PayoutAnchorStatus anchor={confirmedResult.anchor_job} busy={anchorBusy||!browserOnline} onRecover={()=>void recoverAnchor(confirmedResult.distribution_id)} error={anchorError?.id===confirmedResult.distribution_id?anchorError.message:undefined}/>
          <div className="flex flex-wrap gap-2"><Link className="registry-button registry-primary" href={receiptVerificationHref(confirmedResult.distribution_id)}>Check this receipt</Link><button className="registry-button" disabled={loading||!!loadError||anchorBusy} onClick={resetEntry}>Record another payout</button></div><p className="registry-muted">A saved record or matching receipt does not prove cash delivery.</p><details><summary>Receipt references</summary><p className="registry-muted break-all">{confirmedResult.distribution_id}</p><p className="registry-muted break-all">{confirmedResult.receipt_hash}</p></details>
        </div>:<form onSubmit={handleDisburse} aria-busy={step==='SUBMITTING'} className="space-y-5">
          <div><label htmlFor="payout-household">Household</label><select id="payout-household" value={selectedBenId} disabled={requestedId!==null||step==='SUBMITTING'||loading||!!loadError} onChange={e=>{setSelectedBenId(e.target.value);setSubmitError(null);}}><option value="">Choose a household</option>{beneficiaries.filter(b=>b.record_status==='ACTIVE'||b.beneficiary_id===requestedId).map(b=><option key={b.beneficiary_id} value={b.beneficiary_id}>{b.household_name} ({b.barangay_name})</option>)}</select></div>
          {selectedBeneficiaryObj&&!loading&&!loadError&&<div className="desk-person"><span className="household-avatar" aria-hidden="true">{selectedBeneficiaryObj.household_name.split(' ').slice(0,2).map(n=>n[0]).join('')}</span><div><p className="registry-record-id">{selectedBeneficiaryObj.dafac_id||selectedBeneficiaryObj.beneficiary_id}</p><h2>{selectedBeneficiaryObj.household_name}</h2><p className="registry-muted">{selectedBeneficiaryObj.barangay_name} · {selectedBatch?.calamity_name}</p><span className={'registry-badge '+(selectedIsApproved?'registry-approved':'registry-pending')}>{selectedIsApproved?'Approved':'Needs DSWD review'}</span></div></div>}
          <div className="payout-amount-field"><div><label htmlFor="payout-amount">Fictional amount (PHP)</label><input id="payout-amount" type="text" inputMode="decimal" value={amountStr} disabled={!selectedBenId||step==='SUBMITTING'||loading||!!loadError} onChange={e=>setAmountStr(e.target.value)} aria-describedby="payout-amount-help"/><p id="payout-amount-help" className="registry-muted mt-2">{selectedBatch&&amountValid&&numericAmount!==standardGrant?'This differs from the standard grant. Check before saving.':'Use up to two decimal places.'}</p></div>{selectedBatch&&<div className="payout-standard"><span>Standard grant</span><strong>{formatPeso(standardGrant)}</strong></div>}</div>
          {selectedBenId&&amountValid&&!loading&&!loadError&&<section aria-label="Desk checks" className="space-y-3"><h3>Desk checks</h3>{!deskCurrent?<p role="status" className="registry-muted">Checking current approval and budget...</p>:deskCurrent.error?<p role="alert" className="registry-error">{deskCurrent.error} Refresh records to retry.</p>:deskCurrent.result&&<><p className={deskCurrent.result.can_record?'registry-approved':'registry-pending'}>{deskCurrent.result.can_record?'Ready to record this amount.':deskCurrent.result.checks.find(c=>!c.passed)?.message||'Recording is outside your role.'}</p>{deskCurrent.result.existing_distribution_id&&<Link className="registry-button" href={receiptVerificationHref(deskCurrent.result.existing_distribution_id)}>Open existing household receipt</Link>}<details><summary>Approval and budget checks</summary><ul className="desk-check-list">{deskCurrent.result.checks.map(c=><li key={c.code}><span className="desk-check-icon" style={{color:c.passed?'var(--st-ok)':'var(--st-warn)'}}>{c.passed?'✓':'!'}</span>{c.message}</li>)}</ul></details></>}</section>}
          {deskBlock&&!loading&&!loadError&&(!deskCurrent?.result||!selectedBenId||!amountValid)&&<p className="registry-notice">{deskBlock}</p>}
          {submitError&&<p role="alert" className="registry-error">{submitError} Retry the same details to retrieve a payout if the response was lost.</p>}
          <div className="payout-save"><p className="registry-muted">The API checks approval, budget and prior payouts again when saving.</p><button type="submit" className="registry-button registry-primary" disabled={step==='SUBMITTING'||!browserOnline||loading||!!loadError||!!blockedReason||!deskCurrent?.result?.can_record}>{step==='SUBMITTING'?'Saving payout...':!browserOnline?'Reconnect to record a payout':submitError?'Retry payout request':'Record demo payout'}</button></div>
        </form>}
      </section>
      <aside className="space-y-4"><section className="workflow-panel space-y-4"><h2>At the desk</h2><ol className="material-steps"><li className={selectedBenId?'done':'current'}><span className="step-dot">1</span><div><strong>Find the household</strong><p>Use its name or household reference.</p></div></li><li className={deskCurrent?.result?.can_record?'done':selectedBenId?'current':''}><span className="step-dot">2</span><div><strong>Review the amount</strong><p>Approval, available funds and earlier payouts.</p></div></li><li className={confirmedResult?'done':''}><span className="step-dot">3</span><div><strong>Record the payout</strong><p>Keep the exact saved receipt.</p></div></li></ol>{allocation&&<div className="workflow-facts"><span className="registry-muted">Remaining allocation</span><strong>{formatPeso(remainingCentavos/100)}</strong></div>}</section>
       {deskCurrent?.result?.arrangement&&<section className="workflow-panel space-y-3"><h2>Collection arrangement</h2><p>{deskCurrent.result.arrangement.state==='CANCELLED'?'Cancelled appointment':deskCurrent.result.arrangement.collection_date+' · '+deskCurrent.result.arrangement.time_window}</p><p>{deskCurrent.result.arrangement.site}</p><details><summary>Requirements and contact</summary><ul>{deskCurrent.result.arrangement.requirements.map(r=><li key={r}>{r}</li>)}</ul><p>{deskCurrent.result.arrangement.responsible_staff}</p></details></section>}
       {selectedBenId&&<section className="workflow-panel space-y-3"><h2>Need staff assistance?</h2><p className="registry-muted">Record a concern under your staff account.</p><Link className="registry-button" href={'/concerns?'+new URLSearchParams({beneficiary_id:selectedBenId})}>Record an assisted concern</Link></section>}
       <details className="workflow-panel"><summary>Demo evidence and connection</summary><p className="registry-muted">{chainLabel(chain)}. Recording and blockchain confirmation are separate.</p><p className="registry-muted">The shared receipt template is not household-specific evidence. Recipient acknowledgement is made by the household account.</p></details>
      </aside>
    </div>}
    {!loading&&!loadError&&!householdUnavailable&&<section className="workflow-panel payout-records space-y-4" aria-label="Recorded payouts"><div className="workflow-section-heading"><h2>{role==='DISBURSING'?'Recent payout records':requestedHousehold?.household_name||'Recorded payouts'}</h2><span className="registry-muted">{filteredPayouts.length} records</span></div><div className="registry-search"><label htmlFor="payout-search">Find a recorded payout</label><input id="payout-search" type="search" placeholder="Household or receipt reference" value={searchTerm} onChange={e=>setSearchTerm(e.target.value)}/>{searchTerm&&<button type="button" className="registry-button registry-text-button" onClick={()=>setSearchTerm('')}>Clear search</button>}</div>{!filteredPayouts.length?<div className="registry-empty"><h3>{searchTerm?'No matching payouts':requestedId?'No payouts recorded for this household':'No recorded payouts'}</h3><p className="registry-muted">{searchTerm?'Try another household or receipt reference.':'A recorded payout will appear here after it is saved.'}</p></div>:<div className="material-table-wrap"><table className="material-table"><caption className="sr-only">Permitted recorded payouts</caption><thead><tr><th>Household</th><th>Amount</th><th>Recorded</th><th>Receipt</th></tr></thead><tbody>{filteredPayouts.map(d=><tr key={d.distribution_id}><td><strong>{beneficiaries.find(b=>b.beneficiary_id===d.beneficiary_id)?.household_name||d.beneficiary_id}</strong><small>{d.beneficiary_id}</small></td><td data-label="Amount">{formatPeso(d.amount)}</td><td data-label="Recorded">{formatRecordedDate(d.distributed_at)}<details><summary>Anchor status</summary><PayoutAnchorStatus anchor={d.anchor_job} busy={anchorBusy||!browserOnline} onRecover={role==='DISBURSING'?()=>void recoverAnchor(d.distribution_id):undefined} error={anchorError?.id===d.distribution_id?anchorError.message:undefined}/></details></td><td><p className="registry-record-id break-all">{d.distribution_id}</p><div className="flex flex-wrap gap-2"><Link className="registry-button registry-text-button" href={receiptVerificationHref(d.distribution_id)}>Check receipt</Link><button className="registry-button registry-text-button" onClick={()=>setPreviewReceipt(d)}>Receipt details</button></div></td></tr>)}</tbody></table></div>}</section>}
    {previewReceipt&&<RegistryDialog title="Recorded receipt" onClose={()=>setPreviewReceipt(null)} wide returnFocusId="payout-heading"><div className="registry-dialog-content"><ReceiptDetails checkLink record={previewReceipt} household={beneficiaries.find(b=>b.beneficiary_id===previewReceipt.beneficiary_id)}/><button className="registry-button" onClick={()=>setPreviewReceipt(null)}>Back to payouts</button></div></RegistryDialog>}
  </div>;
}

function HouseholdPayoutPage() {
  const params = useSearchParams();
  const requestedId = params.get("beneficiary_id");
  return (
    <DistributionsContent
      key={requestedId === null ? "all" : `household:${requestedId}`}
      requestedId={requestedId}
    />
  );
}

export default function DistributionsPage() {
  return (
    <Suspense fallback={<p role="status">Loading payout records...</p>}>
      <HouseholdPayoutPage />
    </Suspense>
  );
}
