import Navbar from "@/components/Navbar";
import DemoPitchBar from "@/components/DemoPitchBar";
import RoleIndicatorBanner from "@/components/RoleIndicatorBanner";
import { RoleProvider } from "@/lib/roleContext";

export default function OperationsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <RoleProvider>
          <Navbar />
          <DemoPitchBar />
          <RoleIndicatorBanner />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
        </RoleProvider>
        <footer className="bg-slate-900 border-t border-slate-800 text-slate-400 py-8 px-4 sm:px-6 lg:px-8 text-xs">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
              <p className="font-bold text-slate-300">AYUDACHAIN — NATIONAL RELIEF INTEGRITY &amp; AUDIT INFRASTRUCTURE</p>
              <p className="text-slate-500 mt-0.5">
                Architecture: Off-chain operational storage + on-chain receipt integrity proofs.
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
