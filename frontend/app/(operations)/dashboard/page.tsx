"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { fetchDashboard, DashboardStats, formatPeso } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";
import { Banknote, Layers3, HandCoins, Wallet, ArrowRight, RefreshCw, Activity, Users } from "lucide-react";
import { useRole } from "@/lib/roleContext";

export default function DashboardPage() {
  const { account } = useRole();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const version = useRef(0);
  const loadData = async () => {
    const request = ++version.current;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDashboard();
      if (request === version.current) setStats(data);
    } catch (err) {
      if (request === version.current)
        setError(
          err instanceof Error
            ? err.message
            : "Relief summary could not be loaded.",
        );
    } finally {
      if (request === version.current) setLoading(false);
    }
  };
  useEffect(() => {
    void loadData();
    return () => { version.current++; };
  }, [account?.id]);
  const nextAction=account?.role==='BENEFICIARY'?{title:'Your household',text:'Find your collection instructions and saved receipts.',label:'My household',href:'/household'}:account?.role==='DISBURSING'?{title:'At the payout desk',text:'Choose a household and check its amount before recording.',label:'Open payout desk',href:'/distributions'}:account?.role==='AUDITOR'?{title:'Inspect the records',text:'Read the balances, exceptions and receipt evidence.',label:'Open audit',href:'/audit'}:account?{title:'Continue household review',text:'Inspect pending records and retain each decision.',label:'Open households',href:'/beneficiaries'}:{title:'Explore the demo',text:'Use a synthetic account to open a household or staff workspace.',label:'Sign in to continue',href:'/sign-in'};
  return <div className="registry workflow overview-page space-y-6">
    <header className="registry-header"><div><p className="registry-eyebrow">Relief operations</p><h1>Relief overview</h1><p className="registry-description">{stats?.calamity_name||'Funding, household review and recorded assistance.'}</p></div><button className="registry-button" disabled={loading} onClick={()=>void loadData()}><RefreshCw size={16}/>{loading?'Refreshing...':'Refresh overview'}</button></header>
    {loading&&<p role="status">Loading relief summary...</p>}{error&&<div role="alert" className="registry-error"><h2>Overview refresh unavailable</h2><p>{error}{stats?' Totals below are from the previous successful read.':' Try again to load the summary.'}</p><button className="registry-button" disabled={loading} onClick={()=>void loadData()}>Retry overview</button></div>}
    {stats&&<>
      <section aria-label="Recorded funding" className="overview-metrics">{[{label:'Released funds',value:stats.total_released,Icon:Banknote},{label:'Allocated funds',value:stats.total_allocated,Icon:Layers3},{label:'Recorded payouts',value:stats.total_distributed,Icon:HandCoins},{label:'Unallocated funds',value:stats.unallocated_funds,Icon:Wallet}].map(({label,value,Icon})=><div className="overview-metric" key={label}><span className="metric-icon"><Icon size={20}/></span><h2>{label}</h2><p>{formatPeso(value)}</p></div>)}</section>
      <div className="overview-layout">
        <section aria-label="Recent activity" className="workflow-panel space-y-4"><div className="workflow-section-heading"><h2>Recent activity</h2><Link href={'/batch/'+stats.batch_id} className="registry-button registry-text-button">View batch <ArrowRight size={16}/></Link></div><p className="registry-muted">{account?.role==='DSWD'||account?.role==='AUDITOR'?'Events available to your office account.':'Public activity shows funding and allocations.'}</p>{!stats.recent_transactions.length&&<p>No recent activity is available.</p>}<ol className="overview-activity">{stats.recent_transactions.map((event,i)=><li key={i} className="activity-row"><span className="activity-icon"><Activity size={18}/></span><div><p>{event.description}</p><span className="registry-muted">{formatRecordedDate(event.timestamp)}</span></div>{typeof event.amount==='number'&&Number.isFinite(event.amount)&&<strong>{formatPeso(event.amount)}</strong>}</li>)}</ol><details><summary>Event references</summary><ul>{stats.recent_transactions.map((e,i)=><li key={i} className="workflow-record"><p>{e.event_type}</p><p className="registry-muted break-all">{e.tx_hash||'No transaction recorded'}</p></li>)}</ul></details></section>
        <aside className="space-y-4"><section className="workflow-panel overview-next space-y-4"><p className="registry-eyebrow">Your next step</p><h2>{nextAction.title}</h2><p>{nextAction.text}</p><Link href={nextAction.href} className="registry-button registry-primary">{nextAction.label}<ArrowRight size={16}/></Link></section><section className="workflow-panel space-y-4" aria-label="Household and payout counts"><div className="workflow-section-heading"><h2>Household progress</h2><Users size={20}/></div><dl className="workflow-facts"><dt>Active households</dt><dd>{stats.total_beneficiaries}</dd><dt>Approved</dt><dd>{stats.verified_beneficiaries}</dd><dt>Review flags</dt><dd>{stats.flagged_records}</dd><dt>Payouts recorded</dt><dd>{stats.confirmed_distributions}</dd>{stats.historical_beneficiaries>0&&<><dt>Retained duplicates</dt><dd>{stats.historical_beneficiaries}</dd></>}</dl><p className="registry-muted">Recorded payouts are separate from verified receipt hashes.</p></section><details className="workflow-panel"><summary>Blockchain service details</summary><div className="space-y-3 mt-3"><p>{error?'The latest service refresh failed.':stats.blockchain_status==='CONNECTED'?'The backend reported a connection at the last refresh.':'The configured blockchain is unavailable at the last refresh.'}</p><dl className="receipt-references"><dt>Network</dt><dd>{stats.active_network||'Not reported'}</dd><dt>Contract</dt><dd className="font-mono">{stats.contract_address||'Not reported'}</dd></dl><p className="registry-muted">A connection or transaction reference does not verify a receipt.</p></div></details></aside>
      </div>
    </>}
  </div>;
}
