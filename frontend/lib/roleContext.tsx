"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { DemoAccount, fetchSession, clearSession, signOut } from "./api";

export type UserRole = "PUBLIC" | DemoAccount["role"];
const RoleContext = createContext<{ role: UserRole; account: DemoAccount | null; loading: boolean; error: string | null; refresh: () => Promise<void>; logout: () => Promise<void> }>({ role: "PUBLIC", account: null, loading: true, error: null, refresh: async () => {}, logout: async () => {} });

export function RoleProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<DemoAccount | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  async function refresh() { setLoading(true); setError(null); try { setAccount(await fetchSession()); } catch (e) { setAccount(null); clearSession(); setError(e instanceof Error ? e.message : "Session unavailable"); } finally { setLoading(false); } }
  async function logout() { await signOut(); setAccount(null); }
  useEffect(() => {
    void refresh();
    const expire = () => { setAccount(null); clearSession(); };
    window.addEventListener("ayudachain-session-expired", expire);
    return () => window.removeEventListener("ayudachain-session-expired", expire);
  }, []);
  return <RoleContext.Provider value={{ role: account?.role || "PUBLIC", account, loading, error, refresh, logout }}>{children}</RoleContext.Provider>;
}
export function useRole() { return useContext(RoleContext); }
