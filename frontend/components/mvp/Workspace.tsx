'use client';
import {useEffect,useState,useRef,Suspense,Fragment} from 'react';
import {useSearchParams} from 'next/navigation';
import Link from 'next/link';
import {ShieldCheck,ChevronDown,Menu,X,ArrowLeft,Wifi,UserRound} from 'lucide-react';
import {Actor,Ref,request} from '@/lib/mvp-client';
import {workspaces} from './workspaces';
import {Icon} from './UI';
import Dashboard from './Dashboard';
import Funds from './Funds';
import Registry from './Registry';
import Claims from './Claims';
import Lists from './Lists';
import Sessions from './Sessions';
import Payouts from './Payouts';
import Outcomes from './Outcomes';
import Audit from './Audit';
import Queue from './Queue';
import Operations from './Operations';
import {LanguageProvider,LanguageSelector} from './Language';
export default function Workspace(props:{slug:string;section:string}){return <LanguageProvider><Suspense fallback={<div className="ac-loading" role="status">Opening your workspace…</div>}><WorkspaceBody {...props}/></Suspense></LanguageProvider>;}
function WorkspaceBody({slug,section}:{slug:string;section:string}){
  const config=workspaces[slug],search=useSearchParams();
  const [actors,setActors]=useState<Actor[]>([]),[disasters,setDisasters]=useState<Ref[]>([]),[barangays,setBarangays]=useState<Ref[]>([]);
  const [actorID,setActorID]=useState(''),[disaster,setDisaster]=useState(''),[error,setError]=useState(''),[loading,setLoading]=useState(true),[mobileMenu,setMobileMenu]=useState(false),[online,setOnline]=useState(true),[retry,setRetry]=useState(0);
  const menuTrigger=useRef<HTMLButtonElement>(null),sidebar=useRef<HTMLElement>(null),wasOpen=useRef(false);
  useEffect(()=>{if(mobileMenu){sidebar.current?.querySelector<HTMLAnchorElement>('nav a')?.focus();wasOpen.current=true;}else if(wasOpen.current){menuTrigger.current?.focus();wasOpen.current=false;}},[mobileMenu]);
  useEffect(()=>{const c=new AbortController();setLoading(true);setError('');setActorID('');Promise.all([request<Actor[]>('/actors/catalogue',null,c.signal),request<Ref[]>('/disasters',null,c.signal),request<Ref[]>('/barangays',null,c.signal)]).then(([a,d,b])=>{
    const eligible=a.filter(v=>v.role===config.role&&v.status==='active');let savedActor='',savedDisaster='';try{savedActor=localStorage.getItem(`ayudachain:${slug}:account`)||'';savedDisaster=localStorage.getItem('ayudachain:disaster')||'';}catch{}
    const candidate=search.get('account')||savedActor;setActors(a);setDisasters(d);setBarangays(b);setActorID(eligible.find(v=>v.id===candidate)?.id||eligible[0]?.id||'');const target=search.get('disaster')||savedDisaster;setDisaster(d.find(v=>v.id===target)?.id||d[0]?.id||'');
  }).catch(e=>{if(e.name!=='AbortError')setError('We couldn’t load your workspace. Check the connection and try again.');}).finally(()=>{if(!c.signal.aborted)setLoading(false);});return()=>c.abort();},[slug,retry]);
  useEffect(()=>{setMobileMenu(false);},[section]);
  useEffect(()=>{const account=search.get('account'),selected=search.get('disaster');if(account&&actors.some(a=>a.id===account&&a.role===config.role&&a.status==='active'))setActorID(account);if(selected&&disasters.some(d=>d.id===selected))setDisaster(selected);},[search,actors,disasters,config.role]);
  useEffect(()=>{const update=()=>setOnline(navigator.onLine);update();window.addEventListener('online',update);window.addEventListener('offline',update);return()=>{window.removeEventListener('online',update);window.removeEventListener('offline',update);};},[]);
  useEffect(()=>{if(!actorID)return;try{localStorage.setItem(`ayudachain:${slug}:account`,actorID);if(disaster)localStorage.setItem('ayudachain:disaster',disaster);}catch{}},[actorID,disaster,slug]);
  const actor=actors.find(a=>a.id===actorID&&a.role===config.role),current=config.navigation.find(n=>n.key===section);
  const href=(key:string)=>{const query=new URLSearchParams(),account=actorID||search.get('account'),selectedDisaster=disaster||search.get('disaster');if(account)query.set('account',account);if(selectedDisaster)query.set('disaster',selectedDisaster);return `/mvp/${slug}${key==='overview'?'':'/'+key}${query.size?'?'+query.toString():''}`;};
  const chooseContext=(nextActor:string,nextDisaster:string)=>{setActorID(nextActor);setDisaster(nextDisaster);const url=new URL(window.location.href);url.searchParams.delete('record');url.searchParams.delete('history');url.hash='';url.searchParams.set('account',nextActor);url.searchParams.set('disaster',nextDisaster);window.history.replaceState(null,'',url.pathname+url.search+url.hash);};
  const place=actor?.barangay_id?barangays.find(b=>b.id===actor.barangay_id)?.name:'DSWD Field Office';
  return <div className={`ac-app mvp-shell ${config.role==='beneficiary'?'ac-beneficiary':''}`} data-workspace={slug}>
    <a className="ac-skip" href="#main-content">Skip to main content</a>
    <aside id="workspace-navigation" ref={sidebar} className={`ac-sidebar ${mobileMenu?'is-open':''}`} onKeyDown={e=>{if(!mobileMenu||!window.matchMedia('(max-width: 760px)').matches)return;if(e.key==='Escape'){e.preventDefault();setMobileMenu(false);}if(e.key==='Tab'){const items=Array.from(sidebar.current?.querySelectorAll<HTMLElement>('a, button')||[]),first=items[0],last=items.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}}}><Link href={href('overview')} className="ac-brand"><span className="ac-brand-mark"><ShieldCheck size={23}/></span>AyudaChain</Link><div className="ac-workspace-label">{config.label}<span>{config.role==='beneficiary'?'Your household assistance':place}</span></div>
      <nav aria-label="Workspace navigation">{config.navigation.map(n=><Link key={n.key} href={href(n.key)} aria-current={section===n.key?'page':undefined}><Icon name={n.icon}/><span>{n.label}</span></Link>)}</nav>
      <div className="ac-sidebar-bottom"><ShieldCheck size={19}/><p>Every step leaves a record.<span>Private details stay off-chain.</span></p></div>
      <button className="ac-mobile-close" aria-label="Close navigation" onClick={()=>setMobileMenu(false)}><X size={20}/></button>
    </aside>
    <div className="ac-main-frame"><header className="ac-topbar"><button ref={menuTrigger} className="ac-menu-button" aria-controls="workspace-navigation" aria-label="Open navigation" aria-expanded={mobileMenu} onClick={()=>setMobileMenu(v=>!v)}><Menu size={22}/></button><span className="ac-breadcrumb">{config.label}<span>/</span><strong>{current?.label||'Page unavailable'}</strong></span><details className="ac-account"><summary><span className="ac-avatar"><UserRound size={17}/></span><span>{actor?.display_name||config.label}</span><ChevronDown size={14}/></summary><div className="ac-account-panel"><strong>{config.label} account</strong><p>Synthetic accounts have no sign-in. Selected identities are unverified.</p><label>Account<select aria-label="Account" value={actorID} onChange={e=>chooseContext(e.target.value,disaster)}>{actors.filter(a=>a.role===config.role&&a.status==='active').map(a=><option key={a.id} value={a.id}>{a.display_name}{a.position?' · '+a.position:''}</option>)}</select></label>{config.role==='disbursing'&&<p>For an independent exit check, use a different eligible assigned officer account.</p>}</div></details></header>
      <div className="ac-contextbar"><LanguageSelector/><div><span className="ac-context-dot"/><span>{config.role==='beneficiary'?'Assistance for your household':place}</span>{config.role==='auditor'&&<span className="ac-readonly">Read-only</span>}</div><label>Disaster<select aria-label="Disaster" value={disaster} onChange={e=>chooseContext(actorID,e.target.value)}>{disasters.map(d=><option key={d.id} value={d.id}>{d.name}</option>)}</select></label></div>
      {!online&&<div role="alert" className="mvp-warning">Connection lost. Reconnect and read the saved transaction before retrying a handover.</div>}
      <main id="main-content" className="ac-content" tabIndex={-1}><Fragment key={slug+actorID+disaster+section}>
        {loading?<div className="ac-loading" role="status"><span className="ac-loading-bar"/>Loading your records…</div>:error?<div className="ac-empty"><h1>Connection unavailable</h1><p>{error}</p><button className="primary" onClick={()=>setRetry(v=>v+1)}>Try again</button></div>:!current?<div className="ac-empty"><h1>Page unavailable</h1><p>This page isn’t part of your workspace.</p><Link className="ac-button" href={href('overview')}><ArrowLeft size={16}/>Return to overview</Link></div>:!actor?<div className="ac-empty"><h1>No active account</h1><p>A DSWD Officer needs to activate an eligible account for this workspace.</p></div>:!disaster?<div className="ac-empty"><h1>No disaster available</h1><p>No declared disaster is available for this Field Office.</p></div>:section==='queues'?<Queue actor={actor} disaster={disaster} barangays={barangays} href={href}/>:section==='overview'?<><Dashboard actor={actor} disaster={disaster} disasterName={disasters.find(d=>d.id===disaster)?.name||''} barangays={barangays} href={href}/>{['dswd','auditor','barangay'].includes(actor.role)&&<Operations actor={actor} disaster={disaster} href={href}/>}</>:section==='funds'?<Funds actor={actor} disaster={disaster}/>:section==='registry'?<Registry actor={actor} actors={actors} disaster={disaster}/>:section==='claims'?<Claims actor={actor} disaster={disaster}/>:section==='lists'?<Lists actor={actor} disaster={disaster}/>:section==='sessions'?<Sessions actor={actor} actors={actors} disaster={disaster}/>:section==='payouts'?<Payouts actor={actor} actors={actors} disaster={disaster}/>:section==='outcomes'?<Outcomes actor={actor} disaster={disaster}/>:<Audit actor={actor} disaster={disaster}/>}
      </Fragment></main><footer className="ac-app-footer"><span><Wifi size={13}/> {online?'Online workflows':'Connection lost'} · Manila time</span><details><summary>Synthetic records · About this workspace</summary><p>Accounts have no sign-in and identities are unverified. National ID checks and SMS notices are simulated; no handset delivery is claimed. Chain verification uses actual reads. Printed signatures are not authenticated. Use invented data only.</p></details></footer>
    </div>
  </div>;
}
