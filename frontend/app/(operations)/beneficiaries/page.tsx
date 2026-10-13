"use client";

import React, { useState, useEffect, useRef } from "react";
import { formatRecordedDate } from "@/lib/recordedDate";
import Link from "next/link";
import RegistryDialog from "@/components/RegistryDialog";
import CsvOnboarding from "@/components/CsvOnboarding";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import {
  Search,
  UserPlus,
  ArrowRight,
  RefreshCw,
  FileSpreadsheet,
} from "lucide-react";
import {
  fetchBeneficiaries,
  registerBeneficiary,
  verifyBeneficiary,
  fetchBeneficiaryReviews,
  BeneficiaryReview,
  ReviewDecision,
  Beneficiary,
  uploadBeneficiaryCsv,
  CsvBatchResult,
  resolveBeneficiaryDuplicate,
} from "@/lib/api";
import { useRole } from "@/lib/roleContext";
import { useSearchParams } from "next/navigation";

const barangays: Record<string, string> = {
  "BRGY-001": "San Isidro",
  "BRGY-002": "Santa Elena",
  "BRGY-003": "San Roque",
  "BRGY-004": "Maligaya",
};
function householdStatus(ben: Beneficiary) {
  if (ben.record_status === "DUPLICATE") return "Retained duplicate";
  if (
    ben.verification_status === "REJECTED" ||
    ben.review_status === "REJECTED"
  )
    return "Rejected";
  if (
    ben.verification_status === "VERIFIED" &&
    ben.review_status === "APPROVED"
  )
    return "Approved";
  return "Pending review";
}
function Status({ ben }: { ben: Beneficiary }) {
  const status = householdStatus(ben);
  return (
    <span
      className={
        "registry-badge " +
        (status === "Approved"
          ? "registry-approved"
          : status === "Pending review"
            ? "registry-pending"
            : "registry-neutral")
      }
    >
      {status}
    </span>
  );
}

export default function BeneficiariesPage() {
  const params = useSearchParams();
  const requestedHousehold = params.getAll("beneficiary_id").length > 1 ? "" : params.get("beneficiary_id");
  const requestedSearch=params.get("search") || "";
  return <RegistryBody key={(requestedHousehold ?? "direct-registry")+requestedSearch} requestedHousehold={requestedHousehold} requestedSearch={requestedSearch} />;
}

function RegistryBody({ requestedHousehold,requestedSearch }: { requestedHousehold: string | null;requestedSearch:string }) {
  const { role, account } = useRole();
  const online = useBrowserOnline();
  const [registeredId, setRegisteredId] = useState<string | null>(null);
  const [csvError, setCsvError] = useState<string | null>(null);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const csvSubmitting = useRef(false);
  const loadVersion = useRef(0);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [showHistorical, setShowHistorical] = useState(false);
  const [canonicalId, setCanonicalId] = useState("");
  const [filterFlagged, setFilterFlagged] = useState(false);
  const [searchTerm, setSearchTerm] = useState(requestedSearch);
  const [selectedBen, setSelectedBen] = useState<Beneficiary | null>(null);
  const caseHeading = useRef<HTMLHeadingElement>(null);
  const lastSelected = useRef<string | null>(null);
  useEffect(() => {
    if (selectedBen) {
      lastSelected.current = selectedBen.beneficiary_id;
      caseHeading.current?.focus();
    } else if (lastSelected.current) {
      const row = document.querySelector<HTMLElement>(`[data-household-id="${CSS.escape(lastSelected.current)}"]`);
      (row || document.getElementById("household-search"))?.focus();
      lastSelected.current = null;
    }
  }, [selectedBen?.beneficiary_id]);
  const [reviewReason, setReviewReason] = useState("");
  const reviewer = account?.id;
  const canRegister = requestedHousehold === null && (role === "DSWD" || role === "BARANGAY");
  const canInspectHistory =
    role === "DSWD" || role === "AUDITOR" || role === "BENEFICIARY";
  const [reviews, setReviews] = useState<BeneficiaryReview[]>([]);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [reviewSaving, setReviewSaving] = useState(false);
  const reviewSubmitting = useRef(false);
  const [historyVersion, setHistoryVersion] = useState(0);
  const [reviewSaved, setReviewSaved] = useState(false);

  const [showAddModal, setShowAddModal] = useState(false);
  const [newName, setNewName] = useState("");
  const [newBrgy, setNewBrgy] = useState(account?.barangay_id || "BRGY-001");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const registerSubmitting = useRef(false);
  const [registerError, setRegisterError] = useState<string | null>(null);

  const [showCsvImport, setShowCsvImport] = useState(false);
  const [showCsvModal, setShowCsvModal] = useState(false);
  const [csvResult, setCsvResult] = useState<CsvBatchResult | null>(null);
  const [isAnalyzingCsv, setIsAnalyzingCsv] = useState(false);

  const loadBeneficiaries = async () => {
    const version = ++loadVersion.current;
    setLoading(true);
    setLoadError(null);
    try {
      const data = await fetchBeneficiaries({
        include_historical: showHistorical || requestedHousehold !== null,
      });
      if (version === loadVersion.current) setBeneficiaries(data);
    } catch (err) {
      if (version === loadVersion.current)
        setLoadError(
          err instanceof Error
            ? err.message
            : "Household records could not be loaded.",
        );
    } finally {
      if (version === loadVersion.current) setLoading(false);
    }
  };
  useEffect(() => {
    void loadBeneficiaries();
    return () => {
      loadVersion.current++;
    };
  }, [showHistorical, account?.id, requestedHousehold]);
  useEffect(() => {
    if (requestedHousehold !== null && !loading && !loadError) setSelectedBen(beneficiaries.find(b=>b.beneficiary_id===requestedHousehold) || null);
  }, [requestedHousehold, loading, loadError, beneficiaries]);

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
      .then((data) => {
        if (!cancelled) setReviews(data);
      })
      .catch((err) => {
        if (!cancelled)
          setHistoryError(err instanceof Error ? err.message : String(err));
      })
      .finally(() => {
        if (!cancelled) setHistoryLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedBen?.beneficiary_id, historyVersion, canInspectHistory]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || registerSubmitting.current || !navigator.onLine)
      return;
    registerSubmitting.current = true;
    setRegisterError(null);
    setIsSubmitting(true);
    try {
      const barangayId =
        role === "BARANGAY" ? account?.barangay_id || newBrgy : newBrgy;
      const created = await registerBeneficiary({
        beneficiary_id: "BEN-" + crypto.randomUUID(),
        household_name: newName.trim(),
        barangay_id: barangayId,
        barangay_name: barangays[barangayId],
        batch_id: "RELIEF-2026-001",
      });
      setShowAddModal(false);
      setNewName("");
      setRegisteredId(created.beneficiary_id);
      setSelectedBen(created);
      await loadBeneficiaries();
    } catch (err) {
      setRegisterError(
        err instanceof Error ? err.message : "Registration failed. Try again.",
      );
    } finally {
      registerSubmitting.current = false;
      setIsSubmitting(false);
    }
  };

  const handleManualVerify = async (status: ReviewDecision) => {
    if (!selectedBen || reviewSubmitting.current || !navigator.onLine) return;
    if (!reviewReason.trim()) {
      setReviewError("Enter a reason for this decision.");
      return;
    }
    reviewSubmitting.current = true;
    setReviewSaving(true);
    setReviewError(null);
    setReviewSaved(false);
    try {
      const updated = await verifyBeneficiary(
        selectedBen.beneficiary_id,
        status,
        reviewReason.trim(),
        reviewer,
      );
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
    if (
      !selectedBen ||
      !canonicalId ||
      !reviewReason.trim() ||
      reviewSubmitting.current ||
      !navigator.onLine
    )
      return;
    reviewSubmitting.current = true;
    setReviewSaving(true);
    setReviewError(null);
    setReviewSaved(false);
    try {
      const updated = await resolveBeneficiaryDuplicate(
        selectedBen.beneficiary_id,
        canonicalId,
        reviewReason.trim(),
        reviewer,
      );
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

  const analyzeCsv = async (file?: File) => {
    if (csvSubmitting.current || !navigator.onLine) return;
    csvSubmitting.current = true;
    setIsAnalyzingCsv(true);
    setCsvError(null);
    setCsvResult(null);
    try {
      setCsvResult(
        await uploadBeneficiaryCsv(file ? await file.text() : undefined),
      );
    } catch (err) {
      setCsvError(
        err instanceof Error ? err.message : "CSV analysis failed. Try again.",
      );
    } finally {
      csvSubmitting.current = false;
      setIsAnalyzingCsv(false);
    }
  };

  const canonicalCandidates = beneficiaries.filter(
    (b) =>
      b.record_status === "ACTIVE" &&
      b.beneficiary_id !== selectedBen?.beneficiary_id &&
      b.batch_id === selectedBen?.batch_id,
  );
  const query = searchTerm.trim().toLowerCase();
  const filteredList = beneficiaries.filter(
    (b) =>
      (!filterFlagged || householdStatus(b) === "Pending review") &&
      [b.household_name, b.beneficiary_id, b.dafac_id, b.barangay_name].some(
        (value) => value?.toLowerCase().includes(query),
      ),
  );
  const pendingCount = beneficiaries.filter(
    (b) => householdStatus(b) === "Pending review",
  ).length;
  const selectedStatus = selectedBen ? householdStatus(selectedBen) : "";
  const canInspectEvidence = role === "DSWD" || role === "AUDITOR";
  const reviewDisabled = reviewSaving || !online || !reviewReason.trim();
  if (requestedHousehold !== null && !loading && !loadError && !beneficiaries.some(b=>b.beneficiary_id===requestedHousehold)) return <section className="registry space-y-4"><h1>Household unavailable</h1><p>That exact household is missing or outside your scope. No other record was substituted.</p><Link className="registry-button" href="/beneficiaries">Open household registry</Link></section>;
  return (
    <div className="registry registry-page space-y-6">
      <header className="registry-header">
        <div>
          <p className="registry-eyebrow">
            {role === "BARANGAY"
              ? barangays[account?.barangay_id || ""] || "Assigned barangay"
              : "Household records"}
          </p>
          <h1 id="registry-heading" tabIndex={-1}>
            {role === "BENEFICIARY" ? "My household" : "Household registry"}
          </h1>
          <p className="registry-description">
            {role === "DSWD"
              ? "Review pending households and record eligibility decisions."
              : role === "BARANGAY"
                ? "Register households in your barangay and follow their review status."
                : role === "BENEFICIARY"
                  ? "Check your household status and recorded payouts."
                  : role === "DISBURSING"
                    ? "Check household status before recording a payout."
                    : "Inspect household decisions and retained evidence."}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">{role!=="BENEFICIARY"&&<Link className="registry-button" href="/lists">Validated lists</Link>}
        {canRegister && (
          <button
            onClick={() => {
              setRegisterError(null);
              setShowAddModal(true);
            }}
            className="registry-button registry-primary"
          >
            <UserPlus size={18} aria-hidden="true" />
            Register a household
          </button>
        )}</div>
      </header>
      {!online && (
        <p role="status" className="registry-notice">
          Browser is offline. Reconnect to register or save a review. Nothing is
          queued.
        </p>
      )}
      <div className={"registry-workspace "+(selectedBen?"has-selection":"")}><section aria-label="Household list" className="registry-panel">
        <div className="registry-list-tools">
          <div className="registry-search">
            <label htmlFor="household-search">Search households</label>
            <div className="relative">
              <Search size={18} aria-hidden="true" />
              <input
                id="household-search"
                type="search"
                placeholder="Name or reference"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          {role !== "BENEFICIARY" && (
            <div className="registry-filters" aria-label="Review status filter">
              <button
                aria-pressed={!filterFlagged}
                onClick={() => setFilterFlagged(false)}
                className={
                  "registry-button " +
                  (!filterFlagged ? "registry-filter-selected" : "")
                }
              >
                All households
              </button>
              <button
                aria-pressed={filterFlagged}
                onClick={() => setFilterFlagged(true)}
                className={
                  "registry-button " +
                  (filterFlagged ? "registry-filter-selected" : "")
                }
              >
                Needs review
                {!loading && !loadError ? " (" + pendingCount + ")" : ""}
              </button>
            </div>
          )}
          {role !== "BENEFICIARY" && <label className="registry-checkbox">
            <input type="checkbox" checked={showHistorical} onChange={event => setShowHistorical(event.target.checked)} />
            Include historical duplicates
          </label>}
          {role === "DSWD" && <div role="group" className="registry-import-tools" aria-label="Household CSV tools">
            <button className="registry-button registry-text-button" onClick={() => setShowCsvImport(true)}>
              <FileSpreadsheet size={16} aria-hidden="true" />Import a CSV
            </button>
            <button className="registry-button registry-text-button" onClick={() => { setCsvFile(null); setCsvError(null); setShowCsvModal(true); }}>
              Analyze a CSV
            </button>
          </div>}
        </div>
        <div className="registry-list-caption">
          <p role="status">
            {loading
              ? "Loading households..."
              : loadError
                ? "Household list unavailable"
                : filteredList.length +
                  (filteredList.length === 1 ? " household" : " households") +
                  (filterFlagged ? " awaiting review" : " shown")}
          </p>
          <button
            onClick={() => void loadBeneficiaries()}
            disabled={loading}
            className="registry-button"
          >
            <RefreshCw size={16} aria-hidden="true" />
            Refresh
          </button>
        </div>
        {loadError && (
          <div role="alert" className="registry-error mx-5 mb-5">
            {loadError} The list could not be refreshed.{" "}
            <button
              onClick={() => void loadBeneficiaries()}
              className="registry-button underline"
            >
              Retry loading households
            </button>
          </div>
        )}
        {!loading && !loadError && filteredList.length === 0 && (
          <div className="registry-empty">
            <h2>
              {query
                ? "No matching households"
                : filterFlagged
                  ? "No households awaiting review"
                  : "No households to show"}
            </h2>
            <p>
              {query
                ? "Try another name, household ID or barangay."
                : filterFlagged
                  ? "Choose All households to see other decisions."
                  : canRegister
                    ? "Register a fictional household to begin."
                    : "No records are available to your account."}
            </p>
            {(query || filterFlagged) && (
              <button
                className="registry-button"
                onClick={() => {
                  setSearchTerm("");
                  setFilterFlagged(false);
                }}
              >
                Clear filters
              </button>
            )}
          </div>
        )}
        {!loading && !loadError && filteredList.length > 0 && (
          <ul className="registry-household-list" aria-label="Household records" tabIndex={0}>
            {filteredList.map(ben=><li key={ben.beneficiary_id}><button data-household-id={ben.beneficiary_id} className="registry-household-row" aria-pressed={selectedBen?.beneficiary_id===ben.beneficiary_id} aria-label={(role==='DSWD'?'Review ':'Inspect ')+ben.household_name} onClick={()=>setSelectedBen(ben)}><span className="household-avatar" aria-hidden="true">{ben.household_name.split(' ').slice(0,2).map(w=>w[0]).join('')}</span><span><span className="registry-household-name">{ben.household_name}</span><span className="registry-row-meta">{ben.barangay_name} · <Status ben={ben}/></span>{ben.record_status!=='DUPLICATE'&&(ben.duplicate_flag||ben.anomaly_flag)&&<span className="registry-flag">{ben.duplicate_flag?'Possible duplicate':'Amount needs review'}</span>}</span></button></li>)}
          </ul>
        )}
      </section>
      {selectedBen ? (
        <section className="registry-case" aria-label="Selected household">
          <div className="registry-case-heading"><h2 ref={caseHeading} tabIndex={-1}>{role==='DSWD'&&selectedBen.record_status!=='DUPLICATE'?'Review household':'Household details'}</h2><button className="registry-button registry-text-button" disabled={reviewSaving} onClick={()=>setSelectedBen(null)}>Back to list</button></div>
          <div className="registry-dialog-content">
            {registeredId === selectedBen.beneficiary_id && (
              <p role="status" className="registry-success">
                Household registered.
              </p>
            )}
            {reviewSaved && (
              <p role="status" className="registry-success">
                Review saved.
              </p>
            )}
            <div className="registry-household-summary">
              <h3>{selectedBen.household_name}</h3>
              <p>{selectedBen.barangay_name}</p>
              <Status ben={selectedBen} />
            </div>
            <div className="registry-next-step">
              {selectedStatus === "Retained duplicate" ? (
                <p>
                  Retained duplicate of{" "}
                  <span className="break-all">
                    {selectedBen.canonical_beneficiary_id}
                  </span>
                  . Its payouts, receipts and decisions are preserved. This
                  record cannot receive a new payout.
                </p>
              ) : selectedStatus === "Approved" ? (
                <>
                  <p>
                    Eligibility approved. The desk checks funding and earlier payouts.
                  </p>
                </>
              ) : selectedStatus === "Rejected" ? (
                <p>
                  This household is not approved for payout.
                  {role === "DSWD"
                    ? " Record a new decision below if further evidence changes the review."
                    : " Eligibility decisions belong to the DSWD Officer."}
                </p>
              ) : (
                <p>
                  {role === "DSWD"
                    ? "Check the household and any flagged evidence, then record your decision."
                    : "Awaiting DSWD review. This household cannot receive a payout yet. Eligibility decisions belong to the DSWD Officer."}
                </p>
              )}
            </div>
            {role !== "BARANGAY" && (
              <Link
                href={`/distributions?${new URLSearchParams({ beneficiary_id: selectedBen.beneficiary_id }).toString()}`}
                className="registry-button registry-text-button"
              >
                {role === "DISBURSING" && selectedStatus === "Approved"
                  ? "Open payouts"
                  : "View payout records"}
                <ArrowRight size={16} aria-hidden="true" />
              </Link>
            )}
            {!online && (
              <p role="status" className="registry-notice">
                Reconnect to save a review. Your reason stays here.
              </p>
            )}
            {canInspectEvidence &&
              (selectedBen.duplicate_flag || selectedBen.anomaly_flag) && (
                <div className="registry-notice">
                  <strong>
                    {selectedBen.duplicate_flag
                      ? "Possible duplicate"
                      : "Amount needs review"}
                  </strong>
                  <p>
                    Check the evidence before deciding. A suggested match is not
                    proof of a duplicate.
                  </p>
                </div>
              )}
            {canInspectEvidence &&
              (selectedBen.duplicate_matched_id ||
                selectedBen.review_notes ||
                selectedBen.anomaly_flag) && (
                <details className="registry-detail">
                  <summary>Review evidence</summary>
                  <div className="space-y-3 mt-3">
                    {selectedBen.duplicate_matched_id && (
                      <p>
                        {selectedBen.duplicate_flag
                          ? "Suggested match"
                          : "Original match"}
                        :{" "}
                        <span className="break-all">
                          {selectedBen.duplicate_matched_id}
                        </span>
                        . Similarity:{" "}
                        {Math.round(selectedBen.duplicate_confidence * 100)}%.
                      </p>
                    )}
                    {selectedBen.review_notes && (
                      <p className="whitespace-pre-wrap break-words">
                        {selectedBen.review_notes}
                      </p>
                    )}
                  </div>
                </details>
              )}
            {role === "DSWD" && selectedBen.record_status !== "DUPLICATE" && (
              <section
                aria-label="Eligibility decision"
                className="registry-decision"
              >
                <h3>Record a decision</h3>
                <p className="registry-muted">
                  Saved under {account?.display_name}.
                </p>
                <label htmlFor="review-reason">Reason for decision</label>
                <textarea
                  id="review-reason"
                  value={reviewReason}
                  disabled={reviewSaving}
                  maxLength={2000}
                  rows={3}
                  onChange={(e) => setReviewReason(e.target.value)}
                  aria-describedby="review-reason-help"
                  placeholder="Explain the evidence for your decision."
                />
                <p id="review-reason-help" className="registry-muted">
                  A reason is required for every decision.
                </p>
                {reviewError && (
                  <p role="alert" className="registry-error">
                    {reviewError}
                  </p>
                )}
                {reviewSaving && <p role="status">Saving review...</p>}
                <div className="registry-decision-actions">
                  <button
                    disabled={reviewDisabled}
                    onClick={() => void handleManualVerify("VERIFIED")}
                    className="registry-button registry-primary"
                  >
                    Approve household
                  </button>
                  <button
                    disabled={reviewDisabled}
                    onClick={() =>
                      void handleManualVerify("FLAGGED_FOR_REVIEW")
                    }
                    className="registry-button"
                  >
                    Keep for review
                  </button>
                  <button
                    disabled={reviewDisabled}
                    onClick={() => void handleManualVerify("REJECTED")}
                    className="registry-button registry-reject"
                  >
                    Reject household
                  </button>
                </div>
                <details className="registry-detail">
                  <summary>Resolve as a duplicate</summary>
                  <div className="space-y-3 mt-3">
                    <label htmlFor="canonical-household">
                      Keep household record
                    </label>
                    <select
                      id="canonical-household"
                      value={
                        canonicalCandidates.some(
                          (b) => b.beneficiary_id === canonicalId,
                        )
                          ? canonicalId
                          : ""
                      }
                      disabled={reviewSaving}
                      onChange={(e) => setCanonicalId(e.target.value)}
                    >
                      <option value="">Select the surviving household</option>
                      {canonicalCandidates.map((b) => (
                        <option key={b.beneficiary_id} value={b.beneficiary_id}>
                          {b.household_name} ({b.beneficiary_id})
                        </option>
                      ))}
                    </select>
                    <p>
                      This record will leave the active list. Its payouts,
                      receipts and review history remain available. Use the
                      reason above.
                    </p>
                    <button
                      disabled={
                        reviewDisabled ||
                        !canonicalCandidates.some(
                          (b) => b.beneficiary_id === canonicalId,
                        )
                      }
                      onClick={handleResolveDuplicate}
                      className="registry-button"
                    >
                      Mark duplicate and retain history
                    </button>
                  </div>
                </details>
              </section>
            )}
            {canInspectHistory && (
              <details className="registry-detail">
                <summary>
                  Review history{" "}
                  {historyLoading ? "" : "(" + reviews.length + ")"}
                </summary>
                <div className="space-y-3 mt-3">
                  <p className="registry-muted">
                    Decisions are stored in the local database. This history is
                    not protected by the blockchain.
                  </p>
                  {historyLoading && <p role="status">Loading reviews...</p>}
                  {historyError && (
                    <div role="alert" className="registry-error">
                      {historyError}
                      <button
                        onClick={() => setHistoryVersion((value) => value + 1)}
                        className="registry-button"
                      >
                        Retry history
                      </button>
                    </div>
                  )}
                  {!historyLoading && !historyError && reviews.length === 0 && (
                    <p>No recorded human reviews.</p>
                  )}
                  <ol className="space-y-3">
                    {reviews.map((review) => (
                      <li
                        key={review.review_id}
                        className="registry-history-entry"
                      >
                        <p className="font-semibold">
                          {review.decision === "DUPLICATE"
                            ? "Retained duplicate"
                            : review.decision === "VERIFIED"
                              ? "Approved"
                              : review.decision === "REJECTED"
                                ? "Rejected"
                                : "Pending review"}
                        </p>
                        <p className="registry-muted">
                          {review.reviewed_by} ·{" "}
                          {formatRecordedDate(review.reviewed_at)}
                        </p>
                        <p className="whitespace-pre-wrap break-words">
                          {review.reason}
                        </p>
                        {review.linked_beneficiary_id && (
                          <p className="break-all">
                            Surviving household: {review.linked_beneficiary_id}
                          </p>
                        )}
                        {review.matched_beneficiary_id && (
                          <p className="break-all">
                            Match reviewed: {review.matched_beneficiary_id} (
                            {Math.round(review.duplicate_confidence * 100)}%)
                          </p>
                        )}
                      </li>
                    ))}
                  </ol>
                </div>
              </details>
            )}
            <details className="registry-detail">
              <summary>Record references</summary>
              <dl className="registry-references">
                <dt>Household ID</dt>
                <dd>{selectedBen.beneficiary_id}</dd>
                <dt>DAFAC reference</dt>
                <dd>{selectedBen.dafac_id || "Not recorded"}</dd>
                <dt>Batch</dt>
                <dd>{selectedBen.batch_id}</dd>
              </dl>
            </details>
            <button
              className="registry-button"
              disabled={reviewSaving}
              onClick={() => setSelectedBen(null)}
            >
              Back to households
            </button>
          </div>
        </section>
      ) : <section className="registry-case registry-case-empty" aria-label="Household details"><Search size={32} aria-hidden="true"/><h2>Choose a household</h2><p>Open a record to review its details, decisions and next step.</p></section>}
      </div>
{showAddModal && (
        <RegistryDialog
          title="Register a household"
          busy={isSubmitting}
          initialFocus="#new-household-name"
          onClose={() => setShowAddModal(false)}
        >
          <form onSubmit={handleRegister} className="registry-dialog-content">
            <p className="registry-muted">
              Use a fictional household for Typhoon Salinlahi (RELIEF-2026-001).
            </p>
            {role === "BARANGAY" && (
              <p>Registration sends this household for DSWD review.</p>
            )}
            {!online && (
              <p role="status" className="registry-notice">
                Reconnect to register. Your input stays here.
              </p>
            )}
            {registerError && (
              <p role="alert" className="registry-error">
                {registerError}
              </p>
            )}
            <div>
              <label htmlFor="new-household-name">
                Household Head Full Name
              </label>
              <input
                id="new-household-name"
                disabled={isSubmitting}
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                required
                maxLength={255}
                autoComplete="off"
              />
            </div>
            <div>
              <label htmlFor="new-household-barangay">Barangay Locality</label>
              <select
                id="new-household-barangay"
                disabled={role === "BARANGAY" || isSubmitting}
                value={newBrgy}
                onChange={(e) => setNewBrgy(e.target.value)}
              >
                {Object.entries(barangays).map(([id, name]) => (
                  <option key={id} value={id}>
                    Barangay {name}
                  </option>
                ))}
              </select>
            </div>
            <div className="registry-form-actions">
              <button
                type="button"
                disabled={isSubmitting}
                onClick={() => setShowAddModal(false)}
                className="registry-button"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !online || !newName.trim()}
                className="registry-button registry-primary"
              >
                {isSubmitting ? "Registering..." : "Register household"}
              </button>
            </div>
          </form>
        </RegistryDialog>
      )}
      {showCsvImport && <CsvOnboarding onClose={() => { setShowCsvImport(false); void loadBeneficiaries(); }} onReview={id => { setShowCsvImport(false); setSearchTerm(id); setFilterFlagged(true); void loadBeneficiaries(); }} />}
      {showCsvModal && (
        <RegistryDialog
          title="Analyze a CSV"
          busy={isAnalyzingCsv}
          wide
          onClose={() => setShowCsvModal(false)}
        >
          <div className="registry-dialog-content">
            <p>
              Find possible duplicate pairs in a fictional CSV. Analysis does
              not import households or change eligibility.
            </p>
            {!online && (
              <p role="status" className="registry-notice">
                Reconnect to analyze a CSV.
              </p>
            )}
            <div className="space-y-3">
              <label htmlFor="registry-csv-file">Fictional CSV file</label>
              <input
                id="registry-csv-file"
                type="file"
                accept=".csv"
                disabled={isAnalyzingCsv}
                onChange={(e) => {
                  setCsvFile(e.target.files?.[0] || null);
                  setCsvResult(null);
                  setCsvError(null);
                }}
              />
              <div className="registry-decision-actions">
                <button
                  onClick={() => void analyzeCsv(csvFile || undefined)}
                  disabled={isAnalyzingCsv || !online || !csvFile}
                  className="registry-button registry-primary"
                >
                  Analyze selected CSV
                </button>
                <button
                  onClick={() => void analyzeCsv()}
                  disabled={isAnalyzingCsv || !online}
                  className="registry-button"
                >
                  Analyze sample CSV
                </button>
              </div>
            </div>
            {isAnalyzingCsv && <p role="status">Analyzing CSV...</p>}
            {csvError && (
              <p role="alert" className="registry-error">
                {csvError}
              </p>
            )}
            {csvResult && (
              <section aria-label="CSV results" className="space-y-4">
                <p role="status">
                  {csvResult.total_records_processed} records analyzed.{" "}
                  {csvResult.flagged_duplicates_count} possible duplicate pairs.
                </p>
                {csvResult.flagged_records.map((item, idx) => (
                  <div key={idx} className="registry-csv-pair">
                    <div className="grid sm:grid-cols-2 gap-4">
                      {[item.record_a, item.record_b].map((record, index) => (
                        <div key={index}>
                          <p className="font-semibold">{record.name}</p>
                          <p>{record.address}</p>
                          <p className="registry-muted break-all">
                            {record.id} · {record.barangay}
                          </p>
                        </div>
                      ))}
                    </div>
                    <details className="registry-detail mt-3">
                      <summary>Match details</summary>
                      <p>
                        Overall similarity: {item.match_metrics.overall_score}%.
                        Name: {item.match_metrics.name_score}%. Address:{" "}
                        {item.match_metrics.address_score}%. DAFAC:{" "}
                        {item.match_metrics.dafac_match
                          ? "same reference"
                          : "different references"}
                        .
                      </p>
                      <p className="break-words">{item.anomaly_type}</p>
                    </details>
                  </div>
                ))}
                <p className="registry-muted">
                  Suggested matches need human review. No records have been
                  imported.
                </p>
              </section>
            )}
            <button
              onClick={() => setShowCsvModal(false)}
              disabled={isAnalyzingCsv}
              className="registry-button"
            >
              Back to households
            </button>
          </div>
        </RegistryDialog>
      )}
    </div>
  );
}
