"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Check, Clock, ArrowRight, UserRound, MessageSquare } from "lucide-react";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { Beneficiary, DamageClaim, Distribution, Entitlement, HouseholdArrangement, fetchBeneficiaries, fetchClaims, fetchDistributions, fetchMyArrangements, fetchMyEntitlement, formatPeso } from "@/lib/api";
import HouseholdClaim, { amountLine } from "@/components/HouseholdClaim";
import { formatRecordedDate } from "@/lib/recordedDate";
import { receiptVerificationHref as receiptHref } from "@/lib/receiptNavigation";

export default function HouseholdPage() {
  const { account } = useRole();
  const online = useBrowserOnline();
  const generation = useRef(0);
  const details = useRef<HTMLDetailsElement>(null);
  const collection = useRef<HTMLElement>(null);
  const [household, setHousehold] = useState<Beneficiary | null>(null);
  const [payouts, setPayouts] = useState<Distribution[]>([]);
  const [loading, setLoading] = useState(true);
  const [householdError, setHouseholdError] = useState(false);
  const [payoutError, setPayoutError] = useState(false);
  const [arrangements, setArrangements] = useState<HouseholdArrangement[]>([]);
  const [arrangementError, setArrangementError] = useState(false);
  const [claim, setClaim] = useState<DamageClaim | null>(null);
  const [entitlement, setEntitlement] = useState<Entitlement | null>(null);
  const [claimError, setClaimError] = useState(false);
  const ownId = account?.beneficiary_id;

  async function load() {
    const current = ++generation.current;
    setLoading(true); setHousehold(null); setPayouts([]); setHouseholdError(false); setPayoutError(false); setArrangements([]); setArrangementError(false); setClaim(null); setEntitlement(null); setClaimError(false);
    const [registry, records, instructions, claims, amount] = await Promise.allSettled([
      fetchBeneficiaries({ include_historical: true }), fetchDistributions(), fetchMyArrangements(), fetchClaims(), fetchMyEntitlement(),
    ]);
    if (current !== generation.current) return;
    if (claims.status === "fulfilled") setClaim(claims.value[0] || null);
    else setClaimError(true);
    if (amount.status === "fulfilled") setEntitlement(amount.value);
    if (instructions.status === "fulfilled") setArrangements(instructions.value);
    else setArrangementError(true);
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
  const plan = arrangements[0]?.current;
  const scheduled = approved && !historical && !receipt && plan?.state === "SCHEDULED";
  const collectionDay = (value: string) => new Date(value + "T00:00:00").toLocaleDateString("en-PH", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
  const status = historical ? "Retained duplicate" : rejected ? "Rejected" : approved ? "Approved" : "Pending review";
  const title = householdError ? "Household status unavailable" : !household ? "Linked household not found" : historical ? "Historical household record" : rejected ? "Review the recorded decision" : payoutError ? "Payout records unavailable" : receipt ? "Your payout has a saved receipt" : scheduled ? "Collect your payout on " + collectionDay(plan.collection_date) : approved ? "Eligibility approved; no payout recorded" : "Awaiting staff review";
  function revealDetails() {
    if (details.current) { details.current.open = true; details.current.scrollIntoView({ behavior: "auto", block: "start" }); details.current.querySelector("summary")?.focus(); }
  }
  return <div className="registry workflow household-home space-y-6">
    <header className="registry-header"><div><p className="registry-eyebrow">Household home</p><h1>My household</h1><p className="registry-description">{household?.household_name || "Your assistance, collection details and receipt."}</p></div><button className="registry-button" disabled={loading || !online} onClick={()=>void load()}>Refresh household</button></header>
    {!online && <p role="alert" className="registry-notice">You are offline. Reconnect and refresh before relying on these records.</p>}
    {loading ? <p role="status">Loading your household and payout records...</p> : <>
      <section className="household-next space-y-3" aria-label="Next step">
        <p className="registry-eyebrow">Next step</p><h2>{title}</h2>
        {householdError ? <><p role="alert">The household read failed. No eligibility or payout readiness can be inferred.</p><button className="registry-button registry-primary" disabled={!online} onClick={()=>void load()}>Retry household</button></> : !household ? <><p>Ask your Barangay Officer to check the account link or missing record. Do not share your password or re-enter an already listed household.</p><button className="registry-button registry-primary" disabled={!online} onClick={()=>void load()}>Check again</button></> : <>
          <p>{historical ? "Your earlier receipts remain available." : rejected ? "Ask staff to review the saved decision." : scheduled ? `${plan.time_window} · ${plan.site}` : approved && !receipt ? arrangementError ? "Collection details could not be loaded." : "Staff will publish your collection instructions here." : receipt ? "Open your receipt to review the recorded amount." : "Staff are reviewing your existing record."}</p>
          {receipt ? <Link className="registry-button registry-primary" href={receiptHref(receipt.distribution_id)}>Open saved receipt</Link> : scheduled ? <button className="registry-button registry-primary" onClick={()=>{collection.current?.scrollIntoView({behavior:"auto",block:"start"});collection.current?.focus();}}>View collection details</button> : <button className="registry-button registry-primary" onClick={revealDetails}>Review household details</button>}
        </>}
      </section>
      <div className="household-grid">
      {household && <section className="workflow-panel space-y-5" aria-label="Household status"><div className="workflow-section-heading"><h2>Your progress</h2><span className={"registry-badge "+(approved&&!historical?'registry-approved':'registry-pending')}>{status}</span></div>
        <ol className="material-steps">
          <li className="done"><span className="step-dot"><Check size={15}/></span><div><strong>Household registered</strong><p>{household.barangay_name} · {formatRecordedDate(household.created_at)}</p></div></li>
          <li className={approved?'done':'current'}><span className="step-dot">{approved?<Check size={15}/>:<Clock size={15}/>}</span><div><strong>{approved?'Eligibility approved':rejected?'Decision recorded':'Staff review'}</strong><p>{approved?'DSWD approval is recorded.':rejected?'Read the decision or report a concern.':'Your details are with the review team.'}</p></div></li>
          <li className={receipt?'done':scheduled?'current':''}><span className="step-dot">{receipt?<Check size={15}/>:<span>3</span>}</span><div><strong>{receipt?'Payout recorded':scheduled?'Collection scheduled':historical?'Earlier records retained':'Payout'}</strong><p>{receipt?formatRecordedDate(receipt.distributed_at):scheduled?collectionDay(plan.collection_date):historical?'No new payout for this retained record.':rejected?'Awaiting further staff review.':'Waiting for collection instructions.'}</p></div></li>
        </ol>
        {(household.duplicate_flag||household.anomaly_flag)&&<p className="registry-notice">A review flag remains for staff inspection.</p>}
      </section>}
      <section ref={collection} tabIndex={-1} className="workflow-panel space-y-3 collection-panel" aria-label="Payout and instructions"><h2>{receipt?"Your recorded payout":"Collection details"}</h2>
        {payoutError ? <><p role="alert" className="registry-error">Payout records unavailable. This does not mean no payout exists.</p><button className="registry-button" disabled={!online} onClick={()=>void load()}>Retry payout records</button></> : receipt ? <><p className="workflow-amount">{formatPeso(receipt.amount)}</p><p>Recorded {formatRecordedDate(receipt.distributed_at)} · {receipt.status === "CONFIRMED" ? "Payout recorded" : "Recorded status: " + receipt.status}</p><p className="registry-muted">This recorded amount is not proof of physical cash delivery.</p><Link href={"/distributions?"+new URLSearchParams({beneficiary_id:ownId || ""})} className="registry-button">View all my payout records</Link></> : <p>No payout was returned for your linked household.</p>}
        {receipt ? <p className="registry-muted">A saved receipt is not a new appointment.</p>
          : arrangementError ? <><p role="alert" className="registry-error">Collection instructions unavailable. This does not mean no schedule exists.</p><button className="registry-button" disabled={!online} onClick={()=>void load()}>Retry instructions</button></>
          : !plan ? <p className="registry-muted">Staff have not published a collection date, site or requirements for your household yet.</p>
          : plan.state === "CANCELLED" ? <p role="alert" className="registry-notice">The collection on {collectionDay(plan.collection_date)} at {plan.site} was cancelled by staff. Wait for new instructions; do not go to the site.</p>
          : <div className="workflow-context space-y-2" aria-label="Collection instructions"><h3>Collection instructions{arrangements[0].updated ? " (updated)" : ""}</h3><dl className="receipt-references"><dt>Date</dt><dd>{collectionDay(plan.collection_date)}</dd><dt>Time</dt><dd>{plan.time_window}</dd><dt>Site</dt><dd>{plan.site}</dd><dt>Bring</dt><dd><ul>{plan.requirements.map(r=><li key={r}>{r}</li>)}</ul></dd><dt>Ask for</dt><dd>{plan.responsible_staff}</dd>{entitlement && <><dt>Amount</dt><dd>{amountLine(entitlement)}</dd></>}</dl><p className="registry-muted">{approved ? "These instructions do not guarantee a payout; staff still check eligibility and funding." : "Your household is listed, but staff must confirm eligibility before any payout."}</p></div>}
      </section>
      </div>
      {household && !historical && (claim || !receipt) && (claimError
        ? <section className="workflow-panel space-y-3" aria-label="Damage claim"><h2>Damage claim</h2><p role="alert" className="registry-error">Your damage claim could not be loaded. This does not mean no claim exists.</p><button className="registry-button" disabled={!online} onClick={()=>void load()}>Retry claim</button></section>
        : <HouseholdClaim claim={claim} entitlement={entitlement} online={online !== false} onChanged={next=>{setClaim(next);fetchMyEntitlement().then(setEntitlement).catch(()=>setEntitlement(null));}} />)}
      {household && <details ref={details} className="workflow-panel household-details"><summary>Household details and review history</summary><dl className="receipt-references mt-4"><dt>Household reference</dt><dd>{household.beneficiary_id}</dd><dt>DAFAC reference</dt><dd>{household.dafac_id || "Not recorded"}</dd><dt>Relief batch</dt><dd>{household.batch_id}</dd>{household.canonical_beneficiary_id && <><dt>Retained link</dt><dd>{household.canonical_beneficiary_id}</dd></>}</dl><p className="registry-muted mt-4">Ask staff to review incorrect or missing details using your reference. Assistance does not require sharing credentials.</p><Link href="/beneficiaries" className="registry-button mt-4">Open record and review history</Link></details>}
      {!payoutError && payouts.length > 1 && <details className="workflow-panel"><summary>Other saved receipts ({payouts.length-1})</summary><ul>{payouts.slice(1).map(row=><li key={row.distribution_id} className="workflow-record"><Link href={receiptHref(row.distribution_id)} className="registry-button">Receipt {row.distribution_id}</Link><p>{formatPeso(row.amount)} · {formatRecordedDate(row.distributed_at)}</p></li>)}</ul></details>}
      <section className="household-support"><div><MessageSquare size={22} aria-hidden="true"/><div><h2>Something needs reviewing?</h2><p className="registry-muted">Ask staff about your details, collection or payout.</p></div></div><Link href="/concerns" className="registry-button">Report or follow up a concern <ArrowRight size={16}/></Link></section>
    </>}
  </div>;
}
