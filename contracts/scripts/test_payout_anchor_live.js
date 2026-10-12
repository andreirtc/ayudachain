// Owned disposable Hardhat node; deploy directly without overwriting retained artifacts.
const { spawn } = require("node:child_process");
const net = require("node:net");
const http = require("node:http");
const path = require("node:path");
const fs = require("node:fs");
const { ethers } = require("ethers");
const port = 8547;
const rpc = `http://127.0.0.1:${port}`;
const key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"; // public Hardhat fixture only
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
function readyRpc() {
  return new Promise(resolve => {
    const request = http.request(rpc, { method: "POST", headers: { "Content-Type": "application/json" } }, response => {
      let body = ""; response.on("data", chunk => body += chunk);
      response.on("end", () => { try { resolve(JSON.parse(body).result === "0x7a69"); } catch (_) { resolve(false); } });
    });
    request.setTimeout(500, () => request.destroy());
    request.on("error", () => resolve(false));
    request.end(JSON.stringify({ jsonrpc: "2.0", id: 1, method: "eth_chainId", params: [] }));
  });
}

async function main() {
  await new Promise((resolve, reject) => {
    const server = net.createServer(); server.once("error", reject);
    server.listen(port, "127.0.0.1", () => server.close(resolve));
  });
  const node = spawn(process.execPath, [path.join(__dirname, "../node_modules/hardhat/internal/cli/cli.js"), "node", "--hostname", "127.0.0.1", "--port", String(port)], { cwd: path.join(__dirname, ".."), stdio: ["ignore", "pipe", "pipe"], windowsHide: true });
  fs.mkdirSync(path.join(__dirname, "../../tmp"), { recursive: true });
  const log = fs.createWriteStream(path.join(__dirname, "../../tmp/ayudachain-live-chain.log"));
  node.stdout.pipe(log, { end: false }); node.stderr.pipe(log, { end: false });
  let provider;
  try {
    let ready = false;
    for (let i = 0; i < 300; i++) {
      if (node.exitCode !== null) throw Error("Isolated Hardhat node stopped");
      ready = await readyRpc();
      if (ready) break; await delay(100);
    }
    if (!ready) throw Error("Isolated chain startup timed out");
    provider = new ethers.JsonRpcProvider(rpc);
    const wallet = new ethers.Wallet(key, provider);
    const artifact = JSON.parse(fs.readFileSync(path.join(__dirname, "../artifacts/contracts/AyudaChainRegistry.sol/AyudaChainRegistry.json")));
    const contract = await new ethers.ContractFactory(artifact.abi, artifact.bytecode, wallet).deploy();
    await contract.waitForDeployment();
    console.log("Isolated local contract deployed on 8547; original chain/artifacts untouched.");
    const python = path.join(__dirname, "../../backend/.venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
    const test = spawn(python, [path.join(__dirname, "../../backend/test_payout_anchors_live.py")], {
      env: { ...process.env, POLYGON_RPC_URL: rpc, POLYGON_PRIVATE_KEY: key, CHAIN_ID: "31337", CONTRACT_ADDRESS: await contract.getAddress() },
      stdio: "inherit", windowsHide: true,
    });
    const code = await new Promise((resolve, reject) => { test.once("error", reject); test.once("exit", resolve); });
    if (code !== 0) throw Error("Isolated live recovery checks failed");
  } finally {
    if (provider) provider.destroy();
    node.kill();
    await new Promise(resolve => node.exitCode !== null ? resolve() : node.once("exit", resolve));
    log.end();
  }
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
