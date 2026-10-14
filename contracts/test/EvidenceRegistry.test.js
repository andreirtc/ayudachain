const { expect } = require('chai');
const { ethers } = require('hardhat');
const id = (n) => ethers.zeroPadValue(ethers.toBeHex(n), 32);

describe('AyudaChain evidence registry (separate from legacy)', function () {
  let registry, owner, stranger;
  beforeEach(async function () {
    [owner, stranger] = await ethers.getSigners();
    registry = await (await ethers.getContractFactory('AyudaChainEvidenceRegistry')).deploy(id(999));
  });
  it('round-trips full bytes32 and rejects unauthorized/duplicate/zero records', async function () {
    const opaque='0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe';
    await registry.anchorRecord(opaque,id(21),1,id(4),id(0),id(0));
    expect((await registry.records(opaque)).contentHash).to.equal(id(21));
    await expect(registry.anchorRecord(opaque,id(22),1,id(4),id(0),id(0))).to.be.reverted;
    await expect(registry.connect(stranger).anchorRecord(id(2),id(22),1,id(4),id(0),id(0))).to.be.reverted;
    await expect(registry.anchorRecord(id(2),id(0),1,id(4),id(0),id(0))).to.be.reverted;
  });
  it('atomically exposes signed centavo correction amounts and prevents repeated original correction',async function () {
    await registry.recordFundRelease(id(1),id(100),43500000n,id(11));
    const tx=await registry.recordFundCorrection(id(50),id(1),id(2),id(12),id(3),id(13),49500000n);
    const receipt=await tx.wait();
    expect((await registry.funds(id(2))).deltaCentavos).to.equal(-43500000n);
    expect((await registry.funds(id(3))).deltaCentavos).to.equal(49500000n);
    expect((await registry.corrections(id(50))).original).to.equal(id(1));
    await expect(registry.recordFundCorrection(id(51),id(1),id(4),id(14),id(5),id(15),1n)).to.be.reverted;
    expect((await registry.records(id(4))).contentHash).to.equal(id(0));
    console.log('correction gas units:',receipt.gasUsed.toString());
  });
  it('rejects cross-context lineage and exposes all private answers through one public kind',async function () {
    await registry.anchorRecord(id(1),id(11),6,id(100),id(0),id(0));
    await registry.anchorRecord(id(2),id(12),7,id(100),id(0),id(1));
    await registry.anchorRecord(id(3),id(13),7,id(100),id(2),id(1));
    expect((await registry.records(id(3))).kind).to.equal(7n);
    await expect(registry.anchorRecord(id(4),id(14),7,id(101),id(3),id(1))).to.be.reverted;
    await expect(registry.anchorRecord(id(5),id(15),8,id(100),id(0),id(0))).to.be.reverted;
  });
});
