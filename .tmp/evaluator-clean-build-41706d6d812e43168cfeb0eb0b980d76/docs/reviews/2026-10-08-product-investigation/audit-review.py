"""Read-only preservation/coverage/artifact audit; writes only its review JSON."""
import datetime, hashlib, json, pathlib, re, socket, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
review = pathlib.Path(__file__).resolve().parent
initial = json.loads((review / "initial-state.json").read_text(encoding="utf-8"))
root = pathlib.Path(initial["root"])
expected = {x["path"] for x in initial["files"]}
additional = json.loads((review / "additional-context-state.json").read_text(encoding="utf-8"))
complete_expected = expected | {x["path"] for x in additional}
coverage = json.loads((review / "coverage-ledger.json").read_text(encoding="utf-8"))
changes = []
for row in initial["files"]:
    p = root / row["path"]
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != row["sha256"]:
        changes.append(row["path"])
concurrent_changes = []
for row in additional:
    p = root / row["path"]
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != row["sha256"]:
        concurrent_changes.append(row["path"])
command = ["rg", "--files", "--hidden", "-g", "!node_modules", "-g", "!.git", "-g", "!.next", "-g", "!artifacts", "-g", "!cache", "-g", "!__pycache__", "-g", "!docs/reviews/**"]
current = {p.replace("\\", "/") for p in subprocess.check_output(command, cwd=root, text=True).splitlines()}
status = subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=root, text=True)
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()
def without_reviews(s):
    return [line for line in s.splitlines() if "docs/reviews/" not in line]
main = ["product-review.md", "evidence-and-journeys.md", "redesign-blueprint.md", "validation-and-roadmap.md"]
broken = []
for name in main:
    body = (review / name).read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", body):
        path = target.split("#", 1)[0]
        if not path or re.match(r"https?://", path):
            continue
        if path == "completion-audit.json":
            continue
        if not (review / path).exists():
            broken.append({"file": name, "target": target})
ports = {}
for port in (3000, 8000, 8545, 8400):
    with socket.socket() as s:
        s.settimeout(1)
        ports[str(port)] = s.connect_ex(("127.0.0.1", port)) == 0
journeys = json.loads((review / "browser-journeys.json").read_text(encoding="utf-8"))
result = {
    "audited_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "initial_source_count": len(expected), "current_source_count": len(complete_expected), "covered_source_count": len(coverage),
    "all_original_source_hashes_unchanged": not changes, "changed_original_files": changes,
    "concurrent_context_additions": additional, "concurrent_files_unchanged_since_review": not concurrent_changes,
    "unaccounted_first_party_outside_reviews": sorted(current-complete_expected), "missing_initial_files": sorted(expected-current),
    "coverage_missing": sorted(complete_expected-{x['path'] for x in coverage}),
    "head_unchanged": head == initial['head'], "branch_unchanged": branch == initial['branch'],
    "original_git_status_preserved": without_reviews(status) == without_reviews(initial['status']),
    "final_git_status": status, "main_artifacts": {n:(review/n).stat().st_size for n in main},
    "broken_local_main_artifact_links": broken, "root_journey_snapshots": len(journeys),
    "root_screenshots_all_exist": all((review/'screenshots'/f"{x['label']}.png").exists() for x in journeys),
    "independent_A_screenshots": len(list(review.glob('design-a-*.png'))),
    "listeners_after_owned_cleanup": ports,
    "objective_gate": {
        "problem_and_thesis": "product-review: maintainer hackathon-only/DSWD-intended context, jobs, causal chain, six trust distinctions; no pilot owner/authority",
        "all_first_party_areas": "75-file coverage table/JSON (73 initial +2 concurrent scratch drafts); active and dormant paths attributed",
        "runtime_routes_and_core_jobs": "all five desktop/mobile routes; 10-job table; absent supervisor/correction/dispute recorded as unsupported",
        "failure_and_trust": "E01-E15; real outage/restart, concurrency, lost response, tamper/delete/reset, encoding probes, draft critique; untested permutations explicit",
        "credibility_and_mvp": "direct verdict F01-F11; no arbitrary score; immediate honest synthetic hackathon scope separate from possible later pilot safeguards",
        "alternatives_and_blueprint": "four directions, including conditional finance-first alternative; signed-only vs checkpoint vs per-record witnessing; states/permissions/screens/corrections/privacy",
        "approval_and_compatibility": "proposals only; schema/hash/interface/dependency/deletion/network approvals; v1/ID/money/version migration",
        "validation_and_scale": "immediate H1-H4 contest priorities; ordered future-pilot milestones, measurable unmeasured gates, field research/falsification, explicit scale triggers",
        "evidence_separation": "R/S/T/D/X/I/A/P; synthetic role-play, no real cash/users, limits and missing context explicit",
        "independent_review": "A design/docs, B backend/contract, primary-source audits; material corrections integrated",
        "preservation": "source digests plus git status/head/branch and owned service cleanup checked"
    },
    "remaining_unverified": ["real-user/owner demand and current policy pack", "MC24/2025/full current COA requirements", "production chain/payment integrations, throughput/fiat fees", "backup restore/key incident/full security and accessibility", "unsupported offline sync/conflicts, supervisor/dispute/correction jobs"],
    "note": "Remaining items are explicit limits/future validation, not successful runtime checks. No product redesign implemented."
}
(review / "completion-audit.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
assert not changes and not concurrent_changes and current == complete_expected and not broken
assert result['coverage_missing'] == [] and len(coverage) == len(complete_expected)
assert result['head_unchanged'] and result['branch_unchanged'] and result['original_git_status_preserved']
assert result['root_screenshots_all_exist'] and not any(ports.values())
