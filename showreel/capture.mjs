// Captures read-only plates of the running /mvp workspaces for the showreel.
// Navigation only: no form is submitted and no action button is pressed.
// Usage: node showreel/capture.mjs   (needs the frontend on :3000 and the API on :8000)
import { chromium } from '../frontend/node_modules/playwright/index.mjs';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const base = process.env.SHOWREEL_BASE || 'http://127.0.0.1:3000';
const out = fileURLToPath(new URL('./film/plates/', import.meta.url));
mkdirSync(out, { recursive: true });

// [name, path, tall?] - tall plates are captured twice so the film can scroll the content under the fixed rail.
const shots = [
  ['directory', '/mvp'],
  ['beneficiary-overview', '/mvp/beneficiary/overview', true],
  ['barangay-overview', '/mvp/barangay-officer/overview'],
  ['dswd-overview', '/mvp/dswd-officer/overview'],
  ['dswd-funds', '/mvp/dswd-officer/funds'],
  ['dswd-claims', '/mvp/dswd-officer/claims'],
  ['disbursing-overview', '/mvp/disbursing-officer/overview', true],
  ['auditor-overview', '/mvp/auditor/overview', true],
  ['auditor-audit', '/mvp/auditor/audit'],
];

const browser = await chromium.launch();
const report = [];
async function capture(name, path, height, suffix) {
  const context = await browser.newContext({ viewport: { width: 1600, height }, deviceScaleFactor: 2, reducedMotion: 'reduce' });
  const page = await context.newPage();
  await page.goto(base + path, { waitUntil: 'networkidle', timeout: 45000 });
  // The Next.js development badge is tooling, not product UI.
  await page.addStyleTag({ content: 'nextjs-portal{display:none!important}' });
  await page.waitForTimeout(900);
  await page.screenshot({ path: `${out}${name}${suffix}.png` });
  const heading = await page.locator('h1').first().innerText().catch(() => '');
  report.push({ name: name + suffix, path, viewport: `1600x${height}@2x`, heading, capturedAt: new Date().toISOString() });
  console.log('ok', name + suffix, '|', heading);
  await context.close();
}
const only = process.env.SHOWREEL_ONLY;
for (const [name, path, tall] of shots) {
  if (only && name !== only) continue;
  await capture(name, path, 1000, '');
  if (tall) await capture(name, path, 2000, '-tall');
}
if (!only) writeFileSync(`${out}captures.json`, JSON.stringify(report, null, 2));
await browser.close();
