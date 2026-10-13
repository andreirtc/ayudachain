const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AyudaChainRegistry Smart Contract", function () {
  let registry;
  let owner, operator, unauthorizedUser;

  const batchId = ethers.encodeBytes32String("RELIEF-2026-001");
  const allocationId = ethers.encodeBytes32String("ALLOC-0001");
  const barangayId = ethers.encodeBytes32String("BRGY-001");
  const beneficiaryId = ethers.encodeBytes32String("BEN-0001");
  const distributionId = ethers.encodeBytes32String("DIST-0001");
  const sampleReceiptHash = ethers.keccak256(ethers.toUtf8Bytes("CANONICAL_RECEIPT_BEN_0001"));

  beforeEach(async function () {
    [owner, operator, unauthorizedUser] = await ethers.getSigners();

    const AyudaChainRegistry = await ethers.getContractFactory("AyudaChainRegistry");
    registry = await AyudaChainRegistry.deploy();
    await registry.waitForDeployment();
  });

  describe("Access Control & Initialization", function () {
    it("should set deployer as owner and default operator", async function () {
      expect(await registry.owner()).to.equal(owner.address);
      expect(await registry.authorizedOperators(owner.address)).to.be.true;
    });

    it("should allow owner to authorize new operators", async function () {
      await expect(registry.setOperator(operator.address, true))
        .to.emit(registry, "OperatorUpdated")
        .withArgs(operator.address, true);

      expect(await registry.authorizedOperators(operator.address)).to.be.true;
    });

    it("should prevent unauthorized accounts from releasing funds", async function () {
      await expect(
        registry.connect(unauthorizedUser).releaseFund(
          batchId,
          ethers.parseEther("10000000"),
          "Typhoon Salinlahi",
          "DSWD Central"
        )
      ).to.be.revertedWith("AyudaChain: Caller not authorized");
    });
  });

  describe("P0 Workflow: Fund Release -> Allocation -> Distribution", function () {
    it("should successfully record fund release and emit event", async function () {
      const amount = ethers.parseEther("10000000"); // 10 Million units
      await expect(registry.releaseFund(batchId, amount, "Typhoon Salinlahi", "DSWD Central"))
        .to.emit(registry, "FundReleased");

      const batch = await registry.batches(batchId);
      expect(batch.exists).to.be.true;
      expect(batch.totalAmount).to.equal(amount);
      expect(batch.calamityName).to.equal("Typhoon Salinlahi");
    });

    it("should prevent duplicate batch creation (append-only integrity)", async function () {
      const amount = ethers.parseEther("10000000");
      await registry.releaseFund(batchId, amount, "Typhoon Salinlahi", "DSWD Central");

      await expect(
        registry.releaseFund(batchId, amount, "Typhoon Salinlahi", "DSWD Central")
      ).to.be.revertedWith("AyudaChain: Batch already exists");
    });

    it("should record barangay allocation under an active batch", async function () {
      const batchAmount = ethers.parseEther("10000000");
      await registry.releaseFund(batchId, batchAmount, "Typhoon Salinlahi", "DSWD Central");

      const allocAmount = ethers.parseEther("2500000");
      await expect(registry.allocateFund(batchId, allocationId, barangayId, allocAmount))
        .to.emit(registry, "FundAllocated");

      const alloc = await registry.allocations(allocationId);
      expect(alloc.exists).to.be.true;
      expect(alloc.amount).to.equal(allocAmount);
    });

    it("should confirm distribution and anchor cryptographic receipt hash", async function () {
      const batchAmount = ethers.parseEther("10000000");
      await registry.releaseFund(batchId, batchAmount, "Typhoon Salinlahi", "DSWD Central");

      const distAmount = ethers.parseEther("5000");
      await expect(
        registry.confirmDistribution(batchId, distributionId, beneficiaryId, distAmount, sampleReceiptHash)
      ).to.emit(registry, "DistributionConfirmed")
       .withArgs(batchId, distributionId, beneficiaryId, distAmount, sampleReceiptHash, (ts) => ts > 0);

      const dist = await registry.distributions(distributionId);
      expect(dist.exists).to.be.true;
      expect(dist.receiptHash).to.equal(sampleReceiptHash);
    });

    it("should verify matching receipt hash and reject mismatched/altered hash", async function () {
      const batchAmount = ethers.parseEther("10000000");
      await registry.releaseFund(batchId, batchAmount, "Typhoon Salinlahi", "DSWD Central");

      const distAmount = ethers.parseEther("5000");
      await registry.confirmDistribution(batchId, distributionId, beneficiaryId, distAmount, sampleReceiptHash);

      // Verify authentic hash
      const [matched, timestamp] = await registry.verifyReceipt(distributionId, sampleReceiptHash);
      expect(matched).to.be.true;
      expect(timestamp).to.be.gt(0);

      // Tampered hash check
      const fakeHash = ethers.keccak256(ethers.toUtf8Bytes("TAMPERED_RECEIPT_DATA"));
      const [fakeMatched] = await registry.verifyReceipt(distributionId, fakeHash);
      expect(fakeMatched).to.be.false;
    });

    it("should anchor generic audit report hashes", async function () {
      const recordId = ethers.encodeBytes32String("AUDIT-LOG-001");
      const reportHash = ethers.keccak256(ethers.toUtf8Bytes("AUDIT_COMPLIANCE_REPORT_SEPT_2026"));

      await expect(registry.anchorRecord(recordId, reportHash, "COA_ANNUAL_AUDIT"))
        .to.emit(registry, "RecordAnchored");

      const rec = await registry.anchoredRecords(recordId);
      expect(rec.exists).to.be.true;
      expect(rec.recordHash).to.equal(reportHash);
    });
  });
});
