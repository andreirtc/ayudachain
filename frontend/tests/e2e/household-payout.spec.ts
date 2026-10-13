import { test, expect, Page } from "@playwright/test";

const API = "http://127.0.0.1:8101";
test.beforeEach(async ({ page }) => {
  await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, (route) => {
    const url = new URL(route.request().url());
    url.hostname = "127.0.0.1";
    url.port = "8101";
    return route.continue({ url: url.toString() });
  });
});

async function login(page: Page, account: string) {
  await page.goto("/sign-in");
  await page.getByRole("textbox", { name: "Account", exact: true }).fill(account);
  await page.getByLabel("Password", { exact: true }).fill("synthetic-test-password-only");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByText("Authenticated synthetic account.", { exact: false })).toBeVisible();
}

async function mutationHeaders(page: Page) {
  const session = await (await page.context().request.get(API + "/api/auth/session")).json();
  return { "X-AyudaChain-Client": "web", "X-CSRF-Token": session.csrf_token, Origin: "http://127.0.0.1:3101" };
}

async function fixture(page: Page, id: string, name: string, approved: boolean, area = "BRGY-001") {
  const headers = await mutationHeaders(page);
  const created = await page.context().request.post(API + "/api/beneficiaries", {
    headers,
    data: { beneficiary_id: id, household_name: name, barangay_id: area, barangay_name: area === "BRGY-001" ? "San Isidro" : "Santa Elena", batch_id: "RELIEF-2026-001" },
  });
  expect(created.status()).toBe(201);
  if (approved) {
    const reviewed = await page.context().request.post(API + "/api/beneficiaries/" + encodeURIComponent(id) + "/verify", {
      headers, data: { status: "VERIFIED", review_notes: "Synthetic household handoff fixture reviewed" },
    });
    expect(reviewed.status()).toBe(200);
  }
}

function href(id: string) {
  return "/distributions?" + new URLSearchParams({ beneficiary_id: id });
}

test("household links filter exact IDs, survive refresh, and open only that receipt", async ({ page }, info) => {
  await login(page, "demo-auditor-01");
  const records = await (await page.context().request.get(API + "/api/distributions")).json();
  const activeHouseholds = await (await page.context().request.get(API + "/api/beneficiaries")).json();
  const target = records.find((row: { beneficiary_id: string }) =>
    activeHouseholds.some((household: { beneficiary_id: string }) => household.beneficiary_id === row.beneficiary_id),
  );
  expect(target).toBeTruthy();
  const expected = records.filter((row: { beneficiary_id: string }) => row.beneficiary_id === target.beneficiary_id);
  await page.goto("/beneficiaries");
  await page.getByLabel("Search households", { exact: true }).fill(target.beneficiary_id);
  await page.getByRole("button", { name: /^Inspect / }).click();
  const link = page.getByRole("link", { name: "View payout records", exact: true });
  expect(new URL((await link.getAttribute("href"))!, page.url()).searchParams.get("beneficiary_id")).toBe(target.beneficiary_id);
  await link.click();
  const list = page.getByRole("region", { name: "Recorded payouts" });
  await expect(list.locator("li.workflow-record")).toHaveCount(expected.length);
  for (const row of expected) await expect(list.getByText(row.distribution_id, { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Refresh", exact: true }).click();
  await expect(list.locator("li.workflow-record")).toHaveCount(expected.length);
  await page.reload();
  await expect(list.locator("li.workflow-record")).toHaveCount(expected.length);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: info.outputPath("household-payout-records.png"), fullPage: true });
  await list.getByRole("link", { name: "Check receipt", exact: true }).first().click();
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(expected[0].distribution_id);
  await page.goto(href(target.beneficiary_id));
  await page.getByRole("link", { name: "View all permitted payouts", exact: true }).click();
  await expect(list.locator("li.workflow-record")).toHaveCount(records.length);
});

test("unknown, empty and out-of-scope references never select or reveal another household", async ({ page }, info) => {
  await login(page, "demo-officer-01");
  const outside = "BEN-HANDOFF-OUTSIDE-" + info.project.name;
  await fixture(page, outside, "Synthetic outside-scope " + info.project.name, true, "BRGY-002");
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "demo-disbursing-001");
  for (const id of ["BEN-HANDOFF-MISSING", "", outside]) {
    await page.goto(href(id));
    await expect(page.getByRole("heading", { name: "Household unavailable", exact: true })).toBeVisible();
    await expect(page.getByLabel("Household", { exact: true })).toHaveCount(0);
    await expect(page.getByRole("region", { name: "Recorded payouts" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Record demo payout", exact: true })).toHaveCount(0);
    await expect(page.getByText("Synthetic outside-scope " + info.project.name, { exact: true })).toHaveCount(0);
  }
  await page.getByRole("link", { name: "Choose another household", exact: true }).click();
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue("");
  await expect(page.getByRole("button", { name: "Record demo payout", exact: true })).toBeDisabled();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "demo-beneficiary-01");
  await page.goto(href(outside));
  await expect(page.getByRole("heading", { name: "Household unavailable", exact: true })).toBeVisible();
  await page.goto(href("BEN-0004"));
  await expect(page.getByRole("region", { name: "Household payout context" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Household unavailable", exact: true })).toHaveCount(0);
});

test("linked household entry preserves API eligibility, exact amount and one payout", async ({ page }, info) => {
  await login(page, "demo-officer-01");
  const id = "BEN-HANDOFF ?&#+ " + info.project.name;
  const pending = "BEN-HANDOFF-PENDING-" + info.project.name;
  await fixture(page, id, "Synthetic same-name handoff " + info.project.name, true);
  await fixture(page, pending, "Synthetic same-name handoff " + info.project.name, false);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "demo-disbursing-001");
  await page.goto(href(pending));
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue(pending);
  await expect(page.getByText("This household needs DSWD approval before payout.", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Record demo payout", exact: true })).toBeDisabled();
  await page.goto(href(id));
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue(id);
  await expect(page.getByLabel("Household", { exact: true })).toBeDisabled();
  await page.getByLabel("Fictional amount (PHP)").fill("100.25");
  await page.route(/8000\/api\/beneficiaries\?/, (route) => route.abort(), { times: 1 });
  await page.getByRole("button", { name: "Refresh", exact: true }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Previously loaded records are hidden");
  await expect(page.getByRole("button", { name: "Record demo payout", exact: true })).toBeDisabled();
  await page.getByRole("button", { name: "Refresh records", exact: true }).click();
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue(id);
  await expect(page.getByLabel("Fictional amount (PHP)")).toHaveValue("100.25");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: info.outputPath("household-payout-entry.png"), fullPage: true });
  await page.getByRole("button", { name: "Record demo payout", exact: true }).click();
  await expect(page.getByRole("link", { name: "Check this receipt", exact: true })).toBeVisible();
  const records = await (await page.context().request.get(API + "/api/distributions")).json();
  const saved = records.filter((row: { beneficiary_id: string }) => row.beneficiary_id === id);
  expect(saved).toHaveLength(1);
  expect(saved[0].amount_centavos).toBe(10025);
  await page.reload();
  await expect(page.getByText("A payout is already recorded for this household in this batch.", { exact: false })).toBeVisible();
  await expect(page.getByRole("button", { name: "Record demo payout", exact: true })).toBeDisabled();
  await page.getByRole("link", { name: "Open recorded receipt", exact: true }).click();
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(saved[0].distribution_id);
});

test("retained duplicate handoff keeps its original receipts and blocks new payouts", async ({ page }, info) => {
  await login(page, "demo-officer-01");
  const id = "BEN-HANDOFF-HISTORY-" + info.project.name;
  await fixture(page, id, "Synthetic retained handoff " + info.project.name, true);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "demo-disbursing-001");
  await page.goto(href(id));
  await page.getByLabel("Fictional amount (PHP)").fill("100");
  await page.getByRole("button", { name: "Record demo payout", exact: true }).click();
  const receipt = page.getByRole("link", { name: "Check this receipt", exact: true });
  await expect(receipt).toBeVisible();
  const receiptHref = await receipt.getAttribute("href");
  await page.getByRole("button", { name: "Record another payout", exact: true }).click();
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue("");
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "demo-officer-01");
  const result = await page.context().request.post(API + "/api/beneficiaries/" + id + "/resolve-duplicate", {
    headers: await mutationHeaders(page),
    data: { canonical_beneficiary_id: "BEN-0002", review_notes: "Synthetic duplicate resolution retaining the paid record" },
  });
  expect(result.status()).toBe(200);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "demo-disbursing-001");
  await page.goto("/beneficiaries");
  await page.getByText("More registry options", { exact: true }).click();
  await page.getByLabel("Include historical duplicates").check();
  await page.getByLabel("Search households", { exact: true }).fill(id);
  await page.getByRole("button", { name: "Inspect Synthetic retained handoff " + info.project.name, exact: true }).click();
  await page.getByRole("link", { name: "View payout records", exact: true }).click();
  await expect(page.getByText("This retained duplicate cannot receive a new payout.", { exact: false })).toBeVisible();
  await expect(page.getByRole("button", { name: "Record demo payout", exact: true })).toBeDisabled();
  const list = page.getByRole("region", { name: "Recorded payouts" });
  await expect(list.locator("li.workflow-record")).toHaveCount(1);
  await expect(list.getByRole("link", { name: "Check receipt", exact: true })).toHaveAttribute("href", receiptHref!);
});
