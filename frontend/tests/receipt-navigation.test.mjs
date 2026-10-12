import assert from "node:assert/strict";
import test from "node:test";
import { receiptVerificationHref, selectReceiptId } from "../lib/receiptNavigation.ts";

const records = [{ distribution_id: "DIST-OTHER" }, { distribution_id: "DIST-NEW" }];

test("payout handoff selects its exact receipt even when another receipt is first", () => {
  const href = receiptVerificationHref("DIST-NEW");
  const id = new URL(href, "http://localhost").searchParams.get("distribution_id");
  assert.equal(selectReceiptId(records, id), "DIST-NEW");
});

test("missing or empty explicit links never select a different household receipt", () => {
  assert.equal(selectReceiptId(records, "DIST-MISSING"), "");
  assert.equal(selectReceiptId(records, ""), "");
  assert.equal(selectReceiptId([], "DIST-NEW"), "");
});

test("direct verification entry chooses an available receipt without assuming a fixture ID", () => {
  assert.equal(selectReceiptId(records, null), "DIST-OTHER");
  assert.equal(selectReceiptId([], null), "");
});

test("receipt references round-trip without becoming extra query parameters", () => {
  const reference = "synthetic /?&#+ receipt";
  const url = new URL(receiptVerificationHref(reference), "http://localhost");
  assert.equal(url.pathname, "/verify");
  assert.equal(url.searchParams.size, 1);
  assert.equal(url.searchParams.get("distribution_id"), reference);
  assert.equal(url.hash, "");
});
