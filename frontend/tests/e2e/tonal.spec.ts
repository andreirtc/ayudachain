import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, route => {
    const url = new URL(route.request().url()); url.hostname = "127.0.0.1"; url.port = "8101";
    return route.continue({ url: url.toString() });
  });
});

for (const scheme of ["light", "dark"] as const) {
  test(`Tonal ${scheme} preserves scoped journeys, fonts, focus and status visibility`, async ({ page }, info) => {
    const fontUrls: string[] = [];
    page.on("request", request => { if (request.resourceType() === "font") fontUrls.push(request.url()); });
    await page.emulateMedia({ colorScheme: scheme, reducedMotion: "reduce" });
    // Provision a real own-household payout in the disposable API if this spec runs alone.
    const api = page.context().request;
    const clientHeaders = { "X-AyudaChain-Client": "web", Origin: "http://127.0.0.1:3101" };
    const login = await api.post("http://127.0.0.1:8101/api/auth/login", { headers: clientHeaders, data: { username: "demo-disbursing-001", password: "synthetic-test-password-only" } });
    expect(login.ok()).toBe(true);
    const rows = await (await api.get("http://127.0.0.1:8101/api/distributions")).json();
    let receipt = rows.find((row: { beneficiary_id: string }) => row.beneficiary_id === "BEN-0004");
    const session = await (await api.get("http://127.0.0.1:8101/api/auth/session")).json();
    const headers = { ...clientHeaders, "X-CSRF-Token": session.csrf_token };
    if (!receipt) {
      const saved = await api.post("http://127.0.0.1:8101/api/distributions/confirm", { headers: { ...headers, "Idempotency-Key": "tonal-own-household" }, data: { beneficiary_id: "BEN-0004", batch_id: "RELIEF-2026-001", amount: "100.25" } });
      expect(saved.status()).toBe(201); receipt = await saved.json();
    }
    expect((await api.post("http://127.0.0.1:8101/api/auth/logout", { headers })).ok()).toBe(true);
    await page.goto("/sign-in?returnTo=%2Fdistributions%3Fbeneficiary_id%3DBEN-0004");
    await page.getByRole("button", { name: scheme === "dark" ? "Dark theme" : "Light theme", exact: true }).click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", scheme);
    await page.getByRole("textbox", { name: "Account", exact: true }).fill("demo-beneficiary-01");
    await page.getByLabel("Password", { exact: true }).fill("synthetic-test-password-only");
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    await expect(page).toHaveURL(/distributions\?beneficiary_id=BEN-0004$/);
    await expect(page.getByText("Authenticated synthetic account.", { exact: false })).toBeVisible();
    await expect(page.getByRole("button", { name: "Record demo payout", exact: true })).toHaveCount(0);
    await page.reload();
    await expect(page.getByRole("button", { name: scheme === "dark" ? "Dark theme" : "Light theme", exact: true })).toHaveAttribute("aria-pressed", "true");
    await page.goto("/verify?distribution_id=" + encodeURIComponent(receipt.distribution_id));
    await expect(page.getByRole("heading", { name: "Verification unavailable", exact: true })).toBeVisible();
    await page.evaluate(() => document.fonts.ready);
    const visual = await page.evaluate(() => {
      const frame = document.querySelector(".operations")!;
      const style = getComputedStyle(frame);
      const rgb = (color: string) => {
        const probe = document.createElement("span"); probe.style.color = color; frame.appendChild(probe);
        const value = getComputedStyle(probe).color.match(/[\d.]+/g)!.slice(0,3).map(Number); probe.remove();
        const linear = value.map(x => { x /= 255; return x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4; });
        return linear[0] * .2126 + linear[1] * .7152 + linear[2] * .0722;
      };
      const contrast = (a: string, b: string) => { const x=rgb(style.getPropertyValue(a)),y=rgb(style.getPropertyValue(b)); return (Math.max(x,y)+.05)/(Math.min(x,y)+.05); };
      return {
        fits: document.documentElement.scrollWidth <= innerWidth,
        interfaceFont: style.fontFamily.includes(style.getPropertyValue("--font-open-sans").split(",")[0].replace(/["']/g, "").trim()),
        textContrast: contrast("--md-on-surface", "--md-surface-container-low"),
        mutedContrast: contrast("--md-on-surface-variant", "--md-surface-container-low"),
        buttonContrast: contrast("--md-on-primary", "--md-primary"),
        outlineContrast: contrast("--md-outline", "--md-surface-container-lowest"),
        statusContrast: ["--st-ok", "--st-warn", "--md-error"].map(x => contrast(x,"--md-surface-container-low")),
      };
    });
    expect(visual.fits).toBe(true); expect(visual.interfaceFont).toBe(true);
    expect(visual.textContrast).toBeGreaterThanOrEqual(4.5); expect(visual.mutedContrast).toBeGreaterThanOrEqual(4.5);
    expect(visual.buttonContrast).toBeGreaterThanOrEqual(4.5); expect(visual.outlineContrast).toBeGreaterThanOrEqual(3);
    visual.statusContrast.forEach(value => expect(value).toBeGreaterThanOrEqual(4.5));
    expect(fontUrls.length).toBeGreaterThan(0); expect(fontUrls.every(url=>new URL(url).origin === "http://127.0.0.1:3101")).toBe(true);
    await page.getByRole("link", { name: "Skip to content", exact: true }).focus(); await page.keyboard.press("Enter");
    await expect(page.getByRole("main")).toBeFocused();
    await page.screenshot({ path: info.outputPath(`tonal-${scheme}-receipt.png`), fullPage: true });
    await page.goto("/beneficiaries");
    await expect(page.getByRole("heading", { name: "My household", exact: true })).toBeVisible();
    await page.screenshot({ path: info.outputPath(`tonal-${scheme}-household.png`), fullPage: true });
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
    await page.goto("/sign-in");
    await page.getByRole("textbox", { name: "Account", exact: true }).fill("demo-officer-01");
    await page.getByLabel("Password", { exact: true }).fill("synthetic-test-password-only");
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    await page.getByPlaceholder("Search household name, ID, barangay...").fill("BEN-0002");
    await page.getByRole("button", { name: /Review|Inspect/ }).first().click();
    await expect(page.getByLabel("Reason for decision")).toBeVisible();
    await page.screenshot({ path: info.outputPath(`tonal-${scheme}-review.png`), fullPage: false });
    await page.getByLabel("Reason for decision").fill("Synthetic foundation QA: retain this case for human review.");
    await page.getByRole("button", { name: "Keep for review", exact: true }).click();
    await expect(page.getByText("Review saved.", { exact: true })).toBeVisible();
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: "Relief overview", exact: true })).toBeVisible();
    await expect(page.getByText(/demo-officer-01 reviewed BEN-0002: FLAGGED_FOR_REVIEW/).first()).toBeVisible();
    await page.screenshot({ path: info.outputPath(`tonal-${scheme}-overview.png`), fullPage: false });
  });
}

test("device theme follows the OS and the control works without persistent storage", async ({ page }) => {
  await page.addInitScript(() => { Storage.prototype.setItem = () => { throw new Error("Storage unavailable"); }; });
  await page.emulateMedia({ colorScheme: "light" });
  await page.goto("/sign-in");
  await page.getByRole("button", { name: "Dark theme", exact: true }).focus(); await page.keyboard.press("Enter");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByRole("button", { name: "Use device theme", exact: true }).click();
  await expect(page.locator("html")).not.toHaveAttribute("data-theme");
  await page.emulateMedia({ colorScheme: "dark" });
  expect(await page.locator(".operations").evaluate(node => getComputedStyle(node).backgroundColor)).toBe("rgb(17, 19, 24)");
  await page.getByRole("button", { name: "Light theme", exact: true }).click();
  expect(await page.locator(".operations").evaluate(node => getComputedStyle(node).backgroundColor)).toBe("rgb(249, 249, 255)");
});
