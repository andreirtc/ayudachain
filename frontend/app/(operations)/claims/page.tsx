"use client";
import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { Beneficiary, ClaimAction, ClaimStatus, DAMAGE_CATEGORIES, DamageCategory, DamageClaim, fetchBeneficiaries, fetchClaims, formatPeso, reviseClaim, submitClaim } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";

const STATUS: Record<ClaimStatus, string> = { SUBMITTED: "Awaiting barangay review", ENDORSED: "Endorsed by barangay", NOT_ENDORSED: "Not endorsed by barangay", NEEDS_INFO: "Waiting for household", APPROVED: "Approved", DECLINED: "Declined" };
const FILTERS: { key: string; label: string; statuses: ClaimStatus[] }[] = [
  { key: "barangay", label: "Barangay review", statuses: ["SUBMITTED"] },
  { key: "decision", label: "Needs DSWD decision", statuses: ["ENDORSED", "NOT_ENDORSED"] },
  { key: "household", label: "Waiting for household", statuses: ["NEEDS_INFO"] },
  { key: "decided", label: "Decided", statuses: ["APPROVED", "DECLINED"] },
  { key: "all", label: "All claims", statuses: [] },
];
const ACTION_LABEL: Record<ClaimAction | "SUBMIT", string> = { SUBMIT: "Submitted", ENDORSE: "Endorsed", NOT_ENDORSE: "Not endorsed", REQUEST_INFO: "Asked household", RESPOND: "Household answered", APPROVE: "Approved", DECLINE: "Declined" };
const badge = (status: ClaimStatus) => "registry-badge " + (status === "APPROVED" ? "registry-approved" : status === "DECLINED" ? "registry-rejected" : "registry-pending");

function amountText(claim: DamageClaim) {
  const e = claim.entitlement;
  if (e.basis === "PENDING" || e.amount_centavos === null) return e.blocked || "Calculated after a decision";
  return formatPeso(e.amount_centavos / 100) + (e.basis === "CLAIM" ? ` · rules version ${e.rule_version}` : " · standard grant");
}

export default function ClaimsPage() {
  const { account } = useRole(), online = useBrowserOnline(), params = useSearchParams(), router = useRouter();
  const role = account?.role;
  const [claims, setClaims] = useState<DamageClaim[]>([]), [households, setHouseholds] = useState<Beneficiary[]>([]);
  const [loading, setLoading] = useState(true), [readError, setReadError] = useState(""), [busy, setBusy] = useState(false), [error, setError] = useState(""), [notice, setNotice] = useState("");
  const [filter, setFilter] = useState(role === "BARANGAY" ? "barangay" : "decision");
  const [action, setAction] = useState<ClaimAction | null>(null), [category, setCategory] = useState<DamageCategory>("PARTIALLY_DAMAGED"), [staffReason, setStaffReason] = useState(""), [householdMessage, setHouseholdMessage] = useState(""), [answer, setAnswer] = useState("");
  const [intake, setIntake] = useState({ beneficiary_id: "", category: "PARTIALLY_DAMAGED" as DamageCategory, description: "" });
  const generation = useRef(0), retry = useRef<string | null>(null);
  const requested = params.get("claim_id");
  const statuses = FILTERS.find(f => f.key === filter)?.statuses || [];
  const shown = claims.filter(c => !statuses.length || statuses.includes(c.current.status));
  const selected = claims.find(c => c.claim_id === requested) || (requested === null ? shown[0] : undefined);
  const staff = role === "DSWD" || role === "BARANGAY" || role === "AUDITOR";

  async function load() {
    const current = ++generation.current; setLoading(true); setReadError("");
    try {
      const [rows, registry] = await Promise.all([fetchClaims(), role === "BARANGAY" ? fetchBeneficiaries() : Promise.resolve([])]);
      if (current !== generation.current) return;
      setClaims(rows); setHouseholds(registry.filter(h => h.record_status === "ACTIVE"));
    } catch (e) { if (current === generation.current) setReadError(e instanceof Error ? e.message : "Damage claims unavailable."); }
    finally { if (current === generation.current) setLoading(false); }
  }
  useEffect(() => { if (staff) void load(); return () => { generation.current++; }; }, [account?.id]);
  useEffect(() => { setFilter(role === "BARANGAY" ? "barangay" : "decision"); }, [role]);
  useEffect(() => { reset(); if (selected) setCategory(selected.current.category); }, [selected?.claim_id, selected?.current.revision]);
  function reset() { setAction(null); setStaffReason(""); setHouseholdMessage(""); setAnswer(""); setError(""); retry.current = null; }
  function changed() { retry.current = null; setError(""); setNotice(""); }

  async function run(work: () => Promise<DamageClaim>, message: string) {
    if (busy || !online) return false;
    setBusy(true); setError(""); retry.current ||= crypto.randomUUID();
    try {
      const result = await work();
      setClaims(prev => [result, ...prev.filter(c => c.claim_id !== result.claim_id)]);
      retry.current = null; setNotice(message); reset();
      router.replace("/claims?" + new URLSearchParams({ claim_id: result.claim_id }), { scroll: false });
      return true;
    } catch (e) { setError(e instanceof Error ? e.message : "Claim step was not saved."); return false; }
    finally { setBusy(false); }
  }
  function step(event: FormEvent) {
    event.preventDefault();
    if (!selected || !action) return;
    const payload = { request_id: retry.current || "", expected_revision: selected.current.revision, action, ...(action === "RESPOND" ? { description: answer } : { staff_reason: staffReason }), ...(action === "APPROVE" ? { category } : {}), ...(householdMessage.trim() ? { household_message: householdMessage } : {}) };
    void run(() => reviseClaim(selected.claim_id, { ...payload, request_id: retry.current! }), ACTION_LABEL[action] + ". The household sees the update on their home.");
  }
  async function assisted(event: FormEvent) {
    event.preventDefault();
    if (await run(() => submitClaim({ request_id: retry.current!, ...intake }), "Claim submitted for the household.")) setIntake({ beneficiary_id: "", category: "PARTIALLY_DAMAGED", description: "" });
  }

  if (role === "BENEFICIARY") return <section className="registry space-y-3"><h1>Your damage claim is on your household home</h1><p>Submit or follow up your claim there.</p><Link href="/household" className="registry-button">My household</Link></section>;
  if (role === "DISBURSING") return <section className="registry space-y-3"><h1>Damage claims are reviewed by barangay and DSWD staff</h1><p>The payout desk shows the calculated amount for each household.</p><Link href="/sessions" className="registry-button">My payout sessions</Link></section>;
  const actions: ClaimAction[] = !selected || selected.payout_recorded ? [] : role === "BARANGAY" ? (selected.current.status === "SUBMITTED" ? ["ENDORSE", "NOT_ENDORSE", "REQUEST_INFO"] : selected.current.status === "NEEDS_INFO" ? ["RESPOND"] : []) : role === "DSWD" ? (["ENDORSED", "NOT_ENDORSED"].includes(selected.current.status) ? ["APPROVE", "DECLINE", "REQUEST_INFO"] : ["APPROVED", "DECLINED"].includes(selected.current.status) ? ["APPROVE", "DECLINE"] : []) : [];
  const actionText: Record<ClaimAction, string> = { ENDORSE: "Endorse", NOT_ENDORSE: "Do not endorse", REQUEST_INFO: "Ask the household", RESPOND: "Answer for the household", APPROVE: selected?.current.status === "APPROVED" ? "Change category" : selected?.current.status === "DECLINED" ? "Approve instead" : "Approve", DECLINE: selected?.current.status === "APPROVED" ? "Decline instead" : selected?.current.status === "DECLINED" ? "Change explanation" : "Decline" };

  return <div className="registry workflow claims-page space-y-6">
    <header className="registry-header"><div><p className="registry-eyebrow">Damage assessment</p><h1>Damage claims</h1><p className="registry-description">{role === "BARANGAY" ? "Check residence and damage, then endorse or ask the household for more." : role === "DSWD" ? "Decide each claim's damage category. Approved categories set the household's amount." : "Claims, endorsements and decisions, with every step retained."}</p></div>
      <div className="flex flex-wrap gap-2">{(role === "DSWD" || role === "AUDITOR") && <Link href="/amounts" className="registry-button">Amount rules</Link>}<button className="registry-button registry-text-button" disabled={loading || !online} onClick={() => void load()}>Refresh claims</button></div></header>
    {!online && <p role="alert" className="registry-notice">Offline. These are the last loaded claims. Reconnect before recording a step; nothing is queued.</p>}
    {loading && <p role="status">Loading damage claims...</p>}
    {readError && <div role="alert" className="registry-error"><p>{readError}</p><button className="registry-button" disabled={loading || !online} onClick={() => void load()}>Retry claims</button></div>}
    {notice && <p role="status" className="registry-success">{notice}</p>}
    {!loading && !readError && <div className="workflow-columns list-workspace">
      <div className="space-y-6">
        <section className="workflow-panel space-y-3" aria-label="Claim queue">
          <div className="registry-filters" aria-label="Claim status filter">{FILTERS.map(f => { const count = claims.filter(c => !f.statuses.length || f.statuses.includes(c.current.status)).length; return <button key={f.key} aria-pressed={filter === f.key} className={"registry-button " + (filter === f.key ? "registry-filter-selected" : "")} onClick={() => { setFilter(f.key); router.replace("/claims", { scroll: false }); }}>{f.label} ({count})</button>; })}</div>
          {!shown.length ? <div className="registry-empty"><h2>No claims here</h2><p className="registry-muted">{claims.length ? "Choose another filter." : "Households submit claims from their home, or barangay staff can submit one for them."}</p></div>
            : <ul>{shown.map(c => <li key={c.claim_id} className="workflow-record"><Link className="version-row" aria-current={c.claim_id === selected?.claim_id ? "page" : undefined} href={"/claims?" + new URLSearchParams({ claim_id: c.claim_id })} scroll={false}>{c.household_name} · {c.barangay_name}</Link><p><span className={badge(c.current.status)}>{STATUS[c.current.status]}</span> {c.current.category_label}</p></li>)}</ul>}
        </section>
        {role === "BARANGAY" && <form className="workflow-panel space-y-3" onSubmit={assisted} aria-label="Staff-assisted claim"><h2>Submit for a household</h2><p className="registry-muted">For households without an account or who asked for help. The claim is recorded under your account.</p>
          <label>Household<select required disabled={busy} value={intake.beneficiary_id} onChange={e => { setIntake({ ...intake, beneficiary_id: e.target.value }); changed(); }}><option value="">Choose a household</option>{households.filter(h => !claims.some(c => c.beneficiary_id === h.beneficiary_id)).map(h => <option key={h.beneficiary_id} value={h.beneficiary_id}>{h.household_name} ({h.beneficiary_id})</option>)}</select></label>
          <label>Damage category<select disabled={busy} value={intake.category} onChange={e => { setIntake({ ...intake, category: e.target.value as DamageCategory }); changed(); }}>{(Object.keys(DAMAGE_CATEGORIES) as DamageCategory[]).map(k => <option key={k} value={k}>{DAMAGE_CATEGORIES[k]}</option>)}</select></label>
          <label>What was damaged?<textarea required maxLength={2000} disabled={busy} value={intake.description} onChange={e => { setIntake({ ...intake, description: e.target.value }); changed(); }} /></label>
          <button className="registry-button registry-primary" disabled={busy || !online || !intake.beneficiary_id || !intake.description.trim()}>{busy ? "Submitting..." : "Submit claim"}</button>
        </form>}
      </div>
      <section className="workflow-panel space-y-4" aria-label="Selected claim">
        {!selected ? <><h2>{requested ? "Claim unavailable" : "Select a claim"}</h2><p>{requested ? "This claim is missing or outside your account's records." : "Choose a claim to see the household's description and every review step."}</p></> : <>
          <div className="workflow-section-heading"><h2>{selected.household_name}</h2><span className={badge(selected.current.status)}>{STATUS[selected.current.status]}</span></div>
          <p className="registry-muted">{selected.beneficiary_id} · {selected.barangay_name} · {selected.source === "STAFF_ASSISTED" ? "Submitted with staff help" : "Submitted by the household"}</p>
          <dl className="receipt-references"><dt>Category</dt><dd>{selected.current.category_label}</dd><dt>Description</dt><dd>{selected.current.description}</dd><dt>Amount</dt><dd>{amountText(selected)}</dd><dt>Household sees</dt><dd>{selected.current.household_message}</dd></dl>
          {selected.payout_recorded && <p className="registry-notice">A payout is recorded for this household. The claim is locked.</p>}
          {error && <p role="alert" className="registry-error">{error}</p>}
          {actions.length > 0 && (action ? <form className="registry-decision space-y-3" onSubmit={step}><h3>{actionText[action]}</h3>
            {action === "APPROVE" && <label>Approved damage category<select disabled={busy} value={category} onChange={e => { setCategory(e.target.value as DamageCategory); changed(); }}>{(Object.keys(DAMAGE_CATEGORIES) as DamageCategory[]).map(k => <option key={k} value={k}>{DAMAGE_CATEGORIES[k]}</option>)}</select></label>}
            {action === "RESPOND" ? <label>Household's answer<textarea required maxLength={2000} disabled={busy} value={answer} onChange={e => { setAnswer(e.target.value); changed(); }} /></label> : <>
              {(action === "REQUEST_INFO" || action === "DECLINE" || action === "APPROVE") && <label>{action === "REQUEST_INFO" ? "Question for the household" : action === "DECLINE" ? "Explanation for the household" : "Message for the household (optional)"}<textarea required={action !== "APPROVE"} maxLength={2000} disabled={busy} value={householdMessage} onChange={e => { setHouseholdMessage(e.target.value); changed(); }} /></label>}
              <label>Reason (staff only)<textarea required maxLength={2000} disabled={busy} value={staffReason} onChange={e => { setStaffReason(e.target.value); changed(); }} /></label></>}
            <div className="flex flex-wrap gap-3"><button className="registry-button registry-primary" disabled={busy || !online || (action === "RESPOND" ? !answer.trim() : !staffReason.trim())}>{busy ? "Saving..." : "Confirm: " + actionText[action].toLowerCase()}</button><button type="button" className="registry-button" disabled={busy} onClick={reset}>Back</button></div>
          </form> : <div className="flex flex-wrap gap-3">{actions.map(a => <button key={a} className={"registry-button" + (a === "APPROVE" || a === "ENDORSE" ? " registry-primary" : "")} onClick={() => { setAction(a); changed(); }}>{actionText[a]}</button>)}</div>)}
          <details open><summary>Review history ({selected.history.length})</summary><ul>{selected.history.map(h => <li key={h.revision} className="workflow-record"><p><strong>{ACTION_LABEL[h.action]}</strong> · {h.revised_name} · {formatRecordedDate(h.revised_at)}</p><p>{h.category_label}{h.staff_reason ? " · " + h.staff_reason : ""}</p></li>)}</ul></details>
        </>}
      </section>
    </div>}
  </div>;
}
