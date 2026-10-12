"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck, Banknote, Building2, Users, AlertTriangle, CheckCircle2,
  ArrowRight, ExternalLink, Activity, RefreshCw, Lock, Sparkles, FileText,
  Copy, Check, Settings2, HelpCircle, Globe, ChevronDown, ChevronUp
} from "lucide-react";
import { fetchDashboard, DashboardStats } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Customizable Blockchain Network & Contract Configuration
  const [selectedNetwork, setSelectedNetwork] = useState<string>("Local EVM");
  const [customContract, setCustomContract] = useState<string>("0x5FbDB2315678afecb367f032d93F642f64180aa3");
  const [isEditingContract, setIsEditingContract] = useState(false);
  const [tempContract, setTempContract] = useState(customContract);
  const [copiedContract, setCopiedContract] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

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
        <p className="text-sm text-slate-500 font-medium">Connecting to AyudaChain database &amp; Polygon node...</p>
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
                  Active Calamity Response
                </span>
                <span className="text-xs text-slate-400">Batch Ref: {stats?.batch_id}</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight">{stats?.calamity_name}</h1>
              <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl">
                Province of Albay Emergency Cash &amp; Relief Assistance. Full lifecycle transparency from DSWD fund release to household disbursement.
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

        {/* 5-Step Transparency Pipeline */}
        <div className="mt-8 pt-6 border-t border-slate-800/80">
          <p className="text-[11px] font-bold uppercase tracking-widest text-slate-400 mb-4">
            Auditable End-to-End Pipeline (Proseso ng Ayuda Mula DSWD Hanggang Pamilya)
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-xs">
            <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700/60 flex flex-col justify-between">
              <div>
                <span className="text-white font-bold text-xs block">1. Fund Release</span>
                <span className="text-[10px] text-slate-400">Paglabas ng pondo ng DSWD</span>
              </div>
              <span className="font-black text-white text-base mt-2">₱10,000,000</span>
              <span className="text-[10px] text-emerald-400 mt-1 flex items-center gap-1">✓ On-Chain Anchored</span>
            </div>

            <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700/60 flex flex-col justify-between">
              <div>
                <span className="text-white font-bold text-xs block">2. Barangay Allocation</span>
                <span className="text-[10px] text-slate-400">Alokasyon sa mga barangay</span>
              </div>
              <span className="font-black text-white text-base mt-2">4 Barangays</span>
              <span className="text-[10px] text-emerald-400 mt-1 flex items-center gap-1">✓ 100% Allocated</span>
            </div>

            <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700/60 flex flex-col justify-between">
              <div>
                <span className="text-white font-bold text-xs block">3. AI Entity Resolution</span>
                <span className="text-[10px] text-slate-400">Pagsala sa dobleng listahan</span>
              </div>
              <span className="font-black text-amber-400 text-base mt-2">4 Flagged Records</span>
              <span className="text-[10px] text-amber-300 mt-1 flex items-center gap-1">⚠ Requires Officer Review</span>
            </div>

            <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700/60 flex flex-col justify-between">
              <div>
                <span className="text-white font-bold text-xs block">4. Relief Distribution</span>
                <span className="text-[10px] text-slate-400">Pamamahagi sa evacuees</span>
              </div>
              <span className="font-black text-white text-base mt-2">{stats?.confirmed_distributions} Households</span>
              <span className="text-[10px] text-blue-400 mt-1 flex items-center gap-1">✓ DAFAC QR &amp; Receipt OCR</span>
            </div>

            <div className="bg-emerald-950/40 p-3 rounded-xl border border-emerald-800/60 flex flex-col justify-between">
              <div>
                <span className="text-emerald-300 font-bold text-xs block">5. Blockchain Seal</span>
                <span className="text-[10px] text-emerald-500">Selyado at hindi mababago</span>
              </div>
              <span className="font-black text-emerald-400 text-base mt-2">Immutable Hash</span>
              <span className="text-[10px] text-emerald-400 mt-1 flex items-center gap-1">✓ Publicly Verifiable</span>
            </div>
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
              <span>Selyado sa Polygon Block #1</span>
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
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Confirmed Aid Disbursed</span>
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
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Beneficiaries &amp; AI Flags</span>
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
                      <span className="w-7 h-7 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold text-xs">AI</span>
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
                      Off-Chain AI Flag
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
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-700/60">
                <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot"></span>
                {stats?.blockchain_status || "CONNECTED"}
              </span>
            </div>

            {/* Customizable Network Selector */}
            <div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-slate-400 font-semibold">Active Blockchain Network:</label>
                <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
                  <Globe className="w-3 h-3" /> Live
                </span>
              </div>
              <select
                value={selectedNetwork}
                onChange={(e) => setSelectedNetwork(e.target.value)}
                className="mt-1.5 w-full bg-slate-800 text-white text-xs font-semibold rounded-lg border border-slate-700 p-2 focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                <option value="Local EVM">Local EVM (Fast Offline Demo • Port 8545)</option>
                <option value="Polygon Amoy Testnet">Polygon Amoy Testnet (Public Web3 Explorer)</option>
                <option value="Hardhat Sandbox">Hardhat In-Memory Sandbox</option>
              </select>
            </div>

            {/* Smart Contract Address with Copy & Customization */}
            <div>
              <div className="flex items-center justify-between">
                <label className="text-xs text-slate-400 font-semibold">Smart Contract Address:</label>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(customContract);
                      setCopiedContract(true);
                      setTimeout(() => setCopiedContract(false), 2000);
                    }}
                    className="text-[11px] text-blue-400 hover:text-blue-300 flex items-center gap-1 cursor-pointer"
                    title="Copy contract address"
                  >
                    {copiedContract ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedContract ? "Copied!" : "Copy"}</span>
                  </button>
                  <span className="text-slate-600">•</span>
                  <button
                    onClick={() => setIsEditingContract(!isEditingContract)}
                    className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 cursor-pointer"
                    title="Customize address for custom deployments"
                  >
                    <Settings2 className="w-3 h-3" />
                    <span>{isEditingContract ? "Cancel" : "Customize"}</span>
                  </button>
                </div>
              </div>

              {isEditingContract ? (
                <div className="mt-1.5 space-y-2 bg-slate-950/90 p-2.5 rounded-lg border border-blue-500/50">
                  <span className="text-[10px] text-slate-400 block">
                    Enter custom contract address (e.g. deployed Polygon Amoy address):
                  </span>
                  <input
                    type="text"
                    value={tempContract}
                    onChange={(e) => setTempContract(e.target.value)}
                    placeholder="0x..."
                    className="w-full bg-slate-900 text-blue-300 font-mono text-xs p-2 rounded border border-slate-700 focus:outline-none focus:border-blue-400"
                  />
                  <div className="flex items-center gap-2 pt-1">
                    <button
                      onClick={() => {
                        setCustomContract(tempContract.trim() || stats?.contract_address || "0x5FbDB2315678afecb367f032d93F642f64180aa3");
                        setIsEditingContract(false);
                      }}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-bold rounded cursor-pointer"
                    >
                      Save Address
                    </button>
                    <button
                      onClick={() => {
                        setTempContract("0x5FbDB2315678afecb367f032d93F642f64180aa3");
                        setCustomContract("0x5FbDB2315678afecb367f032d93F642f64180aa3");
                        setIsEditingContract(false);
                      }}
                      className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] rounded cursor-pointer"
                    >
                      Reset Default
                    </button>
                  </div>
                </div>
              ) : (
                <div className="mt-1.5 p-2 bg-slate-950/90 rounded-lg border border-slate-800 flex items-center justify-between gap-2">
                  <p className="font-mono text-xs text-blue-300 truncate" title={customContract}>
                    {customContract}
                  </p>
                  {selectedNetwork.includes("Polygon") && (
                    <a
                      href={`https://amoy.polygonscan.com/address/${customContract}`}
                      target="_blank"
                      rel="noreferrer"
                      title="Open on Polygonscan Block Explorer"
                      className="text-slate-400 hover:text-white shrink-0 p-1 hover:bg-slate-800 rounded"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>
              )}
            </div>

            {/* Explanatory Collapsible for Citizens & Judges */}
            <div className="border-t border-slate-800 pt-3">
              <button
                onClick={() => setShowExplanation(!showExplanation)}
                className="w-full flex items-center justify-between text-xs text-slate-400 hover:text-slate-200 transition cursor-pointer"
              >
                <span className="flex items-center gap-1.5 font-medium">
                  <HelpCircle className="w-3.5 h-3.5 text-blue-400" />
                  What is a Smart Contract? (Bakit may address?)
                </span>
                {showExplanation ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
              {showExplanation && (
                <div className="mt-2.5 p-3 bg-slate-950/95 rounded-xl border border-slate-800 text-[11px] text-slate-300 leading-relaxed space-y-2 animate-in fade-in">
                  <p>
                    📖 <strong>Digital Registry Book Analogy:</strong> Parang Land Title o PSA registry book sa pamahalaan. Ang address na ito ang opisyal na tahanan ng AyudaChain sa blockchain.
                  </p>
                  <p>
                    🔒 <strong>Bakit hindi nababago?</strong> Tuwing may pamilyang bibigyan ng ₱5,000, ang digital hash (fingerprint) ng resibo ay isinusulat sa kontratang ito. Kahit subukan ng sinumang opisyal o hacker na i-edit ang lokal na database, hinding-hindi nila mapapalitan ang nakatatak dito.
                  </p>
                </div>
              )}
            </div>

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
              <strong>Off-Chain:</strong> Heavy receipts, photos, and private PII remain securely in off-chain databases.
            </p>
            <p className="text-slate-600 leading-relaxed mt-1">
              <strong>On-Chain:</strong> Only 32-byte cryptographic SHA-256 integrity hashes are committed to Polygon. Zero private data is leaked.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
