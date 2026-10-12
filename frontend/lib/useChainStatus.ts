"use client";

import { useEffect, useState } from "react";
import { ChainStatus, fetchChainStatus } from "./api";

export type ChainState =
  | { kind: "checking" }
  | { kind: "connected"; status: ChainStatus }
  | { kind: "unavailable"; status?: ChainStatus };

export function useChainStatus(): ChainState {
  const [state, setState] = useState<ChainState>({ kind: "checking" });

  useEffect(() => {
    let cancelled = false;
    fetchChainStatus()
      .then((status) => {
        if (!cancelled) setState(status.success ? { kind: "connected", status } : { kind: "unavailable", status });
      })
      .catch(() => {
        if (!cancelled) setState({ kind: "unavailable" });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}

export function chainLabel(state: ChainState): string {
  if (state.kind === "checking") return "Checking blockchain";
  if (state.kind === "unavailable") return "Blockchain unavailable";
  const { network, chainId } = state.status;
  return chainId ? `${network} (chain ${chainId})` : network;
}
