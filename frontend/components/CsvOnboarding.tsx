"use client";
import { useEffect, useRef, useState } from "react";
import RegistryDialog from "./RegistryDialog";
import { authenticatedFetch, fetchBatches, getApiBase, ReliefBatch } from "@/lib/api";
import { useBrowserOnline } from "@/lib/useBrowserOnline";

type Row = { line: number; data: { beneficiary_id: string; household_name: string; barangay_name: string }; errors: string[]; matches: { beneficiary_id: string; household_name: string; record_status: string; score: number; same_dafac: boolean }[] };
type Plan = { import_id: string | null; valid: boolean; total_rows: number; rows: Row[] };
type Saved = { import_id: string; imported_by: string; imported_at: string; beneficiary_ids: string[] };
async function call(path: string, body?: unknown) {
  const response = await authenticatedFetch(getApiBase() + "/api/beneficiaries/csv/" + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
  if (!response.ok) { const data = await response.json(); throw new Error(typeof data.detail === "string" ? data.detail : "CSV request failed. Try again."); }
  return response.json();
}
export default function CsvOnboarding({ onClose, onReview }: { onClose: () => void; onReview: (id: string) => void }) {
  const online = useBrowserOnline();
  const pending = useRef(false);
  const [busy, setBusy] = useState(false);
  const [batches, setBatches] = useState<ReliefBatch[]>([]);
  const [batch, setBatch] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [saved, setSaved] = useState<Saved | null>(null);
  const [error, setError] = useState("");
  const [attempted, setAttempted] = useState(false);
  const [batchRetry, setBatchRetry] = useState(0);
  useEffect(() => { let cancelled = false; fetchBatches().then(rows => { if (!cancelled) setBatches(rows.filter(row => row.status === "ACTIVE")); }).catch(() => { if (!cancelled) setError("Relief batches could not be loaded."); }); return () => { cancelled = true; }; }, [batchRetry]);
  async function preview() {
    if (pending.current || !navigator.onLine || !file || !batch) return;
    pending.current = true; setBusy(true); setError(""); setPlan(null); setSaved(null); setAttempted(false);
    try {
      if (file.size > 131072) throw new Error("CSV must be at most 128 KiB.");
      const bytes = await file.arrayBuffer();
      let content: string;
      try { content = new TextDecoder("utf-8", { fatal: true }).decode(bytes); } catch { throw new Error("Save this CSV as UTF-8 and preview again."); }
      setPlan(await call("preview", { batch_id: batch, csv_content: content }));
    } catch (e) { setError(e instanceof Error ? e.message : "Preview unavailable."); }
    finally { pending.current = false; setBusy(false); }
  }
  async function importRows() {
    if (pending.current || !navigator.onLine || !plan?.import_id || saved) return;
    pending.current = true; setBusy(true); setError(""); setAttempted(true);
    try { setSaved(await call(encodeURIComponent(plan.import_id) + "/import")); }
    catch (e) { setError((e instanceof Error ? e.message : "Import unavailable.") + " Retry this preview to retrieve any saved result. If the preview is stale or expired, preview the file again."); }
    finally { pending.current = false; setBusy(false); }
  }
  return <RegistryDialog title="Import a CSV" wide busy={busy} onClose={onClose}><div className="registry-dialog-content space-y-4">
    <p>Preview up to 200 fictional households. Import adds pending records for DSWD review; it does not approve eligibility or replace history.</p>
    <details className="registry-detail"><summary>CSV format</summary><p className="break-words">UTF-8, at most 128 KiB. Required headers: beneficiary_id, household_name, barangay_id, barangay_name. Optional: dafac_id, contact_number. References use letters, numbers, dots, underscores and hyphens. Use the current demo barangay names.</p><a href="/import-households.csv" download className="registry-button">Download fictional sample</a></details>
    {!online && <p role="status" className="registry-notice">Reconnect to preview or import. No import is queued.</p>}
    {!saved && <><label htmlFor="csv-batch">Relief batch</label><select id="csv-batch" disabled={busy} value={batch} onChange={e => { setBatch(e.target.value); setPlan(null); setError(""); }}><option value="">Choose an active batch</option>{batches.map(row => <option key={row.batch_id} value={row.batch_id}>{row.calamity_name} ({row.batch_id})</option>)}</select>
    {!batches.length && <button className="registry-button" disabled={busy || !online} onClick={() => { setError(""); setBatchRetry(v => v + 1); }}>Retry loading batches</button>}
    <label htmlFor="csv-import-file">CSV to import</label><input id="csv-import-file" type="file" accept=".csv,text/csv" disabled={busy} onChange={e => { setFile(e.target.files?.[0] || null); setPlan(null); setError(""); }} />
    <button className="registry-button" disabled={busy || !online || !file || !batch} onClick={() => void preview()}>Preview selected CSV</button></>}
    {busy && <p role="status">{attempted ? "Importing pending households..." : "Preparing preview..."}</p>}
    {error && <p role="alert" className="registry-error">{error}</p>}
    {plan && !saved && <section aria-label="Import preview" className="space-y-3"><p role="status">{plan.total_rows} rows. {plan.valid ? "Ready for explicit import." : "Correct the row errors and preview again. Nothing has been imported."}</p>
      {plan.rows.map(row => <article key={row.line} className="registry-csv-pair space-y-2"><h3>Row {row.line}: {row.data.household_name || "Missing household name"}</h3><p className="break-all">{row.data.beneficiary_id} · {row.data.barangay_name}</p>{row.errors.map((msg, i) => <p key={i} className="text-rose-700">{msg}</p>)}{row.matches.length > 0 && <details className="registry-detail"><summary>Possible matches ({row.matches.length})</summary><ul>{row.matches.map(match => <li key={match.beneficiary_id} className="break-words">{match.household_name} ({match.beneficiary_id}), {match.record_status === "IN_FILE" ? "in this file" : match.record_status === "DUPLICATE" ? "retained duplicate" : "existing registry"}; {match.same_dafac ? "same DAFAC" : Math.round(match.score * 100) + "% name/locality similarity"}. Human review required.</li>)}</ul></details>}</article>)}
      <button className="registry-button registry-primary" disabled={busy || !online || !plan.valid} onClick={() => void importRows()}>{attempted ? "Retry import" : "Import pending households"}</button>
    </section>}
    {saved && <section role="status" className="registry-notice space-y-3"><h3>{saved.beneficiary_ids.length} households imported for review</h3><p>Saved by {saved.imported_by}. No household was automatically approved.</p>{saved.beneficiary_ids.map(id => <button key={id} className="registry-button break-all" onClick={() => onReview(id)}>Review {id}</button>)}</section>}
    <button className="registry-button" disabled={busy} onClick={onClose}>Back to households</button>
  </div></RegistryDialog>;
}
