"use client";
import Link from "next/link";
import { useState } from "react";
import { LogOut, Settings2 } from "lucide-react";
import { useRole } from "@/lib/roleContext";
import { useSignInHref } from "@/lib/useSignInHref";
import ThemeToggle from "@/components/ThemeToggle";
const labels={DSWD:'DSWD officer',BARANGAY:'Barangay officer',DISBURSING:'Disbursing officer',BENEFICIARY:'Household',AUDITOR:'Auditor · read-only'};
export default function RoleIndicatorBanner(){const signIn=useSignInHref(),{account,loading,logout}=useRole();const [error,setError]=useState(''),[busy,setBusy]=useState(false);
 async function leave(){if(busy)return;setBusy(true);setError('');try{await logout();}catch(e){setError(e instanceof Error?e.message:'Sign-out failed.');}finally{setBusy(false);}}
 const initials=account?.display_name.split(' ').filter(Boolean).slice(0,2).map(v=>v[0]).join('').toUpperCase()||'AC';
 return <section aria-label="Account" className="app-account">
   <details className="app-preferences" onKeyDown={e=>{if(e.key==='Escape'){e.currentTarget.open=false;e.currentTarget.querySelector('summary')?.focus();}}}><summary aria-label="Display preferences" title="Display preferences"><Settings2 size={20} aria-hidden="true"/></summary><div className="app-preferences-panel">{account&&<div><strong>{account.display_name}</strong><p className="registry-muted">{labels[account.role]}</p></div>}<p>Appearance</p><ThemeToggle/><p className="registry-muted">Synthetic demo · No real payments</p></div></details>
   {loading?<span className="account-role">Checking session...</span>:account?<><div className="account-identity"><strong>{account.display_name}</strong><span>{labels[account.role]}</span><span className="sr-only">Authenticated synthetic account.</span></div><span className="account-avatar" aria-hidden="true">{initials}</span><button onClick={()=>void leave()} disabled={busy} className="account-signout" aria-label={busy?'Signing out...':'Sign out'} title="Sign out"><LogOut size={20} aria-hidden="true"/></button></>:<Link className="registry-button" href={signIn}>Sign in</Link>}
   {error&&<p role="alert" className="account-error">{error}</p>}
 </section>;
}
