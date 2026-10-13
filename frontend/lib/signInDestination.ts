// Navigation only. SessionGate and the API still decide record access.
export function safeReturnTo(value: string | null): string | null {
  if (!value || value.length > 2048 || !value.startsWith("/") || value.startsWith("//")) return null;
  if (/[\\\s#]/.test(value)) return null;
  try {
    const decoded = decodeURIComponent(value);
    if (/[\u0000-\u001f\u007f\\]/.test(decoded)) return null;
    const url = new URL(value, "http://local.invalid");
    if (url.origin !== "http://local.invalid" || url.hash) return null;
    const path = value.split("?")[0];
    if (url.pathname !== path) return null;
    const queryKey = path === "/distributions" || path === "/beneficiaries" || path === "/concerns" ? "beneficiary_id" : path === "/verify" ? "distribution_id" : path === "/lists" || path === "/arrangements" ? "list_id" : null;
    const supported = ["/beneficiaries", "/distributions", "/verify", "/dashboard", "/household", "/lists", "/arrangements", "/concerns", "/audit"].includes(path)
      || /^\/batch\/[A-Za-z0-9_-]+$/.test(path);
    if (!supported) return null;
    if (url.searchParams.size && (!queryKey || url.searchParams.size !== 1 || !url.searchParams.has(queryKey))) return null;
    return value;
  } catch {
    return null;
  }
}

export function signInHref(destination: string): string {
  const returnTo = safeReturnTo(destination);
  return returnTo ? "/sign-in?" + new URLSearchParams({ returnTo }) : "/sign-in";
}

export function afterSignIn(returnTo: string | null, role: string): string {
  return safeReturnTo(returnTo) || (role === "DISBURSING" ? "/distributions" : role === "BENEFICIARY" ? "/household" : "/beneficiaries");
}
