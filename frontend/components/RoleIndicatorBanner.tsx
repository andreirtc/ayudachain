"use client";

import Link from "next/link";
import { useState } from "react";
import { useRole } from "@/lib/roleContext";

const labels = { DSWD: "DSWD Officer", BARANGAY: "Barangay Officer", DISBURSING: "Disbursing Officer", BENEFICIARY: "Beneficiary", AUDITOR: "Auditor" };
const actions = { DSWD: ["Review households", "/beneficiaries"], BARANGAY: ["Open barangay households", "/beneficiaries"], DISBURSING: ["Record a payout", "/distributions"], BENEFICIARY: ["My household", "/beneficiaries"], AUDITOR: ["Inspect records", "/beneficiaries"] };
export default function RoleIndicatorBanner() {
  const { account, loading, logout } = useRole();
  const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function leave() { if (busy) return; setBusy(true); setError(""); try { await logout(); } catch (e) { setError(e instanceof Error ? e.message : "Sign-out failed"); } finally { setBusy(false); } }
  return <section aria-label="Account" className="bg-blue-50 border-b border-blue-200 px-4 py-4 text-sm text-slate-700"><div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
    <div><p className="font-semibold">{loading ? "Checking session..." : account ? labels[account.role] + " · " + account.display_name : "Public view"}</p><p className="text-xs mt-1">{account ? "Authenticated synthetic account. Use fictional records only." : "Funding summaries and limited receipt checks are public."}</p>{error && <p role="alert" className="text-rose-700">{error}</p>}</div>
    {account ? <div className="flex flex-wrap gap-3"><Link href={actions[account.role][1]} className="min-h-11 inline-flex items-center text-blue-800 underline font-semibold">{actions[account.role][0]}</Link><button disabled={busy} onClick={() => void leave()} className="min-h-11 px-3 border border-slate-300 bg-white rounded-lg disabled:opacity-50">{busy ? "Signing out..." : "Sign out"}</button></div> : <Link href="/sign-in" className="min-h-11 inline-flex items-center text-blue-800 underline font-semibold">Sign in</Link>}
  </div></section>;
}
