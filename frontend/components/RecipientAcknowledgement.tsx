"use client";
import { useEffect, useRef, useState } from "react";
import { acknowledgePayout, Distribution, RecipientAcknowledgement as SavedAcknowledgement } from "@/lib/api";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { formatRecordedDate } from "@/lib/recordedDate";

export default function RecipientAcknowledgement({ record }: { record: Pick<Distribution, "distribution_id" | "beneficiary_id" | "status" | "recipient_acknowledgement"> }) {
  const { account } = useRole();
  const online = useBrowserOnline();
  const [saved, setSaved] = useState<SavedAcknowledgement | null>(record.recipient_acknowledgement || null);
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const pending = useRef(false);
  useEffect(() => { setSaved(record.recipient_acknowledgement || null); setConsent(false); setError(""); }, [record.distribution_id, record.recipient_acknowledgement]);
  const canAcknowledge = account?.role === "BENEFICIARY" && account.beneficiary_id === record.beneficiary_id && record.status === "CONFIRMED";
  async function save() {
    if (pending.current || !consent || !navigator.onLine || saved) return;
    pending.current = true; setBusy(true); setError("");
    try { setSaved(await acknowledgePayout(record.distribution_id)); setConsent(false); }
    catch (e) { setError(e instanceof Error ? e.message : "Acknowledgement could not be saved."); }
    finally { pending.current = false; setBusy(false); }
  }
  return <section aria-label="Recipient acknowledgement" className="registry-notice space-y-3">
    <h3>{saved ? "Demo payout acknowledged" : "No recipient acknowledgement recorded"}</h3>
    <p className="registry-muted">This records an account's synthetic acknowledgement. It does not prove physical cash delivery and is separate from blockchain receipt integrity.</p>
    {record.status !== "CONFIRMED" && <p>This payout is no longer recorded as confirmed. Any earlier acknowledgement remains historical evidence.</p>}
    {saved ? <><p>By {saved.account_display_name} ({saved.account_id}) at {formatRecordedDate(saved.acknowledged_at)}.</p><details className="registry-detail"><summary>Acknowledgement references</summary><dl className="receipt-references"><dt>Acknowledgement</dt><dd>{saved.acknowledgement_id}</dd><dt>Payout</dt><dd>{saved.distribution_id}</dd><dt>Recorded centavos at acknowledgement</dt><dd>{saved.amount_centavos}</dd><dt>Receipt hash at acknowledgement</dt><dd className="font-mono break-all">{saved.receipt_hash}</dd></dl></details></> : canAcknowledge ? <><label className="registry-checkbox"><input type="checkbox" checked={consent} disabled={busy} onChange={e => setConsent(e.target.checked)} />I acknowledge this synthetic payout for my linked household.</label>
      {!online && <p role="status">Reconnect to acknowledge. Nothing is queued.</p>}
      {error && <p role="alert" className="registry-error">{error}</p>}
      <button className="registry-button registry-primary" disabled={busy || !online || !consent} onClick={() => void save()}>{busy ? "Saving acknowledgement..." : "Acknowledge demo payout"}</button></> : <p>Only the linked Beneficiary account can add an acknowledgement.</p>}
  </section>;
}
