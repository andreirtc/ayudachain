// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Append-only evidence witness. No eligibility, identity or cash assertions.
contract AyudaChainEvidenceRegistry {
    uint256 public constant MAX_CENTAVOS = 9_000_000_000_000_000_000;
    address public immutable operator;
    bytes32 public immutable deploymentUid;
    struct Record { bytes32 contentHash; uint8 kind; bytes32 context; bytes32 predecessor; bytes32 related; uint256 timestamp; }
    struct Fund { int256 deltaCentavos; bytes32 disaster; bytes32 root; bytes32 correctionSet; }
    struct Correction { bytes32 original; bytes32 reversal; bytes32 replacement; }
    mapping(bytes32 => Record) public records;
    mapping(bytes32 => Fund) public funds;
    mapping(bytes32 => Correction) public corrections;
    mapping(bytes32 => bytes32) public liveFundHead;
    event RecordAnchored(bytes32 indexed id, bytes32 contentHash, uint8 kind, bytes32 indexed context, bytes32 predecessor, bytes32 related);
    event FundReleased(bytes32 indexed entry, bytes32 indexed disaster, int256 deltaCentavos, bytes32 contentHash);
    event FundCorrected(bytes32 indexed correctionSet, bytes32 indexed original, bytes32 reversal, bytes32 reversalHash, int256 reversalCentavos, bytes32 replacement, bytes32 replacementHash, int256 replacementCentavos, bytes32 root);
    modifier onlyOperator() { require(msg.sender == operator, 'operator required'); _; }
    constructor(bytes32 uid) { require(uid != bytes32(0), 'uid required'); operator=msg.sender; deploymentUid=uid; }
    function _put(bytes32 id, bytes32 hash, uint8 kind, bytes32 context, bytes32 predecessor, bytes32 related) private {
        require(id != bytes32(0) && hash != bytes32(0) && context != bytes32(0), 'nonzero required');
        require(records[id].contentHash == bytes32(0), 'already recorded');
        records[id]=Record(hash,kind,context,predecessor,related,block.timestamp);
        emit RecordAnchored(id,hash,kind,context,predecessor,related);
    }
    function anchorRecord(bytes32 id, bytes32 hash, uint8 kind, bytes32 context, bytes32 predecessor, bytes32 related) external onlyOperator {
        require(kind >= 1 && kind <= 7, 'generic kind invalid');
        if (predecessor != bytes32(0)) {
            Record memory prior=records[predecessor];
            require(prior.contentHash != bytes32(0) && prior.kind == kind && prior.context == context, 'lineage invalid');
        }
        if (related != bytes32(0)) require(records[related].contentHash != bytes32(0), 'related absent');
        if (kind == 7) require(related != bytes32(0) && records[related].kind == 6 && records[related].context == context, 'handover required');
        _put(id,hash,kind,context,predecessor,related);
    }
    function recordFundRelease(bytes32 entry, bytes32 disaster, uint256 amountCentavos, bytes32 hash) external onlyOperator {
        require(amountCentavos > 0 && amountCentavos <= MAX_CENTAVOS, 'amount invalid');
        _put(entry,hash,8,disaster,bytes32(0),bytes32(0));
        funds[entry]=Fund(int256(amountCentavos),disaster,entry,bytes32(0));
        liveFundHead[entry]=entry;
        emit FundReleased(entry,disaster,int256(amountCentavos),hash);
    }
    function recordFundCorrection(bytes32 set, bytes32 original, bytes32 reversal, bytes32 reversalHash, bytes32 replacement, bytes32 replacementHash, uint256 replacementCentavos) external onlyOperator {
        require(set != bytes32(0) && corrections[set].original == bytes32(0), 'correction exists');
        require(reversal != replacement && reversal != original && replacement != original, 'distinct entries required');
        require(replacementCentavos > 0 && replacementCentavos <= MAX_CENTAVOS, 'amount invalid');
        Fund memory prior=funds[original];
        require(prior.deltaCentavos > 0 && liveFundHead[prior.root] == original, 'live positive original required');
        _put(reversal,reversalHash,9,prior.disaster,original,set);
        _put(replacement,replacementHash,10,prior.disaster,original,set);
        funds[reversal]=Fund(-prior.deltaCentavos,prior.disaster,prior.root,set);
        funds[replacement]=Fund(int256(replacementCentavos),prior.disaster,prior.root,set);
        corrections[set]=Correction(original,reversal,replacement);
        liveFundHead[prior.root]=replacement;
        emit FundCorrected(set,original,reversal,reversalHash,-prior.deltaCentavos,replacement,replacementHash,int256(replacementCentavos),prior.root);
    }
}
