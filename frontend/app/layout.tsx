import "./globals.css";
import type { Metadata } from "next";
import localFont from "next/font/local";

const headings = localFont({ src: "./fonts/manrope-variable.woff2", weight: "200 800", variable: "--font-heading", display: "swap" });
const body = localFont({ src: "./fonts/source-sans-3-variable.woff2", weight: "200 900", variable: "--font-body", display: "swap" });

export const metadata: Metadata = {
  title: "AyudaChain | Follow the relief trail",
  description: "Explore a fictional disaster relief journey from fund release to household receipt. Built for citizens, field workers, and auditors.",
  icons: { icon: "/logo.png" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" className={`${headings.variable} ${body.variable}`}><body>{children}</body></html>;
}
