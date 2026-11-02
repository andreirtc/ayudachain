# Local evaluation chain interruption

Observed 14October2026 around 08:42 Asia/Manila during compact-layout verification. The previously owned process PID33671 was absent and nothing listened on 8545. The existing fault node 8555 remained alive. The reason for the original node's exit is unknown; its log ended with ordinary reads, not a diagnosed cause.

The fresh capture script stopped on an actual failed integrity check. The compact 24-case browser run completed 23 passes / 1 failure: the all-sections traversal timed out waiting for records during the outage. That run is not a complete green validation. Two new compact-layout cases, role navigation, receipt guidance and error regressions passed. Earlier recorded matching evidence at block 172 is a historical result, not proof of current 8545 availability.

No reset, manifest replacement or attempt to recreate the old registry at the old endpoint was performed. All database records, originals, manifests and earlier captures/results were preserved. Hardhat keeps chain state in memory; the old in-memory history is currently unavailable and cannot be inferred from database history or regenerated transaction hashes.

A separately owned new local node was created on 8546 with its own private startup log and process record. A new random evaluation/test database pair and new manifest/original root were created under `.runtime/finals/labs/3cb6fc3db148/`. The original 8545 endpoint and all its manifests remain unchanged. This is a NEW isolated rehearsal, not recovery or verification of old records. The new node is detached from tool-terminal lifetime and remains local-only.

Current selected configuration is recorded privately in `.runtime/finals/selected-lab-path.txt`. Final rehearsal/tests/captures will explicitly refer to the new lab. Keep new and old evidence separate. Never use the new node to claim verification of an old deployment.

## Resumed workspace —14October2026

After the pause all local service listeners were absent, including the independently owned8546node. Its in-memory history is unavailable; all corresponding DBs/manifests/originals remain. Restarted the existing owned PostgreSQL cluster without initialization/reset. Created a NEW isolated node8547and NEW random labs; no old pinned deployment was recreated. Wrong initial Hardhat cwd caused HH1 before any deployment, then corrected. Actual new handover matches observed at blocks51and71. These do not verify older8545/8546commitments.
