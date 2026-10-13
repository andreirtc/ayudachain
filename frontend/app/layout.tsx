import "./globals.css";
import type { Metadata } from "next";
import AppFrame from "@/components/AppFrame";
import { Open_Sans, Source_Code_Pro } from "next/font/google";

const openSans = Open_Sans({ subsets: ["latin"], weight: ["400", "500", "600", "700"], variable: "--font-open-sans", display: "swap" });
const sourceCodePro = Source_Code_Pro({ subsets: ["latin"], weight: ["500", "600"], variable: "--font-source-code-pro", display: "swap" });

export const metadata: Metadata = {
  title: "AyudaChain — Disaster Relief Transparency Platform",
  description: "Tamper-evident digital trail from disaster relief fund release to household receipt on Polygon blockchain.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${openSans.variable} ${sourceCodePro.variable}`} suppressHydrationWarning>
      <head>
        {/* Apply the saved colour theme before first paint to avoid a light flash. */}
        <script dangerouslySetInnerHTML={{ __html: "try{var t=localStorage.getItem('ayudachain:theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)}catch(e){}" }} />
      </head>
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <AppFrame>{children}</AppFrame>
      </body>
    </html>
  );
}
