"use client";

import React, { useState, useEffect } from "react";
import {
  Users, AlertTriangle, CheckCircle2, Search, UserPlus, Filter,
  Sparkles, ArrowRight, ShieldCheck, X, RefreshCw, AlertCircle,
  FileSpreadsheet, UploadCloud, Trash2, Lock
} from "lucide-react";
import { fetchBeneficiaries, registerBeneficiary, verifyBeneficiary, Beneficiary, uploadBeneficiaryCsv, CsvBatchResult, deleteBeneficiary } from "@/lib/api";
import { useRole } from "@/lib/roleContext";

export default function BeneficiariesPage() {
  const { role, setRole } = useRole();
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterFlagged, setFilterFlagged] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedBen, setSelectedBen] = useState<Beneficiary | null>(null);
  const [deleteSuccessMsg, setDeleteSuccessMsg] = useState<string | null>(null);

  // New beneficiary form modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newName, setNewName] = useState("");
  const [newBrgy, setNewBrgy] = useState("BRGY-001");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Batch CSV Upload & AI Verification State
  const [showCsvModal, setShowCsvModal] = useState(false);
  const [csvResult, setCsvResult] = useState<CsvBatchResult | null>(null);
  const [isAnalyzingCsv, setIsAnalyzingCsv] = useState(false);

  const loadBeneficiaries = async () => {
    try {
      setLoading(true);
      const data = await fetchBeneficiaries({ flagged_only: filterFlagged });
      setBeneficiaries(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBeneficiaries();
  }, [filterFlagged]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    setIsSubmitting(true);
    try {
      const brgyMap: Record<string, string> = {
        "BRGY-001": "San Isidro",
        "BRGY-002": "Santa Elena",
        "BRGY-003": "San Roque",
        "BRGY-004": "Maligaya"
      };
      const created = await registerBeneficiary({
        beneficiary_id: `BEN-${Date.now().toString().slice(-4)}`,
        household_name: newName.trim(),
        barangay_id: newBrgy,
        barangay_name: brgyMap[newBrgy] || "San Isidro",
        batch_id: "RELIEF-2026-001"
      });
      setShowAddModal(false);
      setNewName("");
      await loadBeneficiaries();
      setSelectedBen(created); // Open review modal for newly registered
    } catch (err) {
      alert("Error: " + String(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleManualVerify = async (status: string) => {
    if (!selectedBen) return;
    try {
      const updated = await verifyBeneficiary(selectedBen.beneficiary_id, status, `Manual action by Auditor: ${status}`);
      setSelectedBen(updated);
      await loadBeneficiaries();
    } catch (err) {
      alert("Verification update failed: " + String(err));
    }
  };

  const handleDeleteBeneficiary = async (benId: string, name: string) => {
    if (!confirm(`Sigurado ka bang nais mong tanggalin ang dobleng talaan ni "${name}" (${benId}) mula sa opisyal na listahan ng mga evacuee?`)) {
      return;
    }
    try {
      await deleteBeneficiary(benId);
      setDeleteSuccessMsg(`✓ Matagumpay na natanggal ang dobleng talaan: ${name} (${benId})!`);
      setTimeout(() => setDeleteSuccessMsg(null), 4000);
      if (selectedBen?.beneficiary_id === benId) {
        setSelectedBen(null);
      }
      await loadBeneficiaries();
    } catch (err) {
      alert("Hindi matanggal ang benepisyaryo: " + String(err));
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

  const filteredList = beneficiaries.filter((b) =>
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
          <button
            onClick={() => {
              setShowCsvModal(true);
              if (!csvResult) handleAnalyzeSampleCsv();
            }}
            className="flex items-center gap-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-bold text-xs px-3.5 py-2 rounded-xl shadow-xs transition cursor-pointer"
          >
            <FileSpreadsheet className="w-4 h-4 text-indigo-600" />
            Bulk CSV AI Analyzer (10 Seeded Evacuees)
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs px-4 py-2 rounded-xl shadow transition cursor-pointer"
          >
            <UserPlus className="w-4 h-4" />
            Test Register Beneficiary
          </button>
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

        <div className="flex items-center gap-2 w-full sm:w-auto">
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

      {deleteSuccessMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-300 rounded-xl text-emerald-900 text-xs font-semibold flex items-center justify-between shadow-xs animate-in fade-in">
          <span className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            {deleteSuccessMsg}
          </span>
          <button onClick={() => setDeleteSuccessMsg(null)} className="text-emerald-700 hover:text-emerald-900 font-bold cursor-pointer">
            ✕
          </button>
        </div>
      )}

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
                      {ben.verification_status === "VERIFIED" ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          VERIFIED
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300">
                          <AlertTriangle className="w-3 h-3 text-amber-600" />
                          FLAGGED FOR REVIEW
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
                        <span className="text-xs text-slate-400">Zero duplicates detected</span>
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
                        {role !== "Public Citizen" && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteBeneficiary(ben.beneficiary_id, ben.household_name);
                            }}
                            title="Tanggalin ang Dobleng Talaan (Delete Duplicate)"
                            className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition cursor-pointer"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
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
      {selectedBen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95">
            <button
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
                <h3 className="font-bold text-base text-slate-900">AI Beneficiary Verification Review</h3>
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
              {Boolean(selectedBen.duplicate_flag) && (
                <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-amber-900 flex items-center gap-1.5">
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                      POSSIBLE DUPLICATE DETECTED
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

              {/* Role-Based Decision Actions */}
              {role === "Public Citizen" ? (
                <div className="pt-2 p-3 bg-slate-100 rounded-xl border border-slate-200 text-slate-600 text-xs flex flex-col sm:flex-row items-center justify-between gap-2.5">
                  <div className="flex items-center gap-2">
                    <Lock className="w-4 h-4 text-slate-500 shrink-0" />
                    <span>
                      🔒 <strong>Public Citizen View (Read-Only):</strong> Verification &amp; deleting duplicate records is restricted to Barangay Officers and COA Auditors.
                    </span>
                  </div>
                  <button
                    onClick={() => setRole("Barangay Officer")}
                    className="text-xs font-bold text-blue-700 hover:text-blue-900 bg-white hover:bg-blue-50 px-3 py-1.5 rounded-lg border border-slate-300 shadow-2xs shrink-0 transition cursor-pointer"
                  >
                    Switch to Officer Mode →
                  </button>
                </div>
              ) : (
                <div className="pt-3 border-t border-slate-200 flex flex-wrap items-center justify-between gap-2">
                  <button
                    onClick={() => handleDeleteBeneficiary(selectedBen.beneficiary_id, selectedBen.household_name)}
                    className="px-3 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-bold rounded-xl transition text-xs flex items-center gap-1.5 cursor-pointer"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-rose-600" />
                    Tanggalin ang Doble (Delete Duplicate)
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleManualVerify("REJECTED")}
                      className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl transition text-xs cursor-pointer"
                    >
                      Flag as Invalid
                    </button>
                    <button
                      onClick={() => handleManualVerify("VERIFIED")}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl transition text-xs shadow cursor-pointer"
                    >
                      Confirm &amp; Verify Beneficiary
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Test Register Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 relative animate-in fade-in">
            <button
              onClick={() => setShowAddModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="font-bold text-base text-slate-900 mb-1">Register Beneficiary (Live Test)</h3>
            <p className="text-xs text-slate-500 mb-4">
              Enter a name to test the live AI Entity Resolution duplicate engine.
            </p>

            <form onSubmit={handleRegister} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Household Head Full Name</label>
                <input
                  type="text"
                  placeholder="e.g. Juan D. Cruz or Juan Dela Cruz"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Tip: Type &quot;Juan D. Cruz&quot; to trigger the seeded 94% duplicate match!
                </p>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Barangay Locality</label>
                <select
                  value={newBrgy}
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
                  {isSubmitting ? "Running AI..." : "Register & Run AI Check"}
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
