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
  await page
    .getByRole("textbox", { name: "Account", exact: true })
    .fill(account);
  await page
    .getByLabel("Password", { exact: true })
    .fill("synthetic-test-password-only");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByText("Authenticated synthetic account.", { exact: false }),
  ).toBeVisible();
}
async function headers(page: Page) {
  const session = await (
    await page.context().request.get(API + "/api/auth/session")
  ).json();
  return {
    "X-AyudaChain-Client": "web",
    "X-CSRF-Token": session.csrf_token,
    Origin: "http://127.0.0.1:3101",
  };
}

test("readers see payout records without an entry form and get search/refresh feedback", async ({
  page,
}) => {
  await login(page, "demo-auditor-01");
  await page.goto("/distributions");
  await expect(
    page.getByRole("heading", { name: "Payout records", exact: true }),
  ).toBeVisible();
  await expect(page.getByLabel("Household", { exact: true })).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Record demo payout", exact: true }),
  ).toHaveCount(0);
  await page.getByLabel("Search payout records").fill("no-such-receipt");
  await expect(
    page.getByRole("heading", { name: "No matching payouts" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Clear search" }).click();
  await page.route(/8000\/api\/distributions$/, (route) => route.abort(), {
    times: 1,
  });
  await page.getByRole("button", { name: "Refresh", exact: true }).click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText(
    "Previously loaded records are hidden",
  );
  await page
    .getByRole("button", { name: "Refresh records", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "View receipt", exact: true }).first(),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test("entry uses actual batch/allocation limits and rejects pending households", async ({
  page,
}, info) => {
  await login(page, "demo-officer-01");
  const mutationHeaders = await headers(page);
  const suffix = info.project.name;
  const batchId = "RELIEF-UI-BUDGET-" + suffix;
  expect(
    (
      await page
        .context()
        .request.post(API + "/api/funds/releases", {
          headers: mutationHeaders,
          data: {
            batch_id: batchId,
            calamity_name: "Synthetic UI budget test",
            amount: 600,
            standard_grant: 500,
            max_grant: 500,
          },
        })
    ).status(),
  ).toBe(201);
  expect(
    (
      await page
        .context()
        .request.post(API + "/api/allocations", {
          headers: mutationHeaders,
          data: {
            allocation_id: "ALLOC-UI-" + suffix,
            batch_id: batchId,
            barangay_id: "BRGY-001",
            barangay_name: "San Isidro",
            amount: 300,
          },
        })
    ).status(),
  ).toBe(201);
  const beneficiaryId = "BEN-UI-BUDGET-" + suffix;
  expect(
    (
      await page
        .context()
        .request.post(API + "/api/beneficiaries", {
          headers: mutationHeaders,
          data: {
            beneficiary_id: beneficiaryId,
            household_name: "Synthetic budget household " + suffix,
            barangay_id: "BRGY-001",
            barangay_name: "San Isidro",
            batch_id: batchId,
          },
        })
    ).status(),
  ).toBe(201);
  const pendingId = "BEN-UI-PENDING-" + suffix;
  expect(
    (
      await page
        .context()
        .request.post(API + "/api/beneficiaries", {
          headers: mutationHeaders,
          data: {
            beneficiary_id: pendingId,
            household_name: "Synthetic budget household " + suffix,
            barangay_id: "BRGY-001",
            barangay_name: "San Isidro",
            batch_id: batchId,
          },
        })
    ).status(),
  ).toBe(201);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "demo-disbursing-001");
  const submit = page.getByRole("button", {
    name: "Record demo payout",
    exact: true,
  });
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue("");
  await expect(submit).toBeDisabled();
  await page
    .getByLabel("Household", { exact: true })
    .selectOption(beneficiaryId);
  await expect(page.getByLabel("Fictional amount (PHP)")).toHaveValue("500");
  await expect(page.getByText("₱300.00", { exact: true })).toBeVisible();
  await expect(
    page.getByText("The amount exceeds the remaining recorded allocation.", {
      exact: true,
    }),
  ).toBeVisible();
  await expect(submit).toBeDisabled();
  await page.getByLabel("Fictional amount (PHP)").fill("250.001");
  await expect(
    page.getByText("Enter a positive amount with up to two decimal places.", {
      exact: true,
    }),
  ).toBeVisible();
  await expect(submit).toBeDisabled();
  await page.getByLabel("Fictional amount (PHP)").fill("250.50");
  await expect(submit).toBeEnabled();
  await page.getByLabel("Household", { exact: true }).selectOption(pendingId);
  await expect(
    page.getByText("This household needs DSWD approval before payout.", {
      exact: true,
    }),
  ).toBeVisible();
  await expect(submit).toBeDisabled();
  await page
    .getByLabel("Household", { exact: true })
    .selectOption(beneficiaryId);
  await page.getByLabel("Fictional amount (PHP)").fill("250.50");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: info.outputPath("payout-entry.png"),
    fullPage: false,
  });
});

test("lost payout response retains input and retries one saved payout with the same request key", async ({
  page,
}, info) => {
  await login(page, "demo-officer-01");
  const beneficiaryId = "BEN-UI-RETRY-" + info.project.name;
  const mutationHeaders = await headers(page);
  expect(
    (
      await page
        .context()
        .request.post(API + "/api/beneficiaries", {
          headers: mutationHeaders,
          data: {
            beneficiary_id: beneficiaryId,
            household_name: "Synthetic retry household " + info.project.name,
            barangay_id: "BRGY-001",
            barangay_name: "San Isidro",
            batch_id: "RELIEF-2026-001",
          },
        })
    ).status(),
  ).toBe(201);
  expect(
    (
      await page
        .context()
        .request.post(API + "/api/beneficiaries/" + beneficiaryId + "/verify", {
          headers: mutationHeaders,
          data: {
            status: "VERIFIED",
            review_notes: "Distinct synthetic retry fixture reviewed",
          },
        })
    ).status(),
  ).toBe(200);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await login(page, "demo-disbursing-001");
  await page
    .getByLabel("Household", { exact: true })
    .selectOption(beneficiaryId);
  await page.getByLabel("Fictional amount (PHP)").fill("1200.50");
  const keys: string[] = [];
  page.on("request", (request) => {
    if (request.url().endsWith("/api/distributions/confirm"))
      keys.push(request.headers()["idempotency-key"]);
  });
  await page.route(
    /8000\/api\/distributions\/confirm$/,
    async (route) => {
      const response = await route.fetch({
        url: API + "/api/distributions/confirm",
      });
      expect(response.status()).toBe(201);
      await route.abort(); // The real API saved it; the browser did not receive the response.
    },
    { times: 1 },
  );
  await page
    .getByRole("button", { name: "Record demo payout", exact: true })
    .click();
  await expect(
    page.getByRole("region", { name: "Payout entry" }).getByRole("alert"),
  ).toBeVisible();
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue(
    beneficiaryId,
  );
  await expect(page.getByLabel("Fictional amount (PHP)")).toHaveValue(
    "1200.50",
  );
  await page
    .getByRole("button", { name: "Retry payout request", exact: true })
    .evaluate((element: HTMLButtonElement) => {
      element.click();
      element.click();
    });
  await expect(
    page.getByRole("link", { name: "Check this receipt", exact: true }),
  ).toBeVisible();
  expect(keys).toHaveLength(2);
  expect(keys[0]).toBeTruthy();
  expect(keys[1]).toBe(keys[0]);
  const records = await (
    await page.context().request.get(API + "/api/distributions")
  ).json();
  const saved = records.filter(
    (row: { beneficiary_id: string }) => row.beneficiary_id === beneficiaryId,
  );
  expect(saved).toHaveLength(1);
  expect(saved[0].amount_centavos).toBe(120050);
  expect(saved[0].anchor_job.attempts).toBe(1);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: info.outputPath("payout-saved.png"),
    fullPage: false,
  });
  await page
    .getByRole("button", { name: "Record another payout", exact: true })
    .click();
  await expect(page.getByLabel("Household", { exact: true })).toHaveValue("");
  await page
    .getByLabel("Household", { exact: true })
    .selectOption(beneficiaryId);
  await expect(
    page.getByText(
      "A payout is already recorded for this household in this batch.",
      { exact: false },
    ),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Record demo payout", exact: true }),
  ).toBeDisabled();
});
