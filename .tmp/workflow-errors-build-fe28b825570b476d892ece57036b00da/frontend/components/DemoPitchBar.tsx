"use client";

import React from "react";
import Link from "next/link";
import { PlayCircle, ShieldCheck, AlertTriangle, ArrowRight, Lock, CheckCircle2 } from "lucide-react";

export default function DemoPitchBar() {
  return (
    <div className="bg-gradient-to-r from-blue-950 via-slate-900 to-indigo-950 border-b border-blue-800/40 px-4 py-2.5 shadow-inner">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2.5">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wider border border-blue-400/30">
            <PlayCircle className="w-3.5 h-3.5 text-blue-400" />
            5-Minute Pitch Mode
          </div>
          <span className="text-xs text-slate-300 font-medium hidden sm:inline">
            Fast Track: Follow Typhoon Salinlahi aid from release to household blockchain receipt
          </span>
        </div>

        {/* Quick Pitch Step Shortcuts */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <Link
            href="/batch/RELIEF-2026-001"
            className="flex items-center gap-1 text-xs bg-slate-800/80 hover:bg-slate-700 text-slate-200 hover:text-white px-2.5 py-1 rounded border border-slate-700 transition"
          >
            <span>1. Batch &amp; Allocations</span>
          </Link>

          <span className="text-slate-600">→</span>

          <Link
            href="/beneficiaries"
            className="flex items-center gap-1 text-xs bg-amber-950/40 hover:bg-amber-900/60 text-amber-300 px-2.5 py-1 rounded border border-amber-800/40 transition"
          >
            <AlertTriangle className="w-3 h-3 text-amber-400" />
            <span>2. AI Duplicate Flag (94%)</span>
          </Link>

          <span className="text-slate-600">→</span>

          <Link
            href="/distributions"
            className="flex items-center gap-1 text-xs bg-blue-900/40 hover:bg-blue-800/60 text-blue-300 px-2.5 py-1 rounded border border-blue-700/40 transition"
          >
            <Lock className="w-3 h-3 text-blue-400" />
            <span>3. Disburse &amp; Anchor</span>
          </Link>

          <span className="text-slate-600">→</span>

          <Link
            href="/verify"
            className="flex items-center gap-1 text-xs bg-emerald-950/50 hover:bg-emerald-900/70 text-emerald-300 px-2.5 py-1 rounded border border-emerald-700/50 transition font-semibold"
          >
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>4. Verify On-Chain</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
