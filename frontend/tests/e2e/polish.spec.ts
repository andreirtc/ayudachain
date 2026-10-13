import { API, BASE_URL } from "./support";
import { test, expect, Page } from "./support";

test.beforeEach(async ({ page }) => {
  await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, (route) => {
    const url = new URL(route.request().url());
    url.hostname = "127.0.0.1";
    url.port = new URL(API).port;
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
async function nav(page: Page, phone: boolean) {
  return page.getByRole("navigation", {
    name: phone ? "Mobile navigation" : "Main navigation",
    exact: true,
  });
}

test("public entry has clear copy, keyboard navigation and reduced motion", async ({
  page,
}, info) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await expect(
    page.getByRole("heading", {
      name: "Relief, with a clear record.",
      exact: true,
    }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Explore demo", exact: false }).click();
  await expect(
    page.getByRole("heading", { name: "Relief overview", exact: true }),
  ).toBeVisible();
  await expect(page.getByText("AyudaChain · Synthetic demo", { exact: true })).toBeVisible();
  const phone = info.project.name === "phone";
  const navigation = await nav(page, phone);
  await expect(
    navigation.getByRole("link", { name: "Households", exact: true }),
  ).toHaveCount(0);
  await expect(
    navigation.getByRole("link", { name: "Payouts", exact: true }),
  ).toHaveCount(0);
  const receiptLink = navigation.getByRole("link", { name: "Receipts", exact: true });
  await receiptLink.focus();
  await expect(receiptLink).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("heading", { name: "Check a receipt", exact: true }),
  ).toBeVisible();
  await expect(receiptLink).toHaveAttribute("aria-current", "page");
  await page
    .getByRole("link", { name: "Skip to content", exact: true })
    .focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("main")).toBeFocused();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  const motion = await page.evaluate(() => {
    const node = document.createElement("span");
    node.className = "pulse-dot";
    document.querySelector("main")!.appendChild(node);
    const name = getComputedStyle(node).animationName;
    node.remove();
    return name;
  });
  expect(motion).toBe("none");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: info.outputPath("compact-verification.png"),
    fullPage: false,
  });
});

test("all five authenticated roles get relevant navigation and Barangay remains denied payout access", async ({
  page,
}, info) => {
  for (const [account, ownHousehold] of [
    ["demo-officer-01", false],
    ["demo-barangay-01", false],
    ["demo-disbursing-001", false],
    ["demo-beneficiary-01", true],
    ["demo-auditor-01", false],
  ] as const) {
    await login(page, account);
    const navigation = await nav(page, info.project.name === "phone");
    await expect(
      navigation.getByRole("link", {
        name: ownHousehold ? "Home" : "Households",
        exact: true,
      }),
    ).toBeVisible();
    if (account === "demo-barangay-01")
      await expect(
        navigation.getByRole("link", { name: "Payouts", exact: true }),
      ).toHaveCount(0);
    else
      await expect(
        navigation.getByRole("link", {
          name: "Payouts",
          exact: true,
        }),
      ).toBeVisible();
    if (info.project.name === "phone") await page.keyboard.press("Escape");
    if (account === "demo-barangay-01") {
      await page.goto("/distributions");
      await expect(
        page.getByRole("heading", {
          name: "Payout records are outside your role",
          exact: true,
        }),
      ).toBeVisible();
    }
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
    await expect(
      page.getByRole("heading", { name: "Sign in to continue", exact: true }),
    ).toBeVisible();
  }
});

test("overview uses API totals with truthful payout labels and retained refresh errors", async ({
  page,
}, info) => {
  await page.goto("/dashboard");
  const snapshot = await (
    await page.context().request.get(API + "/api/dashboard")
  ).json();
  await expect(
    page.getByRole("region", { name: "Recorded funding" }),
  ).toContainText("Recorded payouts");
  await expect(page.getByRole("region", { name: "Household and payout counts" }).getByText(String(snapshot.confirmed_distributions), { exact: true })).toBeVisible();
  await expect(page.getByText("100% assigned", { exact: false })).toHaveCount(
    0,
  );
  await expect(
    page.getByText("household receipts verified", { exact: false }),
  ).toHaveCount(0);
  await page.route(/8000\/api\/dashboard$/, (route) => route.abort(), {
    times: 1,
  });
  await page
    .getByRole("button", { name: "Refresh overview", exact: true })
    .click();
  await expect(page.getByRole("main").getByRole("alert")).toContainText(
    "Totals below are from the previous successful read",
  );
  await page
    .getByRole("button", { name: "Retry overview", exact: true })
    .click();
  await expect(page.getByRole("main").getByRole("alert")).toHaveCount(0);
  await expect(
    page.getByRole("region", { name: "Recorded funding" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: info.outputPath("overview.png"),
    fullPage: false,
  });
});

test("batch allocations fit phones and loading errors offer retry without anchor claims", async ({
  page,
}, info) => {
  await page.route(
    /8000\/api\/batches\/RELIEF-2026-001$/,
    (route) => route.abort(),
    { times: 1 },
  );
  await page.goto("/batch/RELIEF-2026-001");
  await expect(
    page.getByRole("heading", {
      name: "Batch details unavailable",
      exact: true,
    }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Retry batch details", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Typhoon Salinlahi", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Barangay allocations" }),
  ).toBeVisible();
  await expect(
    page.getByText("formally initialized and anchored", { exact: false }),
  ).toHaveCount(0);
  await page.getByText("Batch details and references", { exact: true }).click();
  await expect(
    page.getByText("Stored transaction references do not establish current blockchain evidence.", {
      exact: false,
    }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: info.outputPath("batch.png"),
    fullPage: false,
  });
});
