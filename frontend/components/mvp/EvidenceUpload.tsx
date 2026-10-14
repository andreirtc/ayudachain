"use client";
import {useEffect,useRef,useState} from 'react';
import {Ack,request} from '@/lib/mvp-client';

export default function EvidenceUpload({actor,purpose,label,onSaved,preparedFor}:{actor:string;purpose:string;label:string;onSaved:(id:string)=>void;preparedFor?:string}){
  const [status,setStatus]=useState(''),[busy,setBusy]=useState(false);const control=useRef<AbortController|null>(null);
  useEffect(()=>{control.current=new AbortController();return()=>control.current?.abort();},[actor]);
  return <label>{label}<input aria-label={label} type="file" accept="application/pdf,image/png,image/jpeg" disabled={busy} onChange={async e=>{
    const file=e.target.files?.[0];if(!file)return;setBusy(true);setStatus('Uploading original…');
    const data=new FormData();data.set('file',file);data.set('purpose',purpose);if(preparedFor)data.set('prepared_for_actor_id',preparedFor);
    try{const ack=await request<Ack>('/evidence',actor,control.current?.signal,data,crypto.randomUUID());onSaved(ack.resources[0].id);setStatus('Original saved; digital signature not validated.');}
    catch(error){if(error instanceof Error&&error.name!=='AbortError')setStatus(error.message);}finally{setBusy(false);}
  }}/><span role="status" className="mvp-note">{status}</span></label>;
}
