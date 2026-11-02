'use client';
import {useInterfaceText} from "./Language";

import {useEffect,useState,useRef,Suspense,Fragment} from 'react';
import {useSearchParams} from 'next/navigation';
import Link from 'next/link';
import {ShieldCheck,ChevronDown,Menu,X,ArrowLeft,Wifi,UserRound} from 'lucide-react';
import {Actor,Ref,request} from '@/lib/mvp-client';
import {workspaces} from './workspaces';
import {LogoMark} from './Logo';
import DisplayPreferences from './DisplayPreferences';
import EvaluationClock from './EvaluationClock';
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
import {LanguageProvider,useErrorMessage,useLanguage} from './Language';
export default function Workspace(props:{slug:string;section:string}){return <Suspense fallback={<div className="ac-loading" role="status">Opening your workspace…</div>}><LanguageProvider><WorkspaceBody {...props}/></LanguageProvider></Suspense>;}
function WorkspaceBody({slug,section}:{slug:string;section:string}){
  const ui=useInterfaceText();

  const {language}=useLanguage();
  const config=workspaces[slug],search=useSearchParams();
  const explainError=useErrorMessage(config?.role);
  const [actors,setActors]=useState<Actor[]>([]),[disasters,setDisasters]=useState<Ref[]>([]),[barangays,setBarangays]=useState<Ref[]>([]);
  const [actorID,setActorID]=useState(''),[disaster,setDisaster]=useState(''),[error,setError]=useState(''),[loading,setLoading]=useState(true),[mobileMenu,setMobileMenu]=useState(false),[online,setOnline]=useState(true),[retry,setRetry]=useState(0);
  const menuTrigger=useRef<HTMLButtonElement>(null),sidebar=useRef<HTMLElement>(null),wasOpen=useRef(false);
  useEffect(()=>{if(mobileMenu){sidebar.current?.querySelector<HTMLAnchorElement>('nav a')?.focus();wasOpen.current=true;}else if(wasOpen.current){menuTrigger.current?.focus();wasOpen.current=false;}},[mobileMenu]);
  useEffect(()=>{const c=new AbortController();setLoading(true);setError('');setActorID('');Promise.all([request<Actor[]>('/actors/catalogue',null,c.signal),request<Ref[]>('/disasters',null,c.signal),request<Ref[]>('/barangays',null,c.signal)]).then(([a,d,b])=>{
    const eligible=a.filter(v=>v.role===config.role&&v.status==='active');let savedActor='',savedDisaster='';try{savedActor=localStorage.getItem(`ayudachain:${slug}:account`)||'';savedDisaster=localStorage.getItem('ayudachain:disaster')||'';}catch{}
    const candidate=search.get('account')||savedActor;setActors(a);setDisasters(d);setBarangays(b);setActorID(eligible.find(v=>v.id===candidate)?.id||eligible[0]?.id||'');const target=search.get('disaster')||savedDisaster;setDisaster(d.find(v=>v.id===target)?.id||d[0]?.id||'');
  }).catch(e=>{if(e.name!=='AbortError')setError(explainError(e));}).finally(()=>{if(!c.signal.aborted)setLoading(false);});return()=>c.abort();},[slug,retry]);
  useEffect(()=>{setMobileMenu(false);},[section]);
  useEffect(()=>{const account=search.get('account'),selected=search.get('disaster');if(account&&actors.some(a=>a.id===account&&a.role===config.role&&a.status==='active'))setActorID(account);if(selected&&disasters.some(d=>d.id===selected))setDisaster(selected);},[search,actors,disasters,config.role]);
  useEffect(()=>{const update=()=>setOnline(navigator.onLine);update();window.addEventListener('online',update);window.addEventListener('offline',update);return()=>{window.removeEventListener('online',update);window.removeEventListener('offline',update);};},[]);
  useEffect(()=>{if(!actorID)return;try{localStorage.setItem(`ayudachain:${slug}:account`,actorID);if(disaster)localStorage.setItem('ayudachain:disaster',disaster);}catch{}},[actorID,disaster,slug]);
  const actor=actors.find(a=>a.id===actorID&&a.role===config.role),current=config.navigation.find(n=>n.key===section);
  const href=(key:string)=>{const query=new URLSearchParams(),account=actorID||search.get('account'),selectedDisaster=disaster||search.get('disaster');if(account)query.set('account',account);if(selectedDisaster)query.set('disaster',selectedDisaster);return `/mvp/${slug}${key==='overview'?'':'/'+key}${query.size?'?'+query.toString():''}`;};
  const chooseContext=(nextActor:string,nextDisaster:string)=>{setActorID(nextActor);setDisaster(nextDisaster);const url=new URL(window.location.href);url.searchParams.delete('record');url.searchParams.delete('history');url.hash='';url.searchParams.set('account',nextActor);url.searchParams.set('disaster',nextDisaster);window.history.replaceState(null,'',url.pathname+url.search+url.hash);};
  const shortLabels:Record<string,string>={queues:'Tasks',overview:'Home',registry:'Households',claims:config.role==='beneficiary'?'My claim':'Review',funds:'Funding',lists:'Lists',sessions:'Sessions',payouts:config.role==='disbursing'?'Pay desk':'Receipts',outcomes:config.role==='beneficiary'?'Help':'Cases',audit:'Integrity'};
  const quickKeys:Record<string,string[]>={beneficiary:['overview','claims','payouts','outcomes'],barangay:['overview','registry','claims','lists'],dswd:['overview','registry','claims','sessions'],disbursing:['overview','sessions','payouts','outcomes'],auditor:['overview','audit','funds','outcomes']};
  const quickNavigation=quickKeys[config.role].map(key=>config.navigation.find(n=>n.key===key)!);
  const place=actor?.barangay_id?barangays.find(b=>b.id===actor.barangay_id)?.name:'DSWD Field Office';
  return <div className={`ac-app mvp-shell ${config.role==='beneficiary'?'ac-beneficiary':''}`} data-workspace={slug} lang={language}>
    <a className="ac-skip" href="#main-content">{ui("Skip to main content")}</a>
    <aside id="workspace-navigation" ref={sidebar} className={`ac-sidebar ${mobileMenu?'is-open':''}`} onKeyDown={e=>{if(!mobileMenu||!window.matchMedia('(max-width: 760px)').matches)return;if(e.key==='Escape'){e.preventDefault();setMobileMenu(false);}if(e.key==='Tab'){const items=Array.from(sidebar.current?.querySelectorAll<HTMLElement>('a, button')||[]),first=items[0],last=items.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}}}><Link href="/mvp" className="ac-brand" aria-label={ui("AyudaChain, all workspaces")}><span className="ac-brand-mark"><LogoMark size={30}/></span>{ui("AyudaChain")}</Link><div className="ac-workspace-label">{ui(config.label)}<span>{config.role==='beneficiary'?ui("Your household assistance"):place}</span></div>
      <nav aria-label={ui("Workspace navigation")}>{config.navigation.map(n=><Link key={n.key} href={href(n.key)} aria-label={ui(n.label)} title={ui(n.label)} aria-current={section===n.key?'page':undefined}><Icon name={n.icon}/><span className="ac-nav-full">{ui(n.label)}</span><span className="ac-nav-short" aria-hidden="true">{ui(shortLabels[n.key])}</span></Link>)}</nav>
      <Link href="/mvp" className="ac-all-workspaces"><ArrowLeft size={16} aria-hidden="true"/>{ui("All workspaces")}</Link><div className="ac-sidebar-bottom"><ShieldCheck size={19}/><p>{ui("Every step leaves a record.")}<span>{ui("Private details stay off-chain.")}</span></p></div>
      <button className="ac-mobile-close" aria-label={ui("Close navigation")} onClick={()=>setMobileMenu(false)}><X size={20}/></button>
    </aside>
    <div className="ac-main-frame"><header className="ac-topbar"><button ref={menuTrigger} className="ac-menu-button" aria-controls="workspace-navigation" aria-label={ui("Open navigation")} aria-expanded={mobileMenu} onClick={()=>setMobileMenu(v=>!v)}><Menu size={22}/></button><span className="ac-breadcrumb">{config.role==='beneficiary'?ui("Mamamayan"):config.label}<span>/</span><strong>{ui(current?.label||'Page unavailable')}</strong></span><DisplayPreferences context={slug+section+actorID}/><details className="ac-account"><summary><span className="ac-avatar"><UserRound size={17}/></span><span>{actor?.display_name||config.label}</span><ChevronDown size={14}/></summary><div className="ac-account-panel"><strong>{ui(config.label)}{' '}{ui("account")}</strong><p>{ui("Synthetic accounts have no sign-in. Selected identities are unverified.")}</p><label>{ui("Account")}<select aria-label={ui("Account")} value={actorID} onChange={e=>chooseContext(e.target.value,disaster)}>{actors.filter(a=>a.role===config.role&&a.status==='active').map(a=><option key={a.id} value={a.id}>{a.display_name}{a.position?' · '+a.position:''}</option>)}</select></label>{config.role==='disbursing'&&<p>{ui("For an independent exit check, use a different eligible assigned officer account.")}</p>}</div></details></header>
      <div className="ac-contextbar"><div><span className="ac-context-dot"/><span>{config.role==='beneficiary'?ui("Assistance for your household"):place}</span>{config.role==='auditor'&&<span className="ac-readonly">{ui("Read-only")}</span>}</div><label>{ui("Disaster")}<select aria-label={ui("Disaster")} value={disaster} onChange={e=>chooseContext(actorID,e.target.value)}>{disasters.map(d=><option key={d.id} value={d.id}>{d.name}</option>)}</select></label></div>
      {!online&&<div role="alert" className="mvp-warning">{ui("Connection lost. Reconnect and read the saved transaction before retrying a handover.")}</div>}
      <main id="main-content" className="ac-content" tabIndex={-1}><Fragment key={slug+actorID+disaster+section}>
        {loading?<div className="ac-loading" role="status"><span className="ac-loading-bar"/>{ui("Loading your records…")}</div>:error?<div className="ac-empty"><h1>{ui("Connection unavailable")}</h1><p>{error}</p><button className="primary" onClick={()=>setRetry(v=>v+1)}>{ui("Try again")}</button></div>:!current?<div className="ac-empty"><h1>{ui("Page unavailable")}</h1><p>{ui("This page isn’t part of your workspace.")}</p><Link className="ac-button" href={href('overview')}><ArrowLeft size={16}/>{ui("Return to overview")}</Link></div>:!actor?<div className="ac-empty"><h1>{ui("No active account")}</h1><p>{ui("A DSWD Officer needs to activate an eligible account for this workspace.")}</p></div>:!disaster?<div className="ac-empty"><h1>{ui("No disaster available")}</h1><p>{ui("No declared disaster is available for this Field Office.")}</p></div>:section==='queues'?<Queue actor={actor} disaster={disaster} barangays={barangays} href={href}/>:section==='overview'?<><Dashboard actor={actor} disaster={disaster} disasterName={disasters.find(d=>d.id===disaster)?.name||''} barangays={barangays} href={href}/>{['dswd','auditor','barangay'].includes(actor.role)&&<details className="mvp-panel ac-operations-disclosure"><summary><h2>{ui("Barangay operation breakdown")}</h2></summary><Operations actor={actor} disaster={disaster} href={href}/></details>}</>:section==='funds'?<Funds actor={actor} disaster={disaster}/>:section==='registry'?<Registry actor={actor} actors={actors} disaster={disaster}/>:section==='claims'?<Claims actor={actor} disaster={disaster}/>:section==='lists'?<Lists actor={actor} disaster={disaster}/>:section==='sessions'?<Sessions actor={actor} actors={actors} disaster={disaster}/>:section==='payouts'?<Payouts actor={actor} actors={actors} disaster={disaster}/>:section==='outcomes'?<Outcomes actor={actor} disaster={disaster}/>:<Audit actor={actor} disaster={disaster}/>}
      </Fragment></main><footer className="ac-app-footer">{actor&&['dswd','auditor'].includes(actor.role)&&<details><summary>{ui("Evaluation tools (synthetic only)")}</summary><EvaluationClock key={actor.id} actor={actor}/></details>}<span><Wifi size={13}/> {online?ui("Online workflows"):ui("Connection lost")}{' '}{ui("· Manila time")}</span><details><summary>{ui("Synthetic records · About this workspace")}</summary><p>{ui("Accounts have no sign-in and identities are unverified. National ID checks and SMS notices are simulated; no handset delivery is claimed. Chain verification uses actual reads. Printed signatures are not authenticated. Use invented data only.")}</p></details></footer>
    </div>
    <nav className="ac-quick-navigation" aria-label={ui("Quick navigation")}>{quickNavigation.map(n=><Link key={n.key} href={href(n.key)} aria-label={ui('Go to')+' '+ui(n.label)} aria-current={section===n.key?'page':undefined}><Icon name={n.icon}/><span>{ui(shortLabels[n.key])}</span></Link>)}</nav>
  </div>;
}
