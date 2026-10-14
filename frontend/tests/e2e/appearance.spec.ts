import { API, BASE_URL } from "./support";
import { test, expect, Page } from "./support";

async function openAppearance(page: Page) {
  const trigger = page.getByLabel("Display preferences", { exact: true });
  await trigger.click();
  await expect(trigger).toHaveAttribute("aria-expanded", "true");
  return trigger;
}

test("appearance has three labeled choices and dismisses without blocking navigation", async ({ page }) => {
  await page.goto("/sign-in");
  const trigger = await openAppearance(page);
  const choices = page.getByRole("group", { name: "Colour theme", exact: true });
  await expect(choices.getByRole("button")).toHaveCount(3);
  for (const label of ["Light", "Dark", "Device default"]) await expect(choices.getByText(label, { exact: true })).toBeVisible();
  await page.getByRole("textbox", { name: "Account", exact: true }).click();
  await expect(trigger).toHaveAttribute("aria-expanded", "false");
  await expect(page.getByRole("textbox", { name: "Account", exact: true })).toBeFocused();

  await openAppearance(page);
  await page.getByRole("button", { name: "Dark theme", exact: true }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(trigger).toHaveAttribute("aria-expanded", "false");
  await expect(trigger).toBeFocused();
  await openAppearance(page);
  await expect(page.getByRole("button", { name: "Dark theme", exact: true })).toHaveAttribute("aria-pressed", "true");
  await page.keyboard.press("Escape");
  await expect(trigger).toBeFocused();
  await expect(trigger).toHaveAttribute("aria-expanded", "false");

  await openAppearance(page);
  await page.getByRole("button", { name: "Use device theme", exact: true }).focus();
  await page.keyboard.press("Tab");
  await expect(trigger).toHaveAttribute("aria-expanded", "false");
  await openAppearance(page);
  const navigation = page.getByRole("navigation", { name: test.info().project.name === "phone" ? "Mobile navigation" : "Main navigation", exact: true });
  await navigation.getByRole("link", { name: "Receipts", exact: true }).click();
  await expect(page).toHaveURL(/\/verify/, { timeout: 15000 });
  await expect(page.locator(".app-preferences")).not.toHaveAttribute("open");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
});

test("landing and operations share keyboard theme choices even without storage", async ({ page }) => {
  await page.addInitScript(() => {
    Storage.prototype.setItem = () => { throw new Error("Storage unavailable"); };
    Storage.prototype.removeItem = () => { throw new Error("Storage unavailable"); };
  });
  await page.emulateMedia({ colorScheme: "light" });
  await page.goto("/");
  const trigger = page.getByLabel("Display preferences", { exact: true });
  await trigger.focus();
  await page.keyboard.press("Enter");
  await page.getByRole("button", { name: "Dark theme", exact: true }).focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(trigger).toBeFocused();
  await openAppearance(page);
  await page.getByRole("button", { name: "Use device theme", exact: true }).click();
  await expect(page.locator("html")).not.toHaveAttribute("data-theme");
  await page.emulateMedia({ colorScheme: "dark" });
  expect(await page.locator(".material-landing").evaluate(node => getComputedStyle(node).backgroundColor)).toBe("rgb(17, 19, 24)");
  await openAppearance(page);
  await page.getByRole("button", { name: "Light theme", exact: true }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  expect(await page.locator(".material-landing").evaluate(node => getComputedStyle(node).backgroundColor)).toBe("rgb(249, 249, 255)");
  await page.getByRole("link", { name: "Explore demo", exact: false }).click();
  await expect(page.getByRole("heading", { name: "Relief overview", exact: true })).toBeVisible();
  await expect(page.locator(".app-preferences")).not.toHaveAttribute("open");
  await openAppearance(page);
  await expect(page.getByRole("button", { name: "Light theme", exact: true })).toHaveAttribute("aria-pressed", "true");
  await page.keyboard.press("Escape");
});

test("household CSV tools stay reachable for DSWD and dialogs return focus", async ({ page }) => {
  await page.goto("/sign-in");
  await page.getByRole("textbox", { name: "Account", exact: true }).fill("demo-officer-01");
  await page.getByLabel("Password", { exact: true }).fill("synthetic-test-password-only");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("button", { name: "Sign out", exact: true })).toBeVisible();
  await page.goto("/beneficiaries");
  for (const title of ["Register a household", "Import a CSV", "Analyze a CSV"]) {
    const opener = page.getByRole("button", { name: title, exact: true });
    await openAppearance(page);
    await opener.click();
    const dialog = page.getByRole("dialog", { name: title, exact: true });
    await expect(dialog).toBeVisible();
    await expect(page.locator(".app-preferences")).not.toHaveAttribute("open");
    expect(await dialog.evaluate(el => el.scrollWidth <= el.clientWidth)).toBe(true);
    await page.keyboard.press("Escape");
    await expect(dialog).not.toBeVisible();
    await expect(opener).toBeFocused();
    await opener.click();
    await dialog.getByRole("button", { name: "Close " + title.toLowerCase(), exact: true }).click();
    await expect(dialog).not.toBeVisible();
    await expect(opener).toBeFocused();
  }
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await page.goto("/sign-in");
  await page.getByRole("textbox", { name: "Account", exact: true }).fill("demo-barangay-01");
  await page.getByLabel("Password", { exact: true }).fill("synthetic-test-password-only");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("button", { name: "Sign out", exact: true })).toBeVisible();
  await page.goto("/beneficiaries");
  await expect(page.getByRole("heading", { name: "Household registry", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Import a CSV", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Analyze a CSV", exact: true })).toHaveCount(0);
});
