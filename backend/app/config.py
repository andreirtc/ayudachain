"""
AyudaChain backend settings.
Every setting is read here, in this order: process environment, then backend/.env,
then the local contract deployment file, then local development defaults.
"""

import os
import json

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BACKEND_DIR, ".env")
DEPLOYMENT_FILE = os.path.join(BACKEND_DIR, "app", "blockchain", "AyudaChainRegistry.json")

# Hardhat test account #0. Public and only valid for the local chain.
LOCAL_DEV_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

KNOWN_NETWORKS = {31337: "Local EVM", 80002: "Polygon Amoy"}


def _load_env_file(path: str) -> None:
    """Load KEY=VALUE lines without overriding variables already set."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _load_deployment(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


_load_env_file(ENV_FILE)
_deployment = _load_deployment(DEPLOYMENT_FILE)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BACKEND_DIR, 'ayudachain.db')}")
RECEIPTS_DIR = os.getenv("RECEIPTS_DIR", os.path.join(BACKEND_DIR, "app", "data", "receipts"))

RPC_URL = os.getenv("POLYGON_RPC_URL", "http://127.0.0.1:8545")
PRIVATE_KEY = os.getenv("POLYGON_PRIVATE_KEY", LOCAL_DEV_PRIVATE_KEY)
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS") or _deployment.get("contractAddress")
CHAIN_ID = int(os.getenv("CHAIN_ID") or _deployment.get("chainId") or 31337)
NETWORK_NAME = KNOWN_NETWORKS.get(CHAIN_ID, f"Chain {CHAIN_ID}")
EXPLORER_TX_URL = "https://amoy.polygonscan.com/tx/" if CHAIN_ID == 80002 else None

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000,http://127.0.0.1:3001,http://localhost:3001").split(",") if o.strip() and o.strip() != "*"]
DEMO_ACCOUNTS_FILE = os.getenv("DEMO_ACCOUNTS_FILE", os.path.join(BACKEND_DIR, ".demo-accounts.json"))
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
SESSION_TTL_SECONDS = max(60, min(86400, int(os.getenv("SESSION_TTL_SECONDS", "3600"))))
