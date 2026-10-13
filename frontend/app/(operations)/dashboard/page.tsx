"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { fetchDashboard, DashboardStats, formatPeso } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";
import { useRole } from "@/lib/roleContext";

export default function DashboardPage() {
  const { account } = useRole();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const version = useRef(0);
  const loadData = async () => {
    const request = ++version.current;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDashboard();
      if (request === version.current) setStats(data);
    } catch (err) {
      if (request === version.current)
        setError(
          err instanceof Error
            ? err.message
            : "Relief summary could not be loaded.",
        );
    } finally {
      if (request === version.current) setLoading(false);
    }
  };
  useEffect(() => {
    void loadData();
    return () => {
      version.current++;
    };
  }, [account?.id]);
  return (
    <div className="registry workflow space-y-6">
      <header className="registry-header">
        <div>
          <h1>Relief overview</h1>
          <p className="registry-description">
            {stats?.calamity_name ||
              "Recorded funding, household status and synthetic payouts."}
          </p>
        </div>
        <button
          className="registry-button"
          disabled={loading}
          onClick={() => void loadData()}
        >
          Refresh overview
        </button>
      </header>
      {loading && <p role="status">Loading relief summary...</p>}
      {error && (
        <div role="alert" className="registry-error">
          <h2>Overview refresh unavailable</h2>
          <p>
            {error}
            {stats
              ? " Totals below are from the previous successful read."
              : " Try again to load the summary."}
          </p>
          <button
            className="registry-button"
            disabled={loading}
            onClick={() => void loadData()}
          >
            Retry overview
          </button>
        </div>
      )}
      {stats && (
        <>
          <section aria-label="Recorded funding" className="overview-metrics">
            {[
              ["Released funds", stats.total_released],
              ["Allocated funds", stats.total_allocated],
              ["Recorded payouts", stats.total_distributed],
              ["Unallocated funds", stats.unallocated_funds],
            ].map(([label, amount]) => (
              <div className="overview-metric" key={String(label)}>
                <h2>{label}</h2>
                <p>{formatPeso(Number(amount))}</p>
              </div>
            ))}
          </section>
          <section
            className="workflow-context"
            aria-label="Household and payout counts"
          >
            <p>
              {stats.total_beneficiaries} active households ·{" "}
              {stats.verified_beneficiaries} approved · {stats.flagged_records}{" "}
              with review flags
            </p>
            <p>
              {stats.confirmed_distributions} recorded payouts. This count is
              not a count of verified receipt hashes.
            </p>
            {stats.historical_beneficiaries > 0 && (
              <p>
                {stats.historical_beneficiaries} historical duplicates retained.
              </p>
            )}
          </section>
          <div className="flex flex-wrap gap-3">
            <Link
              href={"/batch/" + stats.batch_id}
              className="registry-button registry-primary"
            >
              View batch details
            </Link>
            <Link href="/verify" className="registry-button">
              Check a receipt
            </Link>
          </div>
          <section
            aria-label="Recent activity"
            className="workflow-panel space-y-4"
          >
            <h2>Recent activity</h2>
            <p className="registry-muted">
              {account?.role === "DSWD" || account?.role === "AUDITOR"
                ? "Events available to your office account."
                : "Public activity shows funding and allocations."}
            </p>
            {stats.recent_transactions.length === 0 && (
              <p>No recent activity is available.</p>
            )}
            <ol className="workflow-records">
              {stats.recent_transactions.map((event, index) => (
                <li className="workflow-record" key={index}>
                  <p>{event.description}</p>
                  <p className="registry-muted">
                    {formatRecordedDate(event.timestamp)}
                  </p>
                  {typeof event.amount === "number" && Number.isFinite(event.amount) && (
                    <p className="font-semibold">{formatPeso(event.amount)}</p>
                  )}
                  <details className="registry-detail">
                    <summary>Event references</summary>
                    <dl className="receipt-references">
                      <dt>Event type</dt>
                      <dd>{event.event_type}</dd>
                      <dt>Stored transaction</dt>
                      <dd className="font-mono">
                        {event.tx_hash || "None recorded"}
                      </dd>
                    </dl>
                  </details>
                </li>
              ))}
            </ol>
          </section>
          <details className="workflow-panel">
            <summary className="font-semibold">
              Blockchain service details
            </summary>
            <div className="space-y-3 mt-3">
              <p>
                {error
                  ? "The latest service refresh failed."
                  : stats.blockchain_status === "CONNECTED"
                    ? "The backend reported a connection at the last refresh."
                    : "The backend could not reach the configured blockchain at the last refresh."}
              </p>
              <p className="registry-muted">
                Connection status and stored transaction references do not
                verify individual receipts.
              </p>
              <dl className="receipt-references">
                <dt>Network</dt>
                <dd>{stats.active_network || "Not reported"}</dd>
                <dt>Contract</dt>
                <dd className="font-mono">
                  {stats.contract_address || "Not reported"}
                </dd>
              </dl>
            </div>
          </details>
        </>
      )}
    </div>
  );
}
