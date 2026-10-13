"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export type UserRole = "Public Citizen" | "Barangay Officer" | "Auditor / COA";

interface RoleContextType {
  role: UserRole;
  setRole: (role: UserRole) => void;
}

const RoleContext = createContext<RoleContextType>({
  role: "Public Citizen",
  setRole: () => {},
});

export function RoleProvider({ children }: { children: React.ReactNode }) {
  const [role, setRoleState] = useState<UserRole>("Public Citizen");

  useEffect(() => {
    const saved = localStorage.getItem("ayudachain_role") as UserRole;
    if (saved && ["Public Citizen", "Barangay Officer", "Auditor / COA"].includes(saved)) {
      setRoleState(saved);
    }
  }, []);

  const setRole = (newRole: UserRole) => {
    setRoleState(newRole);
    localStorage.setItem("ayudachain_role", newRole);
  };

  return (
    <RoleContext.Provider value={{ role, setRole }}>
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  return useContext(RoleContext);
}
