"use client";

import React, { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AlertTriangle, CheckCircle2, RefreshCw, ShieldCheck } from "lucide-react";
import { verifyBlockchain, VerifyResponse, fetchDistributions, fetchBeneficiaries, Distribution, Beneficiary, formatPeso } from "@/lib/api";

const outcomes = {
  VERIFIED: { title: "Receipt hash verified", style: "bg-emerald-50 border-emerald-300 text-emerald-950" },
  MISMATCH: { title: "Receipt hash mismatch", style: "bg-rose-50 border-rose-300 text-rose-950" },
  UNANCHORED: { title: "No receipt anchor found", style: "bg-amber-50 border-amber-300 text-amber-950" },
  UNAVAILABLE: { title: "Verification unavailable", style: "bg-slate-50 border-slate-300 text-slate-900" },
};

function VerifyContent() {
  const searchParams = useSearchParams();
  const initialId = searchParams?.get("distribution_id") || "DIST-0001";
  const [distributions, setDistributions] = useState<Distribution[]>([]);
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [loadingRecords, setLoadingRecords] = useState(true);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);
  const [recheck, setRecheck] = useState(0);
  const requestVersion = useRef(0);

  useEffect(() => {
    let cancelled = false;
    setLoadingRecords(true);
    setError(null);
    Promise.all([fetchDistributions(), fetchBeneficiaries({ include_historical: true })])
      .then(([records, households]) => {
        if (cancelled) return;
        setDistributions(records);
        setBeneficiaries(households);
        setSelectedId(records.some((record) => record.distribution_id === initialId) ? initialId : records[0]?.distribution_id || "");
      })
      .catch((err) => { if (!cancelled) setError(err instanceof Error ? err.message : String(err)); })
      .finally(() => { if (!cancelled) setLoadingRecords(false); });
    return () => { cancelled = true; };
  }, [initialId, reload]);

  useEffect(() => {
    if (!selectedId) return;
    const version = ++requestVersion.current;
    let cancelled = false;
    setChecking(true);
    setResult(null);
    setError(null);
    verifyBlockchain(selectedId)
      .then((data) => { if (!cancelled && version === requestVersion.current) setResult(data); })
      .catch((err) => { if (!cancelled && version === requestVersion.current) setError(err instanceof Error ? err.message : String(err)); })
      .finally(() => { if (!cancelled && version === requestVersion.current) setChecking(false); });
    return () => { cancelled = true; };
  }, [selectedId, recheck]);

  const activeDist = distributions.find((record) => record.distribution_id === selectedId);
  const activeBen = beneficiaries.find((household) => household.beneficiary_id === activeDist?.beneficiary_id);
  const currentResult = result?.record_id === selectedId ? result : null;
  const outcome = currentResult ? outcomes[currentResult.verification_status] : null;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2"><ShieldCheck className="w-6 h-6 text-blue-600" />Verify a receipt</h1>
        <p className="text-sm text-slate-600">Compare a synthetic payout receipt hash with its anchor on the configured blockchain.</p>
        <p className="text-xs text-slate-500">This check covers the recorded receipt hash. It cannot prove physical cash delivery or household-name integrity.</p>
      </div>

      <section className="bg-white border border-slate-200 rounded-2xl p-5 sm:p-6 space-y-4">
        {loadingRecords ? <p role="status" className="text-sm text-slate-500">Loading receipts...</p> : distributions.length === 0 && !error ? <p className="text-sm text-slate-600">No payout receipts are recorded yet.</p> : (
          <div className="flex flex-col sm:flex-row gap-3 sm:items-end">
            <div className="flex-1">
              <label htmlFor="receipt-record" className="block text-sm font-semibold text-slate-700 mb-1">Receipt</label>
              <select id="receipt-record" value={selectedId} disabled={loadingRecords || distributions.length === 0} onChange={(event) => { setResult(null); setSelectedId(event.target.value); }} className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500">
                {distributions.map((record) => <option key={record.distribution_id} value={record.distribution_id}>{record.distribution_id}: {record.beneficiary_id} ({formatPeso(record.amount)})</option>)}
              </select>
            </div>
            <button onClick={() => setRecheck((value) => value + 1)} disabled={checking || !selectedId || loadingRecords} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
              <RefreshCw className={checking ? "w-4 h-4 animate-spin" : "w-4 h-4"} />Check again
            </button>
          </div>
        )}
        {error && <div role="alert" className="text-sm text-rose-700">{error} <button onClick={() => { setReload((value) => value + 1); setRecheck((value) => value + 1); }} className="underline">Retry</button></div>}
        {checking && <p role="status" className="text-sm text-slate-600">Reading the blockchain receipt...</p>}
        {activeDist && <div className="p-3 bg-slate-50 rounded-lg text-sm text-slate-700 space-y-1">
          <p className="text-xs font-semibold uppercase text-slate-500">Recorded locally</p>
          <p>{activeBen?.household_name || activeDist.beneficiary_id}</p>
          <p>{formatPeso(activeDist.amount)} · {activeDist.batch_id}</p>
        </div>}

        {currentResult && outcome && <div role="status" className={"p-5 border rounded-xl space-y-3 " + outcome.style}>
          <h2 className="text-lg font-bold flex items-center gap-2">{currentResult.verification_status === "VERIFIED" ? <CheckCircle2 className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}{outcome.title}</h2>
          <p className="text-sm">{currentResult.status_message}</p>
          <p className="text-xs">Network: {currentResult.network}</p>
          {currentResult.timestamp && <p className="text-xs">Anchor timestamp: {new Date(currentResult.timestamp * 1000).toLocaleString()}</p>}
          <details className="pt-2 border-t border-slate-200">
            <summary className="cursor-pointer text-sm font-semibold">Receipt hashes and contract</summary>
            <dl className="mt-3 text-xs space-y-3">
              <div><dt className="font-semibold">Locally calculated hash</dt><dd className="font-mono break-all mt-1">{currentResult.receipt_hash_local}</dd></div>
              <div><dt className="font-semibold">Hash read from blockchain</dt><dd className="font-mono break-all mt-1">{currentResult.receipt_hash_onchain || "No hash available for this lookup"}</dd></div>
              <div><dt className="font-semibold">Configured contract</dt><dd className="font-mono break-all mt-1">{currentResult.contract_address || "No contract configured"}</dd></div>
            </dl>
          </details>
        </div>}
      </section>
    </div>
  );
}

export default function VerifyPage() {
  return <Suspense fallback={<p className="py-12 text-center text-slate-500">Loading verification...</p>}><VerifyContent /></Suspense>;
}
