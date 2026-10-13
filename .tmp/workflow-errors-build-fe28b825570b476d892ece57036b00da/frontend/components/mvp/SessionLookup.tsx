"use client";
import {useErrorMessage} from './Language';
import {useEffect,useRef,useState} from 'react';
import {Actor,request} from '@/lib/mvp-client';
import {Session} from './Sessions';
import {manila} from './UI';

type Detector={detect:(source:HTMLVideoElement)=>Promise<{rawValue:string}[]>};
type DetectorConstructor={new(options:{formats:string[]}):Detector;getSupportedFormats:()=>Promise<string[]>};
export const transactionReference=(id:string)=>`ayudachain:transaction:${id}`;
const validReference=/^(?:ayudachain:transaction:)?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export default function SessionLookup({actor,sessions,onOpen}:{actor:Actor;sessions:Session[];onOpen:(id:string)=>void}){
  const explainError=useErrorMessage(actor.role);
  const [session,setSession]=useState(''),[reference,setReference]=useState(''),[error,setError]=useState(''),[message,setMessage]=useState(''),[busy,setBusy]=useState(false),[scanning,setScanning]=useState(false);
  const video=useRef<HTMLVideoElement|null>(null),stream=useRef<MediaStream|null>(null),timer=useRef<ReturnType<typeof setTimeout>|null>(null),generation=useRef(0),controller=useRef<AbortController|null>(null),last=useRef('');
  const permitted=sessions.filter(s=>['scheduled','open'].includes(s.business_status)&&s.assignments.some(a=>a.actor_id===actor.id));
  function release(){generation.current++;if(timer.current)clearTimeout(timer.current);timer.current=null;stream.current?.getTracks().forEach(track=>track.stop());stream.current=null;if(video.current)video.current.srcObject=null;}
  function stop(){release();setScanning(false);}
  useEffect(()=>{release();controller.current?.abort();setScanning(false);setBusy(false);setSession('');setReference('');setError('');setMessage('');last.current='';return()=>{release();controller.current?.abort();};},[actor.id]);
  useEffect(()=>{if(session&&!permitted.some(s=>s.id===session)){stop();controller.current?.abort();setSession('');setBusy(false);}},[sessions,session]);

  async function lookup(raw:string){
    const text=raw.trim();stop();setError('');setMessage('');
    if(!validReference.test(text)){setError('Use a transaction UUID or an AyudaChain transaction QR reference. No personal details, code or PIN belongs here.');return;}
    const canonical=text.replace(/^ayudachain:transaction:/i,'').toLowerCase();
    if(last.current===`${session}:${canonical}`){setMessage('This reference is already open. Use its current transaction controls; a repeat scan does not authorize payout.');return;}
    controller.current?.abort();const c=new AbortController();controller.current=c;setBusy(true);
    try{const data=await request<{transaction_id:string}>(`/sessions/${session}/lookup`,actor.id,c.signal,{reference:text});if(c.signal.aborted)return;last.current=`${session}:${canonical}`;setMessage('Transaction found. Complete the current identity, amount and recipient authorization checks before handover.');onOpen(data.transaction_id);}
    catch(e){if(e instanceof Error&&e.name!=='AbortError')setError(explainError(e));}
    finally{if(!c.signal.aborted)setBusy(false);}
  }
  async function start(){
    stop();setError('');setMessage('');const token=generation.current;setScanning(true);
    const Barcode=(window as Window&{BarcodeDetector?:DetectorConstructor}).BarcodeDetector;
    if(!Barcode||!navigator.mediaDevices?.getUserMedia){setScanning(false);setError('Camera QR scanning is unavailable in this browser. Enter the same transaction reference below.');return;}
    try{
      const formats=await Barcode.getSupportedFormats();if(token!==generation.current)return;
      if(!formats.includes('qr_code')){setScanning(false);setError('This browser cannot decode QR codes. Enter the transaction reference below.');return;}
      const detector=new Barcode({formats:['qr_code']});
      const camera=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false});
      if(token!==generation.current){camera.getTracks().forEach(track=>track.stop());return;}
      stream.current=camera;
      if(!video.current){stop();return;}video.current.srcObject=camera;await video.current.play();if(token!==generation.current)return;
      async function decode(){
        if(token!==generation.current||!video.current)return;
        try{const codes=await detector.detect(video.current);if(token!==generation.current)return;if(codes[0]){setReference(codes[0].rawValue);await lookup(codes[0].rawValue);return;}}
        catch{if(token!==generation.current)return;stop();setError('The camera could not decode this code. Enter the transaction reference below.');return;}
        timer.current=setTimeout(()=>void decode(),250);
      }
      void decode();
    }catch(e){if(token!==generation.current)return;stop();setError(e instanceof Error&&e.name==='NotAllowedError'?'Camera permission was denied. Allow camera access or enter the transaction reference below.':'Camera unavailable. Check that it is connected and unused, or enter the transaction reference below.');}
  }
  return <section className="mvp-panel"><h2>Open an assigned transaction</h2><p>Scan an opaque transaction QR or enter its reference. Lookup opens a record only. Identity comparison, computed amount, recipient code/PIN and independent checker rules still apply.</p>
    <label>Assigned payout session<select aria-label="Assigned payout session" value={session} onChange={e=>{stop();controller.current?.abort();setBusy(false);setSession(e.target.value);setReference('');setError('');setMessage('');last.current='';}}><option value="">Select an assigned session</option>{permitted.map(s=><option key={s.id} value={s.id}>{manila(s.date,true)} · {s.site}</option>)}</select></label>
    {!permitted.length&&<p>No current assigned payout session is available. Refresh sessions after an assignment changes.</p>}
    <form className="mvp-form" onSubmit={e=>{e.preventDefault();void lookup(reference);}}><label>Transaction reference<input value={reference} autoComplete="off" spellCheck={false} maxLength={100} onChange={e=>setReference(e.target.value)} placeholder="Transaction UUID or ayudachain:transaction:UUID"/></label><div className="mvp-actions"><button className="primary" disabled={!session||!reference.trim()||busy}>{busy?'Looking up…':'Open transaction reference'}</button><button type="button" disabled={!session||busy||scanning} onClick={()=>void start()}>Scan QR with camera</button></div></form>
    {scanning&&<div><video ref={video} muted playsInline aria-label="QR camera preview" style={{width:'100%',maxWidth:480}}/><p role="status">Point the camera at the transaction QR. Scanning does not record a payment.</p><button type="button" onClick={()=>{stop();setMessage('Scanning cancelled. Camera released; manual lookup remains available.');}}>Cancel scanning</button></div>}
    {error&&<p className="mvp-error" role="alert">{error}</p>}{message&&<p role="status">{message}</p>}
  </section>;
}
