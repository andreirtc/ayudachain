"use client";

import Link from "next/link";
import { useState } from "react";
import { usePathname } from "next/navigation";
import { useRole } from "@/lib/roleContext";
import { useSignInHref } from "@/lib/useSignInHref";

const labels = {
  DSWD: "DSWD Officer",
  BARANGAY: "Barangay Officer",
  DISBURSING: "Disbursing Officer",
  BENEFICIARY: "Beneficiary",
  AUDITOR: "Auditor",
};
const actions = {
  DSWD: ["Review households", "/beneficiaries"],
  BARANGAY: ["Open barangay households", "/beneficiaries"],
  DISBURSING: ["Record a payout", "/distributions"],
  BENEFICIARY: ["My household", "/beneficiaries"],
  AUDITOR: ["Inspect records", "/beneficiaries"],
};
export default function RoleIndicatorBanner() {
  const pathname = usePathname();
  const signIn = useSignInHref();
  const { account, loading, logout } = useRole();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function leave() {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      await logout();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sign-out failed");
    } finally {
      setBusy(false);
    }
  }
  return (
    <section aria-label="Account" className="app-account">
      <div className="app-account-row">
        <div className="app-account-context">
          <p className="font-semibold">
            {loading
              ? "Checking session..."
              : account
                ? labels[account.role] + " · " + account.display_name
                : "Public view"}
          </p>
          <p className="text-xs mt-1">
            {account
              ? "Authenticated synthetic account."
              : "Funding summaries and limited receipt checks are public."}
          </p>
          {error && (
            <p role="alert" className="text-rose-700">
              {error}
            </p>
          )}
        </div>
        {account ? (
          <div className="flex flex-wrap gap-3">
            {pathname !== actions[account.role][1] && (
              <Link
                href={actions[account.role][1]}
                className="min-h-11 inline-flex items-center text-blue-800 underline font-semibold"
              >
                {actions[account.role][0]}
              </Link>
            )}
            <button
              disabled={busy}
              onClick={() => void leave()}
              className="min-h-11 px-3 border border-slate-300 bg-white rounded-lg disabled:opacity-50"
            >
              {busy ? "Signing out..." : "Sign out"}
            </button>
          </div>
        ) : (
          pathname !== "/sign-in" && (
            <Link
              href={signIn}
              className="min-h-11 inline-flex items-center text-blue-800 underline font-semibold"
            >
              Sign in
            </Link>
          )
        )}
      </div>
    </section>
  );
}
