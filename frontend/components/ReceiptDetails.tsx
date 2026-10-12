"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  apiUrl,
  Beneficiary,
  Distribution,
  formatPeso,
  PublicReceiptReference,
} from "@/lib/api";
import { receiptVerificationHref } from "@/lib/receiptNavigation";

export default function ReceiptDetails({
  record,
  household,
  checkLink = false,
}: {
  record: PublicReceiptReference & Partial<Distribution>;
  household?: Beneficiary;
  checkLink?: boolean;
}) {
  const [imageStatus, setImageStatus] = useState<
    "LOADING" | "READY" | "FAILED"
  >("LOADING");
  const [imageVersion, setImageVersion] = useState(0);
  useEffect(() => {
    setImageStatus("LOADING");
    setImageVersion(0);
  }, [record.distribution_id, record.receipt_file_path]);
  const sharedTemplate = record.receipt_file_path?.endsWith(
    "/sample_relief_receipt.svg",
  );

  return (
    <section aria-label="Receipt details" className="receipt-details space-y-5">
      {record.amount !== undefined ? (
        <div className="receipt-summary">
          <p className="registry-muted">Local payout record</p>
          <h3>
            {household?.household_name ||
              record.beneficiary_id ||
              "Recorded household"}
          </h3>
          <p className="workflow-amount">{formatPeso(record.amount)}</p>
          {record.distributed_at && (
            <p className="registry-muted">
              Recorded {new Date(record.distributed_at).toLocaleString()}
            </p>
          )}
        </div>
      ) : (
        <p className="registry-muted">
          This public view shows receipt references and hash checks.{" "}
          <Link href="/sign-in" className="underline text-blue-700">
            Sign in
          </Link>{" "}
          for the details available to your account.
        </p>
      )}
      <dl className="receipt-references">
        <dt>Receipt reference</dt>
        <dd>{record.distribution_id}</dd>
        <dt>Relief batch</dt>
        <dd>{record.batch_id}</dd>
        {household?.barangay_name && (
          <>
            <dt>Barangay</dt>
            <dd>{household.barangay_name}</dd>
          </>
        )}
      </dl>
      {record.amount !== undefined && (
        <p className="registry-muted">
          Household information comes from the current registry. A receipt check
          does not verify identity or prove cash delivery.
        </p>
      )}
      {record.receipt_file_path ? (
        <details className="registry-detail">
          <summary>Saved receipt image</summary>
          <div className="space-y-3 mt-3">
            {sharedTemplate && (
              <p className="registry-notice">
                <strong>Shared demo template.</strong> This file can show a
                different fictional household. It is not a household-specific
                receipt.
              </p>
            )}
            {imageStatus === "LOADING" && (
              <p role="status">Loading receipt image...</p>
            )}
            {imageStatus === "FAILED" ? (
              <div role="alert" className="registry-error">
                <p>
                  The receipt image could not be loaded. The payout reference
                  and hash remain available.
                </p>
                <button
                  type="button"
                  className="registry-button"
                  onClick={() => {
                    setImageStatus("LOADING");
                    setImageVersion((value) => value + 1);
                  }}
                >
                  Retry image
                </button>
              </div>
            ) : (
              <img
                key={imageVersion}
                src={apiUrl(record.receipt_file_path)}
                alt={
                  sharedTemplate
                    ? "Shared fictional receipt template"
                    : "Saved receipt image for " + record.distribution_id
                }
                loading="lazy"
                className="receipt-image"
                onLoad={() => setImageStatus("READY")}
                onError={() => setImageStatus("FAILED")}
              />
            )}
          </div>
        </details>
      ) : (
        record.amount !== undefined && (
          <p className="workflow-context">
            No household receipt image is available for this record. Its saved
            hash can still be checked.
          </p>
        )
      )}
      {record.ocr_text && (
        <details className="registry-detail">
          <summary>Saved extracted text</summary>
          <p className="registry-muted">
            Extracted text is stored evidence, not a new identity check.
            {sharedTemplate ? " This text belongs to the shared template." : ""}
          </p>
          <pre className="receipt-extracted">{record.ocr_text}</pre>
        </details>
      )}
      {record.receipt_hash && (
        <details className="registry-detail">
          <summary>Saved hash and transaction</summary>
          <dl className="receipt-references mt-3">
            <dt>Saved receipt hash</dt>
            <dd className="font-mono">{record.receipt_hash}</dd>
            <dt>Recorded transaction</dt>
            <dd className="font-mono">
              {record.blockchain_tx_hash || "None recorded"}
            </dd>
          </dl>
          <p className="registry-muted">
            A stored transaction reference is not a current verification result.
          </p>
        </details>
      )}
      {checkLink && (
        <Link
          href={receiptVerificationHref(record.distribution_id)}
          className="registry-button registry-primary"
        >
          Check this receipt
        </Link>
      )}
    </section>
  );
}
