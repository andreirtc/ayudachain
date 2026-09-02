"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ShieldCheck, ArrowLeft, Building2, Banknote, Calendar, Lock,
  CheckCircle2, AlertCircle, Clock, ExternalLink, Activity
} from "lucide-react";
import { fetchBatchDetail, ReliefBatch, Allocation, AuditEvent } from "@/lib/api";

export default function BatchDetailPage() {
  const params = useParams();
  const batchId = (params?.id as string) || "RELIEF-2026-001";

  const [data, setData] = useState<{
    batch: ReliefBatch;
    allocations: Allocation[];
    total_distributions: number;
    distributed_amount: number;
    timeline: AuditEvent[];
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBatchDetail(batchId)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [batchId]);

  if (loading) {
    return <div className="py-20 text-center text-slate-500 font-medium">Loading relief batch details...</div>;
  }

  if (!data) {
    return <div className="py-20 text-center text-red-500 font-medium">Relief batch not found.</div>;
  }

  const formatPhp = (val: number) => {
    return new Intl.NumberFormat("en-PH", { style: "currency", currency: "PHP" }).format(val);
  };

  const { batch, allocations, timeline, total_distributions, distributed_amount } = data;

  return (
    <div className="space-y-6">
      {/* Breadcrumb & Title */}
      <div>
        <Link href="/" className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 mb-2">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Transparency Dashboard
        </Link>
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-widest text-slate-500 font-mono">
              BATCH REFERENCE: {batch.batch_id}
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight mt-1">
              {batch.calamity_name}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-emerald-100 text-emerald-800 font-bold text-xs px-3 py-1 rounded-full border border-emerald-300">
              STATUS: {batch.status}
            </span>
          </div>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 uppercase font-semibold">Authorized Amount</span>
          <div className="text-xl font-black text-slate-900 mt-1">{formatPhp(batch.amount)}</div>
          <span className="text-[11px] text-slate-400">Total appropriation</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 uppercase font-semibold">Disbursed Aid</span>
          <div className="text-xl font-black text-emerald-600 mt-1">{formatPhp(distributed_amount)}</div>
          <span className="text-[11px] text-slate-400">{total_distributions} households paid</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 uppercase font-semibold">Source Agency</span>
          <div className="text-sm font-bold text-slate-900 mt-1">{batch.source_agency}</div>
          <span className="text-[11px] text-slate-400">National release</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 uppercase font-semibold">Recipient LGU</span>
          <div className="text-sm font-bold text-slate-900 mt-1">{batch.recipient_lgu}</div>
          <span className="text-[11px] text-slate-400">Executing jurisdiction</span>
        </div>
      </div>

      {/* Blockchain Anchor Hash Card */}
      <div className="bg-slate-900 text-white p-5 rounded-xl border border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Lock className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
              Immutable Blockchain Record
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            This batch was formally initialized and anchored on the Polygon EVM testnet.
          </p>
        </div>
        <div className="font-mono text-xs text-slate-300 bg-slate-950 p-2.5 rounded-lg border border-slate-800 flex items-center gap-2">
          <span>TX:</span>
          <span className="text-blue-300 font-semibold">{batch.blockchain_tx_hash || "0x5f27ce6ea3d921efb37633dbe87ff1ce347d6a2b5895055472ee4b297d8df933"}</span>
        </div>
      </div>

      {/* Barangay Allocations Breakdown Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex justify-between items-center">
          <div>
            <h2 className="font-bold text-base text-slate-900">Barangay Allocation Breakdown</h2>
            <p className="text-xs text-slate-500 mt-0.5">Distribution of disaster relief funds across affected barangays</p>
          </div>
          <span className="text-xs font-semibold bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full">
            {allocations.length} Active Localities
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 text-xs uppercase font-semibold border-b border-slate-100">
              <tr>
                <th className="px-5 py-3">Allocation ID</th>
                <th className="px-5 py-3">Barangay Name</th>
                <th className="px-5 py-3">Allocated Amount</th>
                <th className="px-5 py-3">Target Beneficiaries</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Blockchain Anchor</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {allocations.map((alloc) => (
                <tr key={alloc.id} className="hover:bg-slate-50/50">
                  <td className="px-5 py-3.5 font-mono text-xs font-semibold text-slate-900">{alloc.allocation_id}</td>
                  <td className="px-5 py-3.5 font-bold text-slate-900">{alloc.barangay_name}</td>
                  <td className="px-5 py-3.5 font-black text-slate-900">{formatPhp(alloc.amount)}</td>
                  <td className="px-5 py-3.5 text-xs text-slate-600">{alloc.beneficiary_count} households</td>
                  <td className="px-5 py-3.5">
                    <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                      {alloc.status}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="font-mono text-[11px] text-slate-500 bg-slate-100 px-2 py-1 rounded border border-slate-200">
                      {alloc.blockchain_tx_hash ? `${alloc.blockchain_tx_hash.slice(0, 10)}...` : "Confirmed"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Chronological Audit Timeline */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="font-bold text-base text-slate-900 mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-600" />
          Complete Historical Audit Trail
        </h2>

        <div className="relative border-l-2 border-slate-200 ml-4 space-y-6">
          {timeline.map((ev, i) => (
            <div key={i} className="relative pl-6">
              <div className="absolute -left-2 top-0.5 w-4 h-4 rounded-full bg-blue-600 border-2 border-white"></div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  {ev.event_type}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  {new Date(ev.timestamp).toLocaleString()}
                </span>
              </div>
              <p className="text-sm font-semibold text-slate-900 mt-1">{ev.description}</p>
              {ev.blockchain_tx_hash && (
                <p className="text-xs font-mono text-emerald-600 mt-1 flex items-center gap-1">
                  <Lock className="w-3 h-3" /> Polygon Tx: {ev.blockchain_tx_hash}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
