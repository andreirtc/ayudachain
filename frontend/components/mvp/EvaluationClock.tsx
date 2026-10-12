"use client";
import {useEffect,useRef,useState} from 'react';
import {Actor,request} from '@/lib/mvp-client';
type Clock={clock_mode:string;business_utc:string;actual_utc:string;offset_hours:string};
export default function EvaluationClock({actor}:{actor:Actor}){
  const [clock,setClock]=useState<Clock|null>(null),[hours,setHours]=useState('72'),[error,setError]=useState(''),[busy,setBusy]=useState(false);
  const control=useRef<AbortController|null>(null),key=useRef<string|null>(null);
  useEffect(()=>{const c=new AbortController();control.current=c;void request<Clock>('/evaluation/status',actor.id,c.signal).then(setClock).catch(e=>{if(e.name!=='AbortError')setError(e.message);});return()=>c.abort();},[actor.id]);
  return <aside className="mvp-panel"><p>Business clock: {clock?.clock_mode||'checking'} {clock&&`· ${clock.business_utc} · offset ${clock.offset_hours} hours`}. Chain timestamps remain actual.</p>{error&&<p role="alert">{error}</p>}{actor.role==='dswd'&&<form className="mvp-actions" onSubmit={async e=>{e.preventDefault();setBusy(true);key.current??=crypto.randomUUID();try{await request('/evaluation/clock',actor.id,control.current?.signal,{advance_hours:Number(hours)},key.current);key.current=null;setClock(await request<Clock>('/evaluation/status',actor.id,control.current?.signal));setError('');}catch(e){if((e as Error).name!=='AbortError')setError((e as Error).message);}finally{setBusy(false);}}}><label>Advance synthetic business time (hours)<input type="number" min="1" max="720" required value={hours} onChange={e=>{setHours(e.target.value);key.current=null;}}/></label><button disabled={busy}>Advance evaluation clock</button></form>}</aside>;
}
