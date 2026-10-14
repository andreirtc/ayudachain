import "./globals.css";
import "./tonal.css";
import type { Metadata } from "next";
import localFont from "next/font/local";
import { RoleProvider } from "@/lib/roleContext";

const interfaceFont = localFont({ src: "./fonts/open-sans-variable.ttf", weight: "300 800", variable: "--font-open-sans", display: "swap" });
const references = localFont({ src: "./fonts/source-code-pro-variable.ttf", weight: "200 900", variable: "--font-reference", display: "swap" });

export const metadata: Metadata = {
  title: "AyudaChain | Follow the relief trail",
  description: "Explore a fictional disaster relief journey from fund release to household receipt. Built for citizens, field workers, and auditors.",
  icons: { icon: "/ayudachain-mark.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" suppressHydrationWarning className={`${interfaceFont.variable} ${references.variable}`}><head><script dangerouslySetInnerHTML={{ __html: `try{const t=localStorage.getItem('ayudachain:theme');if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;}catch{}` }} /></head><body><RoleProvider>{children}</RoleProvider></body></html>;
}
