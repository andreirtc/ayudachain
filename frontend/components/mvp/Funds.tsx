"use client";
import {useErrorMessage} from './Language';
import {FormEvent,useEffect,useRef,useState} from "react";
import {getApiBase} from "@/lib/api";
import {Ack,Actor,centavos,pesoInput,pesos,request,rejectResponse} from "@/lib/mvp-client";
import {DataFields,readable,manila} from "./UI";
import IntegrityStatus,{useIntegrityChecks} from "./IntegrityStatus";

type Evidence={id:string;purpose:string;attachment_role?:string;extracted_fields:Record<string,string>;extraction_state:string;mime_type:string;signature_state:string};
type Proof={id:string;kind:string;state:string;job_id:string;observed_tx_hash:string|null};
type Entry={id:string;kind:string;reference_number:string;document_type:string;issued_date:string;purpose:string;covered_area:string;delta_centavos:string;head_revision:number;current_entry_id:string;amount_review:Record<string,unknown>;signatories:{printed_name:string;printed_role:string;signature_state:string}[];evidence:Evidence[];proofs:Proof[];exceptions:string[]};
type Ledger={duplicate_document_refusals:{id:string;effective_at:string}[];entries:Entry[];totals:{received_centavos:string;remaining_centavos:string;advanced_centavos:string;returns_centavos:string;approved_known_subtotal_centavos:string;awaiting_amount_count:number;approved_total_complete:boolean;approved_exceeds_recorded_authority:boolean}};
type Form={document_type:string;reference_number:string;issued_date:string;amount:string;purpose:string;covered_area:string;printed_name:string;printed_role:string;document_words:string;document_figures:string;reason:string;correction_kind:string;area_lines:string};
const empty:Form={document_type:"Sub-ARO",reference_number:"",issued_date:new Date().toLocaleDateString("en-CA",{timeZone:"Asia/Manila"}),amount:"",purpose:"",covered_area:"",printed_name:"",printed_role:"",document_words:"",document_figures:"",reason:"",correction_kind:"transcription",area_lines:""};

export default function Funds({actor,disaster}:{actor:Actor;disaster:string}){
  const explainError=useErrorMessage(actor.role);
  const [ledger,setLedger]=useState<Ledger|null>(null),[error,setError]=useState(""),[message,setMessage]=useState("");
  const [editing,setEditing]=useState(false),[correction,setCorrection]=useState<Entry|null>(null),[form,setForm]=useState<Form>(empty);
  const [source,setSource]=useState<Evidence|null>(null),[support,setSupport]=useState<Evidence[]>([]),[url,setURL]=useState("");
  const [busy,setBusy]=useState(false);
  const controller=useRef<AbortController|null>(null),saveKey=useRef<string|null>(null);
  const integrity=useIntegrityChecks(actor.id,controller,setError);
  const load=async(signal?:AbortSignal)=>setLedger(await request<Ledger>(`/funds?disaster_id=${disaster}`,actor.id,signal));
  useEffect(()=>{const c=new AbortController();controller.current=c;load(c.signal).catch(e=>{if(e.name!=="AbortError")setError(explainError(e));});return()=>c.abort();},[actor.id,disaster]); // component is also keyed to actor and disaster
  useEffect(()=>{if(!source){setURL("");return;}const c=new AbortController();let object="";
    fetch(`${getApiBase()}/api/v1/evidence/${source.id}/content`,{headers:{"X-Demo-Actor-ID":actor.id},signal:c.signal,cache:"no-store"}).then(async r=>{if(!r.ok)await rejectResponse(r,`/evidence/${source.id}/content`);return r.blob();}).then(blob=>{object=URL.createObjectURL(blob);setURL(object);}).catch(e=>{if(e.name!=="AbortError")setError(explainError(e));});return()=>{c.abort();if(object)URL.revokeObjectURL(object);};
  },[source?.id,actor.id]);
  const field=(key:keyof Form,value:string)=>{setForm(v=>({...v,[key]:value}));saveKey.current=null;};
  async function upload(file:File,supporting=false){
    setBusy(true);setError("");try{const data=new FormData();data.set("file",file);data.set("purpose",supporting?"supporting":"release_source");
      const ack=await request<Ack>("/evidence",actor.id,controller.current?.signal,data,crypto.randomUUID());
      const e=await request<Evidence>(`/evidence/${ack.resources[0].id}`,actor.id,controller.current?.signal);
      if(supporting)setSupport(v=>[...v,e]);else{setSource(e);const x=e.extracted_fields;setForm(v=>({...v,amount:x.amount_centavos?pesoInput(x.amount_centavos):v.amount,document_words:x.document_words||v.document_words}));}
      saveKey.current=null;
    }catch(e){if(e instanceof Error&&e.name!=="AbortError")setError(explainError(e));}finally{setBusy(false);}
  }
  async function correct(entry:Entry){
    setCorrection(entry);setEditing(true);setSource(null);setSupport([]);setMessage("");setError("");saveKey.current=null;
    setForm({...empty,document_type:entry.document_type,reference_number:entry.reference_number,issued_date:entry.issued_date,amount:pesoInput(entry.delta_centavos),purpose:entry.purpose,covered_area:entry.covered_area,printed_name:entry.signatories[0]?.printed_name||"",printed_role:entry.signatories[0]?.printed_role||"",document_words:String(entry.amount_review.document_words||"")});
    try{
      const original=entry.evidence.find(e=>e.attachment_role==='release_source'||e.attachment_role==='amended_source')||entry.evidence.find(e=>!e.attachment_role&&(e.purpose==='release_source'||e.purpose==='amended_source'));
      if(!original)throw new Error("The primary release original is unavailable. Refresh the ledger before correcting.");
      setSource(await request<Evidence>(`/evidence/${original.id}`,actor.id,controller.current?.signal));
    }catch(e){if(e instanceof Error&&e.name!=="AbortError")setError(explainError(e));}
  }
  async function save(event:FormEvent){
    event.preventDefault();setBusy(true);setError("");setMessage("");try{
      if(!source)throw new Error("Upload the original release document before recording.");
      const area_lines=form.area_lines.trim()?form.area_lines.split("\n").map(line=>{const [area_code,area_name,amount]=line.split("|");if(!amount)throw new Error("Area lines use code | name | peso amount.");return {area_code:area_code.trim(),area_name:area_name.trim(),amount_centavos:centavos(amount.trim())};}):[];
      const body={disaster_id:disaster,source_evidence_id:source.id,supporting_evidence_ids:support.map(e=>e.id),document_type:form.document_type,reference_number:form.reference_number,issued_date:form.issued_date,amount_centavos:centavos(form.amount),purpose:form.purpose,covered_area:form.covered_area,signatories:[{printed_name:form.printed_name,printed_role:form.printed_role}],area_lines,document_words:form.document_words||null,document_figures_centavos:form.document_figures?centavos(form.document_figures):null,...(correction?{expected_revision:correction.head_revision,reason:form.reason,correction_kind:form.correction_kind}:{})};
      saveKey.current??=crypto.randomUUID();await request<Ack>(correction?`/funds/${correction.id}/corrections`:"/funds/releases",actor.id,controller.current?.signal,body,saveKey.current);
      setEditing(false);setCorrection(null);setSource(null);setSupport([]);setForm(empty);saveKey.current=null;setMessage("Saved to the ledger. Required chain proofs are queued; their status appears separately.");await load(controller.current?.signal);
    }catch(e){if(e instanceof Error&&e.name!=="AbortError")setError(explainError(e));}finally{setBusy(false);}
  }
  return <>
    <div className="mvp-title"><div><h1>Disaster funds</h1><p>Recorded funding authority.</p></div><div className="mvp-actions"><button onClick={()=>load(controller.current?.signal).catch(e=>setError(explainError(e)))}>Refresh ledger</button>{actor.role==="dswd"&&<button className="primary" onClick={()=>{setEditing(true);setCorrection(null);setForm(empty);setSource(null);setSupport([]);saveKey.current=null;}}>Record a release</button>}</div></div>
    {error&&<p role="alert" className="mvp-error">{error}</p>}{message&&<p role="status" className="mvp-success">{message}</p>}
    {ledger&&<><div className="mvp-totals">{[["Recorded releases",ledger.totals.received_centavos],["Approved entitlement subtotal",ledger.totals.approved_known_subtotal_centavos],["Awaiting amount",String(ledger.totals.awaiting_amount_count)],["Recorded authority",ledger.totals.remaining_centavos]].map(([label,value])=><div key={label}><span>{label}</span><strong>{label==="Awaiting amount"?value:pesos(value)}</strong></div>)}</div><p className="mvp-note">Approved known subtotal: {pesos(ledger.totals.approved_known_subtotal_centavos)} · {ledger.totals.awaiting_amount_count} awaiting amount · {ledger.totals.approved_total_complete?"complete":"incomplete"}. This does not certify available physical cash.</p>{ledger.totals.approved_exceeds_recorded_authority&&<p className="mvp-warning">Approved amounts exceed recorded authority. Arrange funding outside the app.</p>}</>}
    {editing&&actor.role==="dswd"&&<section className="mvp-panel"><h2>{correction?"Append a linked correction":"Record a document-backed release"}</h2><p>Review the original and confirm the fields. Machine extraction is a prefill; printed signatures remain not validated.</p><div className="mvp-review"><div className="mvp-original"><label>Release original<input type="file" accept="application/pdf,image/png,image/jpeg" disabled={busy} onChange={e=>{if(e.target.files?.[0])void upload(e.target.files[0]);}}/></label>{source&&<><p>{source.extraction_state} · printed signatures not authenticated</p><DataFields data={source.extracted_fields}/></>}{url&&(source?.mime_type==="application/pdf"?<iframe title="Original release document" src={url}/>:<img alt="Uploaded release document" src={url}/>)}</div>
    <form onSubmit={save} className="mvp-form"><div className="mvp-grid">{([['document_type','Document type','text'],['reference_number','Reference number','text'],['issued_date','Issued date','date'],['amount','Confirmed amount (PHP)','text'],['covered_area','Covered area','text'],['printed_name','Printed signatory name','text'],['printed_role','Printed signatory role','text']] as const).map(([key,label,type])=><label key={key}>{label}<input required type={type} value={form[key]} onChange={e=>field(key,e.target.value)}/></label>)}</div>
    <label>Purpose<textarea required value={form.purpose} onChange={e=>field("purpose",e.target.value)}/></label><div className="mvp-grid"><label>Document amount in words (optional)<input value={form.document_words} onChange={e=>field("document_words",e.target.value)}/></label><label>Document figures (PHP, optional)<input value={form.document_figures} onChange={e=>field("document_figures",e.target.value)}/></label></div><label>Area breakdown (optional; one code | name | PHP per line)<textarea value={form.area_lines} onChange={e=>field("area_lines",e.target.value)}/></label><label>Supporting originals (NTA alone is not a release)<input type="file" accept="application/pdf,image/png,image/jpeg" disabled={busy} onChange={e=>{if(e.target.files?.[0])void upload(e.target.files[0],true);}}/></label><p>{support.length} supporting file(s) attached.</p>
    {correction&&<><label>Correction type<select aria-label="Correction type" value={form.correction_kind} onChange={e=>field("correction_kind",e.target.value)}><option value="transcription">Transcription — retain original source</option><option value="source_amendment">Amended authority — upload amended source</option></select></label><label>Reason<textarea required value={form.reason} onChange={e=>field("reason",e.target.value)}/></label></>}
    <div className="mvp-actions"><button disabled={busy||!source} className="primary" type="submit">{busy?"Saving…":correction?"Save reversal and replacement":"Confirm and record"}</button><button type="button" disabled={busy} onClick={()=>setEditing(false)}>Close form</button></div></form></div></section>}
    {!!ledger?.duplicate_document_refusals.length&&<p className="mvp-warning">{ledger.duplicate_document_refusals.length} duplicate-document offers refused. Each refusal remains in the immutable audit history; none counts as a release.</p>}
    {!editing&&url&&<section className="mvp-panel"><h2>Original evidence</h2><div className="mvp-original">{source?.mime_type==="application/pdf"?<iframe title="Saved original evidence" src={url}/>:<img alt="Saved original evidence" src={url}/>}</div><button onClick={()=>setSource(null)}>Close original</button></section>}
    <section className="mvp-panel"><h2>Funding ledger</h2>{!ledger?<p>Loading saved records…</p>:ledger.entries.length===0?<p>No releases recorded for this disaster.</p>:ledger.entries.map(e=><article className="mvp-entry" key={e.id}><div className="mvp-title"><div><h3>{e.reference_number} · {readable(e.kind)}</h3><p>{e.document_type} · {manila(e.issued_date,true)} · {e.covered_area}</p></div><strong>{pesos(e.delta_centavos)}</strong></div><p>{e.purpose}</p><p className="mvp-note">{e.signatories.map(s=>`${s.printed_name}, ${s.printed_role} (${s.signature_state})`).join("; ")}</p>{e.exceptions.length>0&&<p className="mvp-warning">Review flags: {e.exceptions.join(", ")}</p>}<details><summary>Evidence, amount review and chain proofs</summary><DataFields data={e.amount_review}/>{e.evidence.map(v=><button key={v.id} onClick={()=>request<Evidence>(`/evidence/${v.id}`,actor.id,controller.current?.signal).then(setSource).catch(x=>setError(x.message))}>Open {v.purpose} original</button>)}{e.proofs.map(p=><div className="mvp-proof" key={p.id}><span>{p.kind} - {p.state} (historical observation)</span><IntegrityStatus check={integrity.checks[p.id]}/><button disabled={integrity.checks[p.id]?.status==='checking'} onClick={()=>void integrity.check(p.id)}>Check chain now</button></div>)}</details>{actor.role==="dswd"&&e.current_entry_id===e.id&&e.kind!=="reversal"&&<button onClick={()=>void correct(e)}>Append correction</button>}</article>)}</section>
  </>;
}
