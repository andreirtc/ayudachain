import { test, expect, Page } from "@playwright/test";

const API = "http://127.0.0.1:8101";
const PASSWORD = "synthetic-test-password-only";
test.beforeEach(async ({ page }) => {
  await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, route => {
    const url = new URL(route.request().url()); url.hostname = "127.0.0.1"; url.port = "8101";
    return route.continue({ url: url.toString() });
  });
});

async function submit(page: Page, account: string) {
  await page.getByRole("textbox", { name: "Account", exact: true }).fill(account);
  await page.getByLabel("Password", { exact: true }).fill(PASSWORD);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByText("Authenticated synthetic account.", { exact: false })).toBeVisible();
}
async function gateLogin(page: Page, account: string) {
  await page.getByRole("main").getByRole("link", { name: "Sign in", exact: true }).click();
  await submit(page, account);
}
async function revoke(page: Page) {
  // Independent real API logout revokes the token without changing the browser cookie.
  const { request } = await import("@playwright/test");
  const client = await request.newContext({ storageState: await page.context().storageState() });
  try {
    const session = await (await client.get(API + "/api/auth/session")).json();
    const result = await client.post(API + "/api/auth/logout", { headers: {
      "X-AyudaChain-Client": "web", "X-CSRF-Token": session.csrf_token, Origin: "http://127.0.0.1:3101",
    }});
    expect(result.status()).toBe(200);
  } finally { await client.dispose(); }
}
function loginHref(target: string) { return "/sign-in?" + new URLSearchParams({ returnTo: target }); }

test("anonymous exact household survives failure, keyboard retry, reload and sign-in", async ({ page }, info) => {
  const target = "/distributions?beneficiary_id=BEN-0004";
  await page.goto(target);
  const link = page.getByRole("main").getByRole("link", { name: "Sign in", exact: true });
  await expect(link).toHaveAttribute("href", loginHref(target));
  await link.focus(); await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { name: "Sign in to the demo", exact: true })).toBeVisible();
  await page.reload();
  await page.getByRole("textbox", { name: "Account", exact: true }).fill("demo-disbursing-001");
  await page.getByLabel("Password", { exact: true }).fill("wrong-synthetic-password");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.locator("form").getByRole("alert")).toContainText("Incorrect account or password");
  await expect(page.getByRole("textbox", { name: "Account", exact: true })).toHaveValue("demo-disbursing-001");
  expect(new URL(page.url()).searchParams.get("returnTo")).toBe(target);
  expect(page.url()).not.toContain("password");
  await page.getByRole("textbox", { name: "Account", exact: true }).focus(); await page.keyboard.press("Tab");
  await expect(page.getByLabel("Password", { exact: true })).toBeFocused();
  await page.screenshot({ path: info.outputPath("destination-sign-in-retry.png"), fullPage: true });
  await submit(page, "demo-disbursing-001");
  await expect(page).toHaveURL(new URL(target, "http://127.0.0.1:3101").href);
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue("BEN-0004");
  await expect(page.getByLabel("Household", { exact: true })).toBeDisabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: info.outputPath("destination-household.png"), fullPage: true });
});

test("encoded household references remain exact through authentication", async ({ page }, info) => {
  await page.goto("/sign-in"); await submit(page, "demo-barangay-01");
  const session = await (await page.context().request.get(API + "/api/auth/session")).json();
  const id = "BEN-RETURN ?&#+ % " + info.project.name;
  const created = await page.context().request.post(API + "/api/beneficiaries", {
    headers: { "X-AyudaChain-Client": "web", "X-CSRF-Token": session.csrf_token, Origin: "http://127.0.0.1:3101" },
    data: { beneficiary_id: id, household_name: "Synthetic destination " + info.project.name, barangay_id: "BRGY-001", barangay_name: "San Isidro", batch_id: "RELIEF-2026-001" },
  });
  expect(created.status()).toBe(201);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  const target = "/distributions?" + new URLSearchParams({ beneficiary_id: id });
  await page.goto(target); await gateLogin(page, "demo-disbursing-001");
  await expect(page).toHaveURL(new URL(target, "http://127.0.0.1:3101").href);
  expect(new URL(page.url()).searchParams.get("beneficiary_id")).toBe(id);
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue(id);
  await expect(page.getByText("This household needs DSWD approval before payout.", { exact: true })).toBeVisible();
});

test("public exact receipt sign-in and revoked session clear private context", async ({ page }, info) => {
  const target = "/verify?distribution_id=DIST-0001";
  await page.goto(target);
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue("DIST-0001");
  const banner = page.getByRole("region", { name: "Account", exact: true });
  await expect(banner.getByRole("link", { name: "Sign in", exact: true })).toHaveAttribute("href", loginHref(target));
  await banner.getByRole("link", { name: "Sign in", exact: true }).click();
  await submit(page, "demo-auditor-01");
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue("DIST-0001");
  await expect(page.getByText("Saved receipt image", { exact: true })).toBeVisible();
  await revoke(page);
  await page.getByRole("button", { name: "Check again", exact: true }).click();
  await expect(page.getByText("Public view", { exact: true })).toBeVisible();
  await expect(page.getByText("Saved receipt image", { exact: true })).toHaveCount(0);
  await expect(page.getByText("Saved extracted text", { exact: true })).toHaveCount(0);
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue("DIST-0001");
  await page.screenshot({ path: info.outputPath("destination-public-receipt.png"), fullPage: true });
  const receiptSignIn = page.getByRole("region", { name: "Receipt details", exact: true }).getByRole("link", { name: "Sign in", exact: true });
  await expect(receiptSignIn).toHaveAttribute("href", loginHref(target));
  await receiptSignIn.click();
  await submit(page, "demo-auditor-01");
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue("DIST-0001");
  await expect(page.getByText("Saved receipt image", { exact: true })).toBeVisible();
  await page.screenshot({ path: info.outputPath("destination-private-receipt.png"), fullPage: true });
});

test("revoked payout session restores destination without retaining or replaying form", async ({ page }) => {
  const target = "/distributions?beneficiary_id=BEN-0004";
  await page.goto(target); await gateLogin(page, "demo-disbursing-001");
  await page.getByLabel("Fictional amount (PHP)").fill("123.45");
  let submissions = 0;
  page.on("request", request => { if (request.url().endsWith("/api/distributions/confirm")) submissions++; });
  await revoke(page);
  const [response] = await Promise.all([
    page.waitForResponse(r => r.url().includes("/api/beneficiaries?")),
    page.getByRole("button", { name: "Refresh", exact: true }).click(),
  ]);
  expect(response.status()).toBe(401);
  await expect(page.getByRole("heading", { name: "Sign in to continue", exact: true })).toBeVisible();
  await expect(page.getByLabel("Fictional amount (PHP)")).toHaveCount(0);
  await gateLogin(page, "demo-disbursing-001");
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue("BEN-0004");
  await expect(page.getByLabel("Fictional amount (PHP)")).not.toHaveValue("123.45");
  expect(submissions).toBe(0);
});

test("different accounts cannot inherit household or receipt scope", async ({ page }) => {
  const target = "/distributions?beneficiary_id=BEN-0001";
  await page.goto(target); await gateLogin(page, "demo-auditor-01");
  await expect(page.getByRole("region", { name: "Recorded payouts", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page.getByRole("region", { name: "Recorded payouts", exact: true })).toHaveCount(0);
  await gateLogin(page, "demo-beneficiary-01");
  await expect(page.getByRole("heading", { name: "Household unavailable", exact: true })).toBeVisible();
  await expect(page.getByRole("region", { name: "Recorded payouts", exact: true })).toHaveCount(0);
  expect((await page.context().request.get(API + "/api/beneficiaries/BEN-0001")).status()).toBe(404);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await page.goto(loginHref("/verify?distribution_id=DIST-0001")); await submit(page, "demo-beneficiary-01");
  await expect(page.getByRole("heading", { name: "Receipt not found", exact: true })).toBeVisible();
  await expect(page.getByText("Saved receipt image", { exact: true })).toHaveCount(0);
});

test("Barangay return to payouts is explicitly denied by page and API", async ({ page }, info) => {
  await page.goto("/distributions?beneficiary_id=BEN-0004"); await gateLogin(page, "demo-barangay-01");
  await expect(page.getByRole("heading", { name: "Payout records are outside your role", exact: true })).toBeVisible();
  expect((await page.context().request.get(API + "/api/distributions")).status()).toBe(403);
  await page.screenshot({ path: info.outputPath("destination-role-denied.png"), fullPage: true });
  await page.getByRole("link", { name: "Open households", exact: true }).click();
  await expect(page.getByRole("button", { name: "Register a household", exact: true })).toBeVisible();
});

test("hostile or ambiguous return targets cannot redirect outside supported routes", async ({ page }) => {
  for (const target of ["https://outside.invalid/", "//outside.invalid", "/\\outside.invalid", "javascript:alert(1)", "/sign-in?returnTo=/verify", "/batch/../verify", "/verify?distribution_id=%", "/verify?distribution_id=%00", "/unknown"]) {
    await page.goto(loginHref(target)); await submit(page, "demo-disbursing-001");
    await expect(page).toHaveURL("http://127.0.0.1:3101/distributions");
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
  }
  await page.goto("/sign-in?returnTo=/verify&returnTo=/distributions"); await submit(page, "demo-auditor-01");
  await expect(page).toHaveURL("http://127.0.0.1:3101/beneficiaries");
});

test("direct sign-in preserves all role defaults and navigation preserves receipt links", async ({ page }, info) => {
  for (const [account, destination] of [["demo-officer-01", "beneficiaries"], ["demo-barangay-01", "beneficiaries"], ["demo-disbursing-001", "distributions"], ["demo-beneficiary-01", "beneficiaries"], ["demo-auditor-01", "beneficiaries"]]) {
    await page.goto("/sign-in"); await submit(page, account);
    await expect(page).toHaveURL("http://127.0.0.1:3101/" + destination);
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
  }
  const target = "/verify?distribution_id=DIST-0001"; await page.goto(target);
  if (info.project.name === "phone") await page.getByText("Menu", { exact: true }).click();
  const navigation = page.getByRole("navigation", { name: info.project.name === "phone" ? "Mobile navigation" : "Main navigation", exact: true });
  await expect(navigation.getByRole("link", { name: "Sign in", exact: true })).toHaveAttribute("href", loginHref(target));
  await navigation.getByRole("link", { name: "Sign in", exact: true }).click(); await submit(page, "demo-auditor-01");
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue("DIST-0001");
});
