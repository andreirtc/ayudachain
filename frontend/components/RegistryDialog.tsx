"use client";

import { ReactNode, useEffect, useRef } from "react";
import { X } from "lucide-react";

// Native modal dialogs keep keyboard focus inside and make the background inert.
export default function RegistryDialog({
  title,
  children,
  onClose,
  busy = false,
  initialFocus,
  wide = false,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  busy?: boolean;
  initialFocus?: string;
  wide?: boolean;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const element = dialog.current!;
    const opener = document.activeElement as HTMLElement | null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    element.showModal();
    element.querySelector<HTMLElement>(initialFocus || "h2")?.focus();
    return () => {
      element.close();
      document.body.style.overflow = overflow;
      if (opener?.isConnected) opener.focus();
      else document.getElementById("registry-heading")?.focus();
    };
  }, [initialFocus]);

  return (
    <dialog
      ref={dialog}
      aria-labelledby="registry-dialog-title"
      className={`registry-dialog ${wide ? "registry-dialog-wide" : ""}`}
      onCancel={(event) => {
        event.preventDefault();
        if (!busy) onClose();
      }}
      onKeyDown={(event) => {
        if (event.key !== "Tab") return;
        const controls = Array.from(
          event.currentTarget.querySelectorAll<HTMLElement>(
            "button, a[href], input, select, textarea, summary, [tabindex]",
          ),
        ).filter(
          (element) =>
            element.tabIndex >= 0 &&
            !element.matches(":disabled") &&
            element.getClientRects().length > 0 &&
            !Array.from(
              event.currentTarget.querySelectorAll("details:not([open])"),
            ).some(
              (details) =>
                details.contains(element) &&
                details.querySelector(":scope > summary") !== element,
            ),
        );
        const first = controls[0];
        const last = controls[controls.length - 1];
        if (
          event.shiftKey &&
          (document.activeElement === first ||
            document.activeElement === event.currentTarget.querySelector("h2"))
        ) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }}
    >
      <div className="registry-dialog-heading">
        <h2 id="registry-dialog-title" tabIndex={-1}>
          {title}
        </h2>
        <button
          type="button"
          aria-label={`Close ${title.toLowerCase()}`}
          disabled={busy}
          onClick={onClose}
          className="registry-icon-button"
        >
          <X aria-hidden="true" size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}
