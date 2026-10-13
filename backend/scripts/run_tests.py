"""Run every non-live backend suite in a fresh process to isolate global fixtures.

Live-chain recovery uses contracts/scripts/test_payout_anchor_live.js separately.
"""
from pathlib import Path
import os
import subprocess
import sys

backend = Path(__file__).resolve().parents[1]
venv_python = backend / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
python = str(venv_python) if venv_python.is_file() else sys.executable
failed = []
for suite in sorted(backend.glob("test_*.py")):
    if suite.name == "test_payout_anchors_live.py":
        continue
    print(f"Running {suite.name}", flush=True)
    result = subprocess.run([python, str(suite)], cwd=backend)
    if result.returncode:
        failed.append(suite.name)
if failed:
    print("Failed suites: " + ", ".join(failed), file=sys.stderr)
    raise SystemExit(1)
