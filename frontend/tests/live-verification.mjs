// Actual Edge -> FastAPI -> freshly deployed disposable Hardhat contract.
// Original databases, chains and deployment artifacts are never used or reset.
import { spawn, execFile } from "node:child_process";
import { promisify } from "node:util";
import { mkdtemp, readFile, writeFile } from "node:fs/promises";
import { createWriteStream } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import net from "node:net";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { chromium, expect } from "@playwright/test";

const root = path.resolve(import.meta.dirname, "../..");
const contracts = path.join(root, "contracts");
const requireContracts = createRequire(path.join(contracts, "package.json"));
const { ethers } = requireContracts("ethers");
const run = promisify(execFile);
const directory = await mkdtemp(path.join(tmpdir(), "ayudachain-verification-ui-"));
const python = path.join(root, "backend/.venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const rpc = "http://127.0.0.1:8547";
const api = process.env.AYUDACHAIN_LIVE_API_URL || "http://127.0.0.1:8312";
const baseURL = process.env.AYUDACHAIN_LIVE_BASE_URL || "http://127.0.0.1:3312";
for (const value of [api, baseURL]) { const u = new URL(value); if (u.protocol !== "http:" || !["127.0.0.1", "localhost"].includes(u.hostname)) throw Error("Live verification uses loopback servers only"); }
const key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"; // public local test key
const children = [];
const logs = [];
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
let browser, provider, chain;
async function free(port) {
  await new Promise((resolve, reject) => {
    const server = net.createServer(); server.once("error", reject);
    server.listen(port, "127.0.0.1", () => server.close(resolve));
  });
}
async function start(name, command, args, cwd, env = {}) {
  const log = createWriteStream(path.join(directory, name + ".log")); logs.push(log);
  const child = spawn(command, args, { cwd, env: { ...process.env, ...env }, stdio: ["ignore", "pipe", "pipe"], windowsHide: true });
  child.stdout.pipe(log, { end: false });
  child.stderr.pipe(log, { end: false });
  children.push(child);
  child.on("error", error => { child.startError = error; });
  return child;
}
async function stop(child) {
  if (!child || child.exitCode !== null) return;
  if (process.platform === "win32") await run("taskkill", ["/PID", String(child.pid), "/T", "/F"], { windowsHide: true });
  else child.kill("SIGTERM");
  await Promise.race([new Promise(resolve => child.exitCode !== null ? resolve() : child.once("exit", resolve)), delay(5000)]);
}
async function ready(child, url, timeout = 180000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) {
    if (child.startError) throw child.startError;
    if (child.exitCode !== null) throw Error("Owned service stopped before ready: " + url);
    try { if ((await fetch(url, { signal: AbortSignal.timeout(1500) })).ok) return; } catch {}
    await delay(200);
  }
  throw Error("Owned service startup timed out: " + url);
}
async function change(action) {
  await run(python, [path.join(root, "backend/tests/live_ui_records.py"), directory, action], { cwd: root, windowsHide: true });
}

try {
  await Promise.all([8547, Number(new URL(api).port), Number(new URL(baseURL).port)].map(free));
  chain = await start("chain", process.execPath, ["node_modules/hardhat/internal/cli/cli.js", "node", "--hostname", "127.0.0.1", "--port", "8547"], contracts);
  let connected = false;
  for (let attempt = 0; attempt < 300; attempt++) {
    try {
      const response = await fetch(rpc, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "eth_chainId", params: [] }), signal: AbortSignal.timeout(500) });
      if ((await response.json()).result === "0x7a69") { connected = true; break; }
    } catch {}
    if (chain.startError) throw chain.startError;
    if (chain.exitCode !== null) throw Error("Owned chain stopped");
    await delay(100);
  }
  if (!connected) throw Error("Owned chain did not start");
  provider = new ethers.JsonRpcProvider(rpc);
  const artifact = JSON.parse(await readFile(path.join(contracts, "artifacts/contracts/AyudaChainRegistry.sol/AyudaChainRegistry.json"), "utf8"));
  const contract = await new ethers.ContractFactory(artifact.abi, artifact.bytecode, new ethers.Wallet(key, provider)).deploy();
  await contract.waitForDeployment();
  const backend = await start("api", python, [path.join(root, "backend/tests/live_ui_server.py"), directory], root, { POLYGON_RPC_URL: rpc, POLYGON_PRIVATE_KEY: key, CHAIN_ID: "31337", CONTRACT_ADDRESS: await contract.getAddress(), AYUDACHAIN_LIVE_API_URL: api, AYUDACHAIN_LIVE_BASE_URL: baseURL });
  await ready(backend, api + "/api/public/receipts");
  const frontend = await start("frontend", process.execPath, ["node_modules/next/dist/bin/next", "start", "--hostname", "127.0.0.1", "--port", new URL(baseURL).port], path.join(root, "frontend"));
  await ready(frontend, baseURL);
  await change("unanchored");
  browser = await chromium.launch({ headless: true, channel: process.platform === "win32" ? "msedge" : undefined });
  const pages = [];
  const labels = { VERIFIED: "Receipt hash verified", MISMATCH: "Receipt hash mismatch", UNANCHORED: "No receipt anchor found", UNAVAILABLE: "Verification unavailable" };
  const observations = [];
  let v2;
  const canonical = value => Array.isArray(value) ? value.map(canonical) : value && typeof value === "object" ? Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])])) : value;
  async function observe(page, mode, state, id) {
    const response = await page.context().request.post(api + "/api/blockchain/verify", { headers: { "X-AyudaChain-Client": "web", Origin: baseURL }, data: { distribution_id: id } });
    assert.equal(response.status(), 200);
    const evidence = await response.json();
    assert.equal(evidence.verification_status, state);
    await expect(page.getByRole("heading", { name: labels[state], exact: true })).toBeVisible({ timeout: 60000 });
    await expect(page.getByLabel("Receipt", { exact: true })).toHaveValue(id);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await expect(page.getByText("Roberto Ramos", { exact: true })).toHaveCount(0);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: path.join(directory, mode + "-" + state.toLowerCase() + ".png") });
    observations.push({ mode, state, reference: id, onchainHash: evidence.receipt_hash_onchain });
  }
  for (const [mode, viewport] of [["desktop", { width: 1440, height: 900 }], ["phone", { width: 390, height: 844 }]]) {
    const context = await browser.newContext({ viewport, isMobile: mode === "phone", hasTouch: mode === "phone" });
    const page = await context.newPage(); pages.push([mode, page]);
    await page.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, route => {
      const url = new URL(route.request().url()); url.hostname = "127.0.0.1"; url.port = new URL(api).port;
      return route.continue({ url: url.toString() });
    });
    await page.goto(baseURL + "/sign-in");
    await page.getByRole("textbox", { name: "Account", exact: true }).fill("demo-disbursing-001");
    await page.getByLabel("Password", { exact: true }).fill("synthetic-test-password-only");
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    await expect(page.getByText("Authenticated synthetic account.", { exact: false })).toBeVisible();
    const session = await (await page.context().request.get(api + "/api/auth/session")).json();
    if (!v2) {
      const response = await page.context().request.post(api + "/api/distributions/confirm", { timeout: 120000, headers: { "X-AyudaChain-Client": "web", "X-CSRF-Token": session.csrf_token, Origin: baseURL, "Idempotency-Key": "snapshot-live" }, data: { distribution_id: "DIST-LIVE-SNAPSHOT", beneficiary_id: "BEN-0004", batch_id: "RELIEF-2026-001", amount: "100.25", receipt_filename: "captured-synthetic.svg", ocr_raw_text: "Controlled synthetic receipt evidence" } });
      assert.equal(response.status(), 201); v2 = await response.json();
      assert.equal(v2.receipt_version, 2); assert.equal(v2.anchor_job.state, "CONFIRMED");
      assert.equal(v2.receipt_hash, ethers.sha256(Buffer.from(JSON.stringify(canonical(v2.receipt_snapshot)))));
      const bytes = await (await page.context().request.get(api + v2.receipt_file_path)).body();
      assert.equal(ethers.sha256(bytes), v2.receipt_snapshot.receipt.document.sha256);
      const replay = await page.context().request.post(api + "/api/distributions/confirm", { headers: { "X-AyudaChain-Client": "web", "X-CSRF-Token": session.csrf_token, Origin: baseURL, "Idempotency-Key": "snapshot-live" }, data: { distribution_id: "DIST-LIVE-SNAPSHOT", beneficiary_id: "BEN-0004", batch_id: "RELIEF-2026-001", amount: "100.25", receipt_filename: "captured-synthetic.svg", ocr_raw_text: "Controlled synthetic receipt evidence" } });
      assert.equal(replay.status(), 200); assert.equal((await replay.json()).receipt_hash, v2.receipt_hash);
    }
    await page.goto(baseURL + "/verify?distribution_id=" + v2.distribution_id);
    await observe(page, mode + "-v2", "VERIFIED", v2.distribution_id);
    await change("v2-mismatch"); await page.getByRole("button", { name: "Check again", exact: true }).click();
    await observe(page, mode + "-v2", "MISMATCH", v2.distribution_id);
    await change("v2-restore"); await page.getByRole("button", { name: "Check again", exact: true }).click();
    await observe(page, mode + "-v2-restored", "VERIFIED", v2.distribution_id);
    await change("v2-registry"); await page.reload();
    await observe(page, mode + "-v2-renamed", "VERIFIED", v2.distribution_id);
    await page.getByText("Captured receipt snapshot (version 2)", { exact: true }).click();
    await expect(page.getByRole("definition").filter({ hasText: /^Danilo Soriano$/ })).toBeVisible();
    const captured = await (await page.context().request.get(api + v2.receipt_file_path)).body();
    assert.equal(ethers.sha256(captured), v2.receipt_snapshot.receipt.document.sha256);
    await page.getByText("Captured receipt snapshot (version 2)", { exact: true }).scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(directory, mode + "-v2-captured.png") });
    await page.getByRole("button", { name: "Sign out", exact: true }).click();
    await page.goto(baseURL + "/verify?distribution_id=DIST-0001");
    await observe(page, mode, "VERIFIED", "DIST-0001");
    await change("mismatch");
    await page.getByRole("button", { name: "Check again", exact: true }).click();
    await observe(page, mode, "MISMATCH", "DIST-0001");
    await change("restore");
    await page.getByRole("button", { name: "Check again", exact: true }).click();
    await observe(page, mode + "-restored", "VERIFIED", "DIST-0001");
    await page.goto(baseURL + "/verify?distribution_id=DIST-UI-UNANCHORED");
    await observe(page, mode, "UNANCHORED", "DIST-UI-UNANCHORED");
  }
  await stop(chain);
  for (const [mode, page] of pages) {
    await page.getByRole("button", { name: "Check again", exact: true }).click();
    await observe(page, mode, "UNAVAILABLE", "DIST-UI-UNANCHORED");
  }
  await writeFile(path.join(directory, "observations.json"), JSON.stringify(observations, null, 2));
  console.log("18 real-chain UI observations passed (v1 and v2), including tamper restoration, at both viewport sizes.");
  console.log("Artifacts: " + directory);
} finally {
  if (browser) await browser.close();
  if (provider) provider.destroy();
  for (const child of children.reverse()) await stop(child);
  for (const log of logs) await new Promise(resolve => log.end(resolve));
}
