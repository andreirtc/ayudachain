"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, Layers, Users, Receipt, CheckCircle2 } from "lucide-react";
import { useChainStatus, chainLabel } from "@/lib/useChainStatus";

const navLinks = [
  { name: "Overview", href: "/dashboard", icon: Layers },
  { name: "Relief batch", href: "/batch/RELIEF-2026-001", icon: ShieldCheck },
  { name: "Households", href: "/beneficiaries", icon: Users },
  { name: "Payouts", href: "/distributions", icon: Receipt },
  { name: "Check a receipt", href: "/verify", icon: CheckCircle2 },
];

export default function Navbar() {
  const pathname = usePathname();
  const chain = useChainStatus();
  return (
    <header className="sticky top-0 z-50 bg-slate-900 text-white border-b border-slate-800">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:block focus:p-3 focus:bg-white focus:text-blue-800">Skip to content</a>
      <div className="bg-slate-950 px-4 py-2 text-xs text-slate-300 border-b border-slate-800 flex flex-wrap justify-between gap-2">
        <span>Fictional relief demo · No real money</span>
        <span>{chainLabel(chain)}</span>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-wrap justify-between items-center gap-4 py-3">
          <Link href="/" className="flex items-center gap-3 rounded-lg focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-white">
            <img src="/logo-emblem.png" alt="" className="w-10 h-10 rounded-lg bg-white object-contain" />
            <span className="font-bold text-xl tracking-tight">AyudaChain</span>
          </Link>
          <nav aria-label="Main navigation" className="hidden md:flex flex-wrap gap-1">
            {navLinks.map(({ name, href, icon: Icon }) => {
              const active = pathname === href || (href.startsWith("/batch/") && pathname.startsWith("/batch/"));
              return <Link key={href} href={href} aria-current={active ? "page" : undefined} className={"flex items-center gap-2 min-h-11 px-3 py-2 rounded-lg text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white " + (active ? "bg-blue-600 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white")}><Icon className="w-4 h-4" aria-hidden="true" />{name}</Link>;
            })}
          </nav>
          <details className="md:hidden w-full">
            <summary className="cursor-pointer min-h-11 py-3 text-sm font-semibold">Navigation</summary>
            <nav aria-label="Mobile navigation" className="flex flex-wrap gap-1">
              {navLinks.map(({ name, href, icon: Icon }) => {
              const active = pathname === href || (href.startsWith("/batch/") && pathname.startsWith("/batch/"));
              return <Link key={href} href={href} aria-current={active ? "page" : undefined} className={"flex items-center gap-2 min-h-11 px-3 py-2 rounded-lg text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white " + (active ? "bg-blue-600 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white")}><Icon className="w-4 h-4" aria-hidden="true" />{name}</Link>;
            })}
            </nav>
          </details>
        </div>
      </div>
    </header>
  );
}
