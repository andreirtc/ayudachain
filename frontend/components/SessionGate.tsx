"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { useRole } from "@/lib/roleContext";

export default function SessionGate({ children }: { children: ReactNode }) {
  const path = usePathname();
  const { account, loading, error, refresh } = useRole();
  const restricted = path === "/beneficiaries" || path === "/distributions";
  if (restricted && loading) return <p role="status">Checking your session...</p>;
  if (restricted && error) return <div role="alert"><h1 className="text-xl font-bold">Session unavailable</h1><p>{error}</p><button className="underline min-h-11" onClick={() => void refresh()}>Try again</button></div>;
  if (restricted && !account) return <section className="max-w-xl bg-white p-6 rounded-xl border border-slate-200 space-y-3"><h1 className="text-xl font-bold">Sign in to continue</h1><p>Household and payout records belong to authenticated synthetic accounts.</p><Link href="/sign-in" className="inline-flex min-h-11 px-4 py-2 bg-blue-600 text-white rounded-lg items-center">Sign in</Link></section>;
  if (path === "/distributions" && account?.role === "BARANGAY") return <section className="space-y-3"><h1 className="text-xl font-bold">Payout records are outside your role</h1><p>Use the household registry for your assigned barangay.</p><Link href="/beneficiaries" className="underline text-blue-700">Open households</Link></section>;
  return <div key={account?.id || "public"}>{children}</div>;
}
