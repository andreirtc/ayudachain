"use client";

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
  return <section className="max-w-md mx-auto bg-white border border-slate-200 rounded-xl p-6 space-y-4">
    <div><h1 className="text-2xl font-bold">Sign in to the demo</h1><p className="mt-2 text-sm text-slate-600">Use your synthetic account to open the records and tasks available to your role.</p></div>
    {returnTo && <p className="text-sm text-slate-600">After signing in, return to the page you opened. Your account determines which records you can see.</p>}
    <form onSubmit={submit} className="space-y-4">
      <div><label htmlFor="account-name" className="block font-semibold mb-1">Account</label><input id="account-name" autoComplete="username" required maxLength={64} value={username} disabled={busy} onChange={e => setUsername(e.target.value)} className="w-full min-h-11 border border-slate-300 rounded-lg px-3" /></div>
      <div><label htmlFor="account-password" className="block font-semibold mb-1">Password</label><input id="account-password" type="password" autoComplete="current-password" required maxLength={256} value={password} disabled={busy} onChange={e => setPassword(e.target.value)} className="w-full min-h-11 border border-slate-300 rounded-lg px-3" /></div>
      {error && <p role="alert" className="text-rose-700">{error}</p>}
      <button disabled={busy} className="w-full min-h-11 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg disabled:opacity-50">{busy ? "Signing in..." : "Sign in"}</button>
    </form>
    <p className="text-xs text-slate-500">Fictional data only. These accounts do not establish government affiliation or real household identity.</p>
  </section>;
}
