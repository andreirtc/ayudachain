export function browserIsOnline(): boolean {
  return navigator.onLine;
}

export function subscribeToConnectivity(onChange: () => void): () => void {
  window.addEventListener("online", onChange);
  window.addEventListener("offline", onChange);
  return () => {
    window.removeEventListener("online", onChange);
    window.removeEventListener("offline", onChange);
  };
}

export async function submitOnlinePayout<T>(online: boolean, send: () => Promise<T>): Promise<T> {
  if (!online) throw new Error("You are offline. Reconnect before recording a payout. No payout has been queued.");
  return send();
}
