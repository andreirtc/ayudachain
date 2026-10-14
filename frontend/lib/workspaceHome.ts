// Entry navigation only. Account permissions remain enforced by the API.
export function workspaceHome(role?: string): string {
  return role === "BENEFICIARY" ? "/household" : role ? "/dashboard" : "/";
}
