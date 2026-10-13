"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { Beneficiary, Distribution, fetchBeneficiaries, fetchDistributions, formatPeso } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";
import { receiptVerificationHref as receiptHref } from "@/lib/receiptNavigation";

export default function HouseholdPage() {
  const { account } = useRole();
  const online = useBrowserOnline();
  const generation = useRef(0);
  const details = useRef<HTMLDetailsElement>(null);
  const [household, setHousehold] = useState<Beneficiary | null>(null);
  const [payouts, setPayouts] = useState<Distribution[]>([]);
  const [loading, setLoading] = useState(true);
  const [householdError, setHouseholdError] = useState(false);
  const [payoutError, setPayoutError] = useState(false);
  const ownId = account?.beneficiary_id;

  async function load() {
    const current = ++generation.current;
    setLoading(true); setHousehold(null); setPayouts([]); setHouseholdError(false); setPayoutError(false);
    const [registry, records] = await Promise.allSettled([
      fetchBeneficiaries({ include_historical: true }), fetchDistributions(),
    ]);
    if (current !== generation.current) return;
    if (registry.status === "fulfilled") setHousehold(registry.value.find(row => row.beneficiary_id === ownId) || null);
    else setHouseholdError(true);
    if (records.status === "fulfilled") setPayouts(records.value.filter(row => row.beneficiary_id === ownId).sort((a,b)=>b.id-a.id));
    else setPayoutError(true);
    setLoading(false);
  }
  useEffect(() => {
    if (account?.role === "BENEFICIARY") void load();
    return () => { generation.current++; };
  }, [account?.id, ownId]);

  if (account?.role !== "BENEFICIARY") return <section className="registry space-y-4"><h1>Household home is for linked household accounts</h1><p>Use your staff workspace to inspect permitted records.</p><Link href="/beneficiaries" className="registry-button">Open household registry</Link></section>;
  const receipt = payouts[0];
  const historical = household?.record_status === "DUPLICATE";
  const rejected = household?.review_status === "REJECTED" || household?.verification_status === "REJECTED";
  const approved = household?.review_status === "APPROVED" && household?.verification_status === "VERIFIED";
  const status = historical ? "Retained duplicate" : rejected ? "Rejected" : approved ? "Approved" : "Pending review";
  const title = householdError ? "Household status unavailable" : !household ? "Linked household not found" : historical ? "Historical household record" : rejected ? "Review the recorded decision" : payoutError ? "Payout records unavailable" : receipt ? "Your payout has a saved receipt" : approved ? "Eligibility approved; no payout recorded" : "Awaiting staff review";
  function revealDetails() {
    if (details.current) { details.current.open = true; details.current.scrollIntoView({ behavior: "auto", block: "start" }); details.current.querySelector("summary")?.focus(); }
  }
  return <div className="registry workflow household-home space-y-6">
    <header className="registry-header"><div><h1>My household</h1><p className="registry-description">Your assistance status, recorded payout and receipt.</p></div><button className="registry-button" disabled={loading || !online} onClick={()=>void load()}>Refresh household</button></header>
    {!online && <p role="alert" className="registry-notice">You are offline. Reconnect and refresh before relying on these records.</p>}
    {loading ? <p role="status">Loading your household and payout records...</p> : <>
      <section className="household-next space-y-3" aria-label="Next step">
        <p className="registry-eyebrow">Next step</p><h2>{title}</h2>
        {householdError ? <><p role="alert">The household read failed. No eligibility or payout readiness can be inferred.</p><button className="registry-button registry-primary" disabled={!online} onClick={()=>void load()}>Retry household</button></> : !household ? <><p>Ask your Barangay Officer to check the account link or missing record. Do not share your password or re-enter an already listed household.</p><button className="registry-button registry-primary" disabled={!online} onClick={()=>void load()}>Check again</button></> : <>
          <p>{historical ? "This original record is retained. It cannot receive a new payout; earlier receipts remain available." : rejected ? "Read the saved review history and ask staff to review incorrect details. A concern does not automatically change eligibility." : approved && !receipt ? "Approval is an eligibility decision. Staff must still check funding, prior payouts and any required evidence." : receipt ? "A recorded payout, recipient acknowledgement and receipt hash check are separate facts." : "Staff will review the existing record. You do not need to submit the same household again."}</p>
          {receipt ? <Link className="registry-button registry-primary" href={receiptHref(receipt.distribution_id)}>Open saved receipt</Link> : <button className="registry-button registry-primary" onClick={revealDetails}>Review household details</button>}
        </>}
      </section>
      {household && <section className="workflow-panel space-y-3" aria-label="Household status"><h2>{household.household_name}</h2><p>{household.barangay_name}</p><p className={"registry-badge "+(approved && !historical ? "registry-approved" : "registry-pending")}>{status}</p>{(household.duplicate_flag || household.anomaly_flag) && <p className="registry-notice">A review flag remains on this record. It is a reason for staff inspection, not a fraud finding.</p>}</section>}
      <section className="workflow-panel space-y-3" aria-label="Payout and instructions"><h2>Payout and instructions</h2>
        {payoutError ? <><p role="alert" className="registry-error">Payout records unavailable. This does not mean no payout exists.</p><button className="registry-button" disabled={!online} onClick={()=>void load()}>Retry payout records</button></> : receipt ? <><p className="workflow-amount">{formatPeso(receipt.amount)}</p><p>Recorded {formatRecordedDate(receipt.distributed_at)} · {receipt.status === "CONFIRMED" ? "Payout recorded" : "Recorded status: " + receipt.status}</p><p className="registry-muted">This recorded amount is not proof of physical cash delivery.</p><Link href={"/distributions?"+new URLSearchParams({beneficiary_id:ownId || ""})} className="registry-button">View all my payout records</Link></> : <p>No payout was returned for your linked household.</p>}
        <p className="registry-muted">No date, collection site or accepted requirements have been published in this prototype yet. A saved receipt is not a new appointment.</p>
      </section>
      {household && <details ref={details} className="workflow-panel household-details"><summary>Household details and review history</summary><dl className="receipt-references mt-4"><dt>Household reference</dt><dd>{household.beneficiary_id}</dd><dt>DAFAC reference</dt><dd>{household.dafac_id || "Not recorded"}</dd><dt>Relief batch</dt><dd>{household.batch_id}</dd>{household.canonical_beneficiary_id && <><dt>Retained link</dt><dd>{household.canonical_beneficiary_id}</dd></>}</dl><p className="registry-muted mt-4">Ask staff to review incorrect or missing details using your reference. Assistance does not require sharing credentials.</p><Link href="/beneficiaries" className="registry-button mt-4">Open record and review history</Link></details>}
      {!payoutError && payouts.length > 1 && <details className="workflow-panel"><summary>Other saved receipts ({payouts.length-1})</summary><ul>{payouts.slice(1).map(row=><li key={row.distribution_id} className="workflow-record"><Link href={receiptHref(row.distribution_id)} className="registry-button">Receipt {row.distribution_id}</Link><p>{formatPeso(row.amount)} · {formatRecordedDate(row.distributed_at)}</p></li>)}</ul></details>}
    </>}
  </div>;
}
