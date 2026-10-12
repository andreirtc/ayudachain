"""PostgreSQL-only MVP connections. Migration and seeding are explicit tools."""
import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from psycopg import sql
from .config import load_local_environment


@contextmanager
def connection(*, purpose='runtime'):
    load_local_environment()
    name = {'runtime':'MVP_DATABASE_URL','worker':'MVP_WORKER_DATABASE_URL','inspection':'MVP_INSPECTION_DATABASE_URL','owner':'MVP_OWNER_DATABASE_URL'}[purpose]
    dsn = os.environ.get(name)
    if not dsn or not dsn.startswith('postgresql://'):
        raise RuntimeError('Explicit PostgreSQL configuration required')
    with psycopg.connect(dsn, row_factory=dict_row) as db:
        schema = os.environ.get('MVP_SCHEMA','public')
        db.execute(sql.SQL('SET search_path TO {}, public').format(sql.Identifier(schema)))
        db.execute("SET timezone TO 'UTC'")
        db.execute("SET lock_timeout TO '10s'")
        if purpose!='owner':
            role={'runtime':'mvp_runtime','worker':'mvp_worker','inspection':'mvp_inspection'}[purpose]
            db.execute(sql.SQL('SET LOCAL ROLE {}').format(sql.Identifier(role)))
        yield db
