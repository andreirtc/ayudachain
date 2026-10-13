"use client";
import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { fetchBatches, fetchValidatedLists, prepareValidatedList, finalizeValidatedList, ReliefBatch, ValidatedListVersion } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";

const areas={"BRGY-001":"San Isidro","BRGY-002":"Santa Elena","BRGY-003":"San Roque","BRGY-004":"Maligaya"};
export default function ListsPage() {
  const {account}=useRole(), online=useBrowserOnline(), params=useSearchParams(), router=useRouter();
  const [versions,setVersions]=useState<ValidatedListVersion[]>([]),[batches,setBatches]=useState<ReliefBatch[]>([]);
  const [batch,setBatch]=useState(""),[area,setArea]=useState(account?.barangay_id || "BRGY-001"),[exclude,setExclude]=useState(""),[excludeReason,setExcludeReason]=useState("");
  const [loading,setLoading]=useState(true),[busy,setBusy]=useState(false),[error,setError]=useState(""),[readError,setReadError]=useState(""),[saved,setSaved]=useState(false),[reason,setReason]=useState(""),[consent,setConsent]=useState(false);
  const [search,setSearch]=useState(""),[resultFilter,setResultFilter]=useState("all");
  const [opening,setOpening]=useState<{id:string;from:string|null}|null>(null);
  const generation=useRef(0),submitting=useRef(false),retry=useRef<string|null>(null);
  const requested=params.getAll("list_id").length>1 ? "" : params.get("list_id");
  const transitioning=opening!==null&&requested===opening.from&&requested!==opening.id;
  const selected=transitioning ? undefined : requested!==null ? versions.find(v=>v.list_id===requested) : versions[0];
  const shownRows=(selected?.snapshot.rows || []).filter(row=>(resultFilter==="all"||row.included===(resultFilter==="included"))&&(row.household_name+" "+row.beneficiary_id).toLowerCase().includes(search.toLowerCase()));
  const canPrepare=account?.role==="DSWD"||account?.role==="BARANGAY";
  async function load() {
    const current=++generation.current; setLoading(true);setReadError("");setVersions([]);
    try { const [v,b]=await Promise.all([fetchValidatedLists(),fetchBatches()]); if(current!==generation.current)return;setVersions(v);setBatches(b);setBatch(prev=>prev||b.find(x=>x.status==="ACTIVE")?.batch_id||""); }
    catch(e){if(current===generation.current)setReadError(e instanceof Error?e.message:"Lists unavailable.");}
    finally {if(current===generation.current)setLoading(false);}
  }
  useEffect(()=>{ if(account?.role!=="BENEFICIARY")void load();return()=>{generation.current++;}; },[account?.id]);
  useEffect(()=>{setReason("");setConsent(false);setError("");setSearch("");setResultFilter("all");},[selected?.list_id]);
  useEffect(()=>{if(opening&&(requested!==opening.from||requested===opening.id))setOpening(null);},[requested,opening]);
  function changed(){retry.current=null;setSaved(false);setError("");}
  async function prepare(event:FormEvent) {
    event.preventDefault();if(submitting.current||!online)return;submitting.current=true;setBusy(true);setError("");
    retry.current ||= crypto.randomUUID();
    try { const exclusions=Object.fromEntries(exclude.split(/\s+/).filter(Boolean).map(id=>[id,excludeReason])); const result=await prepareValidatedList({batch_id:batch,barangay_id:area,request_id:retry.current,exclusions});setVersions(prev=>[result,...prev.filter(v=>v.list_id!==result.list_id)]);setOpening({id:result.list_id,from:requested});setSaved(true);router.replace("/lists?"+new URLSearchParams({list_id:result.list_id})); }
    catch(e){setError(e instanceof Error?e.message:"Preparation failed.");}
    finally{submitting.current=false;setBusy(false);}
  }
  async function finalize() {
    if(!selected||!consent||!reason.trim()||submitting.current||!online)return;submitting.current=true;setBusy(true);setError("");
    try{const result=await finalizeValidatedList(selected.list_id,reason);setVersions(prev=>prev.map(v=>v.list_id===result.list_id?result:v));setConsent(false);setReason("");}
    catch(e){setError(e instanceof Error?e.message:"Finalization failed.");}
    finally{submitting.current=false;setBusy(false);}
  }
  if(account?.role==="BENEFICIARY")return <section className="registry space-y-3"><h1>Validated lists are a staff task</h1><Link href="/household" className="registry-button">My household</Link></section>;
  return <div className="registry workflow validated-lists-page space-y-6">
    <header className="registry-header"><div><h1>Validated lists</h1><p className="registry-description">Prepare, inspect and finalize a version for one barangay.</p></div><Link href="/beneficiaries" className="registry-button">Registration and review</Link></header>
    {!online&&<p role="alert" className="registry-notice">Offline. These are the last loaded versions. Reconnect and refresh before preparing or finalizing; nothing is queued.</p>}
    {loading&&<p role="status">Loading list versions...</p>}
    {readError&&<div role="alert" className="registry-error"><p>{readError}</p><button className="registry-button" disabled={loading||!online} onClick={()=>void load()}>Retry lists</button></div>}
    {error&&<p role="alert" className="registry-error">{error}</p>}
    {!loading&&!readError&&<div className="workflow-columns list-workspace">
      <div className="space-y-6">
        {canPrepare&&<form className="workflow-panel space-y-4" onSubmit={prepare}><h2>Prepare a version</h2><p className="registry-muted">Registration and CSV remain pending until an individual review. Preparing a list never approves a household.</p>
          <label htmlFor="list-batch">Relief batch</label><select id="list-batch" required disabled={busy||saved} value={batch} onChange={e=>{setBatch(e.target.value);changed();}}>{batches.filter(b=>b.status==="ACTIVE").map(b=><option key={b.batch_id} value={b.batch_id}>{b.calamity_name}</option>)}</select>
          <label htmlFor="list-area">Barangay</label><select id="list-area" disabled={busy||saved||account?.role==="BARANGAY"} value={area} onChange={e=>{setArea(e.target.value);changed();}}>{Object.entries(areas).map(([id,name])=><option key={id} value={id}>{name}</option>)}</select>
          <details><summary>Explicit staff exclusions</summary><label>Excluded household references<textarea disabled={busy||saved} value={exclude} onChange={e=>{setExclude(e.target.value);changed();}} placeholder="One reference per line" /></label><label>Reason for these exclusions<textarea maxLength={512} required={!!exclude.trim()} disabled={busy||saved} value={excludeReason} onChange={e=>{setExcludeReason(e.target.value);changed();}} /></label></details>
          {saved?<><p role="status" className="registry-success">Preparation saved. Inspect the frozen version.</p><button type="button" className="registry-button" onClick={changed}>Prepare a new version</button></>:<button className="registry-button registry-primary" disabled={busy||!online||!batch}>{busy?"Saving...":"Prepare list version"}</button>}
        </form>}
        <section className="workflow-panel space-y-3" aria-label="List versions"><div className="workflow-section-heading"><h2>Retained versions</h2><button className="registry-button" disabled={busy||loading||!online} onClick={()=>void load()}>Refresh lists</button></div>{!versions.length?<p>No list versions have been prepared in your scope.</p>:<ul>{versions.map(v=><li className="workflow-record" key={v.list_id}><Link className="version-row" aria-current={v.list_id===selected?.list_id?"page":undefined} href={"/lists?"+new URLSearchParams({list_id:v.list_id})}>{v.snapshot.barangay_name} · version {v.version}</Link><p>{v.state==="FINALIZED"?"Staff finalized":"Prepared for inspection"}{v.stale?" · Changed since preparation":""}</p><p className="registry-muted">{v.snapshot.batch_name}</p></li>)}</ul>}</section>
      </div>
      <section className="workflow-panel space-y-4" aria-label="Selected list">
        {transitioning?<p role="status">Opening the saved version...</p>:!selected?<><h2>{requested!==null?"List unavailable":canPrepare?"Select or prepare a list":"No list version available"}</h2><p>{requested!==null?"That exact version is missing or outside your scope. No other version was substituted.":canPrepare?"A saved version keeps its original record and decision references.":"Assigned staff need to prepare a version before you can inspect it."}</p></>:<>
          <h2>{selected.snapshot.barangay_name} · version {selected.version}</h2><p>{selected.state==="FINALIZED"?"Staff-finalized list":"Prepared list; human finalization required"}</p><p className="registry-muted">{selected.snapshot.batch_name} · prepared {formatRecordedDate(selected.prepared_at)} by {selected.prepared_by}</p>
          {selected.stale&&<p role="alert" className="registry-notice">{selected.current_check==="UNAVAILABLE"?"Current records cannot be reconciled with this version.":"Current records changed after preparation."} This original version stays retained. Prepare and inspect a new version for further planning.</p>}
          <p>{selected.snapshot.rows.filter(r=>r.included).length} included · {selected.snapshot.rows.filter(r=>!r.included).length} excluded</p>
          <div className="flex flex-wrap gap-3"><label>Find a listed household<input value={search} onChange={e=>setSearch(e.target.value)} /></label><div><label htmlFor="list-result">List result</label><select id="list-result" value={resultFilter} onChange={e=>setResultFilter(e.target.value)}><option value="all">All records</option><option value="included">Included</option><option value="excluded">Excluded</option></select></div></div>
          {!shownRows.length&&<p>No records match these filters.</p>}
          <ul className="list-frozen-rows" tabIndex={0} aria-label="Frozen household rows">{shownRows.map(row=><li key={row.beneficiary_id} className="workflow-record"><h3>{row.household_name}</h3><p><code>{row.beneficiary_id}</code> · {row.included?"✓ Included":"Excluded"}</p>{row.exclusion_reasons.map(r=><p key={r} className="registry-muted">{r}</p>)}<Link className="registry-button registry-text-button" href={"/beneficiaries?"+new URLSearchParams({beneficiary_id:row.beneficiary_id})}>Inspect current household</Link><details><summary>Frozen decision reference</summary>{row.decision?<><p>{row.decision.review_id} · {row.decision.decision}</p><p>{formatRecordedDate(row.decision.at)}{row.decision.actor?" · "+row.decision.actor:""}</p>{row.decision.reason&&<p>{row.decision.reason}</p>}</>:<p>No retained approval decision. No official approval was backfilled.</p>}</details></li>)}</ul>
          {selected.finalization?<div className="workflow-context"><h3>Finalization retained</h3><p>{selected.finalization.name} · {formatRecordedDate(selected.finalization.at)}</p>{selected.finalization.reason&&<p>{selected.finalization.reason}</p>}<Link className="registry-button mt-3" href={"/arrangements?"+new URLSearchParams({list_id:selected.list_id})}>Payout arrangement</Link></div>:account?.role==="DSWD"&&<div className="registry-decision"><h3>Finalize inspected version</h3><label>Finalization reason<textarea maxLength={512} disabled={busy} value={reason} onChange={e=>setReason(e.target.value)} /></label><label className="registry-checkbox"><input type="checkbox" checked={consent} disabled={busy} onChange={e=>setConsent(e.target.checked)} />I inspected the included records, exclusions and retained approval references.</label><button className="registry-button registry-primary" disabled={busy||!online||selected.stale||!consent||!reason.trim()||!selected.snapshot.rows.some(r=>r.included)} onClick={()=>void finalize()}>{busy?"Saving...":"Finalize list version"}</button></div>}
          <details><summary>About this list evidence</summary><p className="registry-muted">Local staff evidence. This list does not reserve funds or record a payout; current approval, budget and once-only checks still apply.</p></details>
        </>}
      </section>
    </div>}
  </div>;
}
