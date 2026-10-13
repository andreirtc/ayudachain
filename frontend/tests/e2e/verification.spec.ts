import { API, BASE_URL } from "./support";
import { test, expect } from "./support";

test.beforeEach(async ({ page }) => {
  await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, (route) => {
    const url = new URL(route.request().url());
    url.hostname = "127.0.0.1";
    url.port = new URL(API).port;
    return route.continue({ url: url.toString() });
  });
});

test("manual references preserve not-found behavior and offline checks stay explicit", async ({
  page,
}, info) => {
  let requests = 0;
  page.on("request", (request) => {
    if (request.url().endsWith("/api/blockchain/verify")) requests++;
  });
  await page.goto("/verify?distribution_id=DIST-UNKNOWN");
  await expect(
    page.getByRole("heading", { name: "Receipt not found", exact: true }),
  ).toBeVisible();
  expect(requests).toBe(0);
  await page.getByText("Enter a receipt reference", { exact: true }).click();
  await page.getByLabel("Receipt reference", { exact: true }).fill("DIST-0001");
  await page.getByRole("button", { name: "Open receipt", exact: true }).click();
  await expect(
    page.getByRole("heading", {
      name: "Verification unavailable",
      exact: true,
    }),
  ).toBeVisible();
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(
    "DIST-0001",
  );
  await expect(
    page.getByLabel("Receipt reference", { exact: true }),
  ).toHaveValue("DIST-0001");
  await expect(page.getByText("Roberto Ramos", { exact: true })).toHaveCount(0);
  const beforeOffline = requests;
  await page.context().setOffline(true);
  await expect(
    page.getByText("The displayed result is from an earlier check.", {
      exact: false,
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Check again", exact: true }),
  ).toBeDisabled();
  await page.context().setOffline(false);
  await expect(
    page.getByRole("button", { name: "Check again", exact: true }),
  ).toBeEnabled();
  expect(requests).toBe(beforeOffline);
  await page.getByRole("button", { name: "Check again", exact: true }).click();
  await expect(
    page.getByRole("heading", {
      name: "Verification unavailable",
      exact: true,
    }),
  ).toBeVisible();
  expect(requests).toBe(beforeOffline + 1);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: info.outputPath("verification-unavailable.png"),
    fullPage: false,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test("lookup failures retain receipt context and repeated retry clicks send one lookup", async ({
  page,
}) => {
  await page.route(/8000\/api\/blockchain\/verify$/, (route) => route.abort(), {
    times: 1,
  });
  await page.goto("/verify?distribution_id=DIST-0001");
  const result = page.getByRole("region", { name: "Verification result" });
  await expect(result.getByRole("alert")).toBeVisible();
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(
    "DIST-0001",
  );
  await expect(
    page
      .getByRole("region", { name: "Receipt details" })
      .getByText("DIST-0001", { exact: true }),
  ).toBeVisible();
  let release!: () => void;
  const waiting = new Promise<void>((resolve) => {
    release = resolve;
  });
  let requests = 0;
  await page.route(
    /8000\/api\/blockchain\/verify$/,
    async (route) => {
      requests++;
      await waiting;
      await route.fallback();
    },
    { times: 1 },
  );
  await result
    .getByRole("button", { name: "Retry lookup", exact: true })
    .evaluate((button: HTMLButtonElement) => {
      button.click();
      button.click();
    });
  await expect(
    page.getByText("Reading the blockchain receipt...", { exact: true }),
  ).toBeVisible();
  release();
  await expect(
    page.getByRole("heading", {
      name: "Verification unavailable",
      exact: true,
    }),
  ).toBeVisible();
  expect(requests).toBe(1);
});

test("a late actual lookup cannot overwrite the selected receipt's evidence", async ({
  page,
}) => {
  let release!: () => void;
  const waiting = new Promise<void>((resolve) => {
    release = resolve;
  });
  let delivered!: () => void;
  const delivery = new Promise<void>((resolve) => {
    delivered = resolve;
  });
  await page.route(
    /8000\/api\/blockchain\/verify$/,
    async (route) => {
      const actualResponse = await route.fetch({
        url: API + "/api/blockchain/verify",
      });
      await waiting;
      await route.fulfill({ response: actualResponse });
      delivered();
    },
    { times: 1 },
  );
  await page.goto("/verify?distribution_id=DIST-0001");
  await expect(
    page.getByText("Reading the blockchain receipt...", { exact: true }),
  ).toBeVisible();
  const [response] = await Promise.all([
    page.waitForResponse((r) => r.url().endsWith("/api/blockchain/verify")),
    page.getByLabel("Receipt", { exact: true }).selectOption("DIST-0002"),
  ]);
  const evidence = await response.json();
  expect(evidence.record_id).toBe("DIST-0002");
  await page
    .getByText("Hash comparison and lookup details", { exact: true })
    .click();
  const result = page.getByRole("region", { name: "Verification result" });
  await expect(
    result.getByText(evidence.receipt_hash_local, { exact: true }),
  ).toBeVisible();
  release();
  await delivery;
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(
    "DIST-0002",
  );
  await expect(
    result.getByText(evidence.receipt_hash_local, { exact: true }),
  ).toBeVisible();
});

test("receipt index failures have their own retry without a fabricated proof result", async ({
  page,
}) => {
  await page.route(/8000\/api\/public\/receipts$/, (route) => route.abort(), {
    times: 1,
  });
  await page.goto("/verify?distribution_id=DIST-0001");
  await expect(
    page.getByRole("region", { name: "Choose a receipt" }).getByRole("alert"),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Verification result" }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Retry loading receipts", exact: true })
    .click();
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(
    "DIST-0001",
  );
  await expect(
    page.getByRole("heading", {
      name: "Verification unavailable",
      exact: true,
    }),
  ).toBeVisible();
});
