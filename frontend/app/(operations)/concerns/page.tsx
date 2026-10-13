"use client";
import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { Beneficiary, ReliefBatch, HouseholdConcern, ConcernCategory, ConcernRevision, CreateConcernPayload, ReplyConcernPayload, fetchConcerns, fetchBeneficiaries, fetchBatches, createConcern, replyToConcern } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";

const categories:Record<ConcernCategory,string>={DETAILS:'Household details',ELIGIBILITY:'Eligibility decision',PAYOUT:'Payout or amount',ARRANGEMENT:'Collection arrangement',OTHER:'Other concern'};
const statuses:Record<ConcernRevision['status'],string>={OPEN:'Open',IN_REVIEW:'In review',RESOLVED:'Resolved'};
function Concerns({requestedId}:{requestedId:string|null}) {
  const {account}=useRole(), online=useBrowserOnline();
  const [rows,setRows]=useState<HouseholdConcern[]>([]),[households,setHouseholds]=useState<Beneficiary[]>([]),[batches,setBatches]=useState<ReliefBatch[]>([]);
  const [loading,setLoading]=useState(true),[error,setError]=useState(''),[notice,setNotice]=useState(''),[busy,setBusy]=useState(false);
  const [selectedId,setSelectedId]=useState(''),[creating,setCreating]=useState(false);
  const [householdId,setHouseholdId]=useState(requestedId||account?.beneficiary_id||''),[batchId,setBatchId]=useState(''),[category,setCategory]=useState<ConcernCategory>('DETAILS'),[message,setMessage]=useState('');
  const [replyMessage,setReplyMessage]=useState(''),[staffReason,setStaffReason]=useState(''),[status,setStatus]=useState<ConcernRevision['status']>('IN_REVIEW');
  const generation=useRef(0), saving=useRef(false),pendingCreate=useRef<{serialized:string;payload:CreateConcernPayload}|null>(null),pendingReply=useRef<{serialized:string;payload:ReplyConcernPayload}|null>(null);
  const isHousehold=account?.role==='BENEFICIARY',canCreate=!!account&&account.role!=='AUDITOR',canReply=account?.role==='DSWD';
  const selected=rows.find(r=>r.concern_id===selectedId);
  const household=households.find(h=>h.beneficiary_id===householdId);
  const missingRequested=!!requestedId&&!isHousehold&&!households.some(h=>h.beneficiary_id===requestedId);
  async function load() {
    const version=++generation.current;setLoading(true);setError('');
    try { const [concerns,registry,batchList]=await Promise.all([fetchConcerns(requestedId||undefined),fetchBeneficiaries({include_historical:true}),fetchBatches()]);
      if(version!==generation.current)return;setRows(concerns);setHouseholds(registry);setBatches(batchList);setSelectedId(current=>concerns.some(r=>r.concern_id===current)?current:concerns[0]?.concern_id||'');
    } catch(e){if(version===generation.current)setError(e instanceof Error?e.message:'Concerns unavailable.');}
    finally{if(version===generation.current)setLoading(false);}
  }
  useEffect(()=>{void load();return()=>{generation.current++;};},[account?.id,requestedId]);
  useEffect(()=>{if(household)setBatchId(household.batch_id);},[household?.beneficiary_id,household?.batch_id]);
  useEffect(()=>{setReplyMessage('');setStaffReason('');setStatus('IN_REVIEW');pendingReply.current=null;},[selectedId]);
  function saveRow(row:HouseholdConcern){setRows(current=>[row,...current.filter(r=>r.concern_id!==row.concern_id)]);setSelectedId(row.concern_id);}
  async function submit(e:React.FormEvent){
    e.preventDefault();if(saving.current||!online||loading||error||!canCreate||missingRequested)return;
    saving.current=true;setBusy(true);setNotice('');setError('');
    const data={beneficiary_id:isHousehold?account?.beneficiary_id||'':householdId,batch_id:batchId,category,message:message.trim()};const serialized=JSON.stringify(data);
    if(pendingCreate.current?.serialized!==serialized)pendingCreate.current={serialized,payload:{...data,request_id:crypto.randomUUID()}};
    try{saveRow(await createConcern(pendingCreate.current.payload));setNotice('Concern submitted.');setCreating(false);setMessage('');pendingCreate.current=null;}
    catch(e){setNotice(e instanceof Error?e.message:'Concern was not saved. Retry the same details.');}
    finally{saving.current=false;setBusy(false);}
  }
  async function reply(e:React.FormEvent){
    e.preventDefault();if(saving.current||!online||loading||error||!selected||!canReply)return;
    saving.current=true;setBusy(true);setNotice('');
    const data={expected_revision:selected.current.revision,status,household_message:replyMessage.trim(),staff_reason:staffReason.trim()};const serialized=JSON.stringify({id:selected.concern_id,...data});
    if(pendingReply.current?.serialized!==serialized)pendingReply.current={serialized,payload:{...data,request_id:crypto.randomUUID()}};
    try{saveRow(await replyToConcern(selected.concern_id,pendingReply.current.payload));setNotice('Reply saved.');setReplyMessage('');setStaffReason('');pendingReply.current=null;}
    catch(e){setNotice(e instanceof Error?e.message:'Reply was not saved.');}
    finally{saving.current=false;setBusy(false);}
  }
  return <div className="registry workflow space-y-6">
    <header className="registry-header"><div><h1>{isHousehold?'My concerns':'Household concerns'}</h1><p className="registry-description">Ask staff to review a detail, decision or payout.</p></div><div className="flex flex-wrap gap-2"><button className="registry-button" disabled={loading||busy||!online} onClick={()=>void load()}>Refresh concerns</button>{canCreate&&<button className="registry-button registry-primary" disabled={loading||busy||!!error||missingRequested} onClick={()=>{setCreating(true);setNotice('');}}>Report a concern</button>}</div></header>
    {!online&&<p role="alert" className="registry-notice">Reconnect before sending. No concern is queued.</p>}
    {loading&&<p role="status">Loading concerns...</p>}{error&&<p role="alert" className="registry-error">{error} Refresh concerns to try again.</p>}{notice&&<p role="status" className="registry-notice">{notice}</p>}
    {!loading&&!error&&<>
      {missingRequested&&<section className="workflow-panel"><h2>Household unavailable</h2><p>The linked household is outside your records. No other household was selected.</p><Link href="/concerns" className="registry-button">Open permitted concerns</Link></section>}
      {creating&&canCreate&&!missingRequested&&<form onSubmit={submit} className="workflow-panel space-y-4" aria-label="Concern intake" aria-busy={busy}>
        <h2>{isHousehold?'Report a concern':'Record an assisted concern'}</h2>
        {!isHousehold&&<p className="registry-muted">Recorded under your staff account. The household does not need to share its password.</p>}
        <fieldset disabled={busy} className="space-y-4">
          {!isHousehold&&<div><label htmlFor="concern-household">Household</label><select id="concern-household" required value={householdId} disabled={!!requestedId} onChange={e=>setHouseholdId(e.target.value)}><option value="">Choose a household</option>{households.map(h=><option key={h.beneficiary_id} value={h.beneficiary_id}>{h.household_name} ({h.beneficiary_id})</option>)}</select></div>}
          {household?<p>{household.household_name} · {household.barangay_name}</p>:isHousehold?<p>Ask staff to check your missing account link. Your concern will retain the linked reference.</p>:null}
          <div><label htmlFor="concern-batch">Relief batch</label><select id="concern-batch" required value={batchId} disabled={!!household} onChange={e=>setBatchId(e.target.value)}><option value="">Choose a batch</option>{batches.map(b=><option key={b.batch_id} value={b.batch_id}>{b.calamity_name}</option>)}</select></div>
          <div><label htmlFor="concern-category">Concern about</label><select id="concern-category" value={category} onChange={e=>setCategory(e.target.value as ConcernCategory)}>{Object.entries(categories).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></div>
          <div><label htmlFor="concern-message">What needs reviewing?</label><textarea id="concern-message" required maxLength={2000} rows={4} value={message} onChange={e=>setMessage(e.target.value)} /></div>
        </fieldset>
        <p className="registry-muted">A concern does not approve eligibility, award assistance or reverse a payout.</p>
        <div className="flex flex-wrap gap-2"><button type="submit" className="registry-button registry-primary" disabled={busy||!online||!householdId||!batchId||!message.trim()}>{busy?'Saving...':'Submit concern'}</button><button type="button" className="registry-button" disabled={busy} onClick={()=>setCreating(false)}>Keep draft and close</button></div>
      </form>}
      <div className="list-workspace">
        <aside className="workflow-panel space-y-3" aria-label="Concern records"><h2>{isHousehold?'Your concerns':'Recorded concerns'}</h2>{!rows.length?<p>No concerns were returned.</p>:rows.map(row=><button className={'registry-button w-full '+(row.concern_id===selectedId?'registry-filter-selected':'')} key={row.concern_id} disabled={busy} aria-pressed={row.concern_id===selectedId} onClick={()=>{setSelectedId(row.concern_id);setNotice('');}}>{categories[row.category]} · {statuses[row.current.status]}{!isHousehold?' · '+row.beneficiary_id:''}</button>)}</aside>
        {selected&&<section className="workflow-panel space-y-4" aria-label="Selected concern"><h2>{categories[selected.category]}</h2><p className="registry-badge">{statuses[selected.current.status]} · revision {selected.current.revision}</p><p className="whitespace-pre-wrap break-words">{selected.message}</p><p className="registry-muted">Submitted {formatRecordedDate(selected.created_at)}{selected.source==='STAFF_ASSISTED'?' with staff assistance':''}</p><div className="workflow-context space-y-2"><h3>Staff response</h3><p className="whitespace-pre-wrap break-words">{selected.current.household_message}</p></div>
          <details><summary>Concern history ({selected.history.length})</summary><ul>{selected.history.map(r=><li key={r.revision} className="registry-history-entry space-y-2"><p>{statuses[r.status]} · {formatRecordedDate(r.revised_at)}</p><p className="whitespace-pre-wrap break-words">{r.household_message}</p>{r.staff_reason&&<p className="whitespace-pre-wrap break-words">Staff reason: {r.staff_reason}</p>}</li>)}</ul><p className="registry-muted break-all">Reference: {selected.concern_id}</p></details>
          {canReply&&<form onSubmit={reply} className="space-y-4" aria-label="Reply to concern"><h3>Reply to household</h3><fieldset disabled={busy} className="space-y-4"><div><label htmlFor="concern-status">Review status</label><select id="concern-status" value={status} onChange={e=>setStatus(e.target.value as ConcernRevision['status'])}>{Object.entries(statuses).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></div><div><label htmlFor="concern-reply">Response shown to household</label><textarea id="concern-reply" required rows={3} maxLength={2000} value={replyMessage} onChange={e=>setReplyMessage(e.target.value)}/></div><div><label htmlFor="concern-reason">Reason (staff only)</label><textarea id="concern-reason" required rows={2} maxLength={2000} value={staffReason} onChange={e=>setStaffReason(e.target.value)}/></div></fieldset><button className="registry-button registry-primary" disabled={busy||!online||!replyMessage.trim()||!staffReason.trim()}>{busy?'Saving...':'Save response'}</button></form>}
        </section>}
      </div>
    </>}
  </div>;
}
function QueryPage(){const params=useSearchParams();const id=params.get('beneficiary_id');return <Concerns key={id||'all'} requestedId={id}/>;}
export default function ConcernsPage(){return <Suspense fallback={<p role="status">Loading concerns...</p>}><QueryPage/></Suspense>;}
