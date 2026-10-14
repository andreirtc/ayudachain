"use client";

import React, { Suspense, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  verifyBlockchain,
  VerifyResponse,
  fetchDistributions,
  fetchBeneficiaries,
  Distribution,
  Beneficiary,
  formatPeso,
  fetchPublicReceipts,
  PublicReceiptReference,
} from "@/lib/api";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import ReceiptDetails from "@/components/ReceiptDetails";
import {
  receiptVerificationHref,
  selectReceiptId,
} from "@/lib/receiptNavigation";

const outcomes = {
  VERIFIED: {
    title: "Receipt hash verified",
    style: "verification-verified",
    description:
      "The current receipt hash matches the hash read from the configured blockchain.",
  },
  MISMATCH: {
    title: "Receipt hash mismatch",
    style: "verification-mismatch",
    description:
      "The current receipt hash differs from its blockchain record. Investigate the covered fields before relying on this receipt.",
  },
  UNANCHORED: {
    title: "No receipt anchor found",
    style: "verification-unanchored",
    description:
      "The blockchain was read successfully, but no receipt anchor was found for this reference.",
  },
  UNAVAILABLE: {
    title: "Verification unavailable",
    style: "verification-unavailable",
    description:
      "A reliable blockchain lookup could not be completed. Try again when the service is available.",
  },
};

function VerifyContent() {
  const { account, loading: sessionLoading } = useRole();
  const online = useBrowserOnline();
  const privateContext = !!account && account.role !== "BARANGAY";
  const searchParams = useSearchParams();
  const router = useRouter();
  const requestedId = searchParams.get("distribution_id");
  const [loadedReference, setLoadedReference] = useState<
    string | null | undefined
  >(undefined);
  const [distributions, setDistributions] = useState<
    (PublicReceiptReference & Partial<Distribution>)[]
  >([]);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [manualReference, setManualReference] = useState("");
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [checkedAt, setCheckedAt] = useState(0);
  const [loadingRecords, setLoadingRecords] = useState(true);
  const [checking, setChecking] = useState(false);
  const [recordError, setRecordError] = useState<string | null>(null);
  const [checkError, setCheckError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);
  const [recheck, setRecheck] = useState(0);
  const requestVersion = useRef(0);
  const checkPending = useRef(false);

  useEffect(() => {
    if (sessionLoading) return;
    let cancelled = false;
    setLoadingRecords(true);
    setLoadedReference(undefined);
    setRecordError(null);
    setCheckError(null);
    setSelectedId("");
    setResult(null);
    setChecking(false);
    setCheckedAt(0);
    Promise.all([
      privateContext ? fetchDistributions() : fetchPublicReceipts(),
      privateContext
        ? fetchBeneficiaries({ include_historical: true })
        : Promise.resolve([]),
    ])
      .then(([records, households]) => {
        if (cancelled) return;
        setDistributions(records);
        setBeneficiaries(households);
        setSelectedId(selectReceiptId(records, requestedId));
        setLoadedReference(requestedId);
      })
      .catch((err) => {
        if (!cancelled)
          setRecordError(
            err instanceof Error
              ? err.message
              : "Receipt references could not be loaded.",
          );
      })
      .finally(() => {
        if (!cancelled) setLoadingRecords(false);
      });
    return () => {
      cancelled = true;
    };
  }, [requestedId, reload, account?.id, privateContext, sessionLoading]);

  useEffect(() => {
    if (!selectedId) {
      checkPending.current = false;
      return;
    }
    if (!navigator.onLine) {
      checkPending.current = false;
      setChecking(false);
      setCheckError("Reconnect to check this receipt.");
      return;
    }
    const version = ++requestVersion.current;
    let cancelled = false;
    checkPending.current = true;
    setChecking(true);
    setResult(null);
    setCheckError(null);
    verifyBlockchain(selectedId)
      .then((data) => {
        if (cancelled || version !== requestVersion.current) return;
        if (
          data.record_id !== selectedId ||
          !outcomes[data.verification_status]
        )
          throw new Error(
            "The lookup did not return evidence for this receipt. Try again.",
          );
        setResult(data);
        setCheckedAt(Date.now());
      })
      .catch((err) => {
        if (!cancelled && version === requestVersion.current)
          setCheckError(
            err instanceof Error
              ? err.message
              : "Receipt lookup failed. Try again.",
          );
      })
      .finally(() => {
        if (!cancelled && version === requestVersion.current) {
          checkPending.current = false;
          setChecking(false);
        }
      });
    return () => {
      cancelled = true;
      if (version === requestVersion.current) checkPending.current = false;
    };
  }, [selectedId, recheck]);

  const recordsReady = !loadingRecords && loadedReference === requestedId;
  const missingReference =
    recordsReady &&
    requestedId !== null &&
    !distributions.some((record) => record.distribution_id === requestedId);
  const activeDist = recordsReady
    ? distributions.find((record) => record.distribution_id === selectedId)
    : undefined;
  const activeBen = beneficiaries.find(
    (household) => household.beneficiary_id === activeDist?.beneficiary_id,
  );
  const currentResult =
    activeDist && result?.record_id === selectedId ? result : null;
  const outcome = currentResult
    ? outcomes[currentResult.verification_status]
    : null;
  const recheckReceipt = () => {
    if (
      checkPending.current ||
      !navigator.onLine ||
      !selectedId ||
      !recordsReady
    )
      return;
    checkPending.current = true;
    setChecking(true);
    setRecheck((value) => value + 1);
  };
  const openReference = (reference: string) => {
    if (reference === requestedId && recordsReady && selectedId) {
      recheckReceipt();
      return;
    }
    setResult(null);
    setSelectedId("");
    router.replace(receiptVerificationHref(reference), { scroll: false });
  };

  return (
    <div className="registry workflow verification-page space-y-6">
      <header>
        <h1>Check a receipt</h1>
        <p className="registry-description">
          Compare a saved receipt with its current proof.
        </p>
      </header>
      {online === false && (
        <p role="status" className="registry-notice">
          Browser is offline. Reconnect to check receipt integrity.
          {currentResult
            ? " The displayed result is from an earlier check."
            : ""}
        </p>
      )}
      <div className="verification-layout"><section
        aria-label="Choose a receipt"
        className="workflow-panel space-y-4"
      >
        {loadingRecords || sessionLoading || (!recordsReady && !recordError) ? (
          <p role="status">Loading receipts...</p>
        ) : recordError ? (
          <div role="alert" className="registry-error">
            {recordError}
            <button
              className="registry-button"
              onClick={() => setReload((value) => value + 1)}
            >
              Retry loading receipts
            </button>
          </div>
        ) : (
          <>
            {missingReference && (
              <div role="alert" className="registry-notice">
                <h2>Receipt not found</h2>
                <p className="break-all">
                  No recorded payout available to this view matches{" "}
                  {requestedId || "the empty receipt reference"}. Check the
                  reference or choose a receipt below.
                </p>
              </div>
            )}
            {distributions.length === 0 ? (
              <p>
                No payout receipts are available to this view.
                {privateContext && (
                  <Link
                    href="/distributions"
                    className="registry-button registry-text-button"
                  >
                    View payouts
                  </Link>
                )}
              </p>
            ) : (
              <div>
                <label htmlFor="receipt-record">Receipt</label>
                <select
                  id="receipt-record"
                  value={recordsReady ? selectedId : ""}
                  disabled={!recordsReady}
                  onChange={(event) => openReference(event.target.value)}
                >
                  {!selectedId && (
                    <option value="" disabled>
                      Choose a recorded receipt
                    </option>
                  )}
                  {distributions.map((record) => (
                    <option
                      key={record.distribution_id}
                      value={record.distribution_id}
                    >
                      {record.amount !== undefined
                        ? (beneficiaries.find(
                            (b) => b.beneficiary_id === record.beneficiary_id,
                          )?.household_name || record.beneficiary_id) +
                          " (" +
                          formatPeso(record.amount) +
                          ") · "
                        : ""}
                      {record.distribution_id}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </>
        )}
        <details className="registry-detail">
          <summary>Enter a receipt reference</summary>
          <form
            className="space-y-3 mt-3"
            onSubmit={(event) => {
              event.preventDefault();
              if (manualReference.trim()) openReference(manualReference.trim());
            }}
          >
            <label htmlFor="manual-receipt">Receipt reference</label>
            <input
              id="manual-receipt"
              value={manualReference}
              onChange={(event) => setManualReference(event.target.value)}
              maxLength={128}
              autoComplete="off"
              required
            />
            <button
              className="registry-button"
              disabled={!manualReference.trim() || loadingRecords}
            >
              Open receipt
            </button>
          </form>
        </details>
      </section><div className="workflow-panel space-y-5">
      {activeDist && (
        <section aria-label="Verification result" className="space-y-4">
          {checking && <p role="status">Reading the blockchain receipt...</p>}
          {checkError && (
            <div role="alert" className="registry-error">
              <p>{checkError}</p>
              <button
                className="registry-button"
                disabled={checking || !online}
                onClick={recheckReceipt}
              >
                Retry lookup
              </button>
            </div>
          )}
          {currentResult && outcome && (
            <div
              role="status"
              className={"verification-result " + outcome.style}
            >
              <h2>{outcome.title}</h2>
              <p>{outcome.description}</p>
              <p className="registry-muted">
                Checked this session at{" "}
                {new Date(checkedAt).toLocaleTimeString()}.
              </p>
            </div>
          )}
          <button
            className="registry-button registry-primary"
            disabled={checking || !online || !recordsReady}
            onClick={recheckReceipt}
          >
            {checking ? "Checking receipt..." : "Check again"}
          </button>
          <p className="registry-muted">
            This checks the receipt hash only. It does not prove cash delivery
            or validate every household and document field.
          </p>
          {currentResult && (
            <details className="registry-detail">
              <summary>Hash comparison and lookup details</summary>
              <dl className="receipt-references mt-3">
                <dt>Current record hash</dt>
                <dd className="font-mono">
                  {currentResult.receipt_hash_local}
                </dd>
                <dt>Hash read from blockchain</dt>
                <dd className="font-mono">
                  {currentResult.receipt_hash_onchain ||
                    "No hash returned by this lookup"}
                </dd>
                <dt>Network</dt>
                <dd>{currentResult.network}</dd>
                <dt>Configured contract</dt>
                <dd className="font-mono">
                  {currentResult.contract_address || "No contract configured"}
                </dd>
                {currentResult.timestamp && (
                  <>
                    <dt>Anchor timestamp</dt>
                    <dd>
                      {new Date(
                        currentResult.timestamp * 1000,
                      ).toLocaleString()}
                    </dd>
                  </>
                )}
                <dt>Lookup explanation</dt>
                <dd>{currentResult.status_message}</dd>
              </dl>
            </details>
          )}
        </section>
      )}
      {activeDist && (
        <div>
          <ReceiptDetails
            key={activeDist.distribution_id}
            record={activeDist}
            household={activeBen}
          />
        </div>
      )}
      {!activeDist && !loadingRecords && <div className="registry-case-empty"><h2>Choose a receipt to check</h2><p>Select a saved record or enter its exact reference.</p></div>}
      </div></div>
    </div>
  );
}

export default function VerifyPage() {
  return (
    <Suspense
      fallback={
        <p role="status" className="py-12 text-center">
          Loading verification...
        </p>
      }
    >
      <VerifyContent />
    </Suspense>
  );
}
