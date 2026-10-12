"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Users, AlertTriangle, CheckCircle2, Search, UserPlus, Filter,
  Sparkles, ArrowRight, ShieldCheck, X, RefreshCw, AlertCircle,
  FileSpreadsheet, UploadCloud
} from "lucide-react";
import { fetchBeneficiaries, registerBeneficiary, verifyBeneficiary, fetchBeneficiaryReviews, BeneficiaryReview, ReviewDecision, Beneficiary, uploadBeneficiaryCsv, CsvBatchResult, resolveBeneficiaryDuplicate } from "@/lib/api";
import { useRole } from "@/lib/roleContext";

export default function BeneficiariesPage() {
  const { role, account } = useRole();
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [showHistorical, setShowHistorical] = useState(false);
  const [canonicalId, setCanonicalId] = useState("");
  const [filterFlagged, setFilterFlagged] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedBen, setSelectedBen] = useState<Beneficiary | null>(null);
  const [reviewReason, setReviewReason] = useState("");
  const reviewer = account?.id;
  const canRegister = role === "DSWD" || role === "BARANGAY";
  const canInspectHistory = role === "DSWD" || role === "AUDITOR" || role === "BENEFICIARY";
  const [reviews, setReviews] = useState<BeneficiaryReview[]>([]);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [reviewSaving, setReviewSaving] = useState(false);
  const reviewSubmitting = useRef(false);
  const [historyVersion, setHistoryVersion] = useState(0);
  const [reviewSaved, setReviewSaved] = useState(false);

  // New beneficiary form modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newName, setNewName] = useState("");
  const [newBrgy, setNewBrgy] = useState(account?.barangay_id || "BRGY-001");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const registerSubmitting = useRef(false);
  const [registerError, setRegisterError] = useState<string | null>(null);

  // Batch CSV Upload & AI Verification State
  const [showCsvModal, setShowCsvModal] = useState(false);
  const [csvResult, setCsvResult] = useState<CsvBatchResult | null>(null);
  const [isAnalyzingCsv, setIsAnalyzingCsv] = useState(false);

  const loadBeneficiaries = async () => {
    try {
      setLoading(true);
      setLoadError(null);
      const data = await fetchBeneficiaries({ include_historical: showHistorical });
      setBeneficiaries(data);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : "Household records could not be loaded.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBeneficiaries();
  }, [showHistorical, account?.id]);

  useEffect(() => {
    setReviewReason("");
    setCanonicalId(selectedBen?.duplicate_matched_id || "");
    setReviewError(null);
    setReviewSaved(false);
  }, [selectedBen?.beneficiary_id]);

  useEffect(() => {
    if (!selectedBen || !canInspectHistory) return;
    let cancelled = false;
    setReviews([]);
    setHistoryError(null);
    setHistoryLoading(true);
    fetchBeneficiaryReviews(selectedBen.beneficiary_id)
      .then((data) => { if (!cancelled) setReviews(data); })
      .catch((err) => { if (!cancelled) setHistoryError(err instanceof Error ? err.message : String(err)); })
      .finally(() => { if (!cancelled) setHistoryLoading(false); });
    return () => { cancelled = true; };
  }, [selectedBen?.beneficiary_id, historyVersion, canInspectHistory]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || registerSubmitting.current) return;
    registerSubmitting.current = true;
    setRegisterError(null);
    setIsSubmitting(true);
    try {
      const brgyMap: Record<string, string> = {
        "BRGY-001": "San Isidro",
        "BRGY-002": "Santa Elena",
        "BRGY-003": "San Roque",
        "BRGY-004": "Maligaya"
      };
      const created = await registerBeneficiary({
        beneficiary_id: "BEN-" + crypto.randomUUID(),
        household_name: newName.trim(),
        barangay_id: account?.role === "BARANGAY" ? account.barangay_id || newBrgy : newBrgy,
        barangay_name: brgyMap[newBrgy] || "San Isidro",
        batch_id: "RELIEF-2026-001"
      });
      setShowAddModal(false);
      setNewName("");
      await loadBeneficiaries();
      setSelectedBen(created); // Open review modal for newly registered
    } catch (err) {
      setRegisterError(err instanceof Error ? err.message : "Registration failed. Try again.");
    } finally {
      registerSubmitting.current = false;
      setIsSubmitting(false);
    }
  };

  const handleManualVerify = async (status: ReviewDecision) => {
    if (!selectedBen || reviewSubmitting.current) return;
    if (!reviewReason.trim()) {
      setReviewError("Enter a reason for this decision.");
      return;
    }
    reviewSubmitting.current = true;
    setReviewSaving(true);
    setReviewError(null);
    setReviewSaved(false);
    try {
      const updated = await verifyBeneficiary(selectedBen.beneficiary_id, status, reviewReason.trim(), reviewer);
      setSelectedBen(updated);
      setReviewReason("");
      setReviewSaved(true);
      setHistoryVersion((value) => value + 1);
      await loadBeneficiaries();
    } catch (err) {
      setReviewError(err instanceof Error ? err.message : String(err));
    } finally {
      reviewSubmitting.current = false;
      setReviewSaving(false);
    }
  };

  const handleResolveDuplicate = async () => {
    if (!selectedBen || !canonicalId || !reviewReason.trim() || reviewSubmitting.current) return;
    reviewSubmitting.current = true;
    setReviewSaving(true);
    setReviewError(null);
    setReviewSaved(false);
    try {
      const updated = await resolveBeneficiaryDuplicate(selectedBen.beneficiary_id, canonicalId, reviewReason.trim(), reviewer);
      setSelectedBen(updated);
      setReviewReason("");
      setReviewSaved(true);
      setHistoryVersion((value) => value + 1);
      await loadBeneficiaries();
    } catch (err) {
      setReviewError(err instanceof Error ? err.message : String(err));
    } finally {
      reviewSubmitting.current = false;
      setReviewSaving(false);
    }
  };

  const handleAnalyzeSampleCsv = async () => {
    setIsAnalyzingCsv(true);
    try {
      const res = await uploadBeneficiaryCsv();
      setCsvResult(res);
    } catch (err) {
      alert("CSV analysis error: " + String(err));
    } finally {
      setIsAnalyzingCsv(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (evt) => {
      const text = evt.target?.result as string;
      setIsAnalyzingCsv(true);
      try {
        const res = await uploadBeneficiaryCsv(text);
        setCsvResult(res);
      } catch (err) {
        alert("CSV upload error: " + String(err));
      } finally {
        setIsAnalyzingCsv(false);
      }
    };
    reader.readAsText(file);
  };

  const canonicalCandidates = beneficiaries.filter((b) => b.record_status === "ACTIVE" && b.beneficiary_id !== selectedBen?.beneficiary_id && b.batch_id === selectedBen?.batch_id);
  const filteredList = beneficiaries.filter((b) => !filterFlagged || b.verification_status === "FLAGGED_FOR_REVIEW" || b.duplicate_flag || b.anomaly_flag).filter((b) =>
    b.household_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    b.beneficiary_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (b.dafac_id && b.dafac_id.toLowerCase().includes(searchTerm.toLowerCase())) ||
    b.barangay_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Beneficiary Registry &amp; AI Verification</h1>
            <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-blue-600" /> AI Entity Resolution
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Deterministic fuzzy matching flags probable duplicates for human review without automated denial.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {role === "DSWD" && <button
            onClick={() => {
              setShowCsvModal(true);
              if (!csvResult) handleAnalyzeSampleCsv();
            }}
            className="flex items-center gap-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-bold text-xs px-3.5 py-2 rounded-xl shadow-xs transition cursor-pointer"
          >
            <FileSpreadsheet className="w-4 h-4 text-indigo-600" />
            Analyze a CSV
          </button>}

          {canRegister && <button
            onClick={() => { setRegisterError(null); setShowAddModal(true); }}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs px-4 py-2 rounded-xl shadow transition cursor-pointer"
          >
            <UserPlus className="w-4 h-4" />
            Register a household
          </button>}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-center gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search household name, ID, barangay..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <label className="flex items-center gap-2 text-xs text-slate-700">
            <input type="checkbox" checked={showHistorical} onChange={(e) => setShowHistorical(e.target.checked)} />
            Include historical duplicates
          </label>
          <button
            onClick={() => setFilterFlagged(!filterFlagged)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition w-full sm:w-auto justify-center ${
              filterFlagged
                ? "bg-amber-500 text-white border-amber-600 shadow-sm"
                : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            {filterFlagged ? "Showing Flagged Records Only" : "Filter: Flagged Records"}
          </button>
        </div>
      </div>

      {/* Beneficiaries Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 text-xs uppercase font-semibold border-b border-slate-100">
              <tr>
                <th className="px-5 py-3">Beneficiary ID</th>
                <th className="px-5 py-3">Household Head</th>
                <th className="px-5 py-3">Barangay</th>
                <th className="px-5 py-3">AI Verification Status</th>
                <th className="px-5 py-3">AI Detection Signal</th>
                <th className="px-5 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filteredList.map((ben) => {
                const isFlagged = ben.verification_status === "FLAGGED_FOR_REVIEW" || ben.duplicate_flag || ben.anomaly_flag;
                return (
                  <tr
                    key={ben.id}
                    onClick={() => setSelectedBen(ben)}
                    className={`cursor-pointer transition-colors ${
                      isFlagged ? "bg-amber-50/40 hover:bg-amber-50/80" : "hover:bg-slate-50/60"
                    }`}
                  >
                    <td className="px-5 py-3.5 text-xs">
                      <span className="font-mono font-bold text-slate-900 block">{ben.beneficiary_id}</span>
                      <span className="font-mono text-[10px] text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 inline-block mt-0.5 font-bold">
                        {ben.dafac_id || `DFC-2026-${ben.beneficiary_id.slice(-4)}`}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-semibold text-slate-900">
                      {ben.household_name}
                    </td>
                    <td className="px-5 py-3.5 text-xs text-slate-600">
                      {ben.barangay_name}
                    </td>
                    <td className="px-5 py-3.5">
                      {ben.record_status === "DUPLICATE" ? (
                        <span className="inline-flex text-[11px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">RETAINED DUPLICATE</span>
                      ) : ben.verification_status === "VERIFIED" ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          APPROVED
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300">
                          <AlertTriangle className="w-3 h-3 text-amber-600" />
                          {ben.verification_status === "REJECTED" ? "REJECTED" : ben.verification_status === "FLAGGED_FOR_REVIEW" ? "PENDING REVIEW" : ben.verification_status}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      {ben.duplicate_flag ? (
                        <span className="text-xs text-amber-700 font-medium">
                          ⚠ {Math.round(ben.duplicate_confidence * 100)}% match with {ben.duplicate_matched_id}
                        </span>
                      ) : ben.anomaly_flag ? (
                        <span className="text-xs text-rose-700 font-medium">
                          ⚠ Non-standard aid amount request
                        </span>
                      ) : (
                        <span className="text-xs text-slate-500">{ben.record_status === "DUPLICATE" ? "Linked to " + ben.canonical_beneficiary_id : "No pending flags"}</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedBen(ben);
                          }}
                          className="text-xs text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center gap-1 cursor-pointer"
                        >
                          Inspect <ArrowRight className="w-3 h-3" />
                        </button>

                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* AI Duplicate Inspection Drawer / Modal */}
      {loadError && <div role="alert" className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-sm">{loadError} <button onClick={() => void loadBeneficiaries()} className="underline min-h-11">Retry loading households</button></div>}
      {selectedBen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95">
            <button
              aria-label="Close household review"
              disabled={reviewSaving}
              onClick={() => setSelectedBen(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base text-slate-900">Review household</h3>
                <p className="text-xs text-slate-400">Record ID: {selectedBen.beneficiary_id}</p>
              </div>
            </div>

            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3 p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                <div>
                  <span className="text-slate-500 uppercase font-semibold">Household Name</span>
                  <p className="font-bold text-sm text-slate-900 mt-0.5">{selectedBen.household_name}</p>
                </div>
                <div>
                  <span className="text-slate-500 uppercase font-semibold">Barangay Locality</span>
                  <p className="font-bold text-sm text-slate-900 mt-0.5">{selectedBen.barangay_name}</p>
                </div>
                <div>
                  <span className="text-slate-500 uppercase font-semibold">Verification Status</span>
                  <p className="font-bold text-slate-900 mt-0.5">{selectedBen.verification_status}</p>
                </div>
                <div>
                  <span className="text-slate-500 uppercase font-semibold">Review State</span>
                  <p className="font-bold text-slate-900 mt-0.5">{selectedBen.review_status}</p>
                </div>
              </div>

              {/* Duplicate Flag Callout */}
              {Boolean(selectedBen.duplicate_matched_id) && (
                <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-amber-900 flex items-center gap-1.5">
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                      {selectedBen.duplicate_flag ? "Possible duplicate" : "Original match evidence"}
                    </span>
                    <span className="bg-amber-200 text-amber-900 font-mono font-bold px-2 py-0.5 rounded text-[11px]">
                      {Math.round(selectedBen.duplicate_confidence * 100)}% Similarity
                    </span>
                  </div>

                  <p className="text-amber-800">
                    AI Entity Resolution flagged a probable match with existing record:{" "}
                    <strong className="font-mono">{selectedBen.duplicate_matched_id}</strong>
                  </p>

                  <div className="text-[11px] text-amber-700 bg-amber-100/60 p-2.5 rounded-lg border border-amber-200">
                    <p className="font-semibold">Reasoning:</p>
                    <ul className="list-disc list-inside mt-0.5 space-y-0.5">
                      <li>Normalized phonetic &amp; token-set similarity threshold exceeded</li>
                      <li>Identical Barangay locality ({selectedBen.barangay_name})</li>
                    </ul>
                  </div>
                </div>
              )}

              {/* Anomaly Callout */}
              {Boolean(selectedBen.anomaly_flag) && (
                <div className="p-4 bg-rose-50 border border-rose-300 rounded-xl space-y-1">
                  <span className="font-bold text-rose-900 flex items-center gap-1.5">
                    <AlertCircle className="w-4 h-4 text-rose-600" />
                    STATISTICAL ANOMALY FLAGGED
                  </span>
                  <p className="text-rose-800">
                    {selectedBen.review_notes || "Irregular distribution amount requested."}
                  </p>
                </div>
              )}

              {/* Ethical AI Notice */}
              <div className="bg-slate-100 p-3 rounded-lg text-slate-500 text-[11px]">
                <strong>Governance Rule:</strong> The AI acts purely as a decision-support tool. It flags suspicious records for human review, and never automatically accuses, rejects, or denies aid.
              </div>

              {/* Human decision form */}
              {selectedBen.record_status === "DUPLICATE" ? (
                <p className="p-3 bg-slate-100 rounded-lg text-slate-700">
                  Retained duplicate of {selectedBen.canonical_beneficiary_id}. Payouts, receipts, and review history are preserved. This record cannot receive a new payout.
                </p>
              ) : role !== "DSWD" ? (
                <p className="p-3 bg-slate-100 rounded-lg text-slate-600">
                  Eligibility decisions belong to the DSWD Officer. Your account can inspect the records available to its role.
                </p>
              ) : (
                <div className="pt-3 border-t border-slate-200 space-y-3">
                  <div>
                    <p className="font-semibold">Reviewer: {account?.display_name}</p>
                    <p className="text-slate-500 mt-1">The signed-in account is recorded with this decision.</p>
                  </div>
                  <div>
                    <label htmlFor="review-reason" className="block font-semibold text-slate-700 mb-1">Reason for decision</label>
                    <textarea id="review-reason" value={reviewReason} disabled={reviewSaving} maxLength={2000} rows={3} onChange={(e) => setReviewReason(e.target.value)} placeholder="Explain why this household should be approved, rejected, or kept for review." className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
                  </div>
                  {reviewError && <p role="alert" className="text-rose-700">{reviewError}</p>}
                  {reviewSaved && <p role="status" className="text-emerald-700">Review saved.</p>}
                  <div className="flex flex-wrap gap-2">
                    <button disabled={reviewSaving || !reviewReason.trim()} onClick={() => handleManualVerify("VERIFIED")} className="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg disabled:opacity-50">Approve household</button>
                    <button disabled={reviewSaving || !reviewReason.trim()} onClick={() => handleManualVerify("REJECTED")} className="px-3 py-2 bg-rose-50 text-rose-700 border border-rose-200 font-semibold rounded-lg disabled:opacity-50">Reject household</button>
                    <button disabled={reviewSaving || !reviewReason.trim()} onClick={() => handleManualVerify("FLAGGED_FOR_REVIEW")} className="px-3 py-2 bg-slate-100 text-slate-700 font-semibold rounded-lg disabled:opacity-50">Keep for review</button>
                  </div>
                  <details className="border-t border-slate-200 pt-3">
                    <summary className="font-semibold text-slate-700 cursor-pointer">Resolve as a duplicate</summary>
                    <div className="mt-3 space-y-2">
                      <label htmlFor="canonical-household" className="block font-semibold text-slate-700">Keep household record</label>
                      <select id="canonical-household" value={canonicalCandidates.some((b) => b.beneficiary_id === canonicalId) ? canonicalId : ""} disabled={reviewSaving} onChange={(e) => setCanonicalId(e.target.value)} className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                        <option value="">Select the surviving household</option>
                        {canonicalCandidates.map((b) => <option key={b.beneficiary_id} value={b.beneficiary_id}>{b.beneficiary_id}: {b.household_name}</option>)}
                      </select>
                      <p className="text-slate-600">This record will leave the active list. Its payouts, receipts, and review history remain available. Use the reviewer and reason above.</p>
                      <button disabled={reviewSaving || !reviewReason.trim() || !canonicalCandidates.some((b) => b.beneficiary_id === canonicalId)} onClick={handleResolveDuplicate} className="px-3 py-2 bg-slate-800 text-white font-semibold rounded-lg disabled:opacity-50">Mark duplicate and retain history</button>
                    </div>
                  </details>
                  {reviewSaving && <p role="status" className="text-slate-600">Saving review...</p>}
                </div>
              )}

              {canInspectHistory && <details className="border-t border-slate-200 pt-3">
                <summary className="font-semibold text-slate-700 cursor-pointer">Review history ({reviews.length})</summary>
                {historyLoading && <p className="mt-2 text-slate-500">Loading reviews...</p>}
                {historyError && <div role="alert" className="mt-2 text-rose-700">{historyError} <button onClick={() => setHistoryVersion((value) => value + 1)} className="underline">Retry</button></div>}
                {!historyLoading && !historyError && reviews.length === 0 && <p className="mt-2 text-slate-500">No recorded human reviews.</p>}
                <ol className="mt-2 space-y-3">
                  {reviews.map((review) => (
                    <li key={review.review_id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1">
                      <p className="font-semibold text-slate-900">{review.decision === "DUPLICATE" ? "Retained duplicate" : review.decision === "VERIFIED" ? "Approved" : review.decision === "REJECTED" ? "Rejected" : "Pending review"}</p>
                      <p className="text-slate-500">{review.reviewed_by} · {new Date(review.reviewed_at).toLocaleString()}</p>
                      <p className="text-slate-700 whitespace-pre-wrap break-words">{review.reason}</p>
                      {review.linked_beneficiary_id && <p className="text-slate-700">Surviving household: {review.linked_beneficiary_id}</p>}
                      {review.matched_beneficiary_id && <p className="text-slate-500">Match reviewed: {review.matched_beneficiary_id} ({Math.round(review.duplicate_confidence * 100)}%)</p>}
                    </li>
                  ))}
                </ol>
              </details>}
            </div>
          </div>
        </div>
      )}

      {/* Test Register Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 relative animate-in fade-in">
            <button
              disabled={isSubmitting}
              aria-label="Close registration"
              onClick={() => setShowAddModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="font-bold text-base text-slate-900 mb-1">Register a household</h3>
            <p className="text-xs text-slate-500 mb-4">
              Use a fictional household. Registration checks for possible duplicate records; DSWD handles eligibility decisions.
            </p>

            <form onSubmit={handleRegister} className="space-y-4 text-xs">
              {registerError && <p role="alert" className="text-rose-700">{registerError}</p>}
              <div>
                <label htmlFor="new-household-name" className="block font-semibold text-slate-700 mb-1">Household Head Full Name</label>
                <input
                  id="new-household-name"
                  type="text"
                  disabled={isSubmitting}
                  placeholder="e.g. Juan D. Cruz or Juan Dela Cruz"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label htmlFor="new-household-barangay" className="block font-semibold text-slate-700 mb-1">Barangay Locality</label>
                <select
                  id="new-household-barangay"
                  disabled={role === "BARANGAY" || isSubmitting} value={newBrgy}
                  onChange={(e) => setNewBrgy(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="BRGY-001">Barangay San Isidro</option>
                  <option value="BRGY-002">Barangay Santa Elena</option>
                  <option value="BRGY-003">Barangay San Roque</option>
                  <option value="BRGY-004">Barangay Maligaya</option>
                </select>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-2 text-slate-600 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg shadow disabled:opacity-50"
                >
                  {isSubmitting ? "Registering..." : "Register household"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Batch CSV Upload & AI Analyzer Modal */}
      {showCsvModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-2xl border border-slate-200 relative animate-in fade-in max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setShowCsvModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2.5 mb-2">
              <div className="w-9 h-9 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-black text-slate-900">
                  Batch Disaster Masterlist AI Entity Analyzer
                </h2>
                <p className="text-xs text-slate-500">
                  Bulk fuzzy matching for evacuation centers across DAFAC IDs, clerical typos, and cross-barangay claims.
                </p>
              </div>
            </div>

            {/* Quick Actions Bar */}
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 my-4 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <button
                  onClick={handleAnalyzeSampleCsv}
                  disabled={isAnalyzingCsv}
                  className="px-3 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-xs shadow transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  {isAnalyzingCsv ? "Processing AI..." : "Load Seeded CSV (10 Households)"}
                </button>

                <label className="px-3 py-2 bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 font-semibold rounded-lg text-xs transition flex items-center gap-1.5 cursor-pointer">
                  <UploadCloud className="w-3.5 h-3.5 text-slate-500" />
                  Upload Custom .CSV
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </div>

              {csvResult && (
                <div className="flex items-center gap-2 text-xs font-semibold">
                  <span className="text-slate-600">Processed: {csvResult.total_records_processed}</span>
                  <span className="bg-amber-100 text-amber-800 border border-amber-300 px-2 py-0.5 rounded-full font-bold">
                    {csvResult.flagged_duplicates_count} Flagged For Review
                  </span>
                </div>
              )}
            </div>

            {/* Analysis Results Table */}
            {csvResult && (
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Detected Duplicates &amp; Cross-List Anomalies ({csvResult.flagged_duplicates_count})
                </h3>

                <div className="space-y-3">
                  {csvResult.flagged_records.map((item, idx) => (
                    <div key={idx} className="p-3.5 bg-amber-50/50 border border-amber-200 rounded-xl space-y-2 text-xs">
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-amber-200/60 pb-2">
                        <span className="bg-amber-100 text-amber-900 px-2 py-0.5 rounded text-[11px] font-bold border border-amber-300">
                          {item.anomaly_type}
                        </span>
                        <div className="flex items-center gap-2 font-mono text-[11px]">
                          <span className="text-slate-500">Overall Match:</span>
                          <strong className="text-amber-800 font-bold bg-white px-2 py-0.5 rounded border border-amber-200">
                            {item.match_metrics.overall_score}%
                          </strong>
                          <span className="text-slate-400">|</span>
                          <span className="text-slate-600">Name: {item.match_metrics.name_score}%</span>
                          <span className="text-slate-400">|</span>
                          <span className="text-slate-600">Address: {item.match_metrics.address_score}%</span>
                          <span className="text-slate-400">|</span>
                          <span className={item.match_metrics.dafac_match ? "text-emerald-700 font-bold" : "text-slate-500"}>
                            DAFAC: {item.match_metrics.dafac_match ? "MATCH ✓" : "DIFFERENT"}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                        <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                          <span className="text-[10px] text-slate-400 uppercase font-bold block">Record A ({item.record_a.id})</span>
                          <p className="font-bold text-slate-900 mt-0.5">{item.record_a.name}</p>
                          <p className="text-[11px] text-slate-500">{item.record_a.address}</p>
                          <p className="font-mono text-[10px] text-blue-700 mt-1">DAFAC: {item.record_a.dafac_id}</p>
                        </div>

                        <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                          <span className="text-[10px] text-slate-400 uppercase font-bold block">Record B ({item.record_b.id})</span>
                          <p className="font-bold text-slate-900 mt-0.5">{item.record_b.name}</p>
                          <p className="text-[11px] text-slate-500">{item.record_b.address}</p>
                          <p className="font-mono text-[10px] text-blue-700 mt-1">DAFAC: {item.record_b.dafac_id}</p>
                        </div>
                      </div>

                      <p className="text-[10px] text-amber-800 font-semibold italic">
                        ℹ Policy: Flagged for barangay officer verification before aid is released. No citizen is denied automatically.
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-5 pt-3 border-t border-slate-200 flex justify-end">
              <button
                onClick={() => setShowCsvModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-lg text-xs cursor-pointer shadow transition"
              >
                Done Inspecting
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
