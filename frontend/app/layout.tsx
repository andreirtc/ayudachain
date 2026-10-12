import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AyudaChain | Follow the relief trail",
  description: "Explore a fictional disaster relief journey from fund release to household receipt. Built for citizens, field workers, and auditors.",
  icons: { icon: "/logo.png" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
