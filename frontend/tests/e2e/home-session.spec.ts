import { test, expect, API, BASE_URL } from "./support";

test("logo, landing visits and reload keep every role signed in until explicit logout", async ({ page }) => {
  test.setTimeout(120000);
  for (const [identity, role] of [
    ["demo-officer-01", "DSWD"], ["demo-barangay-01", "BARANGAY"],
    ["demo-disbursing-001", "DISBURSING"], ["demo-beneficiary-01", "BENEFICIARY"],
    ["demo-auditor-01", "AUDITOR"],
  ]) {
    await page.goto("/sign-in");
    await page.getByRole("textbox", { name: "Account", exact: true }).fill(identity);
    await page.getByLabel("Password", { exact: true }).fill("synthetic-test-password-only");
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    await expect(page.getByRole("button", { name: "Sign out", exact: true })).toBeVisible();
    await page.getByRole("link", { name: "AyudaChain home", exact: true }).click();
    const home = role === "BENEFICIARY" ? "/household" : "/dashboard";
    await expect(page).toHaveURL(BASE_URL + home);
    await page.reload();
    await expect(page.getByRole("button", { name: "Sign out", exact: true })).toBeVisible();
    const session = await page.context().request.get(API + "/api/auth/session");
    expect(session.status()).toBe(200);
    expect((await session.json()).account).toMatchObject({ id: identity, role });
    await page.goto("/");
    await expect(page.getByRole("button", { name: "Sign out", exact: true })).toBeVisible();
    await expect(page.getByRole("region", { name: "Account", exact: true }).getByRole("link", { name: "Sign in", exact: true })).toHaveCount(0);
    await page.getByRole("link", { name: "AyudaChain home", exact: true }).click();
    await expect(page).toHaveURL(BASE_URL + home);
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
    await expect(page.getByRole("region", { name: "Account", exact: true }).getByRole("link", { name: "Sign in", exact: true })).toBeVisible();
    expect((await page.context().request.get(API + "/api/auth/session")).status()).toBe(401);
  }
});
