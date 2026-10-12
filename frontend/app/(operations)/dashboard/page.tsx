"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck, Banknote, Building2, Users, AlertTriangle, CheckCircle2,
  ArrowRight, Activity, RefreshCw, Lock, Sparkles, FileText
} from "lucide-react";
import { fetchDashboard, DashboardStats } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await fetchDashboard();
      setStats(data);
      setError(null);
    } catch (err) {
      setError("Failed to load dashboard data. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
        <p className="text-sm text-slate-500 font-medium">Connecting to AyudaChain database &amp; blockchain node...</p>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center text-red-800 my-8">
        <AlertTriangle className="w-10 h-10 text-red-600 mx-auto mb-2" />
        <h3 className="font-bold text-lg">Backend Connection Failed</h3>
        <p className="text-sm mt-1">{error}</p>
        <button
          onClick={loadData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-semibold hover:bg-red-700 transition"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const formatPhp = (val: number) => {
    return new Intl.NumberFormat("en-PH", { style: "currency", currency: "PHP" }).format(val);
  };

  return (
    <div className="space-y-6">
      {error && <p role="alert" className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-950">The latest refresh failed. Totals below are from the last successful read. <button type="button" onClick={() => void loadData()} className="underline font-semibold">Refresh</button></p>}
      {/* Hero Calamity Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-950 rounded-2xl p-6 sm:p-8 text-white shadow-xl border border-slate-800 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
          <div className="flex items-start gap-4">
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-white p-2 shadow-2xl shrink-0 flex items-center justify-center border border-slate-600/60">
              <img src="/logo.png" alt="AyudaChain Logo" className="w-full h-full object-contain" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="bg-rose-500 text-white text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider animate-pulse">
                  Fictional relief batch
                </span>
                <span className="text-xs text-slate-400">Batch Ref: {stats?.batch_id}</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight">{stats?.calamity_name}</h1>
              <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl">
                Recorded fictional funds, household reviews and payout receipts.
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Link
              href={`/batch/${stats?.batch_id}`}
              className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs px-4 py-2.5 rounded-xl shadow transition"
            >
              <FileText className="w-4 h-4" />
              View Batch Breakdown
            </Link>
            <Link
              href="/verify"
              className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-emerald-400 font-semibold text-xs px-4 py-2.5 rounded-xl border border-slate-700 transition"
            >
              <Lock className="w-4 h-4 text-emerald-400" />
              Verify Blockchain Proof
            </Link>
          </div>
        </div>

      </div>

      {/* Top Level Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Released */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <div>
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Kabuuang Pondo (Total)</span>
              <span className="text-[10px] text-slate-400">Pondong inilabas ng DSWD</span>
            </div>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <Banknote className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-2xl font-black text-slate-900 tracking-tight">
              {formatPhp(stats?.total_released || 0)}
            </span>
            <div className="flex items-center gap-1.5 mt-2 text-xs text-emerald-700 font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Selyado sa blockchain</span>
            </div>
          </div>
        </div>

        {/* Total Allocated */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Barangay Allocations</span>
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <Building2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-black text-slate-900">{formatPhp(stats?.total_allocated || 0)}</div>
            <p className="text-xs text-emerald-600 font-medium mt-1">100% assigned to 4 local barangays</p>
          </div>
        </div>

        {/* Total Distributed */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Recorded payouts</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-black text-emerald-600">{formatPhp(stats?.total_distributed || 0)}</div>
            <p className="text-xs text-slate-500 mt-1">{stats?.confirmed_distributions} household receipts verified</p>
          </div>
        </div>

        {/* Beneficiaries & AI Flags */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Households and review flags</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-black text-slate-900">{stats?.total_beneficiaries}</span>
              <span className="text-xs text-slate-500">total ({stats?.verified_beneficiaries} verified)</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-amber-600 font-semibold mt-1">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{stats?.flagged_records} records flagged for review</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid: Blockchain Integrity Box + Activity Log */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Activity Timeline */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              <h2 className="font-bold text-base text-slate-900">Live Calamity Relief Audit Timeline</h2>
            </div>
            <span className="text-xs font-mono text-slate-400">Chronological Trail</span>
          </div>

          <div className="divide-y divide-slate-100">
            {stats?.recent_transactions.map((tx, idx) => (
              <div key={idx} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {tx.event_type === "FUND_RELEASE" && (
                      <span className="w-7 h-7 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">FR</span>
                    )}
                    {tx.event_type === "ALLOCATION" && (
                      <span className="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs">AL</span>
                    )}
                    {tx.event_type === "DISTRIBUTION_CONFIRMED" && (
                      <span className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-xs">DC</span>
                    )}
                    {tx.event_type.includes("FLAG") && (
                      <span className="w-7 h-7 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold text-xs">!</span>
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{tx.description}</p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {new Date(tx.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })} • Event: {tx.event_type}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center">
                  {tx.tx_hash ? (
                    <span className="font-mono text-[11px] bg-slate-100 text-slate-700 px-2 py-1 rounded border border-slate-200 flex items-center gap-1" title={tx.tx_hash}>
                      <Lock className="w-3 h-3 text-emerald-600" />
                      {tx.tx_hash.slice(0, 10)}...{tx.tx_hash.slice(-4)}
                    </span>
                  ) : (
                    <span className="text-[11px] bg-amber-50 text-amber-700 px-2 py-0.5 rounded font-medium border border-amber-200">
                      Review flag
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-slate-100 flex justify-end">
            <Link
              href={`/batch/${stats?.batch_id}`}
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1"
            >
              View complete historical audit log <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Right 1 Col: Blockchain Architecture & Verification Card */}
        <div className="space-y-4">
          <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">Blockchain Ledger Status</span>
                <span className="text-[10px] text-slate-500">Selyo ng Ayuda sa Smart Contract</span>
              </div>
              <span
                className={`flex items-center gap-1.5 text-xs font-semibold px-2 py-0.5 rounded border ${
                  !error && stats?.blockchain_status === "CONNECTED"
                    ? "text-emerald-400 bg-emerald-950/80 border-emerald-700/60"
                    : "text-amber-300 bg-amber-950/60 border-amber-700/60"
                }`}
              >
                <span className={`w-2 h-2 rounded-full ${!error && stats?.blockchain_status === "CONNECTED" ? "bg-emerald-400" : "bg-amber-400"}`}></span>
                {error ? "REFRESH UNAVAILABLE" : stats?.blockchain_status || "CHECKING"}
              </span>
            </div>

            <p className="text-xs text-slate-300">Connection status is separate from receipt verification.</p>
            <details className="text-sm text-slate-300">
              <summary className="cursor-pointer py-2 font-semibold">Reported network and contract</summary>
              <dl className="mt-2 space-y-3 text-xs">
                <div><dt className="font-semibold">Network</dt><dd>{error ? "Refresh unavailable" : stats?.active_network || "Not reported"}</dd></div>
                <div><dt className="font-semibold">Contract</dt><dd className="font-mono break-all">{error ? "Refresh unavailable" : stats?.contract_address || "Not reported"}</dd></div>
              </dl>
              <p className="mt-3 text-xs">Configuration comes from the backend. This dashboard does not change the network or deployment.</p>
            </details>

            <div className="pt-1">
              <Link
                href="/verify"
                className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold py-2.5 rounded-lg shadow transition"
              >
                <CheckCircle2 className="w-4 h-4" />
                Run Integrity Verification Tool
              </Link>
            </div>
          </div>

          {/* Educational Callout: Off-Chain Data vs On-Chain Proof */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900">
            <h4 className="font-bold flex items-center gap-1 text-blue-950 mb-1">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              Hybrid Storage Principle
            </h4>
            <p className="text-slate-600 leading-relaxed">
              <strong>Local records:</strong> Synthetic household details and receipt files are stored in the database and local files. Authenticated privacy remains unfinished.
            </p>
            <p className="text-slate-600 leading-relaxed mt-1">
              <strong>Blockchain:</strong> The current registry stores record references, amounts and receipt hashes. A receipt check covers only the fields included in its hash.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
