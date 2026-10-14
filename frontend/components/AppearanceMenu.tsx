"use client";

import { ReactNode, useEffect, useId, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { Settings2 } from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";

export default function AppearanceMenu({ children, accountId }: { children?: ReactNode; accountId?: string }) {
  const preferences = useRef<HTMLDetailsElement>(null);
  const panelId = useId();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const previousContext = useRef({ pathname, accountId });

  function close(returnFocus = false) {
    const element = preferences.current;
    if (!element?.open) return;
    element.open = false;
    setOpen(false);
    if (returnFocus) element.querySelector("summary")?.focus();
  }

  useEffect(() => {
    const outside = (event: Event) => {
      if (event.target instanceof Node && !preferences.current?.contains(event.target)) close();
    };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && preferences.current?.open) {
        event.preventDefault();
        close(true);
      }
    };
    document.addEventListener("pointerdown", outside);
    document.addEventListener("focusin", outside);
    document.addEventListener("keydown", escape);
    return () => {
      document.removeEventListener("pointerdown", outside);
      document.removeEventListener("focusin", outside);
      document.removeEventListener("keydown", escape);
    };
  }, []);

  useEffect(() => {
    const previous = previousContext.current;
    if (previous.pathname !== pathname || previous.accountId !== accountId) close();
    previousContext.current = { pathname, accountId };
  }, [pathname, accountId]);

  return <details ref={preferences} className="app-preferences" onToggle={event => setOpen(event.currentTarget.open)}>
    <summary aria-label="Display preferences" title="Display preferences" aria-expanded={open} aria-controls={panelId}>
      <Settings2 size={20} aria-hidden="true" />
    </summary>
    <div id={panelId} className="app-preferences-panel">
      {children}
      <p>Appearance</p>
      <ThemeToggle menu onSelect={() => close(true)} />
      <p className="registry-muted">Synthetic demo · No real payments</p>
    </div>
  </details>;
}
