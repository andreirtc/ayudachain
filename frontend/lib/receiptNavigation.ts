type ReceiptReference = { distribution_id: string };

export function receiptVerificationHref(id: string): string {
  return `/verify?${new URLSearchParams({ distribution_id: id }).toString()}`;
}

export function selectReceiptId(records: ReceiptReference[], requestedId: string | null): string {
  // An explicit reference must never be substituted with another household's receipt.
  if (requestedId !== null) {
    return records.some((record) => record.distribution_id === requestedId) ? requestedId : "";
  }
  return records[0]?.distribution_id || "";
}
