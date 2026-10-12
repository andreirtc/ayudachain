// Prepare without broadcasting; recover only the exact stored signed transaction.
const { ethers } = require("ethers");
const fs = require("node:fs");
const path = require("node:path");

function failure(code) { const error = new Error(code); error.safeCode = code; throw error; }
// Preserve the registry's existing encoding for historical compatibility.
function id(value) { return /^0x[\da-f]{64}$/i.test(value) ? value : ethers.encodeBytes32String(value.slice(0, 31)); }
function same(a, b) { return typeof a === "string" && typeof b === "string" && a.toLowerCase() === b.toLowerCase(); }
function callArgs(p) { return [id(p.batch_id), id(p.allocation_id), id(p.distribution_id), id(p.beneficiary_id), BigInt(p.amount_centavos), p.receipt_hash]; }

async function context(p, pin) {
  const provider = new ethers.JsonRpcProvider(process.env.POLYGON_RPC_URL);
  const chainId = Number((await provider.getNetwork()).chainId);
  if (![31337, 80002].includes(chainId) || chainId !== p.chain_id || chainId !== Number(process.env.CHAIN_ID)) failure("CHAIN_CHANGED");
  if (!same(p.contract_address, process.env.CONTRACT_ADDRESS)) failure("DEPLOYMENT_CHANGED");
  const code = await provider.getCode(p.contract_address);
  if (code === "0x") failure("DEPLOYMENT_CHANGED");
  const codeHash = ethers.keccak256(code);
  if (pin) {
    const block = await provider.getBlock(pin.block_number);
    if (!block || !same(block.hash, pin.block_hash) || !same(codeHash, pin.code_hash)) failure("DEPLOYMENT_CHANGED");
  }
  const artifact = JSON.parse(fs.readFileSync(path.join(__dirname, "../artifacts/contracts/AyudaChainRegistry.sol/AyudaChainRegistry.json")));
  const contract = new ethers.Contract(p.contract_address, artifact.abi, provider);
  return { provider, contract, codeHash };
}

function recordMatches(record, p) {
  return record.exists === true && same(record.batchId, id(p.batch_id)) && same(record.allocationId, id(p.allocation_id)) &&
    same(record.distributionId, id(p.distribution_id)) && same(record.beneficiaryId, id(p.beneficiary_id)) &&
    record.amount === BigInt(p.amount_centavos) && same(record.receiptHash, p.receipt_hash) && record.timestamp > 0n;
}

async function prepare(p) {
  const { provider, contract, codeHash } = await context(p);
  if ((await contract.distributions(id(p.distribution_id))).exists) failure("ANCHOR_CONFLICT");
  const wallet = new ethers.Wallet(process.env.POLYGON_PRIVATE_KEY, provider);
  const request = await wallet.populateTransaction(await contract.confirmDistribution.populateTransaction(...callArgs(p)));
  const raw = await wallet.signTransaction(request);
  const block = await provider.getBlock("latest");
  return { success: true, raw_transaction: raw, tx_hash: ethers.keccak256(raw), chain_id: p.chain_id,
    contract_address: p.contract_address, pin: { block_number: block.number, block_hash: block.hash, code_hash: codeHash } };
}

async function recover(p, raw, pin, broadcast, expectedHash) {
  if (!pin || !Number.isInteger(pin.block_number) || !/^0x[\da-f]{64}$/i.test(pin.block_hash || "") || !/^0x[\da-f]{64}$/i.test(pin.code_hash || "")) failure("ENVELOPE_CHANGED");
  const { provider, contract } = await context(p, pin);
  let parsed;
  try { parsed = ethers.Transaction.from(raw); } catch (_) { failure("ENVELOPE_CHANGED"); }
  const expectedData = contract.interface.encodeFunctionData("confirmDistribution", callArgs(p));
  if (Number(parsed.chainId) !== p.chain_id || !same(parsed.to, p.contract_address) || !same(parsed.data, expectedData) || parsed.value !== 0n || !parsed.from) failure("ENVELOPE_CHANGED");
  const txHash = ethers.keccak256(raw);
  if (!same(txHash, expectedHash)) failure("ENVELOPE_CHANGED");
  let receipt = await provider.getTransactionReceipt(txHash);
  const record = await contract.distributions(id(p.distribution_id));
  if (receipt) {
    if (receipt.status !== 1) failure("TRANSACTION_REVERTED");
    const block = await provider.getBlock(receipt.blockNumber);
    if (!same(receipt.hash, txHash) || !same(receipt.to, p.contract_address) || !block || !same(block.hash, receipt.blockHash) || !recordMatches(record, p)) failure("ANCHOR_CONFLICT");
    return { success: true, state: "CONFIRMED", tx_hash: txHash, chain_id: p.chain_id, contract_address: p.contract_address,
      block_number: receipt.blockNumber, block_hash: receipt.blockHash, receipt_timestamp: Number(record.timestamp) };
  }
  if (record.exists) failure("ANCHOR_CONFLICT");
  // Never solve unknown nonce consumption by creating a new transaction.
  if (await provider.getTransactionCount(parsed.from, "latest") > parsed.nonce) failure("NONCE_CONFLICT");
  if (broadcast) {
    try { await provider.broadcastTransaction(raw); }
    catch (_) {
      // A lost broadcast response may still have been accepted. Reconcile later.
      return { success: true, state: "SUBMITTED", tx_hash: txHash, error_code: "BROADCAST_UNCERTAIN" };
    }
    // Local automining may already have completed; public testnets can stay pending.
    return recover(p, raw, pin, false, expectedHash);
  }
  return { success: true, state: "SUBMITTED", tx_hash: txHash };
}

async function main() {
  try {
    const input = JSON.parse(fs.readFileSync(0, "utf8"));
    const result = process.argv[2] === "prepare" ? await prepare(input.payload) :
      await recover(input.payload, input.raw_transaction, input.pin, process.argv[2] === "recover", input.candidate_tx_hash);
    console.log(JSON.stringify(result));
  } catch (error) {
    // Never echo RPC errors with raw signed transactions, request bodies or keys.
    console.log(JSON.stringify({ success: false, error_code: error.safeCode || "RPC_UNAVAILABLE" }));
  }
}
if (require.main === module) main();
module.exports = { prepare, recover, recordMatches };
