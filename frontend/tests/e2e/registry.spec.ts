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
async function switchAccount(page: Page, account: string) {
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Sign in to continue" }),
  ).toBeVisible();
  await login(page, account);
}
async function register(page: Page, name: string) {
  await page
    .getByRole("button", { name: "Register a household", exact: true })
    .click();
  await page.getByLabel("Household Head Full Name").fill(name);
  const [response] = await Promise.all([
    page.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        r.url().endsWith("/api/beneficiaries"),
    ),
    page
      .getByRole("button", { name: "Register household", exact: true })
      .click(),
  ]);
  expect(response.ok()).toBe(true);
  await expect(
    page.getByText("Household registered.", { exact: true }),
  ).toBeVisible();
  return response.json();
}
async function fits(page: Page) {
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  const dialog = page.getByRole("dialog");
  if (await dialog.count())
    expect(
      await dialog.evaluate((el) => el.scrollWidth <= el.clientWidth),
    ).toBe(true);
}

test("registry exposes loading, retry, empty search and readable scoped list", async ({
  page,
}, info) => {
  let release!: () => void;
  const waiting = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(
    /8000\/api\/beneficiaries\?/,
    async (route) => {
      await waiting;
      await route.fallback();
    },
    { times: 1 },
  );
  await login(page, "demo-officer-01");
  await expect(
    page.getByText("Loading households...", { exact: true }),
  ).toBeVisible();
  release();
  await expect(
    page.getByRole("button", { name: "Review Juan D. Cruz", exact: true }),
  ).toBeVisible();
  await page.route(/8000\/api\/beneficiaries\?/, (route) => route.abort(), {
    times: 1,
  });
  await page.getByRole("button", { name: "Refresh", exact: true }).click();
  await expect(
    page.getByRole("region", { name: "Household list" }).getByRole("alert"),
  ).toContainText("The list could not be refreshed");
  await expect(
    page.getByRole("button", { name: "Review Juan D. Cruz", exact: true }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Retry loading households" }).click();
  await expect(
    page.getByRole("button", { name: "Review Juan D. Cruz", exact: true }),
  ).toBeVisible();
  await page
    .getByLabel("Search households", { exact: true })
    .fill("no-such-synthetic-household");
  await expect(
    page.getByRole("heading", { name: "No matching households" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Clear filters" }).click();
  await page.getByRole("button", { name: /Needs review/ }).click();
  await expect(
    page.getByRole("button", { name: /Needs review/ }),
  ).toHaveAttribute("aria-pressed", "true");
  await fits(page);
  await page.screenshot({
    path: info.outputPath("registry.png"),
    fullPage: true,
  });
});

test("registration retains input, blocks offline and repeated submits, and manages focus", async ({
  page,
}, info) => {
  await login(page, "demo-barangay-01");
  const opener = page.getByRole("button", {
    name: "Register a household",
    exact: true,
  });
  await opener.click();
  await expect(page.getByLabel("Household Head Full Name")).toBeFocused();
  await page
    .getByLabel("Household Head Full Name")
    .fill("Synthetic focus household " + info.project.name);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(opener).toBeFocused();
  await opener.click();
  const name = "Synthetic focus household " + info.project.name;
  await expect(page.getByLabel("Household Head Full Name")).toHaveValue(name);
  await page.context().setOffline(true);
  await expect(
    page.getByRole("button", { name: "Register household", exact: true }),
  ).toBeDisabled();
  await page.context().setOffline(false);
  await expect(
    page.getByRole("button", { name: "Register household", exact: true }),
  ).toBeEnabled();
  await page.route(/8000\/api\/beneficiaries$/, (route) => route.abort(), {
    times: 1,
  });
  await page
    .getByRole("button", { name: "Register household", exact: true })
    .click();
  await expect(page.getByRole("dialog").getByRole("alert")).toBeVisible();
  await expect(page.getByLabel("Household Head Full Name")).toHaveValue(name);
  let release!: () => void;
  const waiting = new Promise<void>((resolve) => {
    release = resolve;
  });
  let requests = 0;
  await page.route(
    /8000\/api\/beneficiaries$/,
    async (route) => {
      requests++;
      await waiting;
      await route.fallback();
    },
    { times: 1 },
  );
  await page
    .getByRole("button", { name: "Register household", exact: true })
    .evaluate((el: HTMLButtonElement) => {
      el.click();
      el.click();
    });
  await expect(
    page.getByRole("button", { name: "Registering...", exact: true }),
  ).toBeDisabled();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toBeVisible();
  release();
  await expect(
    page.getByText("Household registered.", { exact: true }),
  ).toBeVisible();
  expect(requests).toBe(1);
  await expect(
    page.getByRole("dialog").getByText("Pending review", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Approve household" }),
  ).toHaveCount(0);
  await fits(page);
  await page.screenshot({
    path: info.outputPath("registration.png"),
    fullPage: true,
  });
  await page
    .getByRole("button", { name: "Back to households", exact: true })
    .focus();
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("button", { name: "Close household details" }),
  ).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(
    page.getByRole("button", { name: "Back to households", exact: true }),
  ).toBeFocused();
});

test("barangay registration connects to DSWD decisions, a payout and its exact receipt", async ({
  page,
}, info) => {
  await login(page, "demo-barangay-01");
  const name = "Synthetic journey " + info.project.name;
  const created = await register(page, name);
  expect(created.review_status).toBe("PENDING");
  expect(created.duplicate_flag).toBe(false);
  await page
    .getByRole("button", { name: "Back to households", exact: true })
    .click();
  await switchAccount(page, "demo-officer-01");
  await page
    .getByLabel("Search households", { exact: true })
    .fill(created.beneficiary_id);
  await page
    .getByRole("button", { name: "Review " + name, exact: true })
    .click();
  const reason = page.getByLabel("Reason for decision");
  await reason.fill("Distinct synthetic household, evidence checked");
  await page.route(
    /8000\/api\/beneficiaries\/[^/]+\/verify$/,
    (route) => route.abort(),
    { times: 1 },
  );
  await page
    .getByRole("button", { name: "Approve household", exact: true })
    .click();
  await expect(page.getByRole("dialog").getByRole("alert")).toBeVisible();
  await expect(reason).toHaveValue(
    "Distinct synthetic household, evidence checked",
  );
  await page.context().setOffline(true);
  await expect(
    page.getByRole("button", { name: "Approve household", exact: true }),
  ).toBeDisabled();
  await page.context().setOffline(false);
  await page
    .getByRole("button", { name: "Keep for review", exact: true })
    .click();
  await expect(page.getByText("Review saved.", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "Back to households", exact: true })
    .click();
  await page.getByRole("button", { name: /Needs review/ }).click();
  await expect(
    page.getByRole("button", { name: "Review " + name, exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Review " + name, exact: true })
    .click();
  await reason.fill("Synthetic evidence remains insufficient");
  await page
    .getByRole("button", { name: "Reject household", exact: true })
    .click();
  await expect(
    page.getByRole("dialog").getByText("Rejected", { exact: true }),
  ).toBeVisible();
  await reason.fill("Additional synthetic evidence establishes eligibility");
  let release!: () => void;
  const waiting = new Promise<void>((resolve) => {
    release = resolve;
  });
  let requests = 0;
  await page.route(
    /8000\/api\/beneficiaries\/[^/]+\/verify$/,
    async (route) => {
      requests++;
      await waiting;
      await route.fallback();
    },
    { times: 1 },
  );
  await page
    .getByRole("button", { name: "Approve household", exact: true })
    .evaluate((el: HTMLButtonElement) => {
      el.click();
      el.click();
    });
  await expect(
    page.getByText("Saving review...", { exact: true }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toBeVisible();
  release();
  await expect(
    page.getByRole("dialog").getByText("Approved", { exact: true }),
  ).toBeVisible();
  expect(requests).toBe(1);
  await page.getByText(/Review history \(/).click();
  await expect(
    page
      .getByRole("list")
      .getByText("Additional synthetic evidence establishes eligibility", {
        exact: true,
      }),
  ).toBeVisible();
  const history = await page
    .context()
    .request.get(
      API + "/api/beneficiaries/" + created.beneficiary_id + "/reviews",
    );
  expect(await history.json()).toHaveLength(3);
  expect((await history.json())[0].reviewed_by).toBe("demo-officer-01");
  await fits(page);
  await page.screenshot({
    path: info.outputPath("review.png"),
    fullPage: true,
  });
  await page
    .getByRole("link", { name: "View payout records", exact: true })
    .click();
  await expect(page.getByText("Your signed-in role can inspect these records.", { exact: false })).toBeVisible();
  await expect(page.getByRole("button", { name: "Record demo payout", exact: true })).toHaveCount(0);
  await switchAccount(page, "demo-disbursing-001");
  await page
    .getByLabel("Household", { exact: true })
    .selectOption(created.beneficiary_id);
  await page
    .getByRole("button", { name: "Record demo payout", exact: true })
    .click();
  const receipt = page.getByRole("link", {
    name: "Check this receipt",
    exact: true,
  });
  await expect(receipt).toBeVisible();
  const href = await receipt.getAttribute("href");
  await receipt.click();
  await expect(
    page.getByRole("heading", {
      name: "Verification unavailable",
      exact: true,
    }),
  ).toBeVisible();
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(
    new URL(href!, page.url()).searchParams.get("distribution_id")!,
  );
});

test("duplicate decision retains history and original payouts behind historical options", async ({
  page,
}) => {
  await login(page, "demo-officer-01");
  const payoutsBefore = await (
    await page.context().request.get(API + "/api/distributions")
  ).json();
  const created = await register(page, "Juan Dela Cruz");
  await expect(
    page.getByRole("dialog").getByText("Possible duplicate", { exact: true }),
  ).toBeVisible();
  await page.getByText("Review evidence", { exact: true }).click();
  await expect(page.getByText(/Similarity: 100%/)).toBeVisible();
  await page
    .getByLabel("Reason for decision")
    .fill("Same fictional household, retain the original record and evidence");
  await page.getByText("Resolve as a duplicate", { exact: true }).click();
  await page.getByLabel("Keep household record").selectOption("BEN-0002");
  await page
    .getByRole("button", {
      name: "Mark duplicate and retain history",
      exact: true,
    })
    .click();
  await expect(
    page.getByRole("dialog").getByText("Retained duplicate", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Review saved.", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Approve household" }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Back to households", exact: true })
    .click();
  await page
    .getByLabel("Search households", { exact: true })
    .fill(created.beneficiary_id);
  await expect(
    page.getByRole("heading", { name: "No matching households" }),
  ).toBeVisible();
  await page.getByText("More registry options", { exact: true }).click();
  await page.getByLabel("Include historical duplicates").check();
  await expect(
    page.getByRole("button", { name: "Review Juan Dela Cruz", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Review Juan Dela Cruz", exact: true })
    .click();
  await page.getByText(/Review history \(/).click();
  await expect(
    page
      .getByRole("list")
      .getByText(
        "Same fictional household, retain the original record and evidence",
        { exact: true },
      ),
  ).toBeVisible();
  const payoutsAfter = await (
    await page.context().request.get(API + "/api/distributions")
  ).json();
  expect(payoutsAfter).toEqual(payoutsBefore);
  await fits(page);
});

test("CSV is secondary, keyboard accessible and analysis does not import households", async ({
  page,
}, info) => {
  await login(page, "demo-officer-01");
  const before = await (
    await page.context().request.get(API + "/api/beneficiaries")
  ).json();
  await expect(
    page.getByRole("button", { name: "Analyze a CSV", exact: true }),
  ).toBeHidden();
  await page.getByText("More registry options", { exact: true }).click();
  await page
    .getByRole("button", { name: "Analyze a CSV", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Analyze a CSV", exact: true }),
  ).toBeFocused();
  await page.route(
    /8000\/api\/beneficiaries\/upload-csv$/,
    (route) => route.abort(),
    { times: 1 },
  );
  await page
    .getByRole("button", { name: "Analyze sample CSV", exact: true })
    .click();
  await expect(page.getByRole("dialog").getByRole("alert")).toBeVisible();
  await page
    .getByLabel("Fictional CSV file")
    .setInputFiles("../backend/app/data/seed_beneficiaries.csv");
  await page
    .getByRole("button", { name: "Analyze selected CSV", exact: true })
    .click();
  await expect(
    page.getByRole("status").filter({ hasText: "records analyzed" }),
  ).toContainText("10 records analyzed");
  await expect(
    page.getByText("No records have been imported.", { exact: false }),
  ).toBeVisible();
  expect(
    await (await page.context().request.get(API + "/api/beneficiaries")).json(),
  ).toEqual(before);
  await fits(page);
  await page.screenshot({ path: info.outputPath("csv.png"), fullPage: true });
});
