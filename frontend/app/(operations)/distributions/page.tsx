"use client";

import React, { useEffect, useRef, useState } from "react";
import { formatRecordedDate } from "@/lib/recordedDate";
import Link from "next/link";
import { RefreshCw } from "lucide-react";
import {
  fetchDistributions,
  fetchBeneficiaries,
  fetchBatches,
  fetchBatchDetail,
  Allocation,
  confirmDistribution,
  DistributionConfirmPayload,
  Distribution,
  Beneficiary,
  ReliefBatch,
  apiUrl,
  formatPeso,
} from "@/lib/api";
import { useChainStatus, chainLabel } from "@/lib/useChainStatus";
import { useRole } from "@/lib/roleContext";
import { receiptVerificationHref } from "@/lib/receiptNavigation";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { submitOnlinePayout } from "@/lib/payoutConnection";
import { recoverPayoutAnchor } from "@/lib/api";
import PayoutAnchorStatus from "@/components/PayoutAnchorStatus";
import RegistryDialog from "@/components/RegistryDialog";
import ReceiptDetails from "@/components/ReceiptDetails";

export default function DistributionsPage() {
  const chain = useChainStatus();
  const { role, account } = useRole();
  const browserOnline = useBrowserOnline();
  const [distributions, setDistributions] = useState<Distribution[]>([]);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [batches, setBatches] = useState<ReliefBatch[]>([]);
  const [allocations, setAllocations] = useState<Allocation[]>([]);
  const loadVersion = useRef(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // New Distribution Form State
  const [selectedBenId, setSelectedBenId] = useState("");
  const [amountStr, setAmountStr] = useState("");
  const numericAmount = parseFloat(amountStr) || 0;
  const selectedReceipt = "sample_relief_receipt.svg";
  const [step, setStep] = useState<"IDLE" | "SUBMITTING" | "SUCCESS">("IDLE");
  const submitting = useRef(false);
  const pendingSubmission = useRef<{
    key: string;
    payload: DistributionConfirmPayload;
    serialized: string;
  } | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [confirmedResult, setConfirmedResult] = useState<Distribution | null>(
    null,
  );
  const [previewReceipt, setPreviewReceipt] = useState<Distribution | null>(
    null,
  );
  const recovering = useRef(false);
  const [anchorBusy, setAnchorBusy] = useState(false);
  const [anchorError, setAnchorError] = useState<{
    id: string;
    message: string;
  } | null>(null);

  const recoverAnchor = async (id: string) => {
    if (recovering.current || role !== "DISBURSING") return;
    recovering.current = true;
    setAnchorBusy(true);
    setAnchorError(null);
    try {
      const result = await submitOnlinePayout(navigator.onLine, () =>
        recoverPayoutAnchor(id),
      );
      setDistributions((rows) =>
        rows.map((row) => (row.distribution_id === id ? result : row)),
      );
      setConfirmedResult((current) =>
        current?.distribution_id === id ? result : current,
      );
    } catch (e) {
      setAnchorError({
        id,
        message: e instanceof Error ? e.message : "Recovery failed. Try again.",
      });
    } finally {
      recovering.current = false;
      setAnchorBusy(false);
    }
  };

  const loadData = async () => {
    const version = ++loadVersion.current;
    setLoading(true);
    setLoadError(null);
    try {
      const [dList, bList, batchList] = await Promise.all([
        fetchDistributions(),
        fetchBeneficiaries(),
        fetchBatches(),
      ]);
      const details =
        role === "DISBURSING"
          ? await Promise.all(
              batchList.map((batch) => fetchBatchDetail(batch.batch_id)),
            )
          : [];
      if (version !== loadVersion.current) return;
      setDistributions(dList);
      setBeneficiaries(bList);
      setBatches(batchList);
      setAllocations(details.flatMap((detail) => detail.allocations));
      setSelectedBenId((current) =>
        bList.some((b) => b.beneficiary_id === current) ? current : "",
      );
    } catch (err) {
      if (version === loadVersion.current)
        setLoadError(
          err instanceof Error
            ? err.message
            : "Payout records could not be loaded.",
        );
    } finally {
      if (version === loadVersion.current) setLoading(false);
    }
  };
  useEffect(() => {
    void loadData();
    return () => {
      loadVersion.current++;
    };
  }, [account?.id]);

  const handleDisburse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBenId || submitting.current) return;
    if (role !== "DISBURSING" || loading || loadError || blockedReason) {
      setSubmitError(
        "Sign in as a disbursing officer and refresh the household records before recording a payout.",
      );
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
        receipt_filename: selectedReceipt,
      };
      const serialized = JSON.stringify(payload);
      if (pendingSubmission.current?.serialized !== serialized) {
        const bytes = crypto.getRandomValues(new Uint8Array(16));
        const key =
          "payout-" +
          Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join(
            "",
          );
        pendingSubmission.current = { key, payload, serialized };
      }
      const request = pendingSubmission.current;
      const result = await submitOnlinePayout(navigator.onLine, () =>
        confirmDistribution(request.payload, request.key),
      );
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

  const selectedBeneficiaryObj = beneficiaries.find(
    (b) => b.beneficiary_id === selectedBenId,
  );
  const selectedBatch = batches.find(
    (b) => b.batch_id === selectedBeneficiaryObj?.batch_id,
  );
  const selectedIsApproved =
    selectedBeneficiaryObj?.verification_status === "VERIFIED" &&
    selectedBeneficiaryObj?.review_status === "APPROVED";
  const standardGrant = selectedBatch?.standard_grant ?? 0;
  const maxGrant = selectedBatch?.max_grant ?? 0;

  // Start each household at its batch's standard grant
  useEffect(() => {
    if (selectedBatch) setAmountStr(String(selectedBatch.standard_grant));
  }, [selectedBenId, selectedBatch?.batch_id]);

  const existingPayout = distributions.find(
    (d) =>
      d.beneficiary_id === selectedBenId &&
      d.batch_id === selectedBatch?.batch_id,
  );
  const allocation = allocations.find(
    (a) =>
      a.batch_id === selectedBatch?.batch_id &&
      a.barangay_id === selectedBeneficiaryObj?.barangay_id,
  );
  const spentCentavos = allocation
    ? distributions
        .filter((d) => d.allocation_id === allocation.allocation_id)
        .reduce(
          (sum, d) => sum + (d.amount_centavos ?? Math.round(d.amount * 100)),
          0,
        )
    : 0;
  const remainingCentavos = allocation
    ? (allocation.amount_centavos ?? Math.round(allocation.amount * 100)) -
      spentCentavos
    : 0;
  const amountValid =
    /^\d+(?:\.\d{1,2})?$/.test(amountStr) && numericAmount > 0;
  const blockedReason = !selectedBeneficiaryObj
    ? "Choose a household to begin."
    : existingPayout
      ? "A payout is already recorded for this household in this batch."
      : !selectedIsApproved
        ? "This household needs DSWD approval before payout."
        : !selectedBatch || selectedBatch.status !== "ACTIVE"
          ? "This household's relief batch is not active."
          : !allocation
            ? "No allocation is recorded for this barangay and batch."
            : !amountValid
              ? "Enter a positive amount with up to two decimal places."
              : numericAmount > maxGrant
                ? "The amount exceeds this batch's maximum grant."
                : Math.round(numericAmount * 100) > remainingCentavos
                  ? "The amount exceeds the remaining recorded allocation."
                  : null;
  const query = searchTerm.trim().toLowerCase();
  const filteredPayouts = distributions.filter((d) =>
    [
      d.distribution_id,
      d.beneficiary_id,
      beneficiaries.find((b) => b.beneficiary_id === d.beneficiary_id)
        ?.household_name,
    ].some((value) => value?.toLowerCase().includes(query)),
  );
  return (
    <div className="registry workflow space-y-6">
      <header className="registry-header">
        <div>
          <h1 id="payout-heading" tabIndex={-1}>
            {role === "DISBURSING"
              ? "Record a demo payout"
              : role === "BENEFICIARY"
                ? "My payouts"
                : "Payout records"}
          </h1>
          <p className="registry-description">
            {role === "DISBURSING"
              ? "Choose an approved household, check the amount and record its synthetic payout."
              : "Inspect recorded payouts and their receipts."}
          </p>
        </div>
        <Link href="/verify" className="registry-button">
          Check receipts
        </Link>
      </header>
      {role !== "DISBURSING" && (
        <p className="workflow-context">
          Your signed-in role can inspect these records. A disbursing officer
          records the payout.
        </p>
      )}
      {loading && <p role="status">Loading household and payout records...</p>}
      {loadError && (
        <div role="alert" className="registry-error">
          {loadError} Previously loaded records are hidden until refresh
          succeeds.{" "}
          <button
            type="button"
            onClick={() => void loadData()}
            className="registry-button"
          >
            Refresh records
          </button>
        </div>
      )}
      <div className={role === "DISBURSING" ? "workflow-columns" : ""}>
        {role === "DISBURSING" && (
          <section aria-label="Payout entry" className="workflow-panel">
            {browserOnline === false && (
              <div role="alert" className="registry-notice">
                <p className="font-semibold">Browser is offline</p>
                <p>
                  Reconnect to record or recover a payout. Nothing is queued.
                </p>
              </div>
            )}
            {confirmedResult && step === "SUCCESS" ? (
              <div role="status" className="space-y-4">
                <div className="registry-success">
                  <h2>Payout recorded</h2>
                  <p>
                    {beneficiaries.find(
                      (b) =>
                        b.beneficiary_id === confirmedResult.beneficiary_id,
                    )?.household_name || confirmedResult.beneficiary_id}
                  </p>
                  <p className="workflow-amount">
                    {formatPeso(confirmedResult.amount)}
                  </p>
                  <p className="registry-muted break-all">
                    Receipt: {confirmedResult.distribution_id}
                  </p>
                </div>
                <PayoutAnchorStatus
                  anchor={confirmedResult.anchor_job}
                  busy={anchorBusy || !browserOnline}
                  onRecover={() =>
                    void recoverAnchor(confirmedResult.distribution_id)
                  }
                  error={
                    anchorError?.id === confirmedResult.distribution_id
                      ? anchorError.message
                      : undefined
                  }
                />
                <p className="registry-muted">
                  Synthetic payout. A saved record or receipt match does not
                  prove cash delivery.
                </p>
                <Link
                  href={receiptVerificationHref(
                    confirmedResult.distribution_id,
                  )}
                  className="registry-button registry-primary"
                >
                  Check this receipt
                </Link>
                <button
                  type="button"
                  className="registry-button"
                  disabled={loading || !!loadError || anchorBusy}
                  onClick={() => {
                    setConfirmedResult(null);
                    setStep("IDLE");
                    setSelectedBenId("");
                    setAmountStr("");
                    setSubmitError(null);
                    pendingSubmission.current = null;
                  }}
                >
                  Record another payout
                </button>
                <details className="registry-detail">
                  <summary>Receipt hash and transaction</summary>
                  <dl className="registry-references">
                    <dt>Receipt hash</dt>
                    <dd>{confirmedResult.receipt_hash}</dd>
                    <dt>Anchor transaction</dt>
                    <dd>
                      {confirmedResult.blockchain_tx_hash || "None recorded"}
                    </dd>
                  </dl>
                </details>
              </div>
            ) : (
              <form
                onSubmit={handleDisburse}
                aria-busy={step === "SUBMITTING"}
                className="space-y-5"
              >
                <h2>Payout details</h2>
                <div>
                  <label htmlFor="payout-household">Household</label>
                  <select
                    id="payout-household"
                    value={selectedBenId}
                    disabled={step === "SUBMITTING" || loading || !!loadError}
                    onChange={(e) => {
                      setSelectedBenId(e.target.value);
                      setSubmitError(null);
                    }}
                  >
                    <option value="">Choose a household</option>
                    {beneficiaries.map((b) => (
                      <option key={b.beneficiary_id} value={b.beneficiary_id}>
                        {b.household_name} ({b.barangay_name})
                      </option>
                    ))}
                  </select>
                </div>
                {selectedBeneficiaryObj && !loading && !loadError && (
                  <div className="workflow-context space-y-3">
                    <h3>{selectedBeneficiaryObj.household_name}</h3>
                    <p>{selectedBeneficiaryObj.barangay_name}</p>
                    <p
                      className={
                        selectedIsApproved
                          ? "text-emerald-800"
                          : "text-amber-800"
                      }
                    >
                      {selectedIsApproved
                        ? "Approved"
                        : selectedBeneficiaryObj.verification_status ===
                            "REJECTED"
                          ? "Rejected"
                          : "Pending DSWD review"}
                    </p>
                    <dl className="workflow-facts">
                      <dt>Relief batch</dt>
                      <dd>{selectedBatch?.calamity_name || "Not available"}</dd>
                      <dt>Batch status</dt>
                      <dd>
                        {selectedBatch?.status === "ACTIVE"
                          ? "Active"
                          : selectedBatch?.status || "Not available"}
                      </dd>
                      <dt>Standard grant</dt>
                      <dd>{formatPeso(standardGrant)}</dd>
                      <dt>Maximum grant</dt>
                      <dd>{formatPeso(maxGrant)}</dd>
                      <dt>Remaining recorded allocation</dt>
                      <dd>
                        {allocation
                          ? formatPeso(remainingCentavos / 100)
                          : "No allocation"}
                      </dd>
                    </dl>
                    <p className="registry-muted">
                      This is the recorded budget, not cash on hand. The API
                      checks the current balance when saving.
                    </p>
                  </div>
                )}
                <div>
                  <label htmlFor="payout-amount">Fictional amount (PHP)</label>
                  <input
                    id="payout-amount"
                    type="text"
                    inputMode="decimal"
                    value={amountStr}
                    disabled={
                      !selectedBenId ||
                      step === "SUBMITTING" ||
                      loading ||
                      !!loadError
                    }
                    onChange={(e) => setAmountStr(e.target.value)}
                    aria-describedby="payout-amount-help"
                  />
                  <p id="payout-amount-help" className="registry-muted mt-2">
                    Use up to two decimal places.
                    {selectedBatch &&
                    amountValid &&
                    numericAmount !== standardGrant
                      ? " This differs from the batch's standard grant. Check the amount before saving."
                      : ""}
                  </p>
                </div>
                {blockedReason && !loading && !loadError && (
                  <p
                    className={
                      selectedBenId ? "registry-notice" : "registry-muted"
                    }
                  >
                    {blockedReason}
                    {existingPayout && (
                      <Link
                        href={receiptVerificationHref(
                          existingPayout.distribution_id,
                        )}
                        className="registry-button registry-text-button"
                      >
                        Open recorded receipt
                      </Link>
                    )}
                  </p>
                )}
                {submitError && (
                  <p role="alert" className="registry-error">
                    {submitError} Retry the same details to retrieve an existing
                    payout if the response was lost.
                  </p>
                )}
                {step === "SUBMITTING" && <p role="status">Saving payout...</p>}
                <button
                  type="submit"
                  disabled={
                    step === "SUBMITTING" ||
                    !browserOnline ||
                    loading ||
                    !!loadError ||
                    !!blockedReason
                  }
                  className="registry-button registry-primary w-full"
                >
                  {step === "SUBMITTING"
                    ? "Saving payout..."
                    : !browserOnline
                      ? "Reconnect to record a payout"
                      : submitError
                        ? "Retry payout request"
                        : "Record demo payout"}
                </button>
                <details className="registry-detail">
                  <summary>Demo evidence and connection</summary>
                  <p>
                    The demo uses a shared receipt template. Household-specific
                    receipt uploads and recipient acknowledgement are not
                    available.
                  </p>
                  <p>
                    {chainLabel(chain)}. Payout recording and blockchain
                    confirmation are separate.
                  </p>
                </details>
              </form>
            )}
          </section>
        )}
        <section
          aria-label="Recorded payouts"
          className="workflow-panel space-y-4"
        >
          <div className="workflow-section-heading">
            <h2>Recorded payouts</h2>
            <button
              className="registry-button"
              disabled={loading || step === "SUBMITTING"}
              onClick={() => void loadData()}
            >
              <RefreshCw size={16} aria-hidden="true" />
              Refresh
            </button>
          </div>
          <label htmlFor="payout-search">Search payout records</label>
          <input
            id="payout-search"
            type="search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Household name or receipt reference"
          />
          {!loading && !loadError && filteredPayouts.length === 0 && (
            <div className="registry-empty">
              <h3>{query ? "No matching payouts" : "No payouts recorded"}</h3>
              <p>
                {query
                  ? "Try another household name or receipt reference."
                  : "Recorded payouts will appear here."}
              </p>
              {query && (
                <button
                  className="registry-button"
                  onClick={() => setSearchTerm("")}
                >
                  Clear search
                </button>
              )}
            </div>
          )}
          {!loading && !loadError && (
            <ol className="workflow-records">
              {filteredPayouts.map((dist) => (
                <li key={dist.distribution_id} className="workflow-record">
                  <div className="workflow-section-heading">
                    <h3>
                      {beneficiaries.find(
                        (b) => b.beneficiary_id === dist.beneficiary_id,
                      )?.household_name || dist.beneficiary_id}
                    </h3>
                    <p className="workflow-amount-small">
                      {formatPeso(dist.amount)}
                    </p>
                  </div>
                  <p className="registry-muted">
                    Recorded {formatRecordedDate(dist.distributed_at)}
                  </p>
                  <p className="registry-record-id break-all">
                    {dist.distribution_id}
                  </p>
                  <p
                    className={
                      dist.anchor_job?.state === "FAILED"
                        ? "text-amber-800"
                        : "text-slate-700"
                    }
                  >
                    {dist.anchor_job
                      ? {
                          PENDING: "Anchor pending",
                          SUBMITTED: "Awaiting anchor confirmation",
                          CONFIRMED: "Anchor confirmed",
                          FAILED: "Anchor needs attention",
                        }[dist.anchor_job.state]
                      : "Anchor not tracked"}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => setPreviewReceipt(dist)}
                      className="registry-button"
                    >
                      View receipt
                    </button>
                    <Link
                      href={receiptVerificationHref(dist.distribution_id)}
                      className="registry-button registry-text-button"
                    >
                      Check receipt
                    </Link>
                  </div>
                  <details className="registry-detail">
                    <summary>Anchor status and recovery</summary>
                    <PayoutAnchorStatus
                      anchor={dist.anchor_job}
                      busy={anchorBusy || !browserOnline}
                      onRecover={
                        role === "DISBURSING"
                          ? () => void recoverAnchor(dist.distribution_id)
                          : undefined
                      }
                      error={
                        anchorError?.id === dist.distribution_id
                          ? anchorError.message
                          : undefined
                      }
                    />
                  </details>
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>
      {previewReceipt && (
        <RegistryDialog
          title="Payout receipt"
          returnFocusId="payout-heading"
          onClose={() => setPreviewReceipt(null)}
        >
          <div className="registry-dialog-content">
            <ReceiptDetails
              record={previewReceipt}
              household={beneficiaries.find(
                (b) => b.beneficiary_id === previewReceipt.beneficiary_id,
              )}
              checkLink
            />
            <button
              className="registry-button"
              onClick={() => setPreviewReceipt(null)}
            >
              Back to payouts
            </button>
          </div>
        </RegistryDialog>
      )}
    </div>
  );
}
