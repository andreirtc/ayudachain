import test from "node:test";
import assert from "node:assert/strict";
import { recordedUtcDate, formatRecordedDate } from "../lib/recordedDate.ts";
test("legacy UTC dates do not acquire the browser's local offset", () => {
  assert.equal(
    recordedUtcDate("2026-10-12T17:30:00.123").toISOString(),
    "2026-10-12T17:30:00.123Z",
  );
});
test("explicit UTC and non-UTC offsets retain the same instant", () => {
  assert.equal(
    recordedUtcDate("2026-10-13T01:30:00+08:00").toISOString(),
    "2026-10-12T17:30:00.000Z",
  );
  assert.equal(
    recordedUtcDate("2026-10-12T17:30:00Z").toISOString(),
    "2026-10-12T17:30:00.000Z",
  );
});
test("invalid dates stay unavailable", () => {
  assert.equal(recordedUtcDate("invalid"), null);
  assert.equal(formatRecordedDate("invalid"), "Date unavailable");
});
