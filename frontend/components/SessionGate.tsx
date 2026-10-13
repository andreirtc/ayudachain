"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { useRole } from "@/lib/roleContext";
import { useSignInHref } from "@/lib/useSignInHref";

export default function SessionGate({ children }: { children: ReactNode }) {
  const path = usePathname();
  const signIn = useSignInHref();
  const { account, loading, error, refresh } = useRole();
  const restricted = path === "/beneficiaries" || path === "/distributions" || path === "/household" || path === "/lists" || path === "/arrangements" || path === "/concerns" || path === "/audit";
  if (path !== "/sign-in" && loading) return <p role="status">Checking your session...</p>;
  if (restricted && error) return <div role="alert"><h1 className="text-xl font-bold">Session unavailable</h1><p>{error}</p><button className="underline min-h-11" onClick={() => void refresh()}>Try again</button></div>;
  if (restricted && !account) return <section className="registry workflow-panel max-w-xl mx-auto space-y-4"><h1 className="text-xl font-bold">Sign in to continue</h1><p>Household and payout records belong to authenticated synthetic accounts.</p><Link href={signIn} className="registry-button registry-primary">Sign in</Link></section>;
  if (path === "/distributions" && account?.role === "BARANGAY") return <section className="registry workflow-panel space-y-4"><h1>Payout records are outside your role</h1><p>Use the household registry for your assigned barangay.</p><Link href="/beneficiaries" className="registry-button">Open households</Link></section>;
  return <div key={account?.id || "public"}>{children}</div>;
}
