import Link from 'next/link';
import {ArrowRight,ShieldCheck,Users,Landmark,HandCoins,ScanLine,House} from 'lucide-react';
import {workspaces} from '@/components/mvp/workspaces';
const icons=[House,Users,Landmark,HandCoins,ScanLine];
export default function MVP(){
  return <div className="ac-entry">
    <header className="ac-entry-header"><Link href="/mvp" className="ac-brand"><span className="ac-brand-mark"><ShieldCheck size={23}/></span>AyudaChain</Link><span>Disaster cash assistance</span></header>
    <main id="main-content" className="ac-entry-main">
      <div className="ac-entry-intro"><h1>Relief you can follow.</h1><p>From funding to the family. One clear record of every decision, every handover, and what happened next.</p><div className="ac-entry-process" aria-label="Assistance journey">{['Funding','Claim & review','Payout','Private confirmation','Independent audit'].map((step,i)=><span key={step}>{i>0&&<ArrowRight size={14}/>}<b>{step}</b></span>)}</div></div>
      <section className="ac-workspace-directory" aria-labelledby="workspace-heading"><div className="ac-directory-heading"><h2 id="workspace-heading">Your workspace</h2><p>Choose where you work in the assistance journey.</p></div>
        {Object.entries(workspaces).map(([slug,w],i)=>{const Icon=icons[i];return <Link className="ac-directory-row" href={'/mvp/'+slug} key={slug}><span className="ac-directory-icon"><Icon size={22}/></span><span><h3>{w.label}</h3><p>{w.description}</p></span><ArrowRight size={20}/></Link>;})}
      </section>
      <aside className="ac-entry-disclosure"><ShieldCheck size={18}/><p><strong>Synthetic records only.</strong> Accounts are selected without sign-in; identities are unverified. National ID checks and SMS notices are simulated. Chain checks use actual reads.</p></aside>
    </main><footer className="ac-entry-footer"><span>AyudaChain · One DSWD Field Office</span><span>Clear decisions. Traceable assistance.</span></footer>
  </div>;
}
