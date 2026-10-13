"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { useRole } from "@/lib/roleContext";
import { AccountRole } from "@/lib/api";
import { useSignInHref } from "@/lib/useSignInHref";
import ThemeToggle from "@/components/ThemeToggle";
import { Home, Users, HandCoins, Receipt, LogIn, MessageSquare, ClipboardList } from "lucide-react";

const icons = { overview: Home, households: Users, payouts: HandCoins, receipts: Receipt, signIn: LogIn, concerns: MessageSquare, audit: ClipboardList };

const destinations = {
  overview: { name: "Overview", href: "/dashboard" },
  households: { name: "Households", href: "/beneficiaries" },
  payouts: { name: "Payouts", href: "/distributions" },
  receipts: { name: "Check a receipt", href: "/verify" },
  audit: { name: "Audit", href: "/audit" },
  concerns: { name: "Concerns", href: "/concerns" },
  signIn: { name: "Sign in", href: "/sign-in" },
};
const roleLinks: Record<AccountRole, (keyof typeof destinations)[]> = {
  DSWD: ["households", "concerns", "audit", "payouts"],
  BARANGAY: ["households", "concerns", "overview", "receipts"],
  DISBURSING: ["payouts", "households", "concerns", "receipts"],
  BENEFICIARY: ["households", "concerns", "payouts", "receipts"],
  AUDITOR: ["audit", "households", "payouts", "receipts"],
};

export default function Navbar() {
  const pathname = usePathname();
  const signIn = useSignInHref();
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
    Icon: icons[key],
    ...destinations[key],
    href: key === "signIn" ? signIn : key === "households" && account?.role === "BENEFICIARY" ? "/household" : destinations[key].href,
    name:
      account?.role === "BENEFICIARY" && key === "households"
        ? "My household"
        : account?.role === "BENEFICIARY" && key === "payouts"
          ? "My payouts"
          : destinations[key].name,
  }));
  const navigation = (isMobile: boolean) =>
    links.map(({ name, href, Icon }) => (
      <Link
        key={href}
        href={href}
        aria-current={
          pathname === href.split("?")[0] ||
          (href === "/household" && pathname === "/beneficiaries") ||
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
        <Icon size={20} aria-hidden="true" /><span>{name}</span>
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
        <ThemeToggle />
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
