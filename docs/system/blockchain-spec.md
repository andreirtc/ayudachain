# Current chain and verification specification

The evidence-v1 registry is separate from the unchanged legacy AyudaChainRegistry. [Compatibility ADR](../adr/2026-10-10-mvp-evidence-protocol-and-registry.md) defines canonical bytes, domain separation and compatibility. Exact Python-computed vectors live in shared/protocol/evidence-v1-vectors.json and are independently checked by Node tests.

Ten real commitment kinds are implemented: document, amount input, Barangay submission, system fallback, approved list, handover, outcome, fund release, reversal and replacement. Only required evidence receives standalone document commitments. Actor/member/contact/PIN/code/notices/operational case events do not gain invented anchors. Outcome uses the same opaque public kind with a private random nonce; the private answer is not a public label.

The canonical envelope uses normalized restricted JSON, exact decimal strings, source-byte descriptors, exact private business content, actor assurance, lineage and a private random nonce. Hash domain is AYUDACHAIN-EVIDENCE-v1 followed by a newline and the exact saved UTF-8 envelope. Source-byte hashes, extraction coverage and confirmed business fields are distinct. The unchanged old hasher covers legacy normalized receipt text only.

Deploy_evidence.js permits credential-free loopback chain ID 31337 only, refuses existing manifest paths and generates the new ABI artifact. Manifest pins registry UID, genesis and deployment block hashes, runtime code hash, ABI hash/address/chain and one-mined-local-block policy. Never hand-edit generated artifacts or replace a lost deployment with the latest address. Original legacy generated files remain unchanged.

The durable worker saves raw signed bytes, signer nonce and candidate hash before broadcast. Actual receipt, getter and events determine observations; no caught error can fabricate a hash/match. Unknown nonce consumption retains one uncertain signature and blocks a replacement. Proven actual revert permits a new nonce. Content conflict and deployment loss stop submission. Restart reconciliation and business result application are separate; each application writes one audit marker.

Funding corrections anchor a complete two-item reversal/replacement transaction with signed amounts and live predecessor/root/correction references. Business funding remains recorded during chain failures. Handover consumption remains final when its proof is unavailable. Supporting proof failures do not impose a hidden extra list-publication prerequisite.

Current verification returns exactly match, mismatch, required_anchor_absent, chain_unreachable or evidence_unavailable. A match requires an actual read of the pinned record and comparison of content, kind/context, lineage and funding fields. Changed raw bytes produce mismatch; missing material is unavailable. Earlier confirmed references are labelled historical after a failed fresh read and cannot supply current success.

Signer-free independent CLI: contracts/scripts/verify_evidence.js accepts canonical_utf8, content_hash, deployment and originals [{id,path}] on stdin. Fully permitted readers obtain material via commitments/{id}/material; originals must be actual private files. It needs neither database access nor a signing key. Selective resident inclusion proofs remain Pending. Frozen legacy reads use their imported original protocol/deployment/ABI, never the evidence-v1 registry.

No public-network deployment was performed. Local node state is ephemeral unless the operator preserves it. Backup cannot recreate a lost chain; use explicit deployment-loss handling and retained old history. See [local operation](../guides/local-mvp.md).
