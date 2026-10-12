// Legacy API DateTime values are UTC but omit an offset (datetime.utcnow).
// Explicit offsets and epoch-based verification timestamps retain their meaning.
export function recordedUtcDate(value: string): Date | null {
  const normalized = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(value)
    ? value
    : value + "Z";
  const date = new Date(normalized);
  return Number.isNaN(date.getTime()) ? null : date;
}
export function formatRecordedDate(value: string): string {
  return (
    recordedUtcDate(value)?.toLocaleString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    }) || "Date unavailable"
  );
}
