import { API, BASE_URL } from "./support";
import { test, expect, Page } from "./support";

async function login(page: Page, id = "demo-officer-01") { await page.goto("/sign-in"); await page.getByRole("textbox", { name: "Account", exact: true }).fill(id); await page.getByLabel("Password", { exact: true }).fill("synthetic-test-password-only"); await page.getByRole("button", { name: "Sign in", exact: true }).click(); await expect(page.getByText("Authenticated synthetic account.", { exact: false })).toBeVisible(); }
async function signOut(page: Page) { await page.getByRole("button", { name: "Sign out", exact: true }).click(); await expect(page.getByRole("region", { name: "Account" }).getByRole("link", { name: "Sign in", exact: true })).toBeVisible(); }
async function headers(page: Page) { const s = await (await page.context().request.get(API + "/api/auth/session")).json(); return { "X-AyudaChain-Client": "web", "X-CSRF-Token": s.csrf_token, Origin: BASE_URL }; }
const soon = new Date(Date.now() + 3 * 864e5).toISOString().slice(0, 10);
const noOverflow = async (page: Page) => expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);

test("household claim is endorsed, approved, priced, scheduled and paid in an assigned session", async ({ page }, info) => {
  await login(page); const request = page.context().request;
  expect((await request.post(API + "/api/beneficiaries/BEN-0004/verify", { headers: await headers(page), data: { status: "VERIFIED", review_notes: "Inspected synthetic household" } })).ok()).toBe(true);
  await signOut(page);

  await login(page, "demo-beneficiary-01"); await page.goto("/household");
  const claimPanel = page.getByRole("region", { name: "Damage claim" });
  await claimPanel.getByLabel("Totally damaged house").check();
  await claimPanel.getByLabel("What was damaged?").fill("Roof blown off and kitchen wall collapsed");
  await claimPanel.getByRole("button", { name: "Submit damage claim", exact: true }).click();
  await expect(claimPanel.getByText("Damage claim submitted. Your barangay reviews it first.", { exact: true })).toBeVisible();
  await expect(claimPanel).toContainText("Barangay review");
  await signOut(page);

  await login(page, "demo-barangay-01"); await page.goto("/claims");
  const selected = page.getByRole("region", { name: "Selected claim" });
  await expect(selected).toContainText("Danilo Soriano");
  await selected.getByRole("button", { name: "Endorse", exact: true }).click();
  await selected.getByLabel("Reason (staff only)").fill("Resident; damage seen on barangay visit");
  await selected.getByRole("button", { name: "Confirm: endorse", exact: true }).click();
  await expect(selected).toContainText("Endorsed by barangay");
  await signOut(page);

  await login(page); await page.goto("/claims");
  await expect(selected).toContainText("Roof blown off");
  await selected.getByRole("button", { name: "Approve", exact: true }).click();
  await selected.getByLabel("Approved damage category").selectOption("TOTALLY_DAMAGED");
  await selected.getByLabel("Reason (staff only)").fill("Photos confirm total damage");
  await selected.getByRole("button", { name: "Confirm: approve", exact: true }).click();
  await expect(selected).toContainText("Approved");
  await expect(selected).toContainText("₱10,000.00");
  await noOverflow(page); await page.screenshot({ path: info.outputPath("claims-dswd.png"), fullPage: true });

  const h = await headers(page);
  const list = await (await request.post(API + "/api/validated-lists/prepare", { headers: h, data: { batch_id: "RELIEF-2026-001", barangay_id: "BRGY-001", request_id: crypto.randomUUID() } })).json();
  expect((await request.post(API + "/api/validated-lists/" + list.list_id + "/finalize", { headers: h, data: { confirm: true, reason: "Inspected synthetic list" } })).status()).toBe(201);
  await page.goto("/sessions");
  const schedule = page.getByRole("form", { name: "Schedule a session" });
  await expect(schedule.getByLabel("Finalized list version")).toHaveValue(list.list_id);
  await schedule.getByLabel("Session date").fill(soon);
  await schedule.getByLabel("Payout site").fill("San Isidro covered court");
  await schedule.getByLabel("Demo disbursing officer 1").check();
  await schedule.getByRole("button", { name: "Schedule session", exact: true }).click();
  await expect(page.getByText("Session scheduled. Assigned staff see it in their sessions.", { exact: true })).toBeVisible();
  const session = page.getByRole("region", { name: "Selected session" });
  await expect(session).toContainText("Scheduled");
  await expect(session).toContainText("0 of 1 households paid");
  await signOut(page);

  await login(page, "demo-disbursing-001"); await page.goto("/sessions");
  await expect(session.getByText("Not paid", { exact: true })).toBeVisible();
  await session.getByRole("button", { name: "Open session", exact: true }).click();
  await expect(session).toContainText("Open now");
  await session.getByRole("link", { name: "Record payout", exact: true }).click();
  await expect(page).toHaveURL(/\/distributions\?beneficiary_id=BEN-0004/);
  await expect(page.getByLabel("Fictional amount (PHP)")).toHaveValue("10000");
  await expect(page.getByText("Ready to record this amount.", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Record demo payout", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Payout recorded", exact: true })).toBeVisible();
  await page.goto("/sessions");
  await expect(session).toContainText("1 of 1 households paid");
  await expect(session.getByRole("link", { name: "Paid · check receipt", exact: true })).toBeVisible();
  await session.getByRole("button", { name: "Close session", exact: true }).click();
  await expect(session).toContainText("Closed");
  await noOverflow(page); await page.screenshot({ path: info.outputPath("session-disbursing.png"), fullPage: true });
  await signOut(page);

  await login(page, "demo-beneficiary-01"); await page.goto("/household");
  await expect(claimPanel).toContainText("Approved");
  await expect(claimPanel).toContainText("Calculated amount: ₱10,000.00");
  await expect(page.getByText("Photos confirm total damage")).toHaveCount(0);
});

test("amount rules save a new version that reprices approved claims; non-DSWD roles cannot change them", async ({ page }, info) => {
  await login(page, "demo-auditor-01"); await page.goto("/amounts");
  await expect(page.getByRole("region", { name: "Current rules" })).toContainText("Version 1");
  await expect(page.getByRole("form", { name: "New rule version" })).toHaveCount(0);
  await signOut(page);
  await login(page); await page.goto("/amounts");
  const form = page.getByRole("form", { name: "New rule version" });
  await form.getByLabel("Fixed amount per category").check();
  await form.getByLabel("Totally damaged house (PHP)").fill("12000");
  await form.getByLabel("Partially damaged house (PHP)").fill("4500");
  await expect(form.getByRole("alert")).toContainText("maximum grant");
  await expect(form.getByRole("button", { name: "Save new version", exact: true })).toBeDisabled();
  await form.getByLabel("Totally damaged house (PHP)").fill("9000");
  await form.getByLabel("Reason for this version").fill("Revised fictional budget");
  await form.getByRole("button", { name: "Save new version", exact: true }).click();
  await expect(page.getByText("Version 2 saved. New list versions and payout desk checks use it now.", { exact: true })).toBeVisible();
  await expect(page.getByRole("region", { name: "Current rules" })).toContainText("₱9,000.00");
  await noOverflow(page); await page.screenshot({ path: info.outputPath("amount-rules.png"), fullPage: true });
  await signOut(page);
  for (const [id, heading] of [["demo-barangay-01", "Amount rules are set by DSWD"], ["demo-beneficiary-01", "Amount rules are set by DSWD"]]) {
    await login(page, id); await page.goto("/amounts");
    await expect(page.getByRole("heading", { name: heading, exact: true })).toBeVisible();
    expect((await page.context().request.get(API + "/api/amount-rules?batch_id=RELIEF-2026-001")).status()).toBe(403);
    await signOut(page);
  }
  await login(page, "demo-disbursing-001"); await page.goto("/claims");
  await expect(page.getByRole("heading", { name: "Damage claims are reviewed by barangay and DSWD staff", exact: true })).toBeVisible();
  await page.goto("/sessions");
  await expect(page.getByRole("heading", { name: "No sessions yet", exact: true })).toBeVisible();
});
