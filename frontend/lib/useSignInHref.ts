"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { signInHref } from "./signInDestination";

export function useSignInHref(): string {
  const pathname = usePathname();
  const query = useSearchParams().toString();
  return signInHref(pathname + (query ? "?" + query : ""));
}
