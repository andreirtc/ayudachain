import assert from "node:assert/strict";
import test from "node:test";
import { safeReturnTo, signInHref, afterSignIn } from "../lib/signInDestination.ts";

test("exact household and receipt references survive the sign-in query round trip", () => {
  for (const [path, key] of [["/distributions", "beneficiary_id"], ["/verify", "distribution_id"]]) {
    const destination = path + "?" + new URLSearchParams({ [key]: "synthetic /?&#+ % reference" });
    const login = new URL(signInHref(destination), "http://localhost");
    assert.equal(afterSignIn(login.searchParams.get("returnTo"), "DISBURSING"), destination);
  }
});

test("external, malformed, unsupported and looping destinations fall back safely", () => {
  for (const value of [null, "", "https://outside.invalid", "//outside.invalid", "/\\outside.invalid", "javascript:alert(1)", "/sign-in", "/sign-in?returnTo=/verify", "/unknown", "/verify#receipt", "/verify?distribution_id=%", "/verify?distribution_id=%00", "/%2f%2foutside.invalid", "/batch/../verify", "/batch/%2e%2e", "/verify?returnTo=//outside.invalid", "/distributions?beneficiary_id=A&beneficiary_id=B", " /verify", "/verify\n", "/" + "a".repeat(2048)]) {
    assert.equal(safeReturnTo(value), null, String(value));
    assert.equal(afterSignIn(value, "DISBURSING"), "/distributions");
    assert.equal(afterSignIn(value, "AUDITOR"), "/beneficiaries");
  }
});

test("supported local pages preserve role defaults and never decide permission", () => {
  for (const path of ["/verify", "/beneficiaries", "/dashboard", "/batch/RELIEF-2026-001", "/distributions?beneficiary_id="]) assert.equal(safeReturnTo(path), path);
  assert.equal(afterSignIn("/distributions?beneficiary_id=BEN-OUTSIDE", "BARANGAY"), "/distributions?beneficiary_id=BEN-OUTSIDE");
  assert.equal(signInHref("/sign-in"), "/sign-in");
});
