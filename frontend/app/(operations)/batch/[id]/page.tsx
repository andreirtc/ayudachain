"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchBatchDetail, formatPeso } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";

type BatchDetail = Awaited<ReturnType<typeof fetchBatchDetail>>;
export default function BatchDetailPage() {
  const params = useParams();
  const batchId = String(params?.id || "");
  const [data, setData] = useState<BatchDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setData(null);
    setError(null);
    fetchBatchDetail(batchId)
      .then((value) => {
        if (!cancelled) setData(value);
      })
      .catch((err) => {
        if (!cancelled)
          setError(
            err instanceof Error
              ? err.message
              : "Batch details could not be loaded.",
          );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [batchId, reload]);
  const allocated =
    data?.allocations.reduce(
      (sum, allocation) =>
        sum +
        (allocation.amount_centavos ?? Math.round(allocation.amount * 100)),
      0,
    ) || 0;
  return (
    <div className="registry workflow space-y-6">
      <Link href="/dashboard" className="registry-button registry-text-button">
        Back to overview
      </Link>
      <header>
        <h1>{data?.batch.calamity_name || "Relief batch"}</h1>
        <p className="registry-description break-all">{batchId}</p>
      </header>
      {loading && <p role="status">Loading relief batch details...</p>}
      {error && (
        <div role="alert" className="registry-error">
          <h2>Batch details unavailable</h2>
          <p>{error}</p>
          <button
            className="registry-button"
            onClick={() => setReload((value) => value + 1)}
          >
            Retry batch details
          </button>
        </div>
      )}
      {data && (
        <>
        <section aria-label="Batch funding" className="overview-metrics overview-metrics-three">
            {[
              ["Released funds", data.batch.amount],
              ["Allocated funds", allocated / 100],
              ["Recorded payouts", data.distributed_amount],
            ].map(([label, amount]) => (
              <div className="overview-metric" key={String(label)}>
                <h2>{label}</h2>
                <p>{formatPeso(Number(amount))}</p>
              </div>
            ))}
          </section>
          <p className="workflow-context">
            {data.total_distributions} payout records ·{" "}
            {data.batch.status === "ACTIVE"
              ? "Active batch"
              : data.batch.status}
            . Recorded amounts do not prove cash delivery.
          </p>
          <section
            aria-label="Barangay allocations"
            className="workflow-panel space-y-4"
          >
            <h2>Barangay allocations</h2>
            {data.allocations.length === 0 ? (
              <p>No allocations are recorded for this batch.</p>
            ) : (
              <ol className="allocation-list">
                {data.allocations.map((allocation) => (
                  <li
                    className="workflow-record"
                    key={allocation.allocation_id}
                  >
                    <div className="workflow-section-heading">
                      <h3>{allocation.barangay_name}</h3>
                      <p className="workflow-amount-small">
                        {formatPeso(allocation.amount)}
                      </p>
                    </div>
                    <p>
                      {allocation.beneficiary_count} planned households ·{" "}
                      {allocation.status === "ALLOCATED"
                        ? "Allocated"
                        : allocation.status}
                    </p>
                    <details className="registry-detail">
                      <summary>Allocation references</summary>
                      <dl className="receipt-references">
                        <dt>Allocation ID</dt>
                        <dd>{allocation.allocation_id}</dd>
                        <dt>Stored transaction</dt>
                        <dd className="font-mono">
                          {allocation.blockchain_tx_hash || "None recorded"}
                        </dd>
                      </dl>
                    </details>
                  </li>
                ))}
              </ol>
            )}
          </section>
          <details className="workflow-panel">
            <summary className="font-semibold">
              Batch details and references
            </summary>
            <dl className="receipt-references mt-3">
              <dt>Source agency</dt>
              <dd>{data.batch.source_agency}</dd>
              <dt>Recipient LGU</dt>
              <dd>{data.batch.recipient_lgu}</dd>
              <dt>Purpose</dt>
              <dd>{data.batch.purpose}</dd>
              <dt>Standard grant</dt>
              <dd>{formatPeso(data.batch.standard_grant)}</dd>
              <dt>Maximum grant</dt>
              <dd>{formatPeso(data.batch.max_grant)}</dd>
              <dt>Stored transaction</dt>
              <dd className="font-mono">
                {data.batch.blockchain_tx_hash || "None recorded"}
              </dd>
            </dl>
            <p className="registry-muted mt-3">
              Stored transaction references do not establish current blockchain
              evidence. This page does not verify the funding transaction.
            </p>
          </details>
          <section
            aria-label="Batch activity"
            className="workflow-panel space-y-4"
          >
            <h2>Batch activity</h2>
            {data.timeline.length === 0 && (
              <p>No activity is available to this view.</p>
            )}
            <ol className="workflow-records">
              {data.timeline.map((event) => (
                <li className="workflow-record" key={event.id}>
                  <p>{event.description}</p>
                  <p className="registry-muted">
                    {formatRecordedDate(event.timestamp)}
                  </p>
                  <details className="registry-detail">
                    <summary>Event references</summary>
                    <dl className="receipt-references">
                      <dt>Event type</dt>
                      <dd>{event.event_type}</dd>
                      <dt>Stored transaction</dt>
                      <dd className="font-mono">
                        {event.blockchain_tx_hash || "None recorded"}
                      </dd>
                    </dl>
                  </details>
                </li>
              ))}
            </ol>
          </section>
        </>
      )}
    </div>
  );
}
