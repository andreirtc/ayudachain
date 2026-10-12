"use client";
import {useEffect,useRef,useState} from 'react';
import {Actor,Ref,request} from '@/lib/mvp-client';
import {readable,Status} from './UI';
import {useSearchParams} from 'next/navigation';

type Match={household_id:string|null;display_id:string|null;row_index?:number;name_similarity:string;address_similarity:string;birth_date_comparison:string;reason:string};
type Row={index:number;values:Record<string,string>;status:string;errors:string[];warnings:string[];matches:Match[];resources?:{type:string;id:string}[];replayed?:boolean};
type Preview={digest:string;rows:Row[];duplicate_limitations:string};
type Outcome={index:number;status:string;error?:string;errors?:string[];warnings?:string[];replayed?:boolean;resources?:{type:string;id:string}[]};
type Template={content:string;description:string;max_rows:number;max_bytes:number};

export default function CsvIntake({actor,onSaved}:{actor:Actor;onSaved?:()=>void|Promise<void>}){
  const search=useSearchParams();
  function householdHref(id:string){const query=new URLSearchParams(search.toString());query.set('record',id);return `?${query.toString()}#household-${id}`;}
  const [template,setTemplate]=useState<Template|null>(null),[barangays,setBarangays]=useState<Ref[]>([]);
  const [content,setContent]=useState(''),[fileName,setFileName]=useState(''),[preview,setPreview]=useState<Preview|null>(null),[selected,setSelected]=useState<number[]>([]),[outcomes,setOutcomes]=useState<Outcome[]>([]);
  const [busy,setBusy]=useState(false),[error,setError]=useState(''),[uncertain,setUncertain]=useState(false);
  const control=useRef<AbortController|null>(null),attempt=useRef<number[]>([]),upload=useRef<HTMLInputElement|null>(null);
  useEffect(()=>{const c=new AbortController();control.current=c;
    Promise.all([request<Template>('/registry/csv/template',actor.id,c.signal),request<Ref[]>('/barangays',actor.id,c.signal)]).then(([t,b])=>{setTemplate(t);setBarangays(b.filter(v=>actor.role!=='barangay'||v.id===actor.barangay_id));}).catch(e=>{if(e.name!=='AbortError')setError(e.message);});
    return()=>c.abort();
  },[actor.id,actor.role,actor.barangay_id]);
  function reset(){setContent('');setFileName('');setPreview(null);setSelected([]);setOutcomes([]);setError('');setUncertain(false);attempt.current=[];if(upload.current)upload.current.value='';}
  function download(){if(!template)return;const url=URL.createObjectURL(new Blob([template.content],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`ayudachain-${actor.role}-household-template.csv`;a.click();URL.revokeObjectURL(url);}
  async function loadFile(file:File){
    reset();setBusy(true);
    try{
      if(!template||file.size>template.max_bytes)throw new Error('Choose a UTF-8 CSV file up to 256 KB.');
      const text=new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer());
      const staged=await request<Preview>('/registry/csv/preview',actor.id,control.current?.signal,{content:text});
      setContent(text);setFileName(file.name);setPreview(staged);setOutcomes(staged.rows.filter(r=>r.status==='saved').map(r=>({index:r.index,status:'saved',replayed:true,resources:r.resources})));
    }catch(e){if(e instanceof Error&&e.name!=='AbortError')setError(`${e.message}. Correct the file and upload it again.`);}finally{setBusy(false);}
  }
  async function confirm(retry=false){
    if(!preview)return;const rows=retry?attempt.current:selected;if(!rows.length)return;
    attempt.current=rows;setBusy(true);setError('');
    try{
      const result=await request<{outcomes:Outcome[]}>('/registry/csv/confirm',actor.id,control.current?.signal,{content,digest:preview.digest,rows});
      setOutcomes(current=>[...current.filter(o=>!rows.includes(o.index)),...result.outcomes].sort((a,b)=>a.index-b.index));
      setSelected([]);setUncertain(false);
      if(result.outcomes.some(o=>o.status==='saved')){
        try{await onSaved?.();}catch{setError('Registrations saved. Refresh Household records to load the new entries.');}
      }
    }catch(e){if(e instanceof Error&&e.name!=='AbortError'){setError(`${e.message}. Some confirmed rows may already be saved. Retry this confirmation to recover the same results.`);setUncertain(true);}}finally{setBusy(false);}
  }
  if(!['beneficiary','barangay','dswd'].includes(actor.role))return null;
  const available=preview?.rows.filter(r=>r.status==='valid'&&!outcomes.some(o=>o.index===r.index&&o.status==='saved')).length||0;
  return <details className="mvp-panel"><summary><h2>Import household declarations from CSV</h2></summary>
    <p>Upload a completed template, inspect every row, then confirm the households to register. Preview and cancellation save no records.</p>
    <p className="mvp-note">One head per household; no-ID registration only. Add other members and private details through the ordinary registry forms. Registration starts with unconfirmed residence and does not approve a claim.</p>
    {error&&<p role="alert" className="mvp-error">{error}</p>}
    <div className="mvp-actions"><button type="button" disabled={!template||busy} onClick={download}>Download {actor.role==='beneficiary'?'own household':actor.role==='barangay'?'own barangay':'office household'} template</button></div>
    {template&&<><p>{template.description} Limit: {template.max_rows} {template.max_rows===1?'row':'rows'}, 256 KB.</p><p>Required columns: name, address, zone, declared_barangay_id. Optional birth_date column: YYYY-MM-DD or blank. All five column headers are required; extra or repeated headers are rejected.</p></>}
    <details><summary>Barangay identifiers for the template</summary><ul>{barangays.map(b=><li key={b.id}>{b.name}: <code style={{overflowWrap:'anywhere'}}>{b.id}</code></li>)}</ul></details>
    <label>Completed UTF-8 CSV file<input ref={upload} type="file" accept=".csv,text/csv" disabled={!template||busy||uncertain} onChange={e=>{const file=e.target.files?.[0];if(file)void loadFile(file);}}/></label>
    {busy&&<p role="status">{preview?'Saving confirmed rows…':'Validating the file…'}</p>}
    {preview&&<><h3>Review {fileName}</h3><p role="status">{preview.rows.length} rows · {available} available to confirm · {outcomes.filter(o=>o.status==='saved').length} saved</p><p className="mvp-note">{preview.duplicate_limitations} Similar rows require manual registry review; this importer never approves a possible duplicate.</p>
      {preview.rows.map(row=>{const outcome=outcomes.find(o=>o.index===row.index),saved=outcome?.status==='saved';return <article className="mvp-entry" key={row.index}>
        <h4>Row {row.index}: {row.values.name||'Missing head name'} · <Status value={outcome?.status||row.status}/></h4>
        <p>{row.values.address} · {row.values.zone} · {barangays.find(b=>b.id===row.values.declared_barangay_id)?.name||row.values.declared_barangay_id}</p><p>Birth date: {row.values.birth_date||'not supplied; person comparison incomplete'}</p>
        {row.errors.length>0&&<ul>{row.errors.map(v=><li key={v}>{readable(v)}</li>)}</ul>}{row.warnings.length>0&&<ul>{row.warnings.map(v=><li key={v}>{readable(v)}</li>)}</ul>}
        {row.matches.map((match,i)=><p key={i}>Possible match: {match.display_id||`upload row ${match.row_index}`} · name {Math.round(Number(match.name_similarity)*100)}% · address {Math.round(Number(match.address_similarity)*100)}% · birth date {match.birth_date_comparison}. {match.household_id&&<a href={householdHref(match.household_id)}>Inspect household</a>}</p>)}
        {row.status==='needs_review'&&<p>Inspect the existing record in Household records. DSWD can append a documented registry review; correct mistaken CSV facts and preview again.</p>}
        {row.status==='valid'&&!saved&&<label><span><input style={{width:20,minHeight:20}} type="checkbox" disabled={busy||uncertain} checked={selected.includes(row.index)} onChange={e=>setSelected(v=>e.target.checked?[...v,row.index]:v.filter(i=>i!==row.index))}/> Confirm row {row.index} as a new household declaration</span></label>}
        {outcome?.error&&<p role="alert">{readable(outcome.error)}. Inspect Household records before changing this row.</p>}{saved&&<p>Household {outcome.replayed?'already saved; original acknowledgement recovered':'saved'}. {outcome.resources?.filter(r=>r.type==='household_id').map(r=><a key={r.id} href={householdHref(r.id)}>Open household</a>)}</p>}
      </article>;})}
      <p>Selected rows commit separately. A failed row leaves successful registrations saved. Cancelling after confirmation keeps saved records and their audit history. Uploading the identical file again recovers previously saved rows.</p>
      <div className="mvp-actions">{uncertain?<button className="primary" disabled={busy} onClick={()=>void confirm(true)}>Retry the same confirmation</button>:<button className="primary" disabled={busy||!selected.length} onClick={()=>void confirm()}>Register {selected.length} confirmed {selected.length===1?'household':'households'}</button>}<button disabled={busy} onClick={reset}>{uncertain||outcomes.some(o=>o.status==='saved')?'Close import preview':'Cancel preview'}</button></div>
    </>}
  </details>;
}
