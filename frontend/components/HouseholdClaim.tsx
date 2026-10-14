"use client";
import { FormEvent, useRef, useState } from "react";
import { DAMAGE_CATEGORIES, DamageCategory, DamageClaim, Entitlement, formatPeso, reviseClaim, submitClaim } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";

export const HOUSEHOLD_STATUS: Record<DamageClaim["current"]["status"], string> = { SUBMITTED: "Barangay review", ENDORSED: "DSWD review", NOT_ENDORSED: "DSWD review", NEEDS_INFO: "Staff need more information", APPROVED: "Approved", DECLINED: "Declined" };

export function amountLine(entitlement: Entitlement | null) {
  if (!entitlement) return null;
  if (entitlement.basis === "PENDING" || entitlement.amount_centavos === null) return "Your amount is calculated after DSWD decides on your damage claim.";
  return (entitlement.basis === "CLAIM" ? "Calculated amount: " : "Standard grant: ") + formatPeso(entitlement.amount_centavos / 100);
}

export default function HouseholdClaim({ claim, entitlement, online, onChanged }: { claim: DamageClaim | null; entitlement: Entitlement | null; online: boolean; onChanged: (claim: DamageClaim) => void }) {
  const [category, setCategory] = useState<DamageCategory>("PARTIALLY_DAMAGED"), [description, setDescription] = useState(""), [busy, setBusy] = useState(false), [error, setError] = useState(""), [notice, setNotice] = useState("");
  const retry = useRef<string | null>(null);
  async function send(action: () => Promise<DamageClaim>, message: string) {
    if (busy || !online) return;
    setBusy(true); setError(""); retry.current ||= crypto.randomUUID();
    try { onChanged(await action()); retry.current = null; setDescription(""); setNotice(message); }
    catch (e) { setError(e instanceof Error ? e.message : "Claim was not saved."); }
    finally { setBusy(false); }
  }
  function changed() { retry.current = null; setError(""); setNotice(""); }
  function create(event: FormEvent) { event.preventDefault(); void send(() => submitClaim({ request_id: retry.current!, category, description }), "Damage claim submitted. Your barangay reviews it first."); }
  function respond(event: FormEvent) { event.preventDefault(); if (claim) void send(() => reviseClaim(claim.claim_id, { request_id: retry.current!, expected_revision: claim.current.revision, action: "RESPOND", description }), "Your answer was sent to staff."); }
  const current = claim?.current;
  return <section className="workflow-panel space-y-4 household-claim" aria-label="Damage claim">
    <div className="workflow-section-heading"><h2>Damage claim</h2>{current && <span className={"registry-badge " + (current.status === "APPROVED" ? "registry-approved" : current.status === "DECLINED" ? "registry-rejected" : "registry-pending")}>{HOUSEHOLD_STATUS[current.status]}</span>}</div>
    {notice && <p role="status" className="registry-success">{notice}</p>}
    {error && <p role="alert" className="registry-error">{error}</p>}
    {!claim ? <form className="space-y-3" onSubmit={create}>
      <p className="registry-muted">Tell staff how the typhoon damaged your house. Your assistance amount depends on the approved damage category.</p>
      <fieldset className="space-y-2"><legend>How damaged is your house?</legend>{(Object.keys(DAMAGE_CATEGORIES) as DamageCategory[]).map(key => <label key={key} className="registry-checkbox"><input type="radio" name="damage-category" value={key} checked={category === key} disabled={busy} onChange={() => { setCategory(key); changed(); }} />{DAMAGE_CATEGORIES[key]}</label>)}</fieldset>
      <label>What was damaged?<textarea required maxLength={2000} disabled={busy} value={description} onChange={e => { setDescription(e.target.value); changed(); }} /></label>
      <button className="registry-button registry-primary" disabled={busy || !online || !description.trim()}>{busy ? "Submitting..." : "Submit damage claim"}</button>
    </form> : <>
      <p>{current!.household_message}</p>
      <dl className="receipt-references"><dt>Category</dt><dd>{current!.category_label}</dd><dt>Your description</dt><dd>{current!.description}</dd><dt>Submitted</dt><dd>{formatRecordedDate(claim.created_at)}</dd></dl>
      {entitlement && <p><strong>{amountLine(entitlement)}</strong></p>}
      {current!.status === "NEEDS_INFO" && <form className="registry-decision space-y-3" onSubmit={respond}><h3>Answer staff</h3><label>Your answer<textarea required maxLength={2000} disabled={busy} value={description} onChange={e => { setDescription(e.target.value); changed(); }} /></label><button className="registry-button registry-primary" disabled={busy || !online || !description.trim()}>{busy ? "Sending..." : "Send answer"}</button></form>}
      <details><summary>Claim history ({claim.history.length})</summary><ul>{claim.history.map(h => <li key={h.revision} className="workflow-record"><p>{HOUSEHOLD_STATUS[h.status]} · {formatRecordedDate(h.revised_at)}</p><p className="registry-muted">{h.household_message}</p></li>)}</ul></details>
    </>}
  </section>;
}
