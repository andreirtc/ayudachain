import assert from "node:assert/strict";
import test from "node:test";
import { authenticatedFetch, clearSession, fetchSession, signIn } from "../lib/api.ts";

const session = { account: { id: "synthetic-unit-account", role: "AUDITOR" }, csrf_token: "synthetic-csrf" };
const reply = () => new Response(JSON.stringify(session), { status: 200 });

test("late responses from an ended account cannot expire a new session or restore its CSRF", async () => {
  const originalFetch = globalThis.fetch;
  const originalWindow = globalThis.window;
  let ended = 0;
  globalThis.window = { dispatchEvent: () => { ended++; } };
  try {
    clearSession();
    let release;
    globalThis.fetch = () => new Promise(resolve => { release = resolve; });
    const oldRequest = authenticatedFetch("http://localhost/api/beneficiaries");
    globalThis.fetch = async () => reply();
    await signIn("synthetic-unit-account", "synthetic-unit-password");
    release(new Response(null, { status: 401 }));
    await oldRequest;
    assert.equal(ended, 0);

    globalThis.fetch = () => new Promise(resolve => { release = resolve; });
    const oldSession = fetchSession();
    clearSession();
    globalThis.fetch = async () => reply();
    await signIn("synthetic-unit-account", "synthetic-unit-password");
    release(new Response(JSON.stringify({ ...session, csrf_token: "old-csrf" })));
    assert.equal(await oldSession, null);
    let sentToken;
    globalThis.fetch = async (_url, options) => {
      sentToken = options.headers.get("X-CSRF-Token");
      return new Response(null, { headers: { "X-AyudaChain-Session": "ended" } });
    };
    await authenticatedFetch("http://localhost/api/blockchain/verify");
    assert.equal(sentToken, "synthetic-csrf");
    assert.equal(ended, 1);
  } finally {
    clearSession(); globalThis.fetch = originalFetch; globalThis.window = originalWindow;
  }
});
