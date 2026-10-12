"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { useRole, UserRole } from "@/lib/roleContext";

const views = {
  "Public Citizen": { title: "Citizen demo view", copy: "Follow the recorded aid and check a receipt.", action: "Check a receipt", href: "/verify" },
  "Barangay Officer": { title: "Staff demo view", copy: "Review a household before recording its synthetic payout.", action: "Review households", href: "/beneficiaries" },
  "Auditor / COA": { title: "Auditor demo view", copy: "Inspect review history and compare receipt evidence.", action: "Inspect receipt integrity", href: "/verify" },
};

export default function RoleIndicatorBanner() {
  const { role, setRole } = useRole();
  const view = views[role];
  return <section aria-label="Demo view" className="bg-blue-50 border-b border-blue-200 px-4 py-4 text-sm text-slate-700">
    <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div><h2 className="font-semibold text-slate-900">{view.title}</h2><p>{view.copy}</p><p className="text-xs text-slate-600 mt-1">Views are selected without sign-in. Permissions are not authenticated.</p></div>
      <div className="flex flex-wrap items-center gap-3">
        <label htmlFor="demo-view" className="font-medium">Demo view</label>
        <select id="demo-view" value={role} onChange={event => setRole(event.target.value as UserRole)} className="min-h-11 px-3 py-2 bg-white border border-slate-300 rounded-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">
          <option value="Public Citizen">Citizen</option><option value="Barangay Officer">Staff</option><option value="Auditor / COA">Auditor</option>
        </select>
        <Link href={view.href} className="inline-flex items-center gap-2 min-h-11 font-semibold text-blue-800 underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">{view.action}<ArrowRight className="w-4 h-4" aria-hidden="true" /></Link>
      </div>
    </div>
  </section>;
}
