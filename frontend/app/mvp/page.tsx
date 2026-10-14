'use client';
import Link from 'next/link';
import {ArrowRight,Users,Landmark,HandCoins,ScanLine,House} from 'lucide-react';
import {workspaces} from '@/components/mvp/workspaces';
import {LogoMark} from '@/components/mvp/Logo';
import WelcomeVisual from '@/components/mvp/WelcomeVisual';
import DisplayPreferences from '@/components/mvp/DisplayPreferences';
import {LanguageProvider,LanguageSelector,useLanguage,useInterfaceText} from '@/components/mvp/Language';
const roleIcons=[House,Users,Landmark,HandCoins,ScanLine];
export default function MVP(){return <LanguageProvider><Welcome/></LanguageProvider>;}
function Welcome(){
 const ui=useInterfaceText();const {language}=useLanguage();
 return <div className="ac-entry ac-welcome" lang={language}>
  <header className="ac-welcome-header"><Link href="/mvp" className="ac-brand" aria-label="AyudaChain"><LogoMark size={42}/><span>AyudaChain<small>{ui('Disaster assistance records')}</small></span></Link><div className="ac-welcome-controls"><LanguageSelector/><DisplayPreferences context="welcome" includeLanguage={false}/></div></header>
  <main id="main-content" className="ac-welcome-main">
   <section className="ac-service-introduction"><div><p className="ac-service-kicker">{ui('Disaster assistance records')}</p><h1>{ui('Welcome to AyudaChain')}</h1><p className="ac-service-description">{ui('Follow disaster assistance from the household request to the recorded payout. See the status, understand the amount, and keep the documents and recipient report connected.')}</p><p className="ac-service-trail">{ui('Request → Human review → Payout record → Recipient report → Integrity check')}</p></div><WelcomeVisual/></section>
   <div className="ac-service-heading"><h2>{ui('Choose your work area')}</h2><p>{ui('Open your household status or continue your assigned work.')}</p></div>
   <nav className="ac-service-directory" aria-label={ui('Choose your work area')}>{Object.entries(workspaces).map(([slug,w],i)=>{const Icon=roleIcons[i];return <Link href={'/mvp/'+slug} className="ac-service-row" key={slug}><Icon size={24} aria-hidden="true"/><div><h2>{ui(w.label)}</h2><p>{ui(w.description)}</p></div><span className="ac-service-action">{ui(slug==='beneficiary'?'Open my assistance':'Open workspace')}<ArrowRight size={18} aria-hidden="true"/></span></Link>;})}</nav>
   <aside className="ac-welcome-note"><p><strong>{ui('Demo workspace, not a sign-in.')}</strong>{' '}{ui('Selected identities are unverified. Use fictional records only. National ID and SMS are simulated; chain checks use actual reads.')}</p></aside>
  </main><footer className="ac-welcome-footer"><span>AyudaChain</span><span>{ui('Private details stay off-chain.')}</span></footer>
 </div>;
}
