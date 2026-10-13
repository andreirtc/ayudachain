# AyudaChain — Smart Contract & Blockchain Specifications

## 1. Network Deployment

| Parameter | Local EVM Mode | Polygon Amoy Testnet |
| :--- | :--- | :--- |
| **Network Name** | Localhost Hardhat Node | Polygon Amoy |
| **Chain ID** | `31337` | `80002` (`0x13882`) |
| **RPC Endpoint** | `http://127.0.0.1:8545` | `https://polygon-amoy-bor-rpc.publicnode.com` |
| **Contract Address** | `0x5FbDB2315678afecb367f032d93F642f64180aa3` | Configurable via `CONTRACT_ADDRESS` |
| **Block Explorer** | Local terminal logs | `https://amoy.polygonscan.com/` |

---

## 2. Smart Contract: `AyudaChainRegistry.sol`

- **Solidity Version**: `^0.8.20`
- **Compiler Optimizer**: Enabled (`200` runs)
- **Design Pattern**: Append-only integrity registry with authorized operator access controls.

### Functions

#### `releaseFund(bytes32 batchId, uint256 amount, string calamityName, string sourceAgency)`
- Emits: `event FundReleased(bytes32 indexed batchId, uint256 amount, string calamityName, string sourceAgency, uint256 timestamp)`
- Validations: Batch must not already exist; amount > 0.

#### `allocateFund(bytes32 batchId, bytes32 allocationId, bytes32 barangayId, uint256 amount)`
- Emits: `event FundAllocated(bytes32 indexed batchId, bytes32 indexed allocationId, bytes32 indexed barangayId, uint256 amount, uint256 timestamp)`
- Validations: Referenced batch must exist; allocation must not be duplicated.

#### `confirmDistribution(bytes32 batchId, bytes32 distributionId, bytes32 beneficiaryId, uint256 amount, bytes32 receiptHash)`
- Emits: `event DistributionConfirmed(bytes32 indexed batchId, bytes32 indexed distributionId, bytes32 indexed beneficiaryId, uint256 amount, bytes32 receiptHash, uint256 timestamp)`
- Validations: Distribution must not already exist; receiptHash != bytes32(0).

#### `verifyReceipt(bytes32 distributionId, bytes32 receiptHash) external view returns (bool matched, uint256 timestamp)`
- Public query returning `true` if and only if the queried receipt hash matches the immutable on-chain record.

---

## 3. Gas & Cost Efficiency Analysis

Because files, scanned images, and names are stored off-chain:
- Gas per distribution confirmation: **~183,265 units**.
- At typical Polygon gas prices (30 Gwei), each household receipt anchoring costs **< $0.001 USD**, making nationwide disaster relief tracking economically viable for government LGUs.
