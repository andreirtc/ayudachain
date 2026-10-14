# Teammate reference branch

Requested by the maintainer after the natural Taglish work. **[Draft PR40](https://github.com/andreirtc/ayudachain/pull/40) · Branch:feat/finals-reference**. It is a separate main-based reference snapshot; design-proposal's original worktree stays uncommitted and intact. Main and other branches/PRs are unchanged. This is a draft reference for review, not an instruction to merge wholesale or a production release.

First commit captures the existing approved design-proposal baseline4377db1. The next layer adds finals UI/demo fixes, recreated logo, English/Taglish interface, docs and selected synthetic evidence. The broad PR against main includes the pre-existing MVP; it is not all newly authored finalist work. To inspect only finals differences, compare4377db1 directly with this branch.

```bash
git fetch origin feat/finals-reference
git diff 4377db1..origin/feat/finals-reference -- frontend docs/finals backend/scripts
```

Use your own clean checkout/worktree for experiments. Do not overwrite a teammate's dirty branch. Runtime databases, private .env configuration, originals, manifests/replay keys and signing material are excluded. New checkout requires its own dependencies and isolated lab; the branch does not carry the running local chain.

Start reading docs/finals/taglish/START_HERE.md. Read FINALIST_READINESS and DEMO_RUNBOOK before running. Do not combine PR39's authentication with this branch's claims; it has impersonable selectable actors. Full reviewer approval/merge/deployment is outside this task.
