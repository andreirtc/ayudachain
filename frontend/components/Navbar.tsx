"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { useRole } from "@/lib/roleContext";
import { AccountRole } from "@/lib/api";
import { useSignInHref } from "@/lib/useSignInHref";
import { workspaceHome } from "@/lib/workspaceHome";
import BrandMark from "@/components/BrandMark";
import RoleIndicatorBanner from "@/components/RoleIndicatorBanner";
import { Home, Users, HandCoins, Receipt, LogIn, MessageSquare, ClipboardList, Search } from "lucide-react";
const destinations={overview:{name:'Overview',href:'/dashboard',Icon:Home},households:{name:'Households',href:'/beneficiaries',Icon:Users},payouts:{name:'Payouts',href:'/distributions',Icon:HandCoins},receipts:{name:'Receipts',href:'/verify',Icon:Receipt},concerns:{name:'Concerns',href:'/concerns',Icon:MessageSquare},audit:{name:'Audit',href:'/audit',Icon:ClipboardList},signIn:{name:'Sign in',href:'/sign-in',Icon:LogIn}};
const roleLinks:Record<AccountRole,(keyof typeof destinations)[]>={DSWD:['households','concerns','audit','payouts'],BARANGAY:['households','concerns','overview','receipts'],DISBURSING:['payouts','households','concerns','receipts'],BENEFICIARY:['households','payouts','concerns','receipts'],AUDITOR:['audit','households','payouts','receipts']};
export default function Navbar(){
 const pathname=usePathname(),router=useRouter(),signIn=useSignInHref(),{account}=useRole();const [query,setQuery]=useState('');
 useEffect(()=>setQuery(''),[account?.id]);
 const householdSearch=!!account&&account.role!=='BENEFICIARY';
 function search(e:FormEvent){e.preventDefault();if(!query.trim())return;router.push(householdSearch?'/beneficiaries?'+new URLSearchParams({search:query.trim()}):'/verify?'+new URLSearchParams({distribution_id:query.trim()}));}
 const links=(account?roleLinks[account.role]:['overview','receipts','signIn'] as (keyof typeof destinations)[]).map(key=>{const item=destinations[key];return {...item,href:key==='signIn'?signIn:key==='households'&&account?.role==='BENEFICIARY'?'/household':item.href,name:key==='households'&&account?.role==='BENEFICIARY'?'Home':item.name};});
 const nav=(label:string)=><nav aria-label={label}>{links.map(({name,href,Icon})=><Link key={href} href={href} aria-current={pathname===href.split('?')[0]||(href==='/household'&&pathname==='/beneficiaries')||(href==='/dashboard'&&pathname.startsWith('/batch/'))?'page':undefined}><span className="nav-icon"><Icon size={22} aria-hidden="true"/></span><span>{name}</span></Link>)}</nav>;
 return <header className="app-shell">
   <a href="#main-content" className="app-skip-link">Skip to content</a>
   <div className="app-shell-row">
     <Link href={workspaceHome(account?.role)} className="app-brand" aria-label="AyudaChain home"><BrandMark/><span className="app-wordmark">AyudaChain</span></Link>
     <form onSubmit={search} className="app-search" role="search"><Search size={21} aria-hidden="true"/><input aria-label={householdSearch?'Search households and references':'Search receipt reference'} placeholder={householdSearch?'Search households and references':'Search a receipt reference'} value={query} onChange={e=>setQuery(e.target.value)} maxLength={128}/><button type="submit" className="sr-only">Search</button></form>
     <RoleIndicatorBanner/>
   </div>
   <div className="app-desktop-nav">{nav('Main navigation')}</div>
   <div className="app-bottom-nav">{nav('Mobile navigation')}</div>
 </header>;
}
