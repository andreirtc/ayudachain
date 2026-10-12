import { PayoutAnchor } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";

const errors: Record<string, string> = {
  RPC_UNAVAILABLE:
    "The blockchain could not be reached. Retry when it is available.",
  BROADCAST_UNCERTAIN:
    "The send response was lost. Recovery checks the same transaction.",
  CHAIN_CHANGED: "The connected chain has changed. Recovery is paused.",
  DEPLOYMENT_CHANGED:
    "The saved deployment no longer matches. Recovery is paused.",
  RECORD_CHANGED:
    "Recorded payout details have changed. They need investigation before anchoring.",
  ENVELOPE_CHANGED:
    "Saved transaction details do not match the payout. Recovery is paused.",
  NONCE_CONFLICT:
    "Another transaction used the saved nonce. Recovery needs investigation.",
  TRANSACTION_REVERTED:
    "The transaction reverted. A replacement requires a separate review.",
  ANCHOR_CONFLICT:
    "Observed chain evidence does not match the saved transaction and payout.",
};

export default function PayoutAnchorStatus({
  anchor,
  onRecover,
  busy,
  error,
}: {
  anchor?: PayoutAnchor | null;
  onRecover?: () => void;
  busy?: boolean;
  error?: string;
}) {
  const label = !anchor
    ? "Anchor not tracked"
    : {
        PENDING: "Anchor pending",
        SUBMITTED: "Anchor confirmation pending",
        CONFIRMED: "Anchor confirmed",
        FAILED: "Anchoring needs attention",
      }[anchor.state];
  const description = !anchor
    ? "Historical records have no recovery job. Use the receipt check."
    : anchor.error_code
      ? errors[anchor.error_code] ||
        "Recovery could not be completed. The payout remains saved."
      : {
          PENDING: "The payout is saved. No transaction has been prepared yet.",
          SUBMITTED:
            "A transaction is prepared or awaiting confirmation. Recovery uses the same transaction.",
          CONFIRMED:
            "A mined transaction was observed. The receipt check shows its current integrity.",
          FAILED:
            "The payout remains saved. Retry anchoring when the issue is resolved.",
        }[anchor.state];
  return (
    <div className="space-y-2 text-xs text-slate-700">
      <p className="font-semibold text-slate-900">{label}</p>
      <p>{description}</p>
      {anchor && onRecover && (
        <button
          type="button"
          disabled={busy}
          onClick={onRecover}
          className="min-h-11 px-3 py-2 rounded-lg border border-blue-300 text-blue-800 font-semibold disabled:opacity-50"
        >
          {busy
            ? "Checking anchor..."
            : anchor.state === "CONFIRMED"
              ? "Recheck anchor"
              : "Recover anchor"}
        </button>
      )}
      {error && (
        <p role="alert" className="text-rose-700">
          {error}
        </p>
      )}
      {anchor && (
        <details>
          <summary className="cursor-pointer py-1">Anchor details</summary>
          <dl className="space-y-1 break-all mt-1">
            <div>
              <dt>Prepared transaction</dt>
              <dd className="font-mono">
                {anchor.candidate_tx_hash || "None prepared"}
              </dd>
            </div>
            <div>
              <dt>Observed block</dt>
              <dd>{anchor.block_number ?? "None confirmed"}</dd>
            </div>
            <div>
              <dt>Last check</dt>
              <dd>{formatRecordedDate(anchor.updated_at)}</dd>
            </div>
          </dl>
        </details>
      )}
    </div>
  );
}
