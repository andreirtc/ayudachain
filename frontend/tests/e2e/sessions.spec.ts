import { test, expect, Page } from "@playwright/test";

const API = "http://127.0.0.1:8101";
const PASSWORD = "synthetic-test-password-only";

test.beforeEach(async ({ page }) => {
  // Route the actual browser's API traffic to the isolated API, without fabricating responses.
  await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, route => {
    const url = new URL(route.request().url()); url.hostname = "127.0.0.1"; url.port = "8101";
    return route.continue({ url: url.toString() });
  });
});

async function login(page: Page, account: string) {
  await page.goto("/sign-in");
  await page.getByRole("textbox", { name: "Account", exact: true }).fill(account);
  await page.getByLabel("Password", { exact: true }).fill(PASSWORD);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByText("Authenticated synthetic account.", { exact: false })).toBeVisible();
}

async function mutationHeaders(page: Page) {
  const response = await page.context().request.get(API + "/api/auth/session");
  const session = await response.json();
  return { "X-CSRF-Token": session.csrf_token, "X-AyudaChain-Client": "web", Origin: "http://127.0.0.1:3101" };
}

test("public receipt checks and private sign-in gate do not reveal households", async ({ page }) => {
  await page.goto("/beneficiaries");
  await expect(page.getByRole("heading", { name: "Sign in to continue" })).toBeVisible();
  await expect(page.getByText("Juan Dela Cruz", { exact: true })).toHaveCount(0);
  await page.goto("/verify?distribution_id=DIST-0001");
  await expect(page.getByRole("heading", { name: "Verification unavailable", exact: true })).toBeVisible();
  await expect(page.getByText("Juan Dela Cruz", { exact: true })).toHaveCount(0);
  await page.goto("/verify?distribution_id=DIST-MISSING");
  await expect(page.getByRole("heading", { name: "Receipt not found" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Verification unavailable" })).toHaveCount(0);
});

test("DSWD signs in, records its own review identity and stays signed in after refresh", async ({ page }, info) => {
  await login(page, "demo-officer-01");
  await page.getByPlaceholder("Search household name, ID, barangay...").fill("BEN-0007");
  await page.getByRole("button", { name: /Review|Inspect/ }).first().click();
  await page.getByLabel("Reason for decision").fill("Distinct synthetic household for session testing");
  await page.getByRole("button", { name: "Approve household", exact: true }).click();
  await expect(page.getByText("Review saved.", { exact: true })).toBeVisible();
  await page.screenshot({ path: info.outputPath("review.png"), fullPage: true });
  const history = await page.context().request.get(API + "/api/beneficiaries/BEN-0007/reviews");
  expect((await history.json())[0].reviewed_by).toBe("demo-officer-01");
  await page.reload();
  await expect(page.getByText("Authenticated synthetic account.", { exact: false })).toBeVisible();
  await expect(page.getByRole("button", { name: "Register a household", exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("auditor is read-only in the UI and direct API", async ({ page }) => {
  await login(page, "demo-auditor-01");
  await expect(page.getByRole("button", { name: "Register a household", exact: true })).toHaveCount(0);
  await page.getByPlaceholder("Search household name, ID, barangay...").fill("BEN-0007");
  await page.getByRole("button", { name: /Review|Inspect/ }).first().click();
  await expect(page.getByRole("button", { name: "Approve household", exact: true })).toHaveCount(0);
  const result = await page.context().request.post(API + "/api/beneficiaries/BEN-0007/verify", { headers: await mutationHeaders(page), data: { status: "VERIFIED", review_notes: "Unauthorized synthetic request", reviewed_by: "demo-officer-01" } });
  expect(result.status()).toBe(403);
});

test("barangay registers within its scope without eligibility or evidence controls", async ({ page }, info) => {
  await login(page, "demo-barangay-01");
  const list = await page.context().request.get(API + "/api/beneficiaries");
  expect((await list.json()).every((row: { barangay_id: string }) => row.barangay_id === "BRGY-001")).toBe(true);
  await page.getByRole("button", { name: "Register a household", exact: true }).click();
  const name = info.project.name === "desktop" ? "Synthetic Marisol Bayani" : "Synthetic Tala Manalo";
  await page.getByLabel("Household Head Full Name").fill(name);
  await expect(page.getByLabel("Barangay Locality", { exact: true })).toBeDisabled();
  await page.route(/8000\/api\/beneficiaries$/, route => route.abort(), { times: 1 });
  await page.getByRole("button", { name: "Register household", exact: true }).click();
  await expect(page.locator("form").getByRole("alert")).toBeVisible();
  await expect(page.getByLabel("Household Head Full Name")).toHaveValue(name);
  await page.getByRole("button", { name: "Register household", exact: true }).click();
  await expect(page.getByText(name, { exact: true }).last()).toBeVisible();
  await expect(page.getByText("Eligibility decisions belong to the DSWD Officer.", { exact: false })).toBeVisible();
  await expect(page.getByRole("button", { name: "Approve household", exact: true })).toHaveCount(0);
  await expect(page.getByText(/Review history \(/)).toHaveCount(0);
  const registered = await page.context().request.get(API + "/api/beneficiaries");
  const row = (await registered.json()).find((row: { household_name: string }) => row.household_name === name);
  expect(row.barangay_id).toBe("BRGY-001");
  expect(row.review_status).toBe("PENDING");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("household scope and logout prevent retained private content", async ({ page }) => {
  await login(page, "demo-beneficiary-01");
  await page.getByText("Household details and review history", { exact: true }).click();
  await expect(page.getByText("BEN-0004", { exact: true })).toBeVisible();
  await expect(page.getByText("BEN-0001", { exact: true })).toHaveCount(0);
  expect((await page.context().request.get(API + "/api/beneficiaries/BEN-0001")).status()).toBe(404);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Sign in to continue" })).toBeVisible();
  await expect(page.getByText("BEN-0004", { exact: true })).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole("heading", { name: "Sign in to continue" })).toBeVisible();
});

test("disbursing records a payout, keeps the exact receipt link and cannot queue offline", async ({ page }, info) => {
  await login(page, "demo-officer-01");
  const id = "BEN-SESSION-PAYOUT-" + info.project.name;
  const headers = await mutationHeaders(page);
  const created = await page.context().request.post(API + "/api/beneficiaries", { headers, data: { beneficiary_id: id, household_name: "Synthetic session payout " + info.project.name, barangay_id: "BRGY-001", barangay_name: "San Isidro", batch_id: "RELIEF-2026-001" } });
  expect(created.status()).toBe(201);
  expect((await page.context().request.post(API + "/api/beneficiaries/" + id + "/verify", { headers, data: { status: "VERIFIED", review_notes: "Independent synthetic session payout fixture" } })).status()).toBe(200);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "demo-disbursing-001");
  await page.getByLabel("Household", { exact: true }).selectOption(id);
  await expect(page.getByLabel("Fictional amount (PHP)")).toHaveValue("5000");
  await page.context().setOffline(true);
  await expect(page.getByText("Browser is offline", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Reconnect to record a payout" })).toBeDisabled();
  await page.context().setOffline(false);
  await expect(page.getByRole("button", { name: "Record demo payout", exact: true })).toBeEnabled();
  await page.getByRole("button", { name: "Record demo payout", exact: true }).click();
  const link = page.getByRole("link", { name: "Check this receipt", exact: true });
  await expect(link).toBeVisible();
  const href = await link.getAttribute("href");
  const payoutId = new URL(href!, "http://127.0.0.1:3101").searchParams.get("distribution_id")!;
  const card = page.getByRole("status").filter({ has: link });
  await expect(card.getByText("Anchoring needs attention", { exact: true })).toBeVisible();
  const recover = card.getByRole("button", { name: "Recover anchor", exact: true });
  const [response] = await Promise.all([page.waitForResponse(r => r.url().endsWith("/anchor/retry")), recover.click()]);
  expect(response.status()).toBe(200);
  const rows = await page.context().request.get(API + "/api/distributions");
  const saved = (await rows.json()).find((row: { distribution_id: string }) => row.distribution_id === payoutId);
  expect(saved.anchor_job.state).toBe("FAILED");
  expect(saved.anchor_job.attempts).toBe(2);
  expect(saved.blockchain_tx_hash).toBeNull();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: info.outputPath("payout.png"), fullPage: true });
  expect(href).toMatch(/^\/verify\?distribution_id=DIST-/);
  await page.reload();
  await page.getByText("Anchor status and recovery", { exact: true }).first().click();
  await expect(page.getByRole("button", { name: "Recover anchor", exact: true })).toBeVisible();
  const persisted = await page.context().request.get(API + "/api/distributions");
  expect((await persisted.json()).filter((row: { beneficiary_id: string }) => row.beneficiary_id === id)).toHaveLength(1);
  await page.goto(href!);
  await expect(page.getByRole("heading", { name: "Verification unavailable", exact: true })).toBeVisible();
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(new URL(page.url()).searchParams.get("distribution_id")!);
});

test("sign-in error retains input and page fits the viewport with keyboard navigation", async ({ page }, info) => {
  await page.goto("/sign-in");
  await page.getByRole("textbox", { name: "Account", exact: true }).fill("demo-officer-01");
  await page.getByLabel("Password", { exact: true }).fill("wrong-synthetic-password");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.locator("form").getByRole("alert")).toContainText("Incorrect account or password");
  await expect(page.getByRole("textbox", { name: "Account", exact: true })).toHaveValue("demo-officer-01");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.keyboard.press("Control+Home");
  await page.getByRole("textbox", { name: "Account", exact: true }).focus();
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Password", { exact: true })).toBeFocused();
  await page.screenshot({ path: info.outputPath("sign-in.png"), fullPage: true });
});

test("stored browser roles cannot bypass sign-in or server permissions", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("ayudachain_role", "Barangay Officer"));
  await page.goto("/distributions");
  await expect(page.getByRole("heading", { name: "Sign in to continue" })).toBeVisible();
  const result = await page.context().request.post(API + "/api/distributions/confirm", { headers: { "X-Demo-Actor-ID": "demo-disbursing-001", "X-AyudaChain-Client": "web", Origin: "http://127.0.0.1:3101" }, data: { beneficiary_id: "BEN-0004", batch_id: "RELIEF-2026-001", amount: 5000 } });
  expect(result.status()).toBe(401);
});
