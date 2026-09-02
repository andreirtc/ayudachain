// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AyudaChainRegistry
 * @dev Single, tamper-evident digital trail from disaster relief fund release to household receipt.
 * Optimized for off-chain private data + on-chain cryptographic integrity proofs.
 */
contract AyudaChainRegistry {
    address public immutable owner;

    struct ReliefBatchRecord {
        bytes32 batchId;
        uint256 totalAmount;
        string calamityName;
        string sourceAgency;
        uint256 timestamp;
        bool exists;
    }

    struct AllocationRecord {
        bytes32 batchId;
        bytes32 allocationId;
        bytes32 barangayId;
        uint256 amount;
        uint256 timestamp;
        bool exists;
    }

    struct DistributionRecord {
        bytes32 batchId;
        bytes32 distributionId;
        bytes32 beneficiaryId;
        uint256 amount;
        bytes32 receiptHash; // SHA-256 integrity hash of off-chain receipt/document
        uint256 timestamp;
        bool exists;
    }

    struct GeneralRecord {
        bytes32 recordId;
        bytes32 recordHash;
        string recordType;
        uint256 timestamp;
        bool exists;
    }

    // Mappings
    mapping(bytes32 => ReliefBatchRecord) public batches;
    mapping(bytes32 => AllocationRecord) public allocations;
    mapping(bytes32 => DistributionRecord) public distributions;
    mapping(bytes32 => GeneralRecord) public anchoredRecords;

    // Authorized operators
    mapping(address => bool) public authorizedOperators;

    // Events
    event FundReleased(
        bytes32 indexed batchId,
        uint256 amount,
        string calamityName,
        string sourceAgency,
        uint256 timestamp
    );

    event FundAllocated(
        bytes32 indexed batchId,
        bytes32 indexed allocationId,
        bytes32 indexed barangayId,
        uint256 amount,
        uint256 timestamp
    );

    event DistributionConfirmed(
        bytes32 indexed batchId,
        bytes32 indexed distributionId,
        bytes32 indexed beneficiaryId,
        uint256 amount,
        bytes32 receiptHash,
        uint256 timestamp
    );

    event RecordAnchored(
        bytes32 indexed recordId,
        bytes32 recordHash,
        string recordType,
        uint256 timestamp
    );

    event OperatorUpdated(address indexed operator, bool authorized);

    modifier onlyAuthorized() {
        require(msg.sender == owner || authorizedOperators[msg.sender], "AyudaChain: Caller not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedOperators[msg.sender] = true;
    }

    function setOperator(address operator, bool authorized) external {
        require(msg.sender == owner, "AyudaChain: Only owner can set operator");
        authorizedOperators[operator] = authorized;
        emit OperatorUpdated(operator, authorized);
    }

    /**
     * @notice Records the release of a high-level calamity relief fund
     */
    function releaseFund(
        bytes32 batchId,
        uint256 amount,
        string calldata calamityName,
        string calldata sourceAgency
    ) external onlyAuthorized {
        require(batchId != bytes32(0), "AyudaChain: Invalid batch ID");
        require(!batches[batchId].exists, "AyudaChain: Batch already exists");
        require(amount > 0, "AyudaChain: Amount must be greater than zero");

        batches[batchId] = ReliefBatchRecord({
            batchId: batchId,
            totalAmount: amount,
            calamityName: calamityName,
            sourceAgency: sourceAgency,
            timestamp: block.timestamp,
            exists: true
        });

        emit FundReleased(batchId, amount, calamityName, sourceAgency, block.timestamp);
    }

    /**
     * @notice Records the allocation of funds to a specific barangay
     */
    function allocateFund(
        bytes32 batchId,
        bytes32 allocationId,
        bytes32 barangayId,
        uint256 amount
    ) external onlyAuthorized {
        require(batches[batchId].exists, "AyudaChain: Batch does not exist");
        require(allocationId != bytes32(0), "AyudaChain: Invalid allocation ID");
        require(!allocations[allocationId].exists, "AyudaChain: Allocation already exists");
        require(amount > 0, "AyudaChain: Allocation must be > 0");

        allocations[allocationId] = AllocationRecord({
            batchId: batchId,
            allocationId: allocationId,
            barangayId: barangayId,
            amount: amount,
            timestamp: block.timestamp,
            exists: true
        });

        emit FundAllocated(batchId, allocationId, barangayId, amount, block.timestamp);
    }

    /**
     * @notice Records confirmed distribution to a household beneficiary with off-chain receipt hash
     */
    function confirmDistribution(
        bytes32 batchId,
        bytes32 distributionId,
        bytes32 beneficiaryId,
        uint256 amount,
        bytes32 receiptHash
    ) external onlyAuthorized {
        require(batches[batchId].exists, "AyudaChain: Batch does not exist");
        require(distributionId != bytes32(0), "AyudaChain: Invalid distribution ID");
        require(!distributions[distributionId].exists, "AyudaChain: Distribution already exists");
        require(receiptHash != bytes32(0), "AyudaChain: Invalid receipt hash");

        distributions[distributionId] = DistributionRecord({
            batchId: batchId,
            distributionId: distributionId,
            beneficiaryId: beneficiaryId,
            amount: amount,
            receiptHash: receiptHash,
            timestamp: block.timestamp,
            exists: true
        });

        emit DistributionConfirmed(batchId, distributionId, beneficiaryId, amount, receiptHash, block.timestamp);
    }

    /**
     * @notice Generic anchor for audit records, audit reports, or anomaly investigation logs
     */
    function anchorRecord(
        bytes32 recordId,
        bytes32 recordHash,
        string calldata recordType
    ) external onlyAuthorized {
        require(recordId != bytes32(0), "AyudaChain: Invalid record ID");
        require(!anchoredRecords[recordId].exists, "AyudaChain: Record already anchored");

        anchoredRecords[recordId] = GeneralRecord({
            recordId: recordId,
            recordHash: recordHash,
            recordType: recordType,
            timestamp: block.timestamp,
            exists: true
        });

        emit RecordAnchored(recordId, recordHash, recordType, block.timestamp);
    }

    /**
     * @notice Publicly verify if a given receipt hash matches the immutable anchored on-chain record
     */
    function verifyReceipt(bytes32 distributionId, bytes32 receiptHash) external view returns (bool matched, uint256 timestamp) {
        DistributionRecord memory record = distributions[distributionId];
        if (!record.exists) {
            return (false, 0);
        }
        return (record.receiptHash == receiptHash, record.timestamp);
    }
}
