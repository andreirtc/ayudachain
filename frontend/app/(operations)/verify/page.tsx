"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  ShieldCheck, CheckCircle2, AlertTriangle, XCircle, Lock, RefreshCw,
  ExternalLink, FileText, Database, UserCheck, HelpCircle, ChevronDown, ChevronUp, Info
} from "lucide-react";
import { verifyBlockchain, VerifyResponse, fetchDistributions, fetchBeneficiaries, Distribution, Beneficiary } from "@/lib/api";

function VerifyContent() {
  const searchParams = useSearchParams();
  const initialDistId = searchParams?.get("distribution_id") || "DIST-0001";

  const [distributions, setDistributions] = useState<Distribution[]>([]);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [selectedId, setSelectedId] = useState(initialDistId);
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  
  // Real-world fraud simulation state: null = authentic, "AMOUNT_ALTERED", "NAME_SWAPPED"
  const [fraudType, setFraudType] = useState<null | "AMOUNT_ALTERED" | "NAME_SWAPPED">(null);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  useEffect(() => {
    Promise.all([fetchDistributions(), fetchBeneficiaries()])
      .then(([dList, bList]) => {
        setDistributions(dList);
        setBeneficiaries(bList);
        if (dList.length > 0 && !dList.some((d) => d.distribution_id === initialDistId)) {
          setSelectedId(dList[0].distribution_id);
        }
      })
      .catch(console.error);
  }, [initialDistId]);

  const activeDist = distributions.find((d) => d.distribution_id === selectedId);
  const activeBen = beneficiaries.find((b) => b.beneficiary_id === activeDist?.beneficiary_id);

  const handleVerify = async (simulatedFraud: null | "AMOUNT_ALTERED" | "NAME_SWAPPED" = null) => {
    setLoading(true);
    setFraudType(simulatedFraud);
    try {
      const res = await verifyBlockchain(selectedId);
      if (simulatedFraud === "AMOUNT_ALTERED") {
        setResult({
          ...res,
          receipt_hash_local: "0x4b7c12f098de76aa34b12c89f560e4178bca9921e537482910fedcba7216a908",
          is_verified: false,
          status_message: "TAMPERING DETECTED: The local database record was modified from ₱5,000.00 to ₱2,000.00 after on-chain anchoring!"
        });
      } else if (simulatedFraud === "NAME_SWAPPED") {
        setResult({
          ...res,
          receipt_hash_local: "0x8892bc135f0a28394e5b71946892eab54619d0847253a6c98127390f7201bb74",
          is_verified: false,
          status_message: "TAMPERING DETECTED: The claimant name was secretly changed in the database to an unauthorized person!"
        });
      } else {
        setResult(res);
      }
    } catch (err) {
      alert("Verification error: " + String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedId) {
      handleVerify(null);
    }
  }, [selectedId]);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Friendly Header for Citizens & Judges */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <div className="inline-flex items-center gap-1.5 bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-xs font-bold">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          Public Notary &amp; Receipt Authenticity Checker
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Verify My Calamity Relief Voucher
        </h1>
        <p className="text-xs sm:text-sm text-slate-600">
          Did the aid allocated by the national government actually reach the family intact?
          Verify any household receipt against the permanent, unalterable blockchain seal.
        </p>
      </div>

      {/* Selector & Actions */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="w-full sm:w-80">
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Select Relief Receipt to Inspect:
            </label>
            <select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
            >
              {distributions.map((d) => (
                <option key={d.distribution_id} value={d.distribution_id}>
                  {d.distribution_id} — Beneficiary {d.beneficiary_id} (₱{d.amount.toLocaleString()})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto self-end">
            <button
              onClick={() => handleVerify(null)}
              disabled={loading}
              className="flex-1 sm:flex-initial px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg text-xs shadow transition flex items-center justify-center gap-1.5 disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              Re-Check Authentic Record
            </button>
          </div>
        </div>

        {/* Simple Citizen Guide Callout */}
        <div className="p-3.5 bg-blue-50/80 border border-blue-200 rounded-xl flex items-start gap-3 text-xs">
          <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-blue-950 block">Gabay Para sa Karaniwang Mamamayan:</span>
            <p className="text-slate-700 leading-relaxed">
              Ang bawat ₱5,000 na inilabas ng DSWD ay binibigyan ng <strong>permanenteng digital na selyo</strong> sa blockchain sa oras ng pamimigay.
              Kung may magtangkang bawasan ang pera sa computer o palitan ang pangalan ng nakatanggap, agad itong magpapakita ng <strong className="text-rose-700">RED CORRUPTION ALERT</strong> dahil hinding-hindi tugma ang lokal na listahan sa orihinal na selyo sa blockchain.
            </p>
          </div>
        </div>

        {/* Real-Life Fraud Pitch Simulator Controls */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
              Pitch Demonstration: Test Real-World Calamity Fraud Scenarios
            </span>
            <span className="text-[10px] text-slate-400 font-mono">Live Simulation Tool</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Click a scenario below to demonstrate how AyudaChain catches actual corruption attempts:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1">
            <button
              onClick={() => handleVerify("AMOUNT_ALTERED")}
              className={`p-2.5 rounded-lg text-xs font-bold border text-left transition cursor-pointer flex flex-col justify-between ${
                fraudType === "AMOUNT_ALTERED"
                  ? "bg-rose-100 text-rose-900 border-rose-400 shadow-xs"
                  : "bg-white text-slate-700 hover:bg-rose-50 border-slate-200"
              }`}
            >
              <span className="text-[11px] text-rose-600 font-black">Scenario A: Pocketing Cash</span>
              <span className="text-[10px] text-slate-500 mt-0.5">Kupit sa Pera — clerk reduces ₱5k to ₱2k in local DB</span>
            </button>

            <button
              onClick={() => handleVerify("NAME_SWAPPED")}
              className={`p-2.5 rounded-lg text-xs font-bold border text-left transition cursor-pointer flex flex-col justify-between ${
                fraudType === "NAME_SWAPPED"
                  ? "bg-rose-100 text-rose-900 border-rose-400 shadow-xs"
                  : "bg-white text-slate-700 hover:bg-rose-50 border-slate-200"
              }`}
            >
              <span className="text-[11px] text-rose-600 font-black">Scenario B: Ghost Beneficiary</span>
              <span className="text-[10px] text-slate-500 mt-0.5">Multong Claim — insider swaps evacuee name to relative</span>
            </button>

            <button
              onClick={() => handleVerify(null)}
              className={`p-2.5 rounded-lg text-xs font-bold border text-left transition cursor-pointer flex flex-col justify-between ${
                fraudType === null
                  ? "bg-emerald-100 text-emerald-900 border-emerald-400 shadow-xs"
                  : "bg-white text-slate-700 hover:bg-emerald-50 border-slate-200"
              }`}
            >
              <span className="text-[11px] text-emerald-700 font-black">✓ Restore Authentic Record</span>
              <span className="text-[10px] text-slate-500 mt-0.5">Tunay na Talaan — restore sealed ₱5k government record</span>
            </button>
          </div>
        </div>

        {/* The Big Result Card: Plain English for Citizens */}
        {result && (
          <div
            className={`p-6 rounded-2xl border-2 transition-all ${
              result.is_verified
                ? "bg-emerald-50/90 border-emerald-400 text-emerald-950"
                : "bg-rose-50/90 border-rose-400 text-rose-950"
            }`}
          >
            {/* Main Header Badge */}
            <div className="flex items-start sm:items-center gap-3 mb-4">
              {result.is_verified ? (
                <div className="w-12 h-12 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-lg shrink-0">
                  <CheckCircle2 className="w-7 h-7" />
                </div>
              ) : (
                <div className="w-12 h-12 rounded-full bg-rose-500 text-white flex items-center justify-center shadow-lg shrink-0">
                  <XCircle className="w-7 h-7" />
                </div>
              )}
              <div>
                <h2 className="text-xl font-black tracking-tight">
                  {result.is_verified
                    ? "✓ 100% AUTHENTIC & UNALTERED GOVERNMENT AID"
                    : "⚠️ CORRUPTION ALERT: RECORD HAS BEEN ALTERED!"}
                </h2>
                <p className="text-xs sm:text-sm font-semibold mt-0.5 opacity-90">
                  {result.status_message}
                </p>
              </div>
            </div>

            {/* Plain English Comparison Table */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
              {/* Box 1: What is in the local database / office paper */}
              <div className="bg-white/90 p-4 rounded-xl border border-slate-200 space-y-2">
                <span className="text-[10px] font-bold tracking-wider uppercase text-slate-500 block">
                  1. Current Office / Local Database Record
                </span>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Beneficiary Head:</span>
                    <strong className={fraudType === "NAME_SWAPPED" ? "text-rose-600 font-mono" : "text-slate-900"}>
                      {fraudType === "NAME_SWAPPED" ? "Pedro Santos (Mayor's Relative)" : (activeBen?.household_name || "Danilo Soriano")}
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Disbursement Amount:</span>
                    <strong className={fraudType === "AMOUNT_ALTERED" ? "text-rose-600 font-mono text-sm" : "text-slate-900 text-sm"}>
                      {fraudType === "AMOUNT_ALTERED" ? "₱2,000.00 (Reduced!)" : `₱${(activeDist?.amount || 5000).toLocaleString()}.00`}
                    </strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Location:</span>
                    <span className="font-semibold text-slate-900">{activeBen?.barangay_name || "San Isidro"}</span>
                  </div>
                </div>
                {fraudType && (
                  <div className="p-2 bg-rose-50 rounded text-[11px] text-rose-700 font-bold border border-rose-200">
                    ⚠ Local office record does not match original distribution!
                  </div>
                )}
              </div>

              {/* Box 2: What is permanently sealed in the Polygon Blockchain */}
              <div className="bg-white/90 p-4 rounded-xl border border-slate-200 space-y-2">
                <span className="text-[10px] font-bold tracking-wider uppercase text-slate-500 block">
                  2. Permanent Seal Stamped on Blockchain
                </span>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Original Registered Head:</span>
                    <strong className="text-emerald-800">{activeBen?.household_name || "Danilo Soriano"}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Official Grant Amount:</span>
                    <strong className="text-emerald-800 text-sm font-black">₱5,000.00</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Blockchain Witness:</span>
                    <span className="font-mono text-emerald-700 text-[11px]">Polygon Amoy / EVM</span>
                  </div>
                </div>
                <div className="p-2 bg-emerald-50 rounded text-[11px] text-emerald-800 font-semibold border border-emerald-200">
                  ✓ Immutable seal recorded at time of distribution
                </div>
              </div>
            </div>

            {/* Why This Matters Explainer */}
            <div className="mt-4 pt-4 border-t border-slate-200/80 text-xs">
              <p className="text-slate-700">
                <strong>What this means for citizens &amp; auditors:</strong>{" "}
                {result.is_verified ? (
                  <span>
                    The family received their exact ₱5,000 emergency aid. The local government office cannot claim they gave more or less money than what was sealed.
                  </span>
                ) : (
                  <span className="text-rose-800 font-semibold">
                    Fraud attempt exposed! An insider tried to secretly modify records in the office database. Because the original transaction was sealed on Polygon, the fraud was caught in under 1 second.
                  </span>
                )}
              </p>
            </div>

            {/* Technical Details Toggle */}
            <div className="mt-4 pt-2">
              <button
                onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                className="text-[11px] font-bold text-slate-600 hover:text-slate-900 flex items-center gap-1 cursor-pointer"
              >
                {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                {showTechnicalDetails ? "Hide Raw Cryptographic Hashes" : "Show Raw Cryptographic Hashes (For Technical Auditors & Judges)"}
              </button>

              {showTechnicalDetails && (
                <div className="mt-3 p-3 bg-slate-900 text-white rounded-xl text-[11px] font-mono space-y-2">
                  <div>
                    <span className="text-slate-400 block text-[10px]">LOCAL CALCULATED SHA-256 (OFF-CHAIN DB):</span>
                    <p className="text-amber-400 break-all">{result.receipt_hash_local}</p>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">PERMANENT POLYGON ON-CHAIN HASH:</span>
                    <p className="text-emerald-400 break-all">{result.receipt_hash_onchain}</p>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-[10px] text-slate-400">
                    <div>Smart Contract: {result.contract_address}</div>
                    <div>Tx Hash: {result.blockchain_tx_hash || "Confirmed in Block"}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 3 Everyday Benefits: Why Normal Filipinos Care */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
            1
          </div>
          <h3 className="font-bold text-slate-900 text-sm">For Normal Evacuees</h3>
          <p className="text-slate-500 text-[11px] leading-relaxed">
            If an official hands a family ₱2,000 cash and claims <em>"that's all the government gave us"</em>, the family can look up their voucher and prove the national government sent ₱5,000.
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
            2
          </div>
          <h3 className="font-bold text-slate-900 text-sm">For Honest Barangay Workers</h3>
          <p className="text-slate-500 text-[11px] leading-relaxed">
            Field workers are often falsely accused of stealing relief packs. The on-chain timestamp and voucher receipt protect honest workers with permanent proof of distribution.
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-bold">
            3
          </div>
          <h3 className="font-bold text-slate-900 text-sm">For COA &amp; Ombudsman</h3>
          <p className="text-slate-500 text-[11px] leading-relaxed">
            State auditors don't need 18 months to open thousands of paper boxes. Any altered spreadsheet or padded receipt is caught automatically in seconds.
          </p>
        </div>
      </div>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={<div className="py-20 text-center text-slate-500 font-medium">Loading verification tool...</div>}>
      <VerifyContent />
    </Suspense>
  );
}
