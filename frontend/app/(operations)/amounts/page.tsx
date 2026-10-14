"use client";
import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { AmountRules, DAMAGE_CATEGORIES, DamageCategory, ReliefBatch, fetchAmountRules, fetchBatches, formatPeso, saveAmountRules } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";

const KEYS = Object.keys(DAMAGE_CATEGORIES) as DamageCategory[];
const peso = (centavos: number) => formatPeso(centavos / 100);
type Draft = { mode: "FIXED" | "WAGE_FORMULA"; wage: string; values: Record<DamageCategory, string>; reason: string };
const money = /^\d+(?:\.\d{1,2})?$/;

function draftFrom(rules: AmountRules): Draft {
  const current = rules.current;
  if (!current) return { mode: "FIXED", wage: "", values: { TOTALLY_DAMAGED: "", PARTIALLY_DAMAGED: "" }, reason: "" };
  const values = Object.fromEntries(KEYS.map(k => [k, current.mode === "WAGE_FORMULA" ? String(current.rules[k]?.days ?? "") : String((current.rules[k]?.amount_centavos ?? 0) / 100)])) as Record<DamageCategory, string>;
  return { mode: current.mode, wage: current.daily_wage_centavos ? String(current.daily_wage_centavos / 100) : "", values, reason: "" };
}

function preview(draft: Draft): Record<DamageCategory, number | null> {
  return Object.fromEntries(KEYS.map(k => {
    const value = draft.values[k];
    if (draft.mode === "WAGE_FORMULA") return [k, money.test(draft.wage) && /^\d+$/.test(value) && Number(value) > 0 ? Math.round(Number(draft.wage) * 100) * Number(value) : null];
    return [k, money.test(value) && Number(value) > 0 ? Math.round(Number(value) * 100) : null];
  })) as Record<DamageCategory, number | null>;
}

export default function AmountsPage() {
  const { account } = useRole(), online = useBrowserOnline(), params = useSearchParams(), router = useRouter();
  const [batches, setBatches] = useState<ReliefBatch[]>([]), [rules, setRules] = useState<AmountRules | null>(null), [draft, setDraft] = useState<Draft | null>(null);
  const [loading, setLoading] = useState(true), [readError, setReadError] = useState(""), [busy, setBusy] = useState(false), [error, setError] = useState(""), [notice, setNotice] = useState("");
  const generation = useRef(0), retry = useRef<string | null>(null);
  const batchId = params.get("batch_id") || batches[0]?.batch_id || "";
  const canEdit = account?.role === "DSWD";

  async function load() {
    const current = ++generation.current; setLoading(true); setReadError("");
    try {
      const list = batches.length ? batches : await fetchBatches();
      const id = params.get("batch_id") || list[0]?.batch_id;
      const result = id ? await fetchAmountRules(id) : null;
      if (current !== generation.current) return;
      setBatches(list); setRules(result); setDraft(result ? draftFrom(result) : null);
    } catch (e) { if (current === generation.current) setReadError(e instanceof Error ? e.message : "Amount rules unavailable."); }
    finally { if (current === generation.current) setLoading(false); }
  }
  useEffect(() => { if (account?.role === "DSWD" || account?.role === "AUDITOR") void load(); return () => { generation.current++; }; }, [account?.id, params.get("batch_id")]);
  function edit(next: Draft) { setDraft(next); retry.current = null; setError(""); setNotice(""); }

  async function save(event: FormEvent) {
    event.preventDefault();
    if (!rules || !draft || busy || !online) return;
    setBusy(true); setError(""); retry.current ||= crypto.randomUUID();
    try {
      const result = await saveAmountRules({ batch_id: rules.batch_id, request_id: retry.current, expected_version: rules.current?.version ?? 0, mode: draft.mode, ...(draft.mode === "WAGE_FORMULA" ? { daily_wage: draft.wage } : {}), rules: KEYS.map(k => draft.mode === "WAGE_FORMULA" ? { category: k, days: Number(draft.values[k]) } : { category: k, amount: draft.values[k] }), reason: draft.reason });
      retry.current = null; setRules(result); setDraft(draftFrom(result)); setNotice(`Version ${result.current?.version} saved. New list versions and payout desk checks use it now.`);
    } catch (e) { setError(e instanceof Error ? e.message : "Amount rules were not saved."); }
    finally { setBusy(false); }
  }

  if (account && account.role !== "DSWD" && account.role !== "AUDITOR") return <section className="registry space-y-3"><h1>Amount rules are set by DSWD</h1><p>{account.role === "BENEFICIARY" ? "Your calculated amount appears on your household home." : "The payout desk shows each household's calculated amount."}</p><Link href={account.role === "BENEFICIARY" ? "/household" : "/beneficiaries"} className="registry-button">Back to my workspace</Link></section>;
  const computed = draft ? preview(draft) : null;
  const overLimit = !!rules && !!computed && KEYS.some(k => (computed[k] ?? 0) > rules.max_grant_centavos);
  const complete = !!computed && KEYS.every(k => computed[k] !== null);
  return <div className="registry workflow amounts-page space-y-6">
    <header className="registry-header"><div><p className="registry-eyebrow">Amount calculation</p><h1>Amount rules</h1><p className="registry-description">Each approved damage category gets a fixed amount or a daily wage multiplied by a number of days. Households without an approved claim keep the batch's standard grant.</p></div>
      <div className="flex flex-wrap gap-2"><Link href="/claims" className="registry-button">Damage claims</Link>{batches.length > 1 && <select aria-label="Relief batch" value={batchId} onChange={e => router.replace("/amounts?" + new URLSearchParams({ batch_id: e.target.value }))}>{batches.map(b => <option key={b.batch_id} value={b.batch_id}>{b.calamity_name} ({b.batch_id})</option>)}</select>}</div></header>
    {!online && <p role="alert" className="registry-notice">Offline. Reconnect before saving new rules; nothing is queued.</p>}
    {loading && <p role="status">Loading amount rules...</p>}
    {readError && <div role="alert" className="registry-error"><p>{readError}</p><button className="registry-button" disabled={!online} onClick={() => void load()}>Retry amount rules</button></div>}
    {notice && <p role="status" className="registry-success">{notice}</p>}
    {!loading && !readError && rules && <div className="workflow-columns list-workspace">
      <div className="space-y-6">
        <section className="workflow-panel space-y-4" aria-label="Current rules">
          <div className="workflow-section-heading"><h2>{rules.batch_name}</h2><span className="registry-badge registry-approved">{rules.current ? "Version " + rules.current.version : "No rules yet"}</span></div>
          {rules.current ? <>
            <p className="registry-muted">{rules.current.mode === "WAGE_FORMULA" ? `Daily wage ${peso(rules.current.daily_wage_centavos || 0)} × days` : "Fixed amount per category"} · saved by {rules.current.created_name} · {formatRecordedDate(rules.current.created_at)}</p>
            <div className="material-table-wrap"><table className="material-table"><caption className="sr-only">Current amount per damage category</caption><thead><tr><th>Category</th>{rules.current.mode === "WAGE_FORMULA" && <th>Days</th>}<th>Amount</th></tr></thead><tbody>{KEYS.map(k => <tr key={k}><td>{DAMAGE_CATEGORIES[k]}</td>{rules.current!.mode === "WAGE_FORMULA" && <td data-label="Days">{rules.current!.rules[k]?.days}</td>}<td data-label="Amount"><strong>{peso(rules.current!.rules[k]?.amount_centavos ?? 0)}</strong></td></tr>)}<tr><td>No approved claim</td>{rules.current.mode === "WAGE_FORMULA" && <td data-label="Days">-</td>}<td data-label="Amount">{peso(rules.standard_grant_centavos)} standard grant</td></tr></tbody></table></div>
          </> : <p>No rules are saved for this batch. Approved claims cannot be paid until rules exist.</p>}
          <p className="registry-muted">Maximum grant for this batch: {peso(rules.max_grant_centavos)}.</p>
        </section>
        <details className="workflow-panel"><summary>Version history ({rules.history.length})</summary><ul>{rules.history.map(v => <li key={v.version} className="workflow-record"><p><strong>Version {v.version}</strong> · {v.mode === "WAGE_FORMULA" ? "wage formula" : "fixed"} · {v.created_name} · {formatRecordedDate(v.created_at)}</p><p>{KEYS.map(k => DAMAGE_CATEGORIES[k] + " " + peso(v.rules[k]?.amount_centavos ?? 0)).join(" · ")}</p><p className="registry-muted">{v.reason}</p></li>)}</ul></details>
      </div>
      <div className="space-y-6">
        {canEdit && draft && <form className="workflow-panel space-y-4" onSubmit={save} aria-label="New rule version"><h2>Save a new version</h2>
          <fieldset className="space-y-2"><legend>How amounts are calculated</legend>
            <label className="registry-checkbox"><input type="radio" name="mode" checked={draft.mode === "WAGE_FORMULA"} disabled={busy} onChange={() => edit({ ...draft, mode: "WAGE_FORMULA", values: { TOTALLY_DAMAGED: "", PARTIALLY_DAMAGED: "" } })} />Daily wage × days</label>
            <label className="registry-checkbox"><input type="radio" name="mode" checked={draft.mode === "FIXED"} disabled={busy} onChange={() => edit({ ...draft, mode: "FIXED", values: { TOTALLY_DAMAGED: "", PARTIALLY_DAMAGED: "" } })} />Fixed amount per category</label>
          </fieldset>
          {draft.mode === "WAGE_FORMULA" && <label>Daily wage (PHP)<input inputMode="decimal" required disabled={busy} value={draft.wage} onChange={e => edit({ ...draft, wage: e.target.value })} /></label>}
          {KEYS.map(k => <label key={k}>{DAMAGE_CATEGORIES[k]} {draft.mode === "WAGE_FORMULA" ? "(days)" : "(PHP)"}<input inputMode={draft.mode === "WAGE_FORMULA" ? "numeric" : "decimal"} required disabled={busy} value={draft.values[k]} onChange={e => edit({ ...draft, values: { ...draft.values, [k]: e.target.value } })} /><span className="registry-muted">{computed?.[k] !== null && computed?.[k] !== undefined ? "Household receives " + peso(computed[k]!) : "Enter a positive " + (draft.mode === "WAGE_FORMULA" ? "whole number of days" : "amount")}</span></label>)}
          {overLimit && <p role="alert" className="registry-notice">A category is above the {peso(rules.max_grant_centavos)} maximum grant.</p>}
          <label>Reason for this version<textarea required maxLength={512} disabled={busy} value={draft.reason} onChange={e => edit({ ...draft, reason: e.target.value })} /></label>
          {error && <p role="alert" className="registry-error">{error}</p>}
          <button className="registry-button registry-primary" disabled={busy || !online || !complete || overLimit || !draft.reason.trim()}>{busy ? "Saving..." : "Save new version"}</button>
          <p className="registry-muted">Earlier versions stay retained. Finalized lists made under older rules show as changed and need a new version.</p>
        </form>}
        <section className="workflow-panel space-y-3" aria-label="Calculated amounts"><h2>Calculated amounts</h2>
          {!rules.entitlements.length ? <p className="registry-muted">No damage claims yet for this batch.</p> : <div className="material-table-wrap"><table className="material-table"><caption className="sr-only">Calculated amount per claim</caption><thead><tr><th>Household</th><th>Claim</th><th>Amount</th></tr></thead><tbody>{rules.entitlements.map(e => <tr key={e.claim_id}><td><Link href={"/claims?" + new URLSearchParams({ claim_id: e.claim_id })}><strong>{e.household_name}</strong></Link><small>{e.barangay_name}</small></td><td data-label="Claim">{DAMAGE_CATEGORIES[e.category]}<small>{e.claim_status.replace("_", " ").toLowerCase()}</small></td><td data-label="Amount">{e.amount_centavos === null ? <span className="registry-muted">{e.blocked}</span> : <strong>{peso(e.amount_centavos)}</strong>}{e.basis === "STANDARD" && <small>standard grant</small>}{e.payout_recorded && <small>payout recorded</small>}</td></tr>)}</tbody></table></div>}
        </section>
      </div>
    </div>}
  </div>;
}
