"use client";
import {usePathname} from "next/navigation";
import Navbar from "./Navbar";
import DemoPitchBar from "./DemoPitchBar";
import RoleIndicatorBanner from "./RoleIndicatorBanner";
import {RoleProvider} from "@/lib/roleContext";

export default function AppFrame({children}:{children:React.ReactNode}) {
  const path=usePathname();
  if(path.startsWith("/mvp")||path==="/verify") return <>{children}</>;
  return <RoleProvider><Navbar/><DemoPitchBar/><RoleIndicatorBanner/>
    <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">{children}</main>
    <footer className="p-6 text-sm text-slate-600">Legacy demonstration interface. The five-role local evaluation is available at <a href="/mvp">/mvp</a>.</footer>
  </RoleProvider>;
}
