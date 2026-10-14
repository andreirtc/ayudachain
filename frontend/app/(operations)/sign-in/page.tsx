"use client";

import BrandMark from "@/components/BrandMark";
import { FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { signIn } from "@/lib/api";
import { useRole } from "@/lib/roleContext";
import { afterSignIn, safeReturnTo } from "@/lib/signInDestination";

export default function SignInPage() {
  const router = useRouter();
  const params = useSearchParams();
  const returnTo = params.getAll("returnTo").length === 1 ? safeReturnTo(params.get("returnTo")) : null;
  const { refresh } = useRole();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); if (busy) return; setBusy(true); setError(null);
    try { const account = await signIn(username, password); setPassword(""); await refresh(); router.replace(afterSignIn(returnTo, account.role)); }
    catch (e) { setError(e instanceof Error ? e.message : "Sign-in failed"); }
    finally { setBusy(false); }
  }
  return <section className="registry sign-in-page">
    <div className="sign-in-intro"><span className="sign-in-mark"><BrandMark size={48}/></span><h1>Sign in to the demo</h1><p>Your household, or your staff workspace. One account for the tasks available to you.</p><p className="registry-muted">Synthetic records. No real payments.</p></div>
    <form onSubmit={submit} className="sign-in-form">
      <div><label htmlFor="account-name">Account</label><input id="account-name" autoComplete="username" required maxLength={64} value={username} disabled={busy} onChange={e=>setUsername(e.target.value)}/></div>
      <div><label htmlFor="account-password">Password</label><input id="account-password" type="password" autoComplete="current-password" required maxLength={256} value={password} disabled={busy} onChange={e=>setPassword(e.target.value)}/></div>
      {returnTo&&<p className="registry-muted">You'll return to the page you opened after signing in.</p>}
      {error&&<p role="alert" className="registry-error">{error}</p>}
      <button disabled={busy} className="registry-button registry-primary">{busy?'Signing in...':'Sign in'}</button>
      <p className="registry-muted">Use a locally provisioned synthetic account.</p>
    </form>
  </section>;
}
