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

async function getContract() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const contract = new ethers.Contract(CONTRACT_ADDRESS, abi, wallet);
  return { provider, wallet, contract };
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  try {
    if (command === "status") {
      const provider = new ethers.JsonRpcProvider(RPC_URL);
      const network = await provider.getNetwork();
      const blockNumber = await provider.getBlockNumber();
      console.log(JSON.stringify({
        success: true,
        network: RPC_URL.includes("amoy") ? "Polygon Amoy" : "Local EVM",
        chainId: Number(network.chainId),
        blockNumber: Number(blockNumber),
        contractAddress: CONTRACT_ADDRESS,
        explorerUrl: RPC_URL.includes("amoy") ? `https://amoy.polygonscan.com/address/${CONTRACT_ADDRESS}` : null
      }));
      return;
    }

    const { provider, wallet, contract } = await getContract();

    if (command === "releaseFund") {
      // args: batchId, amount, calamityName, sourceAgency
      const [_, batchId, amount, calamityName, sourceAgency] = args;
      const bId = toBytes32(batchId);
      const amtWei = ethers.parseEther(amount.toString());
      const tx = await contract.releaseFund(bId, amtWei, calamityName, sourceAgency);
      const receipt = await tx.wait();

      console.log(JSON.stringify({
        success: true,
        action: "releaseFund",
        txHash: receipt.hash,
        blockNumber: Number(receipt.blockNumber),
        gasUsed: receipt.gasUsed.toString(),
        contractAddress: CONTRACT_ADDRESS
      }));
    } else if (command === "allocateFund") {
      // args: batchId, allocationId, barangayId, amount
      const [_, batchId, allocationId, barangayId, amount] = args;
      const bId = toBytes32(batchId);
      const aId = toBytes32(allocationId);
      const brgyId = toBytes32(barangayId);
      const amtWei = ethers.parseEther(amount.toString());
      const tx = await contract.allocateFund(bId, aId, brgyId, amtWei);
      const receipt = await tx.wait();

      console.log(JSON.stringify({
        success: true,
        action: "allocateFund",
        txHash: receipt.hash,
        blockNumber: Number(receipt.blockNumber),
        gasUsed: receipt.gasUsed.toString()
      }));
    } else if (command === "confirmDistribution") {
      // args: batchId, distributionId, beneficiaryId, amount, receiptHash
      const [_, batchId, distributionId, beneficiaryId, amount, receiptHash] = args;
      const bId = toBytes32(batchId);
      const dId = toBytes32(distributionId);
      const benId = toBytes32(beneficiaryId);
      const amtWei = ethers.parseEther(amount.toString());
      const rHash = receiptHash.startsWith("0x") ? receiptHash : `0x${receiptHash}`;

      const tx = await contract.confirmDistribution(bId, dId, benId, amtWei, rHash);
      const receipt = await tx.wait();

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
      error: err.message || String(err)
    }));
  }
}

main();
