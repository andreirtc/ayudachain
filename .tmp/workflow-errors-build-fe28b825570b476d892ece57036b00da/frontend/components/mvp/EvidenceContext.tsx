'use client';
import {useErrorMessage} from './Language';
import {useEffect,useRef,useState} from 'react';
import {Actor,request} from '@/lib/mvp-client';
import IntegrityStatus,{useIntegrityChecks} from './IntegrityStatus';
import {manila,readable,Status} from './UI';
type Summary={id:string;kind:string;created_at:string;submission_state:string;versions:{type:string;id:string}[];originals:{id:string;mime_type:string;byte_length:string}[];coverage:string};
export default function EvidenceContext({actor,id}:{actor:Actor;id:string}){
  const explainError=useErrorMessage(actor.role);
 const [data,setData]=useState<Summary|null>(null),[error,setError]=useState(''),[retry,setRetry]=useState(0);
 const control=useRef<AbortController|null>(null),integrity=useIntegrityChecks(actor.id,control,setError);
 useEffect(()=>{const c=new AbortController();control.current=c;setData(null);setError('');request<Summary>(`/commitments/${id}/summary`,actor.id,c.signal).then(setData).catch(e=>{if(!c.signal.aborted)setError(explainError(e));});return()=>c.abort();},[actor.id,id,retry]);
 return <section className="mvp-panel"><h2>Selected evidence version</h2>{error&&<p role="alert">{error}. Refresh the permitted record to retry.</p>}{data?<><h3>{readable(data.kind)}</h3><p>Committed version {data.id} · Saved {manila(data.created_at)} Manila</p><p>Submission: <Status value={data.submission_state}/></p><p>{data.coverage}</p><details><summary>Exact covered versions and originals</summary>{data.versions.map(v=><p key={v.type+v.id}>{readable(v.type)}: {v.id}</p>)}{data.originals.map(f=><p key={f.id}>Original {f.id} · {f.mime_type} · {f.byte_length} bytes</p>)}</details><IntegrityStatus check={integrity.checks[id]}/><button disabled={integrity.checks[id]?.status==='checking'} onClick={()=>void integrity.check(id)}>Refresh selected evidence check</button></>:!error&&<p role="status">Loading covered evidence…</p>}<button onClick={()=>setRetry(v=>v+1)}>Refresh evidence summary</button></section>;
}
