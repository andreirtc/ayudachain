"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, Layers, Users, Receipt, RefreshCw, CheckCircle2, UserCheck } from "lucide-react";
import { resetDemoData } from "@/lib/api";
import { useRole, UserRole } from "@/lib/roleContext";

export default function Navbar() {
  const pathname = usePathname();
  const { role, setRole } = useRole();
  const [isResetting, setIsResetting] = useState(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  const handleReset = async () => {
    if (!confirm("Reset demo data to initial state (Typhoon Salinlahi Batch 2026-001)?")) return;
    setIsResetting(true);
    try {
      await resetDemoData();
      setResetMessage("Demo data reset successfully!");
      setTimeout(() => {
        setResetMessage(null);
        window.location.reload();
      }, 1200);
    } catch (err) {
      alert("Failed to reset demo: " + String(err));
    } finally {
      setIsResetting(false);
    }
  };

  const navLinks = [
    { name: "Public Dashboard", filipino: "Buod ng Ayuda", href: "/", icon: Layers },
    { name: "Relief Batch", filipino: "Pondo ng Calamity", href: "/batch/RELIEF-2026-001", icon: ShieldCheck },
    { name: "Beneficiaries (AI)", filipino: "Listahan ng Evacuees", href: "/beneficiaries", icon: Users },
    { name: "Distributions", filipino: "Pamamahagi ng Pera", href: "/distributions", icon: Receipt },
    { name: "Verify Integrity", filipino: "Selyo sa Blockchain", href: "/verify", icon: CheckCircle2 },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-900 text-white border-b border-slate-800 shadow-md">
      {/* Top Government Transparency Header */}
      <div className="bg-slate-950 px-4 py-1 text-xs text-slate-400 border-b border-slate-800/80 flex flex-wrap justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 pulse-dot"></span>
          <span>REPUBLIC OF THE PHILIPPINES — DISASTER RELIEF TRANSPARENCY PORTAL</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="hidden sm:inline text-slate-500">Polygon Amoy Integrity Layer Active</span>
          <span className="font-mono text-emerald-400 text-[11px] bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/60">
            Chain ID: 80002 / 31337
          </span>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Calamity Badge */}
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-12 h-12 rounded-xl bg-white p-1 shadow-md border border-slate-700/50 flex items-center justify-center overflow-hidden group-hover:scale-105 transition-transform shrink-0">
                <img src="/logo-emblem.png" alt="AyudaChain Emblem" className="w-full h-full object-contain" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-black text-xl tracking-tight text-white">AyudaChain</span>
                  <span className="text-[10px] uppercase font-bold tracking-widest bg-blue-500/20 text-blue-300 border border-blue-400/30 px-1.5 py-0.5 rounded">
                    MVP
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 tracking-wider">Calamity Relief Public Ledger</p>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation Links with Filipino Subtitles */}
          <nav className="hidden md:flex items-center gap-1.5">
            {navLinks.map((item) => {
              const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? "bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-xs"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <div className="text-left">
                    <span className="block font-bold leading-tight">{item.name}</span>
                    <span className="block text-[9px] text-slate-400 font-normal leading-none">{item.filipino}</span>
                  </div>
                </Link>
              );
            })}
          </nav>

          {/* Role Switcher & Demo Reset Button */}
          <div className="flex items-center gap-3">
            {/* Demo Role Selector */}
            <div className="hidden lg:flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-1.5 rounded-lg border border-slate-700">
              <UserCheck className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-xs text-slate-400">View:</span>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as UserRole)}
                className="bg-transparent text-xs font-semibold text-white focus:outline-none cursor-pointer"
              >
                <option value="Public Citizen" className="bg-slate-900 text-white">Public Citizen (Mamamayan)</option>
                <option value="Barangay Officer" className="bg-slate-900 text-white">Barangay Officer (Kawani)</option>
                <option value="Auditor / COA" className="bg-slate-900 text-white">COA / Auditor (Tagasuri)</option>
              </select>
            </div>

            {/* Reset Button */}
            <button
              onClick={handleReset}
              disabled={isResetting}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-medium border border-slate-700 transition shadow-sm disabled:opacity-50"
              title="Reset database to initial demo state"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin text-blue-400" : ""}`} />
              <span className="hidden sm:inline">{isResetting ? "Resetting..." : "Reset Demo"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Reset Toast Notification */}
      {resetMessage && (
        <div className="bg-emerald-600 text-white text-xs font-medium py-1.5 px-4 text-center transition-all">
          ✓ {resetMessage}
        </div>
      )}

      {/* Mobile Nav */}
      <div className="md:hidden flex overflow-x-auto px-4 py-2 border-t border-slate-800 space-x-2 bg-slate-950/80">
        {navLinks.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={`whitespace-nowrap text-xs px-2.5 py-1 rounded-md ${
              pathname === item.href ? "bg-blue-600 text-white" : "text-slate-400 hover:text-white"
            }`}
          >
            {item.name}
          </Link>
        ))}
      </div>
    </header>
  );
}
