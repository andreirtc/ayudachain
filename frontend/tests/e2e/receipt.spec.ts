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

test("payout receipt dialog is keyboard accessible and links to its exact record", async ({
  page,
}, info) => {
  await login(page, "demo-disbursing-001");
  const records = await (await page.context().request.get(API + "/api/distributions")).json();
  const noImage = records.find((row: { receipt_file_path: string | null }) => !row.receipt_file_path);
  expect(noImage).toBeTruthy();
  const open = page.getByRole("region", { name: "Recorded payouts", exact: true }).locator("li.workflow-record").filter({ hasText: noImage.distribution_id }).getByRole("button", { name: "View receipt", exact: true });
  await open.click();
  const dialog = page.getByRole("dialog");
  await expect(
    dialog.getByRole("heading", { name: "Payout receipt", exact: true }),
  ).toBeFocused();
  const details = dialog.getByRole("region", { name: "Receipt details" });
  await expect(
    details.getByText("No household receipt image is available", {
      exact: false,
    }),
  ).toBeVisible();
  await expect(
    details.getByText("does not verify identity or prove cash delivery", {
      exact: false,
    }),
  ).toBeVisible();
  const href = await dialog
    .getByRole("link", { name: "Check this receipt", exact: true })
    .getAttribute("href");
  const id = new URL(href!, "http://127.0.0.1:3101").searchParams.get(
    "distribution_id",
  )!;
  await expect(details.locator(":scope > dl").getByText(id, { exact: true })).toBeVisible();
  expect(
    await dialog.evaluate(
      (element) => element.scrollWidth <= element.clientWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: info.outputPath("receipt-dialog.png"),
    fullPage: false,
  });
  await dialog
    .getByRole("button", { name: "Back to payouts", exact: true })
    .focus();
  await page.keyboard.press("Tab");
  await expect(
    dialog.getByRole("button", { name: "Close payout receipt", exact: true }),
  ).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  await expect(open).toBeFocused();
  await open.click();
  await dialog
    .getByRole("link", { name: "Check this receipt", exact: true })
    .click();
  await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(id);
  await expect(
    page
      .getByRole("region", { name: "Receipt details" })
      .locator(":scope > dl")
      .getByText(id, { exact: true }),
  ).toBeVisible();
});

test("office receipt image shows shared-template limits, inline failure and a real retry", async ({
  page,
}, info) => {
  await login(page, "demo-officer-01");
  await page.goto("/verify?distribution_id=DIST-0001");
  const details = page.getByRole("region", { name: "Receipt details" });
  await expect(
    details.getByRole("heading", { name: "Roberto Ramos", exact: true }),
  ).toBeVisible();
  await page.route(
    /8000\/receipts\/sample_relief_receipt.svg$/,
    (route) => route.abort(),
    { times: 1 },
  );
  await details.getByText("Saved receipt image", { exact: true }).click();
  await expect(
    details.getByText("Shared demo template.", { exact: true }),
  ).toBeVisible();
  await expect(details.getByRole("alert")).toContainText(
    "The receipt image could not be loaded",
  );
  const [response] = await Promise.all([
    page.waitForResponse((r) =>
      r.url().endsWith("/receipts/sample_relief_receipt.svg"),
    ),
    details.getByRole("button", { name: "Retry image", exact: true }).click(),
  ]);
  expect(response.status()).toBe(200);
  const image = details.getByAltText("Shared fictional receipt template");
  await expect(image).toBeVisible();
  await expect
    .poll(() =>
      image.evaluate((element: HTMLImageElement) => element.naturalWidth),
    )
    .toBeGreaterThan(0);
  await details.getByText("Saved extracted text", { exact: true }).click();
  await expect(details.locator("pre")).toBeVisible();
  await details.getByText("Saved receipt image", { exact: true }).click();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: info.outputPath("receipt-page.png"),
    fullPage: false,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test("public and household readers retain restricted receipt representations", async ({
  page,
}) => {
  await page.goto("/verify?distribution_id=DIST-0001");
  const details = page.getByRole("region", { name: "Receipt details" });
  await expect(details.getByText("DIST-0001", { exact: true })).toBeVisible();
  await expect(page.getByText("Roberto Ramos", { exact: true })).toHaveCount(0);
  await expect(
    page.getByText("Saved receipt image", { exact: true }),
  ).toHaveCount(0);
  expect(
    (
      await page
        .context()
        .request.get(API + "/receipts/sample_relief_receipt.svg")
    ).status(),
  ).toBe(401);
  await login(page, "demo-beneficiary-01");
  await page.goto("/verify?distribution_id=DIST-0001");
  await expect(
    page.getByRole("heading", { name: "Receipt not found", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Receipt details" }),
  ).toHaveCount(0);
  expect(
    (
      await page
        .context()
        .request.get(API + "/receipts/sample_relief_receipt.svg")
    ).status(),
  ).toBe(404);
});
