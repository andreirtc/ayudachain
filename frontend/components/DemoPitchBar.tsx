import Link from "next/link";

const steps = [
  { label: "Funds and allocations", href: "/batch/RELIEF-2026-001" },
  { label: "Household review", href: "/beneficiaries" },
  { label: "Record a payout", href: "/distributions" },
  { label: "Check a receipt", href: "/verify" },
];

export default function DemoPitchBar() {
  return <details className="bg-white border-b border-slate-200 px-4 py-3">
    <summary className="max-w-7xl mx-auto cursor-pointer text-sm font-semibold text-slate-700">Follow an example household</summary>
    <nav aria-label="Example relief journey" className="max-w-7xl mx-auto mt-2">
      <ol className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-700">
        {steps.map((step, index) => <li key={step.href}><Link href={step.href} className="inline-flex items-center gap-2 min-h-11 rounded px-1 hover:text-blue-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"><span className="text-xs text-slate-500" aria-hidden="true">{index + 1}.</span>{step.label}</Link></li>)}
      </ol>
    </nav>
  </details>;
}
