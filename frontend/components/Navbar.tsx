"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { useRole } from "@/lib/roleContext";
import { AccountRole } from "@/lib/api";

const destinations = {
  overview: { name: "Overview", href: "/dashboard" },
  households: { name: "Households", href: "/beneficiaries" },
  payouts: { name: "Payouts", href: "/distributions" },
  receipts: { name: "Check a receipt", href: "/verify" },
  signIn: { name: "Sign in", href: "/sign-in" },
};
const roleLinks: Record<AccountRole, (keyof typeof destinations)[]> = {
  DSWD: ["households", "overview", "payouts", "receipts"],
  BARANGAY: ["households", "overview", "receipts"],
  DISBURSING: ["payouts", "households", "overview", "receipts"],
  BENEFICIARY: ["households", "payouts", "receipts"],
  AUDITOR: ["overview", "households", "payouts", "receipts"],
};

export default function Navbar() {
  const pathname = usePathname();
  const { account } = useRole();
  const mobile = useRef<HTMLDetailsElement>(null);
  const focusMain = useRef(false);
  useEffect(() => {
    if (mobile.current) mobile.current.open = false;
    if (focusMain.current) {
      document.getElementById("main-content")?.focus();
      focusMain.current = false;
    }
  }, [pathname, account?.id]);
  const links = (
    account
      ? roleLinks[account.role]
      : (["overview", "receipts", "signIn"] as (keyof typeof destinations)[])
  ).map((key) => ({
    ...destinations[key],
    name:
      account?.role === "BENEFICIARY" && key === "households"
        ? "My household"
        : account?.role === "BENEFICIARY" && key === "payouts"
          ? "My payouts"
          : destinations[key].name,
  }));
  const navigation = (isMobile: boolean) =>
    links.map(({ name, href }) => (
      <Link
        key={href}
        href={href}
        aria-current={
          pathname === href ||
          (href === "/dashboard" && pathname.startsWith("/batch/"))
            ? "page"
            : undefined
        }
        onClick={() => {
          if (!isMobile) return;
          if (mobile.current) mobile.current.open = false;
          if (pathname === href)
            document.getElementById("main-content")?.focus();
          else focusMain.current = true;
        }}
      >
        {name}
      </Link>
    ));
  return (
    <header className="app-shell">
      <a href="#main-content" className="app-skip-link">
        Skip to content
      </a>
      <div className="app-shell-row">
        <Link href="/" className="app-brand">
          <img src="/logo-emblem.png" alt="" width={36} height={36} />
          <span className="app-brand-text"><span className="app-wordmark">AyudaChain</span><span className="app-demo-tag">Synthetic demo</span></span>
        </Link>
        <nav aria-label="Main navigation" className="app-desktop-nav">
          {navigation(false)}
        </nav>
        <details
          ref={mobile}
          className="app-mobile-nav"
          onKeyDown={(event) => {
            if (event.key === "Escape") {
              event.preventDefault();
              if (mobile.current) mobile.current.open = false;
              mobile.current?.querySelector("summary")?.focus();
            }
          }}
          onBlur={(event) => {
            if (
              !event.currentTarget.contains(event.relatedTarget as Node | null)
            )
              event.currentTarget.open = false;
          }}
        >
          <summary>Menu</summary>
          <nav aria-label="Mobile navigation">{navigation(true)}</nav>
        </details>
      </div>
    </header>
  );
}
