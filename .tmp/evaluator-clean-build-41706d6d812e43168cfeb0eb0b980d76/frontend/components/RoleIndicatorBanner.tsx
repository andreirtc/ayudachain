"use client";

import React from "react";
import { useRole } from "@/lib/roleContext";
import { Eye, ShieldAlert, Wrench, Info } from "lucide-react";

export default function RoleIndicatorBanner() {
  const { role, setRole } = useRole();

  if (role === "Public Citizen") {
    return (
      <div className="bg-blue-50 border-b border-blue-200 px-4 py-2.5 text-xs text-blue-900 flex items-center justify-between">
        <div className="max-w-7xl mx-auto w-full flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-blue-600 shrink-0" />
            <div>
              <span className="font-bold">Modo ng Karaniwang Mamamayan (Public Citizen):</span>{" "}
              <span className="text-slate-700">
                Pampublikong silip kung magkano ang pondong inilabas ng gobyerno sa inyong barangay at i-check kung buo ang perang dapat mong matanggap.
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-slate-500 text-[11px] shrink-0 self-end sm:self-auto">
            <span>Para sa taga-barangay?</span>
            <button
              onClick={() => setRole("Barangay Officer")}
              className="text-blue-700 font-bold underline hover:text-blue-900 cursor-pointer"
            >
              Lumipat sa Barangay Officer Mode →
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (role === "Barangay Officer") {
    return (
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-2.5 text-xs text-amber-950">
        <div className="max-w-7xl mx-auto w-full flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Wrench className="w-4 h-4 text-amber-600 shrink-0" />
            <div>
              <span className="font-bold">Modo ng Kawani ng Barangay (Field Payout Mode):</span>{" "}
              <span className="text-slate-700">
                Para sa mga opisyal at health workers sa evacuation center — i-scan ang DAFAC QR voucher, iabot ang ₱5,000 ayuda, at i-selyo ang resibo.
              </span>
            </div>
          </div>
          <button
            onClick={() => setRole("Auditor / COA")}
            className="text-amber-800 font-bold underline hover:text-amber-950 text-[11px] shrink-0 cursor-pointer"
          >
            Tingnan ang Auditor / COA Mode →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-purple-50 border-b border-purple-200 px-4 py-2.5 text-xs text-purple-950">
      <div className="max-w-7xl mx-auto w-full flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-purple-700 shrink-0" />
          <div>
            <span className="font-bold">Modo ng Tagasuri (COA / Ombudsman Auditor Mode):</span>{" "}
            <span className="text-slate-700">
              Pagsusuri sa mga dobleng benepisyaryo, multong claims, at live simulation ng pagkahuli sa pangungupit ng pondo.
            </span>
          </div>
        </div>
        <button
          onClick={() => setRole("Public Citizen")}
          className="text-purple-800 font-bold underline hover:text-purple-950 text-[11px] shrink-0 cursor-pointer"
        >
          Bumalik sa Public Citizen →
        </button>
      </div>
    </div>
  );
}
