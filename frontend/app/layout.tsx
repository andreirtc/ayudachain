import "./globals.css";
import "./tonal.css";
import type { Metadata } from "next";
import localFont from "next/font/local";

const headings = localFont({ src: "./fonts/manrope-variable.woff2", weight: "200 800", variable: "--font-heading", display: "swap" });
const body = localFont({ src: "./fonts/source-sans-3-variable.woff2", weight: "200 900", variable: "--font-body", display: "swap" });
const interfaceFont = localFont({ src: "./fonts/open-sans-variable.ttf", weight: "300 800", variable: "--font-open-sans", display: "swap" });
const references = localFont({ src: "./fonts/source-code-pro-variable.ttf", weight: "200 900", variable: "--font-reference", display: "swap" });

export const metadata: Metadata = {
  title: "AyudaChain | Follow the relief trail",
  description: "Explore a fictional disaster relief journey from fund release to household receipt. Built for citizens, field workers, and auditors.",
  icons: { icon: "/logo.png" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" suppressHydrationWarning className={`${headings.variable} ${body.variable} ${interfaceFont.variable} ${references.variable}`}><head><script dangerouslySetInnerHTML={{ __html: `try{const t=localStorage.getItem('ayudachain:theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;}catch{}` }} /></head><body>{children}</body></html>;
}
