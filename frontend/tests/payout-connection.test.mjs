import assert from "node:assert/strict";
import test from "node:test";
import { subscribeToConnectivity, submitOnlinePayout } from "../lib/payoutConnection.ts";

test("an offline payout attempt sends nothing; reconnection can reuse the original request", async () => {
  const request = { key: "demo-retry-key", beneficiary_id: "BEN-FICTIONAL" };
  const sent = [];
  const send = async () => { sent.push(request); return { distribution_id: "DIST-FICTIONAL" }; };
  await assert.rejects(submitOnlinePayout(false, send), /No payout has been queued/);
  assert.equal(sent.length, 0);
  const receipt = await submitOnlinePayout(true, send);
  assert.equal(receipt.distribution_id, "DIST-FICTIONAL");
  assert.deepEqual(sent, [request]);
});

test("an uncertain online response remains a failure rather than a queued or successful payout", async () => {
  await assert.rejects(submitOnlinePayout(true, async () => { throw new Error("Response lost"); }), /Response lost/);
});

test("connection notices respond to both browser events and unsubscribe when leaving the screen", () => {
  const previousWindow = globalThis.window;
  const events = new EventTarget();
  globalThis.window = events;
  try {
    let updates = 0;
    const unsubscribe = subscribeToConnectivity(() => updates++);
    events.dispatchEvent(new Event("offline"));
    events.dispatchEvent(new Event("online"));
    assert.equal(updates, 2);
    unsubscribe();
    events.dispatchEvent(new Event("offline"));
    events.dispatchEvent(new Event("online"));
    assert.equal(updates, 2);
  } finally {
    if (previousWindow === undefined) delete globalThis.window;
    else globalThis.window = previousWindow;
  }
});
