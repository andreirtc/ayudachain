"""Explicit local MVP configuration; loading it never mutates business state."""
import os
import re
import subprocess
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
LOCAL_HOSTS = {'127.0.0.1', 'localhost', '::1'}


def validate_environment(env=None, *, node_version=None):
    env = os.environ if env is None else env
    rpc = env.get('MVP_RPC_URL', 'http://127.0.0.1:8545')
    parsed = urlparse(rpc)
    if parsed.scheme != 'http' or parsed.hostname not in LOCAL_HOSTS or parsed.username or parsed.password:
        raise ValueError('MVP RPC must be a credential-free loopback HTTP URL; public networks are excluded')
    dsn = env.get('MVP_DATABASE_URL', '')
    db = urlparse(dsn)
    if db.scheme not in {'postgresql', 'postgresql+psycopg'} or db.hostname not in LOCAL_HOSTS:
        raise ValueError('MVP requires an explicit local PostgreSQL database; no SQLite fallback')
    if node_version is None:
        try:
            node_version = subprocess.check_output([env.get('MVP_NODE', 'node'), '--version'], text=True, timeout=5).strip()
        except (OSError, subprocess.SubprocessError):
            raise ValueError('Supported Node tooling is unavailable') from None
    match = re.fullmatch(r'v(\d+)\.\d+\.\d+', node_version)
    if not match or int(match[1]) not in {22, 24}:
        raise ValueError('Node 22 or 24 is required by the local Hardhat 2 tooling')
    return {'rpc_url': rpc, 'database_url': dsn.replace('postgresql+psycopg://', 'postgresql://'), 'node_version': node_version}


def load_local_environment(path=None):
    """Read ignored, operator-owned KEY=value configuration without printing values."""
    path = Path(os.environ.get('MVP_CONFIG_FILE',str(ROOT / '.env.mvp'))) if path is None else Path(path)
    if path.exists():
        if path.suffix=='.json':
            allowed={'MVP_DATABASE_URL','MVP_OWNER_DATABASE_URL','MVP_INSPECTION_DATABASE_URL','MVP_WORKER_DATABASE_URL','MVP_SCHEMA','MVP_EVIDENCE_ROOT','MVP_RPC_URL','MVP_NODE','MVP_COMMAND_DIGEST_KEY'}
            values=json.loads(path.read_text(encoding='utf-8'))
            if set(values)-allowed:raise ValueError('Unknown recovery configuration field')
            for key,value in values.items():os.environ.setdefault(key,str(value))
            return
        for line in path.read_text(encoding='utf-8').splitlines():
            if line and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())


def settings():
    load_local_environment()
    return validate_environment()
