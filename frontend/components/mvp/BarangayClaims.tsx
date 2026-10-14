"use client";
import {useEffect,useRef,useState} from 'react';
import {useSearchParams} from 'next/navigation';
import Guidance from './Guidance';
import {useLanguage,useErrorMessage} from './Language';
import {Ack,Actor,Ref,request} from '@/lib/mvp-client';
import {WorkflowError} from '@/lib/workflow-errors';
import EvidenceUpload from './EvidenceUpload';
import {Status,readable,manila} from './UI';
import {SavedResult} from './Review';
import {Claim,ResponseForm} from './Claims';

const finalStatuses=['approved','declined','reversed'];
const openStatuses=['waiting_barangay','referred'];

// Barangay officers see only claims from their own barangay (the API enforces the scope).
// They record endorsements; DSWD alone approves or declines.
export default function BarangayClaims({actor,disaster}:{actor:Actor;disaster:string}){
  const explainError=useErrorMessage(actor.role),params=useSearchParams(),record=params.get('record'),{t,language}=useLanguage();
  const [claims,setClaims]=useState<Claim[]>([]),[categories,setCategories]=useState<Ref[]>([]),[selected,setSelected]=useState(''),[rounds,setRounds]=useState<string[]>([]),[resolution,setResolution]=useState('');
  const [error,setError]=useState(''),[message,setMessage]=useState(''),[busy,setBusy]=useState(false),[uncertain,setUncertain]=useState(false),[loading,setLoading]=useState(true),[readFailed,setReadFailed]=useState(false);
  const control=useRef<AbortController|null>(null),detail=useRef<HTMLElement|null>(null),picked=useRef(false);
  const punong=actor.position==='Punong Barangay';
  const sendable=(c:Claim)=>c.business_status==='waiting_barangay'?c.rounds.find(r=>r.state==='waiting'&&!r.referral_decision_id&&r.responses.length>0):undefined;
  async function load(signal?:AbortSignal){
    setLoading(true);setReadFailed(false);
    try{
      const [q,cat]=await Promise.all([request<{claims:Claim[]}>(`/claims?disaster_id=${disaster}`,actor.id,signal),request<Ref[]>('/categories',actor.id,signal)]);
      if(signal?.aborted)return;
      let list=q.claims;
      if(record&&!list.some(c=>c.id===record)){
        const one=await request<Claim>(`/claims/${encodeURIComponent(record)}`,actor.id,signal);if(signal?.aborted)return;
        if(one.disaster_id!==disaster)throw new Error(t('This claim belongs to another disaster. Select its disaster before proceeding.','Para sa ibang sakuna ang kahilingang ito. Piliin ang tamang sakuna bago magpatuloy.'));
        list=[one,...list];
      }
      const hashed=window.location.hash.startsWith('#claim-')?window.location.hash.slice(7):'';
      setClaims(list);setCategories(cat);
      setRounds(prior=>prior.filter(id=>list.some(c=>sendable(c)?.id===id)));
      setSelected(v=>v&&list.some(c=>c.id===v)?v:record||(list.some(c=>c.id===hashed)?hashed:''));
      setLoading(false);
    }catch(e){if(!signal?.aborted)setReadFailed(true);throw e;}
  }
  useEffect(()=>{const c=new AbortController();control.current=c;setClaims([]);setSelected('');setRounds([]);setError('');setMessage('');setBusy(false);load(c.signal).catch(e=>{if(e.name!=='AbortError'){setLoading(false);setError(explainError(e));}});return()=>c.abort();},[actor.id,disaster,record]);
  useEffect(()=>{if(picked.current&&selected){picked.current=false;detail.current?.focus();detail.current?.scrollIntoView({block:'nearest'});}},[selected]);
  async function save(path:string,body:object){
    if(uncertain)return;const signal=control.current?.signal;setBusy(true);setError('');setMessage('');
    try{
      await request<Ack>(path,actor.id,signal,body,crypto.randomUUID());if(signal?.aborted)return;
      const name=claims.find(c=>c.id===selected)?.household.name||t('the selected claim','ang napiling kahilingan');
      const kind=(body as {kind?:string}).kind;
      setMessage(path==='/claims/submissions'
        ?t('Formal barangay submission recorded for the selected claims. DSWD reviews them next; digital signature validity remains not validated.','Naitala ang pormal na pagsusumite ng barangay para sa mga napiling kahilingan. Susuriin ito ng DSWD; hindi pa napatutunayan ang bisa ng digital na lagda.')
        :t(`Response ${readable(kind||'')} recorded for ${name}. DSWD makes the decision; earlier responses remain in history.`,`Naitala ang tugon na ${readable(kind||'')} para kay ${name}. DSWD ang magpapasya; mananatili sa kasaysayan ang mga naunang tugon.`));
      if(path==='/claims/submissions'){setResolution('');setRounds([]);}
      await load(signal);
    }catch(e){if(!signal?.aborted&&e instanceof Error&&e.name!=='AbortError'){setError(explainError(e));if(e instanceof WorkflowError&&(e.status===0||e.status>=500||e.code==='invalid_response'))setUncertain(true);}}
    finally{if(!signal?.aborted){setBusy(false);setLoading(false);}}
  }
  const category=(id:string)=>{const name=categories.find(c=>c.id===id)?.name||'';return name==='Totally damaged'?t('Totally damaged','Lubos na napinsala'):name==='Partially damaged'?t('Partially damaged','Bahagyang napinsala'):name||'—';};
  const myResponse=(c:Claim)=>c.rounds.flatMap(r=>r.responses).filter(r=>r.officer_name===actor.display_name).at(-1)?.kind;
  const latestRound=(c:Claim)=>c.rounds.at(-1);
  const open=claims.filter(c=>openStatuses.includes(c.business_status)),history=claims.filter(c=>!openStatuses.includes(c.business_status));
  const chosen=claims.find(c=>c.id===selected);
  function pick(id:string){picked.current=true;setSelected(id);const url=new URL(window.location.href);url.hash=`claim-${id}`;window.history.replaceState(null,'',url.pathname+url.search+url.hash);}
  function table(list:Claim[],caption:string,withSend:boolean){
    return <div className="ac-table-scroll"><table className="ac-table"><caption>{caption}</caption><thead><tr>
      <th scope="col">{t('Household head','Puno ng sambahayan')}</th><th scope="col">{t('Address · zone','Tirahan · purok')}</th><th scope="col">{t('Stated category','Ipinahayag na kategorya')}</th><th scope="col">{t('Submitted','Isinumite')}</th><th scope="col">{t('Response deadline','Palugit sa pagtugon')}</th><th scope="col">{t('Responses','Mga tugon')}</th><th scope="col">{t('Your response','Ang inyong tugon')}</th><th scope="col">{t('Status','Katayuan')}</th>{withSend&&<th scope="col">{t('Send to DSWD','Ipadala sa DSWD')}</th>}
    </tr></thead><tbody>{list.map(c=>{const round=sendable(c),mine=myResponse(c),last=latestRound(c);
      return <tr key={c.id} className={c.id===selected?'is-selected':undefined} onClick={()=>pick(c.id)}>
        <th scope="row"><button type="button" className="ac-row-button" aria-current={c.id===selected?'true':undefined} onClick={e=>{e.stopPropagation();pick(c.id);}}>{c.household.name}</button></th>
        <td>{c.household.address} · {t('zone','purok')} {c.household.zone}</td><td>{category(c.submission.stated_category_id)}</td><td>{c.submission.submitted_at?manila(c.submission.submitted_at):'—'}</td><td>{last?manila(last.deadline_at):'—'}</td>
        <td>{c.rounds.reduce((n,r)=>n+r.responses.length,0)}</td><td>{mine?<Status value={mine}/>:t('Not yet','Wala pa')}</td><td><Status value={c.business_status}/></td>
        {withSend&&<td onClick={e=>e.stopPropagation()}>{round?<label><input type="checkbox" style={{width:20,minHeight:20}} aria-label={`${t('Include in formal submission','Isama sa pormal na pagsusumite')}: ${c.household.name}`} checked={rounds.includes(round.id)} onChange={e=>setRounds(v=>e.target.checked?[...v,round.id]:v.filter(id=>id!==round.id))}/></label>:'—'}</td>}
      </tr>;})}</tbody></table></div>;
  }
  return <div lang={language}>
    <div className="mvp-title"><div><h1>{t('Claim responses','Mga tugon sa kahilingan')}</h1><p>{t('Residents of your barangay who applied for assistance. Your endorsement is an opinion; DSWD decides.','Mga residente ng inyong barangay na nag-apply ng ayuda. Opinyon ang inyong endorsement; DSWD ang nagpapasya.')}</p></div><button onClick={()=>load(control.current?.signal).then(()=>setUncertain(false)).catch(e=>{setLoading(false);setError(explainError(e));})}>{t('Refresh claims','I-refresh ang mga kahilingan')}</button></div>
    {error&&<p role="alert" className="mvp-error">{error}</p>}<SavedResult message={message}/>
    <Guidance flow="endorsement"/>
    <section className="mvp-panel">
      {loading?<p role="status">{t('Loading current claims…','Kinukuha ang kasalukuyang mga kahilingan…')}</p>:readFailed?<p>{t('Claim records unavailable. Refresh before proceeding.','Hindi makuha ang mga kahilingan. I-refresh bago magpatuloy.')}</p>:claims.length===0?<p>{t('No claims from your barangay for this disaster.','Walang kahilingan mula sa inyong barangay para sa sakunang ito.')}</p>:<>
        {table(open,t('Claims waiting for a response','Mga kahilingang naghihintay ng tugon'),punong)}
        {open.length===0&&<p className="mvp-note">{t('No claim is waiting for your response.','Walang kahilingang naghihintay ng inyong tugon.')}</p>}
        {history.length>0&&<><h2>{t('History','Kasaysayan')}</h2>{table(history,t('Claims already sent to DSWD or decided','Mga kahilingang naipadala na sa DSWD o napagpasyahan na'),false)}</>}
      </>}
    </section>
    {chosen&&<section className="mvp-panel" id={`claim-${chosen.id}`} ref={detail} tabIndex={-1} aria-labelledby="claim-detail-heading">
      <div className="ac-section-heading"><h2 id="claim-detail-heading">{chosen.household.name}</h2><Status value={chosen.business_status}/></div>
      <p>{chosen.household.address} · {t('zone','purok')} {chosen.household.zone}</p>
      <p><strong>{t('Stated category','Ipinahayag na kategorya')}:</strong> {category(chosen.submission.stated_category_id)}</p>
      <p>{chosen.submission.damage_description}</p>
      {chosen.submission.new_information&&<p><strong>{t('New information','Bagong impormasyon')}:</strong> {chosen.submission.new_information}</p>}
      {chosen.rounds.map(r=><div key={r.id}>
        <p className="mvp-note">{t('Response deadline','Palugit sa pagtugon')} {manila(r.deadline_at)} Manila · <Status value={r.state}/> · {r.route_kind?<Status value={r.route_kind}/>:t('Awaiting forwarding','Hinihintay ang pagpapasa')}{r.referral_decision_id&&` · ${t('DSWD referral','Referral ng DSWD')}`}</p>
        {r.responses.map(s=><p key={s.id}>{s.officer_name}: <Status value={s.kind}/> {s.reason&&`— ${s.reason}`} {s.related_declared&&`· ${t('relative declared','may kamag-anak na idineklara')}`} {s.category_disputed&&`· ${t('category disputed','pinagtatalunan ang kategorya')}`}</p>)}
        {r.id===latestRound(chosen)?.id&&!finalStatuses.includes(chosen.business_status)&&r.state!=='closed'&&<ResponseForm key={r.id} recordName={`${chosen.household.name} · ${chosen.id}`} categories={categories} referral={!!r.referral_decision_id} busy={busy||uncertain} responses={r.responses} onSave={body=>save(`/claim-rounds/${r.id}/responses`,body)}/>}
      </div>)}
      {chosen.decisions.map(d=><p key={d.id}>DSWD <Status value={d.action}/>: {d.reason||d.question||t('human decision recorded','naitala ang pasya ng tao')}</p>)}
    </section>}
    {punong&&<section className="mvp-panel"><h2>{t('Send responded claims to DSWD','Ipadala sa DSWD ang mga kahilingang may tugon')}</h2><p>{t('Tick the claims in the table above, then attach the council resolution. Negative responses are sent with the rest. Signed evidence records a claimed human submission; digital signature validity is not validated.','Lagyan ng tsek ang mga kahilingan sa talahanayan, saka ilakip ang resolusyon ng konseho. Kasama ring ipinapadala ang mga negatibong tugon. Itinatala ng nilagdaang katibayan ang inaangking pagsusumite ng tao; hindi pa napatutunayan ang bisa ng digital na lagda.')}</p><EvidenceUpload actor={actor.id} purpose="council_resolution" label={t('Council resolution original','Orihinal na resolusyon ng konseho')} onSaved={setResolution}/><button className="primary" disabled={busy||uncertain||!resolution||!rounds.length} onClick={()=>void save('/claims/submissions',{disaster_id:disaster,barangay_id:actor.barangay_id,round_ids:rounds,resolution_evidence_id:resolution})}>{t('Submit selected claims','Isumite ang mga napiling kahilingan')}</button></section>}
  </div>;
}
