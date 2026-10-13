"use client";

import Link from "next/link";
import BrandMark from "@/components/BrandMark";
import RoleIndicatorBanner from "@/components/RoleIndicatorBanner";
import { useRole } from "@/lib/roleContext";
import { workspaceHome } from "@/lib/workspaceHome";

export default function LandingHeader() {
  const { account } = useRole();
  return <header className="landing-header landing-width">
    <Link href={workspaceHome(account?.role)} className="landing-brand" aria-label="AyudaChain home"><BrandMark /><span>AyudaChain</span></Link>
    <nav aria-label="Page navigation"><a href="#how-it-works">How it works</a><Link href="/verify">Check a receipt</Link>{account && <Link href={workspaceHome(account.role)}>My workspace</Link>}</nav>
    <RoleIndicatorBanner />
  </header>;
}
