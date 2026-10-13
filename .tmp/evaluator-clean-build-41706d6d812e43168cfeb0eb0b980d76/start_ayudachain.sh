#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================================"
echo "🇵🇭  STARTING AYUDACHAIN PLATFORM"
echo "========================================================"

# Cleanup function when user presses Ctrl+C
kill_ports() {
    python3 -c '
import os, signal, glob
def kill_port(target_port):
    hex_port = f":{target_port:04X}"
    inodes = set()
    for netfile in ["/proc/net/tcp", "/proc/net/tcp6"]:
        if os.path.exists(netfile):
            with open(netfile) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) > 9 and parts[1].endswith(hex_port):
                        inodes.add(parts[9])
    if not inodes:
        return
    for fd_path in glob.glob("/proc/[0-9]*/fd/*"):
        try:
            target = os.readlink(fd_path)
            for inode in inodes:
                if f"[{inode}]" in target:
                    pid = int(fd_path.split("/")[2])
                    if pid != os.getpid():
                        os.kill(pid, signal.SIGKILL)
        except Exception:
            pass
for p in [8000, 8545, 3000]:
    kill_port(p)
' 2>/dev/null || true
    pkill -f "python3.*server.py" 2>/dev/null || true
    pkill -f "hardhat.*node" 2>/dev/null || true
    pkill -f "next.*start" 2>/dev/null || true
}

# Cleanup function when user presses Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Stopping all AyudaChain services..."
    kill $(jobs -p) 2>/dev/null
    kill_ports
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 0. Clean up any stale processes holding our ports
echo "🧹 [0/3] Checking & clearing ports 8000, 8545, 3000..."
kill_ports
sleep 1

# 1. Start Hardhat Blockchain Node
echo "📦 [1/3] Starting Local EVM Blockchain Node (Port 8545)..."
cd "$ROOT_DIR/contracts"
npx hardhat node --hostname 127.0.0.1 --port 8545 > /tmp/ayudachain_hardhat.log 2>&1 &
for i in {1..15}; do
    if curl -s -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}' http://127.0.0.1:8545 > /dev/null 2>&1; then
        echo "       ✓ Blockchain node is active (Port 8545)"
        break
    fi
    sleep 0.4
done

# Deploy / Anchor Smart Contract
echo "📜       Deploying AyudaChainRegistry Smart Contract..."
npx hardhat run scripts/deploy.js --network localhost > /tmp/ayudachain_deploy.log 2>&1

# 2. Start Python Backend
echo "🐍 [2/3] Starting Python REST API Server (Port 8000)..."
cd "$ROOT_DIR/backend"
python3 server.py 8000 > /tmp/ayudachain_backend.log 2>&1 &
for i in {1..15}; do
    if curl -s http://127.0.0.1:8000/api/dashboard > /dev/null 2>&1; then
        echo "       ✓ Backend API is healthy and responding (Port 8000)"
        break
    fi
    sleep 0.4
done

# 3. Start Next.js Frontend
echo "🌐 [3/3] Starting Next.js Web App (Port 3000)..."
echo "========================================================"
echo "✅ All services successfully started and verified!"
echo "👉 Open your browser at: http://localhost:3000"
echo "Press Ctrl+C anytime to stop all services."
echo "========================================================"
cd "$ROOT_DIR/frontend"
./node_modules/.bin/next start -p 3000
