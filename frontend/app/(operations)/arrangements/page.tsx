"use client";
import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { ArrangementDetails, PayoutArrangement, ValidatedListVersion, createArrangement, fetchArrangements, fetchValidatedLists, reviseArrangement } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";

const blank:ArrangementDetails={collection_date:"",time_window:"",site:"",requirements:[],responsible_staff:""};
const collectionDay=(value:string)=>new Date(value+"T00:00:00").toLocaleDateString("en-PH",{weekday:"long",year:"numeric",month:"long",day:"numeric"});

function DetailsFields({value,onChange,disabled}:{value:ArrangementDetails;onChange:(v:ArrangementDetails)=>void;disabled:boolean}) {
  return <>
    <label>Collection date<input type="date" required disabled={disabled} value={value.collection_date} onChange={e=>onChange({...value,collection_date:e.target.value})} /></label>
    <label>Time window<input required maxLength={64} disabled={disabled} placeholder="8:00 AM - 12:00 NN" value={value.time_window} onChange={e=>onChange({...value,time_window:e.target.value})} /></label>
    <label>Collection site<input required maxLength={200} disabled={disabled} value={value.site} onChange={e=>onChange({...value,site:e.target.value})} /></label>
    <label>Requirements to bring (one per line)<textarea required disabled={disabled} value={value.requirements.join("\n")} onChange={e=>onChange({...value,requirements:e.target.value.split("\n")})} /></label>
    <label>Responsible staff shown to households<input required maxLength={128} disabled={disabled} value={value.responsible_staff} onChange={e=>onChange({...value,responsible_staff:e.target.value})} /></label>
  </>;
}
const tidy=(v:ArrangementDetails)=>({...v,requirements:v.requirements.map(r=>r.trim()).filter(Boolean)});

export default function ArrangementsPage() {
  const {account}=useRole(), online=useBrowserOnline(), params=useSearchParams(), router=useRouter();
  const [arrangements,setArrangements]=useState<PayoutArrangement[]>([]),[lists,setLists]=useState<ValidatedListVersion[]>([]);
  const [loading,setLoading]=useState(true),[busy,setBusy]=useState(false),[readError,setReadError]=useState(""),[error,setError]=useState(""),[notice,setNotice]=useState("");
  const [listId,setListId]=useState(""),[draft,setDraft]=useState<ArrangementDetails>(blank),[edit,setEdit]=useState<ArrangementDetails|null>(null),[reason,setReason]=useState(""),[cancelling,setCancelling]=useState(false);
  const generation=useRef(0),submitting=useRef(false),retry=useRef<string|null>(null);
  const requested=params.getAll("list_id").length>1?"":params.get("list_id");
  const selected=requested!==null?arrangements.find(a=>a.list_id===requested):arrangements[0];
  const canEdit=account?.role==="DSWD"||account?.role==="BARANGAY";
  const open=lists.filter(l=>l.state==="FINALIZED"&&!l.stale&&!arrangements.some(a=>a.list_id===l.list_id));
  async function load() {
    const current=++generation.current;setLoading(true);setReadError("");
    try{const [a,l]=await Promise.all([fetchArrangements(),fetchValidatedLists()]);if(current!==generation.current)return;setArrangements(a);setLists(l);}
    catch(e){if(current===generation.current)setReadError(e instanceof Error?e.message:"Arrangements unavailable.");}
    finally{if(current===generation.current)setLoading(false);}
  }
  useEffect(()=>{if(account&&account.role!=="BENEFICIARY")void load();return()=>{generation.current++;};},[account?.id]);
  useEffect(()=>{setEdit(null);setReason("");setCancelling(false);setError("");retry.current=null;},[selected?.arrangement_id]);
  useEffect(()=>{if(requested&&!arrangements.some(a=>a.list_id===requested)&&open.some(l=>l.list_id===requested))setListId(requested);else if(!listId&&open[0])setListId(open[0].list_id);},[requested,lists,arrangements]);
  function changed(){retry.current=null;setError("");setNotice("");}
  async function run(action:()=>Promise<PayoutArrangement>,message:string) {
    if(submitting.current||!online)return;submitting.current=true;setBusy(true);setError("");retry.current||=crypto.randomUUID();
    try{const result=await action();setArrangements(prev=>[result,...prev.filter(a=>a.arrangement_id!==result.arrangement_id)]);retry.current=null;setNotice(message);setEdit(null);setReason("");setCancelling(false);router.replace("/arrangements?"+new URLSearchParams({list_id:result.list_id}));return true;}
    catch(e){setError(e instanceof Error?e.message:"Change was not saved.");return false;}
    finally{submitting.current=false;setBusy(false);}
  }
  async function publish(event:FormEvent){event.preventDefault();if(await run(()=>createArrangement({...tidy(draft),list_id:listId,request_id:retry.current!}),"Arrangement published to included households."))setDraft(blank);}
  function revise(event:FormEvent){event.preventDefault();if(!selected)return;void run(()=>reviseArrangement(selected.arrangement_id,{request_id:retry.current!,expected_revision:selected.current.revision,action:cancelling?"CANCEL":"EDIT",reason,details:cancelling||!edit?null:tidy(edit)}),cancelling?"Arrangement cancelled. Households now see the cancellation.":"Updated arrangement saved; earlier revisions stay retained.");}
  if(account?.role==="BENEFICIARY")return <section className="registry space-y-3"><h1>Payout arrangements are a staff task</h1><p>Your collection instructions appear on your household home.</p><Link href="/household" className="registry-button">My household</Link></section>;
  const cancelled=selected?.current.state==="CANCELLED";
  return <div className="registry workflow space-y-6">
    <header className="registry-header"><div><h1>Payout arrangements</h1><p className="registry-description">Publish the collection date, site and requirements for a finalized list. Included households see these instructions on their home.</p></div><Link href="/lists" className="registry-button">Validated lists</Link></header>
    {!online&&<p role="alert" className="registry-notice">Offline. These are the last loaded arrangements. Reconnect before publishing or changing; nothing is queued.</p>}
    {loading&&<p role="status">Loading arrangements...</p>}
    {readError&&<div role="alert" className="registry-error"><p>{readError}</p><button className="registry-button" disabled={loading||!online} onClick={()=>void load()}>Retry arrangements</button></div>}
    {notice&&<p role="status" className="registry-success">{notice}</p>}
    {error&&<p role="alert" className="registry-error">{error}</p>}
    {!loading&&!readError&&<div className="workflow-columns list-workspace">
      <div className="space-y-6">
        {canEdit&&<form className="workflow-panel space-y-4" onSubmit={publish}><h2>Publish an arrangement</h2>
          {!open.length?<p>No finalized, unchanged list version is waiting for an arrangement. <Link className="underline" href="/lists">Finalize a list first.</Link></p>:<>
            <label htmlFor="arrangement-list">Finalized list version</label><select id="arrangement-list" disabled={busy} value={listId} onChange={e=>{setListId(e.target.value);changed();}}>{open.map(l=><option key={l.list_id} value={l.list_id}>{l.snapshot.barangay_name} · version {l.version} · {l.snapshot.rows.filter(r=>r.included).length} included</option>)}</select>
            <DetailsFields value={draft} disabled={busy} onChange={v=>{setDraft(v);changed();}} />
            <button className="registry-button registry-primary" disabled={busy||!online||!listId}>{busy?"Saving...":"Publish arrangement"}</button></>}
          <p className="registry-muted">An arrangement tells households where and when to collect. It does not approve anyone or authorize a payout; eligibility, budget and once-only checks still apply at the desk. No SMS is sent.</p>
        </form>}
        <section className="workflow-panel space-y-3" aria-label="Arrangements"><div className="workflow-section-heading"><h2>Published arrangements</h2><button className="registry-button" disabled={busy||loading||!online} onClick={()=>void load()}>Refresh</button></div>
          {!arrangements.length?<p>No arrangements have been published in your scope.</p>:<ul>{arrangements.map(a=><li className="workflow-record" key={a.arrangement_id}><Link className="registry-button" aria-current={a.arrangement_id===selected?.arrangement_id?"page":undefined} href={"/arrangements?"+new URLSearchParams({list_id:a.list_id})}>{a.barangay_name} · {collectionDay(a.current.collection_date)}</Link><p>{a.current.state==="CANCELLED"?"Cancelled":"Scheduled"} · list version {a.list_version}{a.superseded?" · Superseded by a newer list":""}</p></li>)}</ul>}
        </section>
      </div>
      <section className="workflow-panel space-y-4" aria-label="Selected arrangement">
        {!selected?<><h2>{requested!==null&&!open.some(l=>l.list_id===requested)?"Arrangement unavailable":"Select an arrangement"}</h2><p>{requested!==null&&!open.some(l=>l.list_id===requested)?"No arrangement exists for that list in your scope. No other arrangement was substituted.":"Choose a published arrangement to inspect its current instructions and history."}</p></>:<>
          <h2>{selected.barangay_name} · list version {selected.list_version}</h2>
          <p className={"registry-badge "+(cancelled?"registry-pending":"registry-approved")}>{cancelled?"Cancelled":"Scheduled"} · revision {selected.current.revision}</p>
          <p className="registry-muted">{selected.batch_name} · {selected.included_households} included household{selected.included_households===1?"":"s"}</p>
          {selected.superseded&&<p role="alert" className="registry-notice">A newer finalized list exists for this area. Households no longer see these instructions; publish an arrangement for the newer version.</p>}
          <dl className="receipt-references"><dt>Date</dt><dd>{collectionDay(selected.current.collection_date)}</dd><dt>Time</dt><dd>{selected.current.time_window}</dd><dt>Site</dt><dd>{selected.current.site}</dd><dt>Bring</dt><dd><ul>{selected.current.requirements.map(r=><li key={r}>{r}</li>)}</ul></dd><dt>Responsible staff</dt><dd>{selected.current.responsible_staff}</dd></dl>
          {canEdit&&!cancelled&&!selected.superseded&&(edit||cancelling?<form className="registry-decision space-y-3" onSubmit={revise}><h3>{cancelling?"Cancel this arrangement":"Edit this arrangement"}</h3>
            {!cancelling&&edit&&<DetailsFields value={edit} disabled={busy} onChange={v=>{setEdit(v);changed();}} />}
            <label>Reason (staff only)<textarea required maxLength={512} disabled={busy} value={reason} onChange={e=>{setReason(e.target.value);changed();}} /></label>
            <div className="flex flex-wrap gap-3"><button className="registry-button registry-primary" disabled={busy||!online||!reason.trim()}>{busy?"Saving...":cancelling?"Confirm cancellation":"Save new revision"}</button><button type="button" className="registry-button" disabled={busy} onClick={()=>{setEdit(null);setCancelling(false);setReason("");changed();}}>Keep current</button></div>
          </form>:<div className="flex flex-wrap gap-3"><button className="registry-button" onClick={()=>{const c=selected.current;setEdit({collection_date:c.collection_date,time_window:c.time_window,site:c.site,requirements:c.requirements,responsible_staff:c.responsible_staff});}}>Edit arrangement</button><button className="registry-button" onClick={()=>setCancelling(true)}>Cancel arrangement</button></div>)}
          <details><summary>Revision history ({selected.history.length})</summary><ul>{selected.history.map(h=><li key={h.revision} className="workflow-record"><p>Revision {h.revision} · {h.state==="CANCELLED"?"Cancelled":"Scheduled"} · {formatRecordedDate(h.revised_at)}{h.revised_by?" · "+h.revised_by:""}</p><p>{collectionDay(h.collection_date)} · {h.time_window} · {h.site}</p>{h.reason&&<p className="registry-muted">{h.reason}</p>}</li>)}</ul></details>
          <p className="registry-muted">Revisions are append-only local synthetic records. Households see only the current revision, never staff reasons.</p>
        </>}
      </section>
    </div>}
  </div>;
}
