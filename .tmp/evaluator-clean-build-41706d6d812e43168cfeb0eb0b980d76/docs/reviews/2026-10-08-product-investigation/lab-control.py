"""Investigation harness; all runtime mutation is in a disposable source snapshot."""
import json, os, pathlib, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")

review = pathlib.Path(__file__).resolve().parent
lab = pathlib.Path(json.loads((review / "initial-state.json").read_text())["snapshot"])
env = os.environ.copy()
for key in ("POLYGON_PRIVATE_KEY", "CONTRACT_ADDRESS", "POLYGON_RPC_URL", "DATABASE_URL"):
    env.pop(key, None)
env["POLYGON_RPC_URL"] = "http://127.0.0.1:8545"
env["PYTHONUNBUFFERED"] = "1"
env["NEXT_TELEMETRY_DISABLED"] = "1"
statefile = lab / "investigation-processes.json"
state = json.loads(statefile.read_text()) if statefile.exists() else {}
name = sys.argv[1]
commands = {
    "backend-tests": ([sys.executable, "backend/test_backend.py"], lab),
    "contracts-tests": (["npm.cmd", "test"], lab / "contracts"),
    "compile": (["npm.cmd", "run", "compile"], lab / "contracts"),
    "typecheck": (["node", "node_modules/typescript/bin/tsc", "--noEmit"], lab / "frontend"),
    "build": (["npm.cmd", "run", "build"], lab / "frontend"),
    "deploy": (["npm.cmd", "run", "deploy:local"], lab / "contracts"),
    "chain": (["node", "node_modules/hardhat/internal/cli/cli.js", "node", "--hostname", "127.0.0.1", "--port", "8545"], lab / "contracts"),
    "backend": ([sys.executable, "server.py", "8000"], lab / "backend"),
    "frontend": (["node", "node_modules/next/dist/bin/next", "start", "-p", "3000", "-H", "127.0.0.1"], lab / "frontend"),
}
if name == "stop":
    target = sys.argv[2]
    owned = state.get(target)
    if not owned:
        raise SystemExit("No recorded owned process")
    subprocess.run(["taskkill", "/PID", str(owned["pid"]), "/T", "/F"], check=False, capture_output=True)
    owned["stopped"] = time.time()
    statefile.write_text(json.dumps(state, indent=2))
    print(json.dumps({"stopped": target, "pid": owned["pid"]}))
else:
    cmd, cwd = commands[name]
    if name in ("chain", "backend", "frontend"):
        logfile = lab / ("investigation-" + name + ".log")
        with logfile.open("a", encoding="utf-8") as output:
            proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        state[name] = {"pid": proc.pid, "cmd": cmd, "cwd": str(cwd), "log": str(logfile), "started": time.time()}
        statefile.write_text(json.dumps(state, indent=2))
        print(json.dumps(state[name]))
    else:
        proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        output = proc.stdout + proc.stderr
        output = re.sub(r"0x[0-9a-fA-F]{64}", "[64-hex value omitted from setup log]", output) if name == "deploy" else output
        (review / (name + "-output.txt")).write_text("Command: " + subprocess.list2cmdline(cmd) + "\nCWD: " + str(cwd) + "\nExit: " + str(proc.returncode) + "\n\n" + output, encoding="utf-8")
        print(output)
        raise SystemExit(proc.returncode)
