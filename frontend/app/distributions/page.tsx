"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Receipt, CheckCircle2, Lock, ArrowRight, ShieldCheck, Upload,
  FileCheck, Sparkles, ExternalLink, RefreshCw, Eye, AlertTriangle, AlertCircle,
  Camera, QrCode, Wifi, WifiOff, X
} from "lucide-react";
import { fetchDistributions, fetchBeneficiaries, confirmDistribution, Distribution, Beneficiary } from "@/lib/api";
import { useRole } from "@/lib/roleContext";

export default function DistributionsPage() {
  const { role } = useRole();
  const [distributions, setDistributions] = useState<Distribution[]>([]);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [loading, setLoading] = useState(true);

  // New Distribution Form State
  const [selectedBenId, setSelectedBenId] = useState("");
  const [amountStr, setAmountStr] = useState("5000");
  const numericAmount = parseFloat(amountStr) || 0;
  const [selectedReceipt, setSelectedReceipt] = useState("sample_relief_receipt.svg");
  const [step, setStep] = useState<"IDLE" | "PREPARING" | "OFFCHAIN_STORED" | "ANCHORING" | "SUCCESS">("IDLE");
  const [confirmedResult, setConfirmedResult] = useState<Distribution | null>(null);
  const [previewReceipt, setPreviewReceipt] = useState<Distribution | null>(null);

  // QR Scanner & Offline Resilience State
  const [showScanner, setShowScanner] = useState(false);
  const [offlineSimulated, setOfflineSimulated] = useState(false);
  const [scannedAlert, setScannedAlert] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [dList, bList] = await Promise.all([
        fetchDistributions(),
        fetchBeneficiaries()
      ]);
      setDistributions(dList);
      setBeneficiaries(bList);
      if (bList.length > 0) {
        // Find an un-distributed verified beneficiary or default to first
        const candidate = bList.find((b) => b.verification_status === "VERIFIED") || bList[0];
        setSelectedBenId(candidate.beneficiary_id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDisburse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBenId) return;

    setStep("PREPARING");
    try {
      await new Promise((r) => setTimeout(r, 400));
      setStep("OFFCHAIN_STORED");
      await new Promise((r) => setTimeout(r, 400));
      setStep("ANCHORING");

      const distId = `DIST-${Date.now().toString().slice(-4)}`;
      const result = await confirmDistribution({
        distribution_id: distId,
        beneficiary_id: selectedBenId,
        batch_id: "RELIEF-2026-001",
        amount: numericAmount,
        receipt_filename: selectedReceipt
      });

      setConfirmedResult(result);
      setStep("SUCCESS");
      await loadData();
    } catch (err) {
      alert("Distribution failed: " + String(err));
    } finally {
      if (step !== "SUCCESS") setStep("IDLE");
    }
  };

  const selectedBeneficiaryObj = beneficiaries.find((b) => b.beneficiary_id === selectedBenId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              <Receipt className="w-6 h-6 text-blue-600" />
              Household Relief Distribution
            </h1>
            <span className="text-xs text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200 font-semibold">
              Pamamahagi ng Ayuda
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            <strong>Point-of-Payout &amp; Blockchain Seal:</strong> Scan or select the evacuee using their DAFAC ID, release the ₱5,000 cash grant, and generate an immutable on-chain receipt proof.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/verify"
            className="px-3.5 py-1.5 bg-emerald-50 text-emerald-800 border border-emerald-300 font-bold rounded-lg text-xs hover:bg-emerald-100 transition flex items-center gap-1.5"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            Verify Receipts On-Chain →
          </Link>
        </div>
      </div>

      {/* 3-Step Protocol Bar for Barangay Field Workers */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
        <div className="p-3 bg-blue-50/70 border border-blue-200 rounded-xl flex items-start gap-2.5">
          <span className="w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[11px] flex items-center justify-center shrink-0">1</span>
          <div>
            <span className="font-bold text-blue-950 block">1. Scan or Select Evacuee</span>
            <span className="text-[11px] text-blue-700">I-scan ang DAFAC QR code o hanapin ang pangalan.</span>
          </div>
        </div>
        <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-xl flex items-start gap-2.5">
          <span className="w-5 h-5 rounded-full bg-emerald-600 text-white font-bold text-[11px] flex items-center justify-center shrink-0">2</span>
          <div>
            <span className="font-bold text-emerald-950 block">2. Hand Out ₱5,000.00 Ayuda</span>
            <span className="text-[11px] text-emerald-700">Siguraduhing buo ang perang matatanggap ng pamilya.</span>
          </div>
        </div>
        <div className="p-3 bg-indigo-50/70 border border-indigo-200 rounded-xl flex items-start gap-2.5">
          <span className="w-5 h-5 rounded-full bg-indigo-600 text-white font-bold text-[11px] flex items-center justify-center shrink-0">3</span>
          <div>
            <span className="font-bold text-indigo-950 block">3. Confirm &amp; Anchor On-Chain</span>
            <span className="text-[11px] text-indigo-700">Awtomatikong selyuhan ang resibo sa blockchain.</span>
          </div>
        </div>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (5 Cols): Distribution Action Form */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          {/* Offline Resilience Status Pill */}
          <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-xs">
            <div className="flex items-center gap-2">
              {offlineSimulated ? (
                <WifiOff className="w-4 h-4 text-amber-600 shrink-0" />
              ) : (
                <Wifi className="w-4 h-4 text-emerald-600 shrink-0" />
              )}
              <div>
                <span className="font-bold text-slate-800 text-[11px] block">
                  {offlineSimulated ? "Evacuation Center Mode: Offline Caching" : "Network Status: Connected to Polygon"}
                </span>
                <p className="text-[10px] text-slate-500">
                  {offlineSimulated
                    ? "Cell towers down. Vouchers queue in local device storage and batch-sync when reconnected."
                    : "Real-time on-chain confirmation active on Polygon Amoy / Local EVM."}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setOfflineSimulated(!offlineSimulated)}
              className={`px-2.5 py-1 rounded text-[10px] font-bold border transition cursor-pointer shrink-0 ${
                offlineSimulated
                  ? "bg-amber-100 text-amber-800 border-amber-300"
                  : "bg-white text-slate-700 hover:bg-slate-100 border-slate-300"
              }`}
            >
              {offlineSimulated ? "✓ Reconnect" : "Test Offline Mode"}
            </button>
          </div>

          <div className="flex justify-between items-center border-b border-slate-100 pb-3">
            <div>
              <h2 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <Receipt className="w-4 h-4 text-blue-600" />
                Confirm Relief Disbursement
              </h2>
              <span className="text-[10px] text-slate-500 block">
                DAFAC: Disaster Assistance Family Access Card (DSWD Form)
              </span>
            </div>
            <span className="text-[11px] font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-600">Batch 2026-001</span>
          </div>

          {scannedAlert && (
            <div className="p-2.5 bg-emerald-50 border border-emerald-300 rounded-xl text-emerald-900 text-xs font-semibold flex items-center justify-between animate-in fade-in">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                {scannedAlert}
              </span>
              <button onClick={() => setScannedAlert(null)} className="text-emerald-700 hover:text-emerald-900 text-xs">
                ✕
              </button>
            </div>
          )}

          <form onSubmit={handleDisburse} className="space-y-4 text-xs">
            {/* Beneficiary Select with QR Scanner Trigger */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="font-semibold text-slate-700">Select Beneficiary Household</label>
                <button
                  type="button"
                  onClick={() => setShowScanner(true)}
                  className="inline-flex items-center gap-1 text-[11px] font-bold text-blue-700 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-2 py-0.5 rounded-lg border border-blue-200 transition cursor-pointer"
                >
                  <Camera className="w-3 h-3 text-blue-600" />
                  Scan DAFAC QR
                </button>
              </div>
              <select
                value={selectedBenId}
                onChange={(e) => setSelectedBenId(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                {beneficiaries.map((b) => (
                  <option key={b.beneficiary_id} value={b.beneficiary_id}>
                    {b.beneficiary_id} ({b.dafac_id || `DFC-2026-${b.beneficiary_id.slice(-4)}`}) — {b.household_name} ({b.barangay_name})
                  </option>
                ))}
              </select>
            </div>

            {/* Selected Beneficiary Info Card */}
            {selectedBeneficiaryObj && (
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-slate-600 space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-500">Locality:</span>
                  <span className="font-semibold text-slate-900">{selectedBeneficiaryObj.barangay_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Status:</span>
                  <span className="font-bold text-emerald-600">{selectedBeneficiaryObj.verification_status}</span>
                </div>
                {distributions.some((d) => d.beneficiary_id === selectedBenId) && (
                  <div className="pt-1.5 border-t border-slate-200 text-rose-700 font-bold flex items-center gap-1 text-[11px]">
                    <AlertCircle className="w-3.5 h-3.5" />
                    Warning: This household has already received aid! Duplicate claims will be rejected.
                  </div>
                )}
              </div>
            )}

            {/* Amount */}
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Disbursement Amount (PHP)</label>
              <input
                type="number"
                value={amountStr}
                onChange={(e) => setAmountStr(e.target.value)}
                placeholder="5000"
                className={`w-full px-3 py-2 border rounded-lg text-sm font-bold focus:outline-none focus:ring-2 ${
                  numericAmount > 10000 || (amountStr !== "" && numericAmount <= 0)
                    ? "border-rose-400 bg-rose-50/50 text-rose-900 focus:ring-rose-500"
                    : numericAmount !== 5000
                    ? "border-amber-400 bg-amber-50/50 text-amber-900 focus:ring-amber-500"
                    : "border-slate-300 text-slate-900 focus:ring-blue-500"
                }`}
              />

              {/* Real-Time Amount Feedback */}
              {numericAmount === 5000 && (
                <p className="text-[11px] text-emerald-600 font-semibold mt-1 flex items-center gap-1">
                  ✓ Standard Calamity Relief Grant (₱5,000.00)
                </p>
              )}

              {numericAmount > 0 && numericAmount !== 5000 && numericAmount <= 10000 && (
                <div className="p-2.5 bg-amber-50 border border-amber-300 rounded-lg text-[11px] text-amber-900 mt-1.5 space-y-0.5 animate-in fade-in">
                  <p className="font-bold flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    AI Anomaly Flag: Irregular Grant Amount (₱{numericAmount.toLocaleString()})
                  </p>
                  <p className="text-amber-800 text-[10px]">
                    Standard calamity grant is ₱5,000.00. AyudaChain AI Anomaly Engine will automatically record this irregularity on the on-chain audit trail for Ombudsman/COA auditor review.
                  </p>
                </div>
              )}

              {numericAmount > 10000 && (
                <div className="p-2.5 bg-rose-50 border border-rose-300 rounded-lg text-[11px] text-rose-900 mt-1.5 space-y-0.5 animate-in fade-in">
                  <p className="font-bold flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                    Ceiling Limit Exceeded (Max ₱10,000.00)
                  </p>
                  <p className="text-rose-800 text-[10px]">
                    Statutory calamity cash grant limit is ₱10,000.00. This disbursement will be rejected by backend governance rules.
                  </p>
                </div>
              )}

              {amountStr !== "" && numericAmount <= 0 && (
                <p className="text-[11px] text-rose-600 font-semibold mt-1">
                  Amount must be greater than zero.
                </p>
              )}
            </div>

            {/* Receipt Selection & Simulated OCR */}
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Official Voucher Receipt Asset</label>
              <div className="p-3 border border-dashed border-slate-300 rounded-xl bg-slate-50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileCheck className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-bold text-slate-900">sample_relief_receipt.svg</p>
                    <p className="text-[10px] text-slate-400">DSWD Official Acknowledgement Voucher (2.4 KB)</p>
                  </div>
                </div>
                <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded">OCR Ready</span>
              </div>
            </div>

            {/* Architectural Callout: File vs Proof */}
            <div className="bg-slate-900 text-slate-300 p-3 rounded-xl text-[11px] space-y-1.5 font-mono">
              <div className="flex justify-between text-slate-400">
                <span>OFF-CHAIN STORAGE:</span>
                <span className="text-blue-400">receipt.svg (Local File)</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>ON-CHAIN ANCHOR:</span>
                <span className="text-emerald-400">SHA-256 (32 Bytes)</span>
              </div>
            </div>

            {/* Step Progression */}
            {step !== "IDLE" && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl space-y-1.5 text-[11px]">
                <div className="flex items-center gap-2 text-blue-900 font-bold">
                  {step !== "SUCCESS" && <RefreshCw className="w-3.5 h-3.5 animate-spin text-blue-600" />}
                  {step === "PREPARING" && "1. Normalizing OCR text payload..."}
                  {step === "OFFCHAIN_STORED" && "2. Storing receipt off-chain in database..."}
                  {step === "ANCHORING" && "3. Submitting SHA-256 hash to Polygon contract..."}
                  {step === "SUCCESS" && "4. ✓ Successfully confirmed on-chain!"}
                </div>
              </div>
            )}

            {/* Confirmed Success Card */}
            {confirmedResult && step === "SUCCESS" && (
              <div className="p-3.5 bg-emerald-50 border border-emerald-300 rounded-xl space-y-2 text-xs">
                <div className="flex items-center gap-1.5 text-emerald-800 font-bold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Disbursement Confirmed &amp; Anchored!
                </div>
                <div>
                  <span className="text-slate-500 font-mono text-[10px]">RECEIPT INTEGRITY HASH:</span>
                  <p className="font-mono text-[11px] text-slate-900 bg-white p-1.5 rounded border border-emerald-200 break-all">
                    {confirmedResult.receipt_hash}
                  </p>
                </div>
                <div>
                  <span className="text-slate-500 font-mono text-[10px]">POLYGON TRANSACTION HASH:</span>
                  <p className="font-mono text-[11px] text-emerald-700 bg-white p-1.5 rounded border border-emerald-200 break-all">
                    {confirmedResult.blockchain_tx_hash || "Confirmed in Block"}
                  </p>
                </div>
                <Link
                  href="/verify"
                  className="block text-center py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold text-xs shadow transition mt-2"
                >
                  Verify Authenticity on Blockchain Tool →
                </Link>
              </div>
            )}

            {role === "Public Citizen" ? (
              <div className="p-3 bg-slate-100 rounded-xl border border-slate-200 text-center text-slate-500 text-xs space-y-1">
                <p className="font-semibold text-slate-700">🔒 Disbursement Action Restricted</p>
                <p className="text-[11px]">
                  Public Citizen view is read-only. Switch your role to <strong>Barangay Officer</strong> in the top navigation to test relief disbursement.
                </p>
              </div>
            ) : (
              <button
                type="submit"
                disabled={step !== "IDLE" && step !== "SUCCESS" || numericAmount > 10000 || numericAmount <= 0 || distributions.some((d) => d.beneficiary_id === selectedBenId)}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow transition disabled:opacity-50 text-xs flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
              >
                <Lock className="w-3.5 h-3.5" />
                {distributions.some((d) => d.beneficiary_id === selectedBenId)
                  ? "Claim Already Completed for this Household"
                  : numericAmount > 10000
                  ? "Cannot Disburse: Exceeds ₱10,000 Limit"
                  : "Confirm Aid & Anchor on Polygon"}
              </button>
            )}
          </form>
        </div>

        {/* Right Column (7 Cols): Recent Confirmed Distributions */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center border-b border-slate-100 pb-3">
            <div>
              <h2 className="font-bold text-sm text-slate-900">Confirmed Household Distributions</h2>
              <p className="text-xs text-slate-500">Public trail of confirmed relief payments with on-chain proofs</p>
            </div>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-full">
              {distributions.length} Records
            </span>
          </div>

          <div className="divide-y divide-slate-100 overflow-y-auto max-h-[560px]">
            {distributions.map((dist) => (
              <div key={dist.id} className="py-3.5 space-y-2 text-xs">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="font-mono font-bold text-slate-900 text-sm">{dist.distribution_id}</span>
                    <span className="text-slate-400 mx-1.5">•</span>
                    <span className="font-semibold text-slate-700">Beneficiary: {dist.beneficiary_id}</span>
                  </div>
                  <span className="font-black text-slate-900 text-sm">₱{dist.amount.toLocaleString()}</span>
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[11px] text-slate-500 font-mono">
                  <span>Hash: {dist.receipt_hash.slice(0, 16)}...{dist.receipt_hash.slice(-6)}</span>
                  <span className="text-slate-400">{new Date(dist.distributed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    Polygon Anchored
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPreviewReceipt(dist)}
                      className="text-slate-600 hover:text-blue-600 font-semibold flex items-center gap-1 text-xs"
                    >
                      <Eye className="w-3.5 h-3.5" /> View Receipt
                    </button>
                    <Link
                      href={`/verify?distribution_id=${dist.distribution_id}`}
                      className="text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1 text-xs"
                    >
                      Verify <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Modal: View Receipt Preview & OCR Text */}
      {previewReceipt && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4 border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-bold text-base text-slate-900">Official Relief Disbursement Receipt</h3>
                <p className="text-xs text-slate-400 font-mono">ID: {previewReceipt.distribution_id}</p>
              </div>
              <button
                onClick={() => setPreviewReceipt(null)}
                className="text-slate-400 hover:text-slate-600 font-bold"
              >
                ✕
              </button>
            </div>

            {/* Receipt Preview */}
            <div className="bg-slate-100 rounded-xl p-4 flex justify-center border border-slate-200 mb-4">
              <img
                src={previewReceipt.receipt_file_path || "http://127.0.0.1:8000/receipts/sample_relief_receipt.svg"}
                alt="Relief Receipt"
                className="max-h-96 rounded-lg shadow-sm border border-slate-300"
              />
            </div>

            {/* OCR Extracted Text */}
            <div className="space-y-2 text-xs">
              <span className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">
                Normalized Content Hash (SHA-256 Digest)
              </span>
              <p className="font-mono text-[11px] text-emerald-800 bg-emerald-50 p-2 rounded border border-emerald-200 break-all font-semibold">
                {previewReceipt.receipt_hash}
              </p>
              <div className="pt-2 flex justify-end">
                <Link
                  href={`/verify?distribution_id=${previewReceipt.distribution_id}`}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs shadow transition"
                >
                  Verify Integrity On-Chain →
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Mobile DAFAC QR Scanner Viewfinder Modal */}
      {showScanner && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-md w-full p-6 text-white shadow-2xl relative animate-in fade-in space-y-4">
            <button
              onClick={() => setShowScanner(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2">
              <Camera className="w-5 h-5 text-blue-400" />
              <div>
                <h3 className="font-black text-base text-white">Point-of-Payout QR Scanner</h3>
                <p className="text-[11px] text-slate-400">Scan physical DAFAC relief acknowledgement voucher</p>
              </div>
            </div>

            {/* Simulated Camera Viewfinder */}
            <div className="relative bg-slate-950 rounded-2xl h-64 border border-slate-800 flex items-center justify-center overflow-hidden">
              {/* Corner brackets */}
              <div className="absolute top-8 left-8 w-8 h-8 border-t-2 border-l-2 border-blue-400 rounded-tl"></div>
              <div className="absolute top-8 right-8 w-8 h-8 border-t-2 border-r-2 border-blue-400 rounded-tr"></div>
              <div className="absolute bottom-8 left-8 w-8 h-8 border-b-2 border-l-2 border-blue-400 rounded-bl"></div>
              <div className="absolute bottom-8 right-8 w-8 h-8 border-b-2 border-r-2 border-blue-400 rounded-br"></div>

              {/* Animated scanning laser line */}
              <div className="absolute inset-x-8 top-1/2 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-pulse"></div>

              {/* Center QR watermark */}
              <div className="text-center space-y-2 opacity-80">
                <QrCode className="w-24 h-24 text-slate-600 mx-auto stroke-1" />
                <span className="text-[11px] text-slate-400 block font-mono">
                  Align DAFAC QR Code within frame
                </span>
              </div>
            </div>

            {/* Quick Demo Tap Vouchers for Pitching */}
            <div className="space-y-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                Tap Sample Voucher to Simulate Real Camera Scan:
              </span>
              <div className="space-y-1.5">
                {[
                  { id: "BEN-0004", name: "Danilo Soriano", dafac: "DFC-2026-0004", brgy: "San Isidro" },
                  { id: "BEN-0006", name: "Antonio Mercado", dafac: "DFC-2026-0006", brgy: "San Isidro" },
                  { id: "BEN-0005", name: "Carmencita Reyes", dafac: "DFC-2026-0005", brgy: "San Isidro" },
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      setSelectedBenId(item.id);
                      setAmountStr("5000");
                      setScannedAlert(`✓ Scanned DAFAC Voucher: ${item.name} (${item.dafac}) — Auto-loaded for disbursement!`);
                      setShowScanner(false);
                    }}
                    className="w-full text-left p-2.5 rounded-xl bg-slate-800/80 hover:bg-blue-600/30 border border-slate-700 hover:border-blue-500 transition text-xs flex items-center justify-between cursor-pointer group"
                  >
                    <div>
                      <p className="font-bold text-white group-hover:text-blue-300">{item.name}</p>
                      <p className="text-[10px] text-slate-400 font-mono">DAFAC: {item.dafac} • {item.brgy}</p>
                    </div>
                    <span className="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded font-bold">
                      Scan This Voucher →
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
