"use client";

import { useEffect, useState } from "react";
import { Sun, Moon, Monitor, Check } from "lucide-react";

type Theme = "light" | "dark" | "system";
const options = [
  { value: "light", label: "Light theme", text: "Light", Icon: Sun },
  { value: "dark", label: "Dark theme", text: "Dark", Icon: Moon },
  { value: "system", label: "Use device theme", text: "Device default", Icon: Monitor },
] as const;

export default function ThemeToggle({ menu = false, onSelect }: { menu?: boolean; onSelect?: () => void }) {
  const [theme, setTheme] = useState<Theme>("system");
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const current = document.documentElement.dataset.theme;
    setTheme(current === "light" || current === "dark" ? current : "system");
    setReady(true);
    const sync = (event: StorageEvent) => {
      if (event.key === "ayudachain:theme" || event.key === null) choose(event.newValue === "light" || event.newValue === "dark" ? event.newValue : "system", false);
    };
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);
  function choose(next: Theme, persist = true) {
    setTheme(next);
    if (next === "system") delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = next;
    if (persist) try {
      if (next === "system") localStorage.removeItem("ayudachain:theme");
      else localStorage.setItem("ayudachain:theme", next);
    } catch { /* The current choice still works when storage is unavailable. */ }
  }
  return <div className={`app-theme${menu ? " app-theme-menu" : ""}`} role="group" aria-label="Colour theme">
    {options.map(({ value, label, text, Icon }) => <button key={value} type="button" disabled={!ready} aria-label={label} title={label} aria-pressed={theme === value} onClick={() => { choose(value); onSelect?.(); }}><Icon size={18} aria-hidden="true" />{menu && <><span>{text}</span>{theme === value && <Check className="theme-check" size={18} aria-hidden="true" />}</>}</button>)}
  </div>;
}
