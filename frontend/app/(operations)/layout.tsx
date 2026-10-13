import Navbar from "@/components/Navbar";
import DemoPitchBar from "@/components/DemoPitchBar";
import RoleIndicatorBanner from "@/components/RoleIndicatorBanner";
import { RoleProvider } from "@/lib/roleContext";
import SessionGate from "@/components/SessionGate";
import { Suspense } from "react";

export default function OperationsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="operations min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <Suspense fallback={<p role="status" className="p-6">Loading page...</p>}><RoleProvider>
          <Navbar />
          <DemoPitchBar />
          <RoleIndicatorBanner />
          <main id="main-content" tabIndex={-1} className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <SessionGate>{children}</SessionGate>
          </main>
        </RoleProvider></Suspense>
        <footer className="app-footer py-6 px-4 sm:px-6 lg:px-8 text-xs">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
              <p className="font-bold text-slate-300">AyudaChain · Synthetic relief prototype</p>
              <p className="text-slate-500 mt-0.5">
                Receipt checks compare recorded evidence. They do not prove physical cash delivery.
              </p>
            </div>
            <div className="flex items-center gap-4 text-slate-400">
              <span>Fictional Demonstration Calamity: Typhoon Salinlahi</span>
            </div>
          </div>
        </footer>
    </div>
  );
}
