import "./globals.css";
import type { Metadata } from "next";
import AppFrame from "@/components/AppFrame";

export const metadata: Metadata = {
  title: "AyudaChain — Disaster Relief Transparency Platform",
  description: "Tamper-evident digital trail from disaster relief fund release to household receipt on Polygon blockchain.",
  icons: {
    icon: "/logo.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <AppFrame>{children}</AppFrame>
      </body>
    </html>
  );
}
