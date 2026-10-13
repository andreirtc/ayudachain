"""Explicit local database setup/migrations; never invoked during API startup."""
import os
import secrets
from pathlib import Path
import psycopg
from psycopg import sql
from backend.app.config import ROOT,load_local_environment
from backend.app.database import connection
from backend.migrations.catalogue import migrate


def provision():
    load_local_environment()
    admin=os.environ.get('MVP_ADMIN_DATABASE_URL','postgresql://postgres@127.0.0.1:55432/postgres')
    with psycopg.connect(admin,autocommit=True) as db:
        for name in ['mvp_runtime','mvp_worker','mvp_inspection']:
            if not db.execute('SELECT 1 FROM pg_roles WHERE rolname=%s',(name,)).fetchone():
                db.execute(sql.SQL('CREATE ROLE {} NOLOGIN').format(sql.Identifier(name)))
        for name in ['ayudachain_mvp','ayudachain_mvp_test']:
            if not db.execute('SELECT 1 FROM pg_database WHERE datname=%s',(name,)).fetchone():
                db.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
    path=ROOT/'.env.mvp'
    if not path.exists():
        path.write_text('\n'.join([
            'MVP_DATABASE_URL=postgresql://postgres@127.0.0.1:55432/ayudachain_mvp',
            'MVP_OWNER_DATABASE_URL=postgresql://postgres@127.0.0.1:55432/ayudachain_mvp',
            'MVP_WORKER_DATABASE_URL=postgresql://postgres@127.0.0.1:55432/ayudachain_mvp',
            'MVP_INSPECTION_DATABASE_URL=postgresql://postgres@127.0.0.1:55432/ayudachain_mvp',
            'MVP_TEST_DATABASE_URL=postgresql://postgres@127.0.0.1:55432/ayudachain_mvp_test',
            'MVP_RPC_URL=http://127.0.0.1:8545',
            'MVP_NODE='+str(ROOT/'.runtime/tools/node-v22.23.3-win-x64/node.exe'),
            'MVP_COMMAND_DIGEST_KEY='+secrets.token_hex(32),
        ])+'\n',encoding='utf-8')
    load_local_environment()
    with connection(purpose='owner') as db:
        changed=migrate(db)
        grant_roles(db,os.environ.get('MVP_SCHEMA','public'))
    print('Local schema migrated' if changed else 'Existing local schema preserved')


def grant_roles(db,schema):
    from backend.app.models.mvp import metadata,IMMUTABLE
    db.execute(sql.SQL('GRANT USAGE ON SCHEMA {} TO mvp_runtime,mvp_worker,mvp_inspection').format(sql.Identifier(schema)))
    db.execute(sql.SQL('GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA {} TO mvp_runtime').format(sql.Identifier(schema)))
    db.execute(sql.SQL('GRANT SELECT ON {}.mvp_migrations TO mvp_runtime').format(sql.Identifier(schema)))
    for name in metadata.tables:
        target=sql.SQL('{}.{}').format(sql.Identifier(schema),sql.Identifier(name))
        if name.startswith('auditor_access'):
            db.execute(sql.SQL('GRANT SELECT,INSERT ON {} TO mvp_inspection').format(target))
        else:
            operations='SELECT,INSERT' if name in IMMUTABLE else 'SELECT,INSERT,UPDATE'
            db.execute(sql.SQL('GRANT '+operations+' ON {} TO mvp_runtime').format(target))
        if name in {'deployments','commitments','anchor_job_items','anchor_dependencies','evaluation_runs','actors','actor_versions'}:
            db.execute(sql.SQL('GRANT SELECT ON {} TO mvp_worker').format(target))
        if name in {'anchor_submissions','anchor_submission_events','anchor_observations'}:
            db.execute(sql.SQL('GRANT SELECT,INSERT ON {} TO mvp_worker').format(target))
        if name=='anchor_jobs': db.execute(sql.SQL('GRANT SELECT,UPDATE ON {} TO mvp_worker').format(target))


if __name__=='__main__': provision()
