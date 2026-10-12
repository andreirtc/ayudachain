/**
 * AyudaChain Centralized Blockchain Client CLI
 * Executes smart contract actions with real ethers.js transactions
 * Outputs structured JSON for backend consumption.
 */

const { ethers } = require("ethers");
const fs = require("fs");
const path = require("path");

// Load deployment metadata
const metadataPath = path.join(__dirname, "../artifacts/contracts/AyudaChainRegistry.sol/AyudaChainRegistry.json");
const deploymentMetaPath = path.join(__dirname, "../../shared/contracts/AyudaChainRegistry.json");

let abi = [];
let defaultAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

if (fs.existsSync(metadataPath)) {
  const meta = JSON.parse(fs.readFileSync(metadataPath, "utf8"));
  abi = meta.abi;
}

if (fs.existsSync(deploymentMetaPath)) {
  const dep = JSON.parse(fs.readFileSync(deploymentMetaPath, "utf8"));
  if (dep.contractAddress) {
    defaultAddress = dep.contractAddress;
  }
}

const RPC_URL = process.env.POLYGON_RPC_URL || "https://polygon-amoy-bor-rpc.publicnode.com";
const PRIVATE_KEY = process.env.POLYGON_PRIVATE_KEY || "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS || defaultAddress;

function toBytes32(str) {
  // If already 66 chars hex (0x...), return as is
  if (str.startsWith("0x") && str.length === 66) {
    return str;
  }
  // Otherwise UTF8 encode or pad
  return ethers.encodeBytes32String(str.slice(0, 31));
}

let chainContext = { contractAddress: CONTRACT_ADDRESS };

async function getContract(readOnly = false) {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const network = await provider.getNetwork();
  const chainId = Number(network.chainId);
  chainContext = {
    chainId,
    network: chainId === 31337 ? "Local EVM" : chainId === 80002 ? "Polygon Amoy" : "Chain " + chainId,
    contractAddress: CONTRACT_ADDRESS,
  };
  if (process.env.CHAIN_ID && chainId !== Number(process.env.CHAIN_ID)) {
    throw new Error("Connected chain does not match configured CHAIN_ID.");
  }
  if (!abi.length) throw new Error("Contract ABI is unavailable.");
  if (await provider.getCode(CONTRACT_ADDRESS) === "0x") {
    throw new Error("No contract is deployed at the configured address.");
  }
  const runner = readOnly ? provider : new ethers.Wallet(PRIVATE_KEY, provider);
  const contract = new ethers.Contract(CONTRACT_ADDRESS, abi, runner);
  return { provider, contract };
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  try {
    const { provider, contract } = await getContract(command === "status" || command === "verifyReceipt");
    if (command === "status") {
      const blockNumber = await provider.getBlockNumber();
      console.log(JSON.stringify({ success: true, ...chainContext, blockNumber: Number(blockNumber) }));
      return;
    }

    if (command === "releaseFund") {
      // args: batchId, amount (integer centavos), calamityName, sourceAgency
      const [_, batchId, amount, calamityName, sourceAgency] = args;
      const bId = toBytes32(batchId);
      const amtCentavos = BigInt(amount);
      const tx = await contract.releaseFund(bId, amtCentavos, calamityName, sourceAgency);
      const receipt = await tx.wait();
      if (!receipt || receipt.status !== 1) throw new Error("Transaction was not confirmed successfully.");

      console.log(JSON.stringify({
        success: true,
        action: "releaseFund",
        txHash: receipt.hash,
        blockNumber: Number(receipt.blockNumber),
        gasUsed: receipt.gasUsed.toString(),
        contractAddress: CONTRACT_ADDRESS
      }));
    } else if (command === "allocateFund") {
      // args: batchId, allocationId, barangayId, amount (integer centavos)
      const [_, batchId, allocationId, barangayId, amount] = args;
      const bId = toBytes32(batchId);
      const aId = toBytes32(allocationId);
      const brgyId = toBytes32(barangayId);
      const amtCentavos = BigInt(amount);
      const tx = await contract.allocateFund(bId, aId, brgyId, amtCentavos);
      const receipt = await tx.wait();
      if (!receipt || receipt.status !== 1) throw new Error("Transaction was not confirmed successfully.");

      console.log(JSON.stringify({
        success: true,
        action: "allocateFund",
        txHash: receipt.hash,
        blockNumber: Number(receipt.blockNumber),
        gasUsed: receipt.gasUsed.toString()
      }));
    } else if (command === "confirmDistribution") {
      // args: batchId, allocationId, distributionId, beneficiaryId, amount (integer centavos), receiptHash
      const [_, batchId, allocationId, distributionId, beneficiaryId, amount, receiptHash] = args;
      const bId = toBytes32(batchId);
      const aId = toBytes32(allocationId);
      const dId = toBytes32(distributionId);
      const benId = toBytes32(beneficiaryId);
      const amtCentavos = BigInt(amount);
      const rHash = receiptHash.startsWith("0x") ? receiptHash : `0x${receiptHash}`;

      const tx = await contract.confirmDistribution(bId, aId, dId, benId, amtCentavos, rHash);
      const receipt = await tx.wait();
      if (!receipt || receipt.status !== 1) throw new Error("Transaction was not confirmed successfully.");

      console.log(JSON.stringify({
        success: true,
        action: "confirmDistribution",
        txHash: receipt.hash,
        blockNumber: Number(receipt.blockNumber),
        gasUsed: receipt.gasUsed.toString(),
        receiptHash: rHash
      }));
    } else if (command === "verifyReceipt") {
      // args: distributionId, receiptHash
      const [_, distributionId, receiptHash] = args;
      const dId = toBytes32(distributionId);
      const rHash = receiptHash.startsWith("0x") ? receiptHash : `0x${receiptHash}`;

      const [matched, timestamp] = await contract.verifyReceipt(dId, rHash);
      const record = await contract.distributions(dId);

      console.log(JSON.stringify({
        success: true,
        ...chainContext,
        distributionId: distributionId,
        matched: Boolean(matched),
        onchainHash: record.receiptHash,
        queriedHash: rHash,
        timestamp: Number(timestamp),
        exists: Boolean(record.exists),
        contractAddress: CONTRACT_ADDRESS
      }));
    } else {
      console.log(JSON.stringify({ success: false, error: `Unknown command: ${command}` }));
    }
  } catch (err) {
    console.log(JSON.stringify({
      success: false,
      ...chainContext,
      error: err.shortMessage || err.message || String(err)
    }));
  }
}

main();
