"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  Receipt, CheckCircle2, Lock, ArrowRight, ShieldCheck,
  FileCheck, RefreshCw, Eye, AlertTriangle, AlertCircle,
  Wifi, WifiOff, X
} from "lucide-react";
import { fetchDistributions, fetchBeneficiaries, fetchBatches, confirmDistribution, DistributionConfirmPayload, Distribution, Beneficiary, ReliefBatch, apiUrl, formatPeso } from "@/lib/api";
import { useChainStatus, chainLabel } from "@/lib/useChainStatus";
import { useRole } from "@/lib/roleContext";
import { receiptVerificationHref } from "@/lib/receiptNavigation";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { submitOnlinePayout } from "@/lib/payoutConnection";

export default function DistributionsPage() {
  const chain = useChainStatus();
  const { role, account } = useRole();
  const browserOnline = useBrowserOnline();
  const [distributions, setDistributions] = useState<Distribution[]>([]);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [batches, setBatches] = useState<ReliefBatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // New Distribution Form State
  const [selectedBenId, setSelectedBenId] = useState("");
  const [amountStr, setAmountStr] = useState("");
  const numericAmount = parseFloat(amountStr) || 0;
  const selectedReceipt = "sample_relief_receipt.svg";
  const [step, setStep] = useState<"IDLE" | "SUBMITTING" | "SUCCESS">("IDLE");
  const submitting = useRef(false);
  const pendingSubmission = useRef<{ key: string; payload: DistributionConfirmPayload; serialized: string } | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [confirmedResult, setConfirmedResult] = useState<Distribution | null>(null);
  const [previewReceipt, setPreviewReceipt] = useState<Distribution | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setLoadError(null);
      const [dList, bList, batchList] = await Promise.all([
        fetchDistributions(),
        fetchBeneficiaries(),
        fetchBatches()
      ]);
      setDistributions(dList);
      setBeneficiaries(bList);
      setBatches(batchList);
      if (bList.length > 0) {
        // Find an un-distributed verified beneficiary or default to first
        const candidate = bList.find((b) => b.verification_status === "VERIFIED" && b.review_status === "APPROVED" && !dList.some((d) => d.beneficiary_id === b.beneficiary_id && d.batch_id === b.batch_id)) || bList[0];
        setSelectedBenId((current) => current || candidate.beneficiary_id);
      }
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [account?.id]);

  const handleDisburse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBenId || submitting.current) return;
    if (role !== "DISBURSING" || loading || loadError) {
      setSubmitError("Sign in as a disbursing officer and refresh the household records before recording a payout.");
      return;
    }

    submitting.current = true;
    setSubmitError(null);
    setConfirmedResult(null);
    setStep("SUBMITTING");
    try {
      const payload: DistributionConfirmPayload = {
        beneficiary_id: selectedBenId,
        batch_id: selectedBeneficiaryObj?.batch_id || "",
        amount: numericAmount,
        receipt_filename: selectedReceipt
      };
      const serialized = JSON.stringify(payload);
      if (pendingSubmission.current?.serialized !== serialized) {
        const bytes = crypto.getRandomValues(new Uint8Array(16));
        const key = "payout-" + Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
        pendingSubmission.current = { key, payload, serialized };
      }
      const request = pendingSubmission.current;
      const result = await submitOnlinePayout(navigator.onLine, () => confirmDistribution(request.payload, request.key));
      setConfirmedResult(result);
      setStep("SUCCESS");
      await loadData();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : String(err));
      setStep("IDLE");
    } finally {
      submitting.current = false;
    }
  };

  const selectedBeneficiaryObj = beneficiaries.find((b) => b.beneficiary_id === selectedBenId);
  const selectedBatch = batches.find((b) => b.batch_id === selectedBeneficiaryObj?.batch_id);
  const selectedIsApproved =
    selectedBeneficiaryObj?.verification_status === "VERIFIED" && selectedBeneficiaryObj?.review_status === "APPROVED";
  const standardGrant = selectedBatch?.standard_grant ?? 0;
  const maxGrant = selectedBatch?.max_grant ?? 0;

  // Start each household at its batch's standard grant
  useEffect(() => {
    if (selectedBatch) setAmountStr(String(selectedBatch.standard_grant));
  }, [selectedBenId, selectedBatch?.batch_id]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              <Receipt className="w-6 h-6 text-blue-600" />
              Record a demo payout
            </h1>

          </div>
          <p className="text-xs text-slate-500 mt-1">
            Select an approved household, record a fictional grant, then check its receipt.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/verify"
            className="px-3.5 py-1.5 bg-emerald-50 text-emerald-800 border border-emerald-300 font-bold rounded-lg text-xs hover:bg-emerald-100 transition flex items-center gap-1.5"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            Check receipts
          </Link>
        </div>
      </div>

      {loading && <p role="status" className="text-sm text-slate-600">Loading household and payout records...</p>}
      {loadError && <div role="alert" className="p-4 border border-rose-200 bg-rose-50 rounded-xl text-sm text-rose-900">{loadError} <button type="button" onClick={() => void loadData()} className="underline font-semibold min-h-11">Refresh records</button></div>}
      {!loading && !loadError && beneficiaries.length === 0 && <p className="text-sm text-slate-600">No active households are available. <Link href="/beneficiaries" className="underline text-blue-700">Open the household registry</Link>.</p>}

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (5 Cols): Distribution Action Form */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div role={browserOnline === false ? "alert" : "status"} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-sm text-slate-700 space-y-1">
            <p className="flex items-center gap-2 font-semibold">{browserOnline === true ? <Wifi className="w-4 h-4" aria-hidden="true" /> : browserOnline === false ? <WifiOff className="w-4 h-4" aria-hidden="true" /> : null}{browserOnline === true ? "Browser reports a connection" : browserOnline === false ? "Browser is offline" : "Checking browser connection..."}</p>
            <p className="text-xs">{browserOnline === false ? "Reconnect before recording a payout. This screen does not queue payouts offline." : "Record a payout through the API. Blockchain anchoring can still fail."}</p>
            <p className="text-xs">{chainLabel(chain)}</p>
          </div>

          <div className="flex justify-between items-center border-b border-slate-100 pb-3">
            <div>
              <h2 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                <Receipt className="w-4 h-4 text-blue-600" />
                Payout details
              </h2>
              <span className="text-[10px] text-slate-500 block">
                Use fictional household records only.
              </span>
            </div>
            {selectedBatch && <span className="text-xs text-slate-600 break-all">{selectedBatch.batch_id}</span>}
          </div>

          <form onSubmit={handleDisburse} className="space-y-4 text-xs">
            {/* Manual household selection */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label htmlFor="payout-household" className="font-semibold text-slate-700">Household</label>
              </div>
              <select
                id="payout-household"
                value={selectedBenId}
                disabled={step === "SUBMITTING" || loading || Boolean(loadError)}
                onChange={(e) => setSelectedBenId(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                {beneficiaries.map((b) => (
                  <option key={b.beneficiary_id} value={b.beneficiary_id}>
                    {b.beneficiary_id} ({b.dafac_id || "No demo card reference"}) · {b.household_name} ({b.barangay_name})
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
                  <span className={`font-bold ${selectedIsApproved ? "text-emerald-600" : "text-amber-600"}`}>{selectedBeneficiaryObj.verification_status}</span>
                </div>
                {distributions.some((d) => d.beneficiary_id === selectedBenId) && (
                  <div className="pt-1.5 border-t border-slate-200 text-rose-700 font-bold flex items-center gap-1 text-[11px]">
                    <AlertCircle className="w-3.5 h-3.5" />
                    A payout is already recorded for this household. This does not confirm cash delivery.
                  </div>
                )}
              </div>
            )}

            {/* Amount */}
            <div>
              <label htmlFor="payout-amount" className="block font-semibold text-slate-700 mb-1">Fictional amount (PHP)</label>
              <input
                id="payout-amount"
                type="number"
                min="0.01"
                step="0.01"
                value={amountStr}
                disabled={step === "SUBMITTING"}
                onChange={(e) => setAmountStr(e.target.value)}
                placeholder={String(standardGrant || "")}
                className={`w-full px-3 py-2 border rounded-lg text-sm font-bold focus:outline-none focus:ring-2 ${
                  numericAmount > maxGrant || (amountStr !== "" && numericAmount <= 0)
                    ? "border-rose-400 bg-rose-50/50 text-rose-900 focus:ring-rose-500"
                    : numericAmount !== standardGrant
                    ? "border-amber-400 bg-amber-50/50 text-amber-900 focus:ring-amber-500"
                    : "border-slate-300 text-slate-900 focus:ring-blue-500"
                }`}
              />

              {/* Real-Time Amount Feedback */}
              {selectedBatch && numericAmount === standardGrant && (
                <p className="text-[11px] text-emerald-600 font-semibold mt-1 flex items-center gap-1">
                  ✓ Standard grant for this batch ({formatPeso(standardGrant)})
                </p>
              )}

              {selectedBatch && numericAmount > 0 && numericAmount !== standardGrant && numericAmount <= maxGrant && (
                <div className="p-2.5 bg-amber-50 border border-amber-300 rounded-lg text-[11px] text-amber-900 mt-1.5 space-y-0.5 animate-in fade-in">
                  <p className="font-bold flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    Different from the batch standard ({formatPeso(numericAmount)})
                  </p>
                  <p className="text-amber-800 text-[10px]">
                    This batch's standard grant is {formatPeso(standardGrant)}. Check the amount before recording it.
                  </p>
                </div>
              )}

              {selectedBatch && numericAmount > maxGrant && (
                <div className="p-2.5 bg-rose-50 border border-rose-300 rounded-lg text-[11px] text-rose-900 mt-1.5 space-y-0.5 animate-in fade-in">
                  <p className="font-bold flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                    Above this batch's maximum ({formatPeso(maxGrant)})
                  </p>
                  <p className="text-rose-800 text-[10px]">
                    Each fictional batch sets its own maximum grant. The backend rejects payouts above it.
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
              <label className="block font-semibold text-slate-700 mb-1">Demo receipt template</label>
              <div className="p-3 border border-dashed border-slate-300 rounded-xl bg-slate-50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileCheck className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-bold text-slate-900">sample_relief_receipt.svg</p>
                    <p className="text-[10px] text-slate-400">Fictional SVG template; receipt uploads are not available here.</p>
                  </div>
                </div>
                <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded">Sample</span>
              </div>
            </div>

            {/* Step Progression */}
            {step !== "IDLE" && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl space-y-1.5 text-[11px]">
                <div className="flex items-center gap-2 text-blue-900 font-bold">
                  {step !== "SUCCESS" && <RefreshCw className="w-3.5 h-3.5 animate-spin text-blue-600" />}
                  {step === "SUBMITTING" && "Saving payout..."}
                  {step === "SUCCESS" && "Payout recorded."}
                </div>
              </div>
            )}

            {submitError && (
              <p role="alert" className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-900">
                {submitError} Retry the same details to retrieve an existing payout if the response was lost.
              </p>
            )}

            {/* Confirmed Success Card */}
            {confirmedResult && step === "SUCCESS" && (
              <div role="status" className="p-4 bg-blue-50 border border-blue-200 rounded-xl space-y-3 text-sm">
                <div className="flex items-center gap-1.5 text-blue-950 font-bold">
                  <CheckCircle2 className="w-4 h-4" />
                  Payout recorded
                </div>
                <p className="text-slate-800">{beneficiaries.find((household) => household.beneficiary_id === confirmedResult.beneficiary_id)?.household_name || confirmedResult.beneficiary_id} · {formatPeso(confirmedResult.amount)}</p>
                <p className="text-xs text-slate-600 break-all">Receipt: {confirmedResult.distribution_id}</p>
                <p className="text-xs text-slate-700">{confirmedResult.blockchain_tx_hash ? "An anchor transaction is recorded. Check this receipt for its current integrity result." : "No anchor transaction is recorded. The payout is saved; resubmitting it will not retry anchoring."}</p>
                <p className="text-xs text-slate-600">Synthetic payout. A receipt check does not prove cash delivery.</p>
                <Link
                  href={receiptVerificationHref(confirmedResult.distribution_id)}
                  className="flex items-center justify-center gap-2 min-h-11 px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
                >
                  Check this receipt <ArrowRight className="w-4 h-4" aria-hidden="true" />
                </Link>
                <details className="text-xs text-slate-700">
                  <summary className="cursor-pointer py-2 font-semibold">Receipt hash and transaction</summary>
                  <dl className="space-y-2 mt-2">
                    <div><dt className="font-semibold">Receipt hash</dt><dd className="font-mono break-all">{confirmedResult.receipt_hash}</dd></div>
                    <div><dt className="font-semibold">Anchor transaction</dt><dd className="font-mono break-all">{confirmedResult.blockchain_tx_hash || "None recorded"}</dd></div>
                  </dl>
                </details>
              </div>
            )}

            {role !== "DISBURSING" ? (
              <div className="p-3 bg-slate-100 rounded-xl border border-slate-200 text-center text-slate-500 text-xs space-y-1">
                <p className="font-semibold text-slate-700">Payout entry is for disbursing officers</p>
                <p className="text-[11px]">
                  Your signed-in role can inspect these records. A disbursing officer records the payout.
                </p>
              </div>
            ) : (
              <button
                type="submit"
                disabled={step !== "IDLE" && step !== "SUCCESS" || !browserOnline || loading || Boolean(loadError) || selectedBatch?.status !== "ACTIVE" || !selectedBatch || !selectedIsApproved || numericAmount > maxGrant || numericAmount <= 0 || distributions.some((d) => d.beneficiary_id === selectedBenId)}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow transition disabled:opacity-50 text-xs flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed"
              >
                <Lock className="w-3.5 h-3.5" />
                {distributions.some((d) => d.beneficiary_id === selectedBenId)
                  ? "Claim Already Completed for this Household"
                  : browserOnline === null
                  ? "Checking browser connection"
                  : !browserOnline
                  ? "Reconnect to record a payout"
                  : selectedBatch && selectedBatch.status !== "ACTIVE"
                  ? "Batch is not active"
                  : selectedBeneficiaryObj && !selectedIsApproved
                  ? "Household Not Approved for Payout"
                  : numericAmount > maxGrant
                  ? `Cannot Disburse: Above ${formatPeso(maxGrant)} Maximum`
                  : submitError ? "Retry payout request" : "Record demo payout"}
              </button>
            )}
          </form>
        </div>

        {/* Right Column (7 Cols): Recent Confirmed Distributions */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center border-b border-slate-100 pb-3">
            <div>
              <h2 className="font-bold text-sm text-slate-900">Recorded payouts</h2>
              <p className="text-xs text-slate-500">Open a receipt to check its current integrity.</p>
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
                  <span className="text-[10px] text-slate-700 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded font-semibold flex items-center gap-1">
                    <Receipt className="w-3 h-3" aria-hidden="true" />
                    {dist.blockchain_tx_hash ? "Anchor transaction recorded" : "No anchor transaction"}
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPreviewReceipt(dist)}
                      className="text-slate-600 hover:text-blue-600 font-semibold flex items-center gap-1 text-xs"
                    >
                      <Eye className="w-3.5 h-3.5" /> View Receipt
                    </button>
                    <Link
                      href={receiptVerificationHref(dist.distribution_id)}
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
                <h3 className="font-bold text-base text-slate-900">Demo payout receipt</h3>
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
              {previewReceipt.receipt_file_path ? <img
                src={apiUrl(previewReceipt.receipt_file_path)}
                alt="Relief Receipt"
                className="max-h-96 rounded-lg shadow-sm border border-slate-300"
              /> : <p className="text-sm text-slate-600">No household receipt image is available for this record. Its saved hash can still be checked.</p>}
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
                  href={receiptVerificationHref(previewReceipt.distribution_id)}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs shadow transition"
                >
                  Verify Integrity On-Chain →
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
