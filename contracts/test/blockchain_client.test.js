const { expect } = require("chai");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const scriptPath = path.join(__dirname, "../scripts/blockchain_client.js");
const script = fs.readFileSync(scriptPath, "utf8").replace(/main\(\);\s*$/, "module.exports = main;");
const address = "0x" + "1".repeat(40);

async function executeClient(command, overrides = {}) {
  const output = [];
  let walletCalls = 0;
  let writeCalls = 0;
  const chainId = overrides.chainId ?? 31337;
  class Provider {
    async getNetwork() { return { chainId: BigInt(chainId) }; }
    async getBlockNumber() { return 12; }
    async getCode() { return overrides.code ?? "0x1234"; }
  }
  class Wallet {
    constructor() {
      walletCalls++;
      if (overrides.badKey) throw new Error("Invalid signing key");
    }
  }
  class Contract {
    async verifyReceipt() { return [overrides.matched ?? false, BigInt(overrides.timestamp ?? 0)]; }
    async distributions() { return { exists: overrides.exists ?? false, receiptHash: overrides.hash ?? "0x" + "0".repeat(64) }; }
    async releaseFund() {
      writeCalls++;
      return { wait: async () => overrides.receipt ?? { status: 1, hash: "0x" + "a".repeat(64), blockNumber: 12, gasUsed: 100n } };
    }
  }
  const module = { exports: null };
  const context = {
    module,
    __dirname: path.dirname(scriptPath),
    process: { argv: ["node", scriptPath, ...command], env: { CHAIN_ID: "31337", ...overrides.env } },
    console: { log: (value) => output.push(JSON.parse(value)) },
    require(name) {
      if (name === "ethers") return { ethers: { JsonRpcProvider: Provider, Wallet, Contract, encodeBytes32String: (value) => value } };
      if (name === "path") return path;
      if (name === "fs") return { existsSync: () => true, readFileSync: (file) => JSON.stringify(file.includes("artifacts") ? { abi: overrides.abi ?? [{}] } : { contractAddress: address }) };
      throw new Error("Unexpected module");
    },
  };
  vm.runInNewContext(script, context, { filename: scriptPath });
  await module.exports();
  return { result: output[0], walletCalls, writeCalls };
}

describe("Blockchain client evidence boundaries", function () {
  it("reports the observed chain instead of inferring it from the RPC URL", async function () {
    const { result } = await executeClient(["status"], { env: { POLYGON_RPC_URL: "https://amoy-in-name.example" } });
    expect(result.success).to.equal(true);
    expect(result.network).to.equal("Local EVM");
    expect(result.chainId).to.equal(31337);
  });

  it("rejects a missing deployed contract", async function () {
    const { result } = await executeClient(["status"], { code: "0x" });
    expect(result.success).to.equal(false);
    expect(result.error).to.include("No contract");
  });

  it("rejects an unavailable ABI", async function () {
    const { result } = await executeClient(["status"], { abi: [] });
    expect(result.success).to.equal(false);
  });

  it("rejects a chain that differs from configuration before writing", async function () {
    const { result, writeCalls } = await executeClient(["releaseFund", "BATCH", "100", "Flood", "Demo"], { chainId: 80002 });
    expect(result.success).to.equal(false);
    expect(result.chainId).to.equal(80002);
    expect(writeCalls).to.equal(0);
  });

  it("keeps a missing receipt missing without using a signing key", async function () {
    const { result, walletCalls } = await executeClient(["verifyReceipt", "DIST", "0x" + "a".repeat(64)], { badKey: true });
    expect(result.success).to.equal(true);
    expect(result.exists).to.equal(false);
    expect(result.matched).to.equal(false);
    expect(walletCalls).to.equal(0);
  });

  it("returns the actual anchored hash and contract match result", async function () {
    const hash = "0x" + "a".repeat(64);
    const { result } = await executeClient(["verifyReceipt", "DIST", hash], { exists: true, matched: true, hash, timestamp: 123 });
    expect(result.onchainHash).to.equal(hash);
    expect(result.timestamp).to.equal(123);
    expect(result.contractAddress).to.equal(address);
    expect(result.exists).to.equal(true);
  });

  it("does not label a reverted transaction successful", async function () {
    const { result } = await executeClient(["releaseFund", "BATCH", "100", "Flood", "Demo"], { receipt: { status: 0 } });
    expect(result.success).to.equal(false);
    expect(result.txHash).to.equal(undefined);
  });

  it("returns a transaction hash only after a successful receipt", async function () {
    const { result } = await executeClient(["releaseFund", "BATCH", "100", "Flood", "Demo"]);
    expect(result.success).to.equal(true);
    expect(result.txHash).to.equal("0x" + "a".repeat(64));
  });
});
