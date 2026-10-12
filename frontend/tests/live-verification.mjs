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
const api = "http://127.0.0.1:8102";
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
  await Promise.all([8547, 8102, 3102].map(free));
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
  const backend = await start("api", python, [path.join(root, "backend/tests/live_ui_server.py"), directory], root, { POLYGON_RPC_URL: rpc, POLYGON_PRIVATE_KEY: key, CHAIN_ID: "31337", CONTRACT_ADDRESS: await contract.getAddress() });
  await ready(backend, api + "/api/public/receipts");
  const frontend = await start("frontend", process.execPath, ["node_modules/next/dist/bin/next", "start", "--hostname", "127.0.0.1", "--port", "3102"], path.join(root, "frontend"));
  await ready(frontend, "http://127.0.0.1:3102");
  await change("unanchored");
  browser = await chromium.launch({ headless: true, channel: process.platform === "win32" ? "msedge" : undefined });
  const pages = [];
  const labels = { VERIFIED: "Receipt hash verified", MISMATCH: "Receipt hash mismatch", UNANCHORED: "No receipt anchor found", UNAVAILABLE: "Verification unavailable" };
  const observations = [];
  async function observe(page, mode, state, id) {
    const response = await page.context().request.post(api + "/api/blockchain/verify", { headers: { "X-AyudaChain-Client": "web", Origin: "http://127.0.0.1:3102" }, data: { distribution_id: id } });
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
      const url = new URL(route.request().url()); url.hostname = "127.0.0.1"; url.port = "8102";
      return route.continue({ url: url.toString() });
    });
    await page.goto("http://127.0.0.1:3102/verify?distribution_id=DIST-0001");
    await observe(page, mode, "VERIFIED", "DIST-0001");
    await change("mismatch");
    await page.getByRole("button", { name: "Check again", exact: true }).click();
    await observe(page, mode, "MISMATCH", "DIST-0001");
    await change("restore");
    await page.getByRole("button", { name: "Check again", exact: true }).click();
    await observe(page, mode + "-restored", "VERIFIED", "DIST-0001");
    await page.goto("http://127.0.0.1:3102/verify?distribution_id=DIST-UI-UNANCHORED");
    await observe(page, mode, "UNANCHORED", "DIST-UI-UNANCHORED");
  }
  await stop(chain);
  for (const [mode, page] of pages) {
    await page.getByRole("button", { name: "Check again", exact: true }).click();
    await observe(page, mode, "UNAVAILABLE", "DIST-UI-UNANCHORED");
  }
  await writeFile(path.join(directory, "observations.json"), JSON.stringify(observations, null, 2));
  console.log("10 real-chain UI observations passed, including tamper restoration, at both viewport sizes.");
  console.log("Artifacts: " + directory);
} finally {
  if (browser) await browser.close();
  if (provider) provider.destroy();
  for (const child of children.reverse()) await stop(child);
  for (const log of logs) await new Promise(resolve => log.end(resolve));
}
