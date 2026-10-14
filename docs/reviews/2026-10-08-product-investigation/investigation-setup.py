"""Investigation-only: snapshot first-party working-tree files, excluding secrets/runtime state."""
import hashlib, json, pathlib, shutil, subprocess, tempfile

root = pathlib.Path(__file__).resolve().parents[3]
review = pathlib.Path(__file__).resolve().parent
snapshot = pathlib.Path(tempfile.mkdtemp(prefix="ayudachain-investigation-"))
files = subprocess.check_output(["rg", "--files", "--hidden", "-g", "!node_modules", "-g", "!.git", "-g", "!.next", "-g", "!artifacts", "-g", "!cache", "-g", "!__pycache__", "-g", "!docs/reviews/**"], cwd=root, text=True).splitlines()
ledger = []
for name in sorted(files):
    source = root / name
    dest = snapshot / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    ledger.append({"path": name.replace("\\", "/"), "bytes": source.stat().st_size, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
baseline = {"root": str(root), "snapshot": str(snapshot), "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(), "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip(), "status": subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=root, text=True), "files": ledger}
(review / "initial-state.json").write_text(json.dumps(baseline, indent=2), encoding="utf-8")
(review / "investigation-log.md").write_text("# Investigation log\n\nStarted 2026-10-08 Asia/Manila. Expert evaluation with synthetic role-play; no real-user research.\n\n- Initial branch `" + baseline["branch"] + "`, HEAD `" + baseline["head"] + "`. Existing changes and per-file digests: initial-state.json. No branch switch, commit or stash performed.\n- Disposable snapshot: `" + str(snapshot) + "`. Secrets, databases, dependencies and build output excluded. Tests, deployment manifests and synthetic database mutations run here.\n- Required PRD, DFD and ERD absent; ADR directory contains only .gitkeep. Requested authoritative context and pilot owner; redesign assumptions remain provisional pending input.\n- Read AGENTS.md: no nested AGENTS.md found. Preserve all integrity invariants; no backend or product edits.\n", encoding="utf-8")
print(json.dumps({"snapshot": str(snapshot), "files": len(ledger), "review": str(review)}))
