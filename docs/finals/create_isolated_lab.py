"""Create new local synthetic lab databases/config. Never reset/drop/reuse data.

Run with the repository's locked interpreter. Prints only non-secret paths/names.
Existing local PostgreSQL and supported Node must already be available.
"""
import os
import secrets
import shutil
import sys
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse, urlunparse

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend.app.config import load_local_environment, validate_environment


def create(rpc_url=None):
    load_local_environment()
    node = os.environ.get('MVP_NODE') or shutil.which('node')
    if not node:
        raise ValueError('Put supported Node 22/24 on PATH first')
    admin = os.environ.get('MVP_ADMIN_DATABASE_URL', 'postgresql://postgres@127.0.0.1:55432/postgres')
    parsed = urlparse(admin)
    if parsed.scheme != 'postgresql' or parsed.hostname not in {'localhost', '127.0.0.1', '::1'}:
        raise ValueError('Explicit local PostgreSQL administrator URL required')
    label = uuid4().hex[:12]
    database = 'ayudachain_mvp_finals_' + label
    test_database = 'ayudachain_mvp_test_finals_' + label
    directory = ROOT / '.runtime/finals/labs' / label
    directory.mkdir(parents=True, exist_ok=False)
    dsn = urlunparse(parsed._replace(path='/' + database))
    test_dsn = urlunparse(parsed._replace(path='/' + test_database))
    rpc_url = rpc_url or os.environ.get('MVP_RPC_URL', 'http://127.0.0.1:8545')
    validate_environment(dict(os.environ, MVP_NODE=node, MVP_DATABASE_URL=dsn, MVP_RPC_URL=rpc_url))
    # Names are new and quoted. Any collision fails rather than modifying a DB.
    with psycopg.connect(admin, autocommit=True) as db:
        for name in (database, test_database):
            db.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
    values = {key: dsn for key in ('MVP_DATABASE_URL', 'MVP_OWNER_DATABASE_URL', 'MVP_WORKER_DATABASE_URL', 'MVP_INSPECTION_DATABASE_URL')}
    values.update(MVP_TEST_DATABASE_URL=test_dsn, MVP_RPC_URL=rpc_url, MVP_NODE=node,
                  MVP_DEPLOYMENT_MANIFEST=str(directory / 'deployment.json'),
                  MVP_TEST_DEPLOYMENT_MANIFEST=str(directory / 'fault-deployment.json'),
                  MVP_EVIDENCE_ROOT=str(directory / 'originals'), MVP_COMMAND_DIGEST_KEY=secrets.token_hex(32))
    if os.environ.get('MVP_PG_BIN'):
        values['MVP_PG_BIN'] = os.environ['MVP_PG_BIN']
    config = directory / 'lab.env'
    descriptor = os.open(config, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as file:
        file.write(''.join(f'{key}={value}\n' for key, value in values.items()))
    print('Created new isolated databases:', database, test_database)
    print('Configuration:', config)
    print('Select it using MVP_CONFIG_FILE. No migration, deployment, reset or seed was performed.')
    return config


if __name__ == '__main__':
    try:
        create()
    except Exception as error:
        print('Lab creation failed; retain any newly created lab/database for inspection. No cleanup/drop attempted.', file=sys.stderr)
        print(type(error).__name__, file=sys.stderr)
        sys.exit(1)
