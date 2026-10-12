"use client";

import { useSyncExternalStore } from "react";
import { browserIsOnline, subscribeToConnectivity } from "./payoutConnection";

export function useBrowserOnline(): boolean | null {
  return useSyncExternalStore<boolean | null>(subscribeToConnectivity, browserIsOnline, () => null);
}
