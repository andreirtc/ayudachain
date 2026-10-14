"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Banknote, Layers3, HandCoins } from "lucide-react";
import { fetchBatchDetail, formatPeso } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";

type BatchDetail = Awaited<ReturnType<typeof fetchBatchDetail>>;
export default function BatchDetailPage() {
  const params = useParams();
  const batchId = String(params?.id || "");
  const [data, setData] = useState<BatchDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setData(null);
    setError(null);
    fetchBatchDetail(batchId)
      .then((value) => {
        if (!cancelled) setData(value);
      })
      .catch((err) => {
        if (!cancelled)
          setError(
            err instanceof Error
              ? err.message
              : "Batch details could not be loaded.",
          );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [batchId, reload]);
  const allocated =
    data?.allocations.reduce(
      (sum, allocation) =>
        sum +
        (allocation.amount_centavos ?? Math.round(allocation.amount * 100)),
      0,
    ) || 0;
  return <div className="registry workflow batch-page space-y-6">
    <header className="registry-header"><div><p className="registry-eyebrow">Relief batch</p><h1>{data?.batch.calamity_name||'Relief batch'}</h1><p className="registry-description">{data?.batch.recipient_lgu||batchId}</p></div><Link className="registry-button registry-text-button" href="/dashboard"><ArrowLeft size={16}/>Back to overview</Link></header>
    {loading&&<p role="status">Loading relief batch details...</p>}{error&&<div role="alert" className="registry-error"><h2>Batch details unavailable</h2><p>{error}</p><button className="registry-button" onClick={()=>setReload(n=>n+1)}>Retry batch details</button></div>}
    {data&&<>
      <section aria-label="Batch funding" className="audit-summary">{[{label:'Released funds',value:data.batch.amount,Icon:Banknote},{label:'Allocated funds',value:allocated/100,Icon:Layers3},{label:'Recorded payouts',value:data.distributed_amount,Icon:HandCoins}].map(({label,value,Icon})=><div className="overview-metric" key={label}><span className="metric-icon"><Icon size={20}/></span><h2>{label}</h2><p>{formatPeso(value)}</p></div>)}</section>
      <div className="audit-layout"><section aria-label="Barangay allocations" className="workflow-panel space-y-4"><div className="workflow-section-heading"><h2>Barangay allocations</h2><span className="registry-badge">{data.batch.status==='ACTIVE'?'Active batch':data.batch.status}</span></div>{!data.allocations.length?<p>No allocations are recorded for this batch.</p>:<div className="material-table-wrap"><table className="material-table"><caption className="sr-only">Recorded barangay allocations</caption><thead><tr><th>Barangay</th><th>Allocation</th><th>Planned households</th><th>Status</th></tr></thead><tbody>{data.allocations.map(a=><tr key={a.allocation_id}><td><strong>{a.barangay_name}</strong><details><summary>References</summary><p className="registry-muted">{a.allocation_id}</p><p className="registry-muted break-all">{a.blockchain_tx_hash||'No transaction recorded'}</p></details></td><td data-label="Allocation">{formatPeso(a.amount)}</td><td data-label="Planned households">{a.beneficiary_count}</td><td data-label="Status">{a.status==='ALLOCATED'?'Allocated':a.status}</td></tr>)}</tbody></table></div>}<p className="registry-muted">{data.total_distributions} payout records. Recorded amounts do not prove cash delivery.</p></section>
       <aside className="space-y-4"><section className="workflow-panel space-y-4"><h2>Fictional grant policy</h2><dl className="workflow-facts"><dt>Standard grant</dt><dd>{formatPeso(data.batch.standard_grant)}</dd><dt>Maximum grant</dt><dd>{formatPeso(data.batch.max_grant)}</dd></dl><p className="registry-muted">Amounts configured for this synthetic relief batch.</p></section><details className="workflow-panel"><summary>Batch details and references</summary><dl className="receipt-references mt-4"><dt>Batch</dt><dd>{data.batch.batch_id}</dd><dt>Source agency</dt><dd>{data.batch.source_agency}</dd><dt>Recipient LGU</dt><dd>{data.batch.recipient_lgu}</dd><dt>Purpose</dt><dd>{data.batch.purpose}</dd><dt>Stored transaction</dt><dd className="font-mono">{data.batch.blockchain_tx_hash||'None recorded'}</dd></dl><p className="registry-muted mt-4">Stored transaction references do not establish current blockchain evidence.</p></details></aside>
      </div>
      <section aria-label="Batch activity" className="workflow-panel space-y-4"><h2>Batch activity</h2>{!data.timeline.length?<p>No activity is available to this view.</p>:<ol className="audit-activity">{data.timeline.map(e=><li key={e.id} className="workflow-record"><div className="workflow-section-heading"><h3>{e.event_type.replaceAll('_',' ').toLowerCase()}</h3><span className="registry-muted">{formatRecordedDate(e.timestamp)}</span></div><p>{e.description}</p><details><summary>Event references</summary><p className="registry-muted break-all">{e.blockchain_tx_hash||'No transaction recorded'}</p></details></li>)}</ol>}</section>
    </>}
  </div>;
}
