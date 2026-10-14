from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from app.models.entities import Base

# Use check_same_thread=False for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    if _schema_is_outdated():
        raise RuntimeError(
            "The database was created by an older version of AyudaChain. Preserve it and use a compatible "
            "isolated copy or a new synthetic database/chain (see docs/WINDOWS_LOCAL.md)."
        )
    Base.metadata.create_all(bind=engine)
    _migrate_payout_idempotency()
    _migrate_beneficiary_history()
    _protect_receipt_snapshots()
    _protect_validated_lists()

def _migrate_payout_idempotency():
    """Add retry metadata to the preceding SQLite schema without deleting payouts."""
    if engine.dialect.name != "sqlite":
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("distributions")}
        indexes = inspector.get_indexes("distributions") + inspector.get_unique_constraints("distributions")
        if {"idempotency_key", "request_fingerprint"} <= columns and any(
            i["column_names"] == ["idempotency_key"] and i.get("unique", True) for i in indexes
        ):
            return
        raise RuntimeError("Migrate distributions.idempotency_key (unique) and request_fingerprint before startup.")
    with engine.begin() as connection:
        # Serialize startup migrations; re-inspect under the SQLite write lock.
        connection.exec_driver_sql("BEGIN IMMEDIATE")
        columns = {c["name"] for c in inspect(connection).get_columns("distributions")}
        for name, size in (("idempotency_key", 128), ("request_fingerprint", 66)):
            if name not in columns:
                connection.execute(text(f"ALTER TABLE distributions ADD COLUMN {name} VARCHAR({size})"))
        connection.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_distributions_idempotency_key "
            "ON distributions (idempotency_key)"
        ))

def _migrate_beneficiary_history():
    """Retain registry rows while adding duplicate links and decision targets."""
    additions = {
        "beneficiaries": {
            "record_status": "VARCHAR(32) NOT NULL DEFAULT 'ACTIVE'",
            "canonical_beneficiary_id": "VARCHAR(64)",
        },
        "beneficiary_reviews": {"linked_beneficiary_id": "VARCHAR(64)"},
    }
    if engine.dialect.name != "sqlite":
        inspector = inspect(engine)
        for table, required in additions.items():
            columns = {c["name"] for c in inspector.get_columns(table)}
            if not required.keys() <= columns:
                raise RuntimeError("Migrate retained beneficiary status/link fields before startup.")
        return
    with engine.begin() as connection:
        connection.exec_driver_sql("BEGIN IMMEDIATE")
        for table, fields in additions.items():
            columns = {c["name"] for c in inspect(connection).get_columns(table)}
            for name, definition in fields.items():
                if name not in columns:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}"))
        for column in ("record_status", "canonical_beneficiary_id"):
            connection.execute(text(
                f"CREATE INDEX IF NOT EXISTS ix_beneficiaries_{column} ON beneficiaries ({column})"
            ))

REQUIRED_COLUMNS = {
    "distributions": {"amount_centavos", "allocation_id"},
    "relief_batches": {"amount_centavos", "standard_grant_centavos", "max_grant_centavos"},
}

REQUIRED_UNIQUE_CONSTRAINTS = {
    "distributions": "uq_distribution_batch_beneficiary",
}

def _schema_is_outdated():
    inspector = inspect(engine)
    for table, required in REQUIRED_COLUMNS.items():
        if inspector.has_table(table):
            columns = {c["name"] for c in inspector.get_columns(table)}
            if not required <= columns:
                return True
    for table, name in REQUIRED_UNIQUE_CONSTRAINTS.items():
        if inspector.has_table(table):
            names = {c["name"] for c in inspector.get_unique_constraints(table)}
            if name not in names:
                return True
    return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _protect_receipt_snapshots():
    """No ordinary update/delete of captured originals on the supported SQLite DB."""
    if engine.dialect.name == "sqlite":
        with engine.begin() as connection:
            for operation in ("UPDATE", "DELETE"):
                connection.exec_driver_sql(f"CREATE TRIGGER IF NOT EXISTS receipt_snapshot_no_{operation.lower()} BEFORE {operation} ON receipt_snapshots BEGIN SELECT RAISE(ABORT, 'Receipt snapshots are immutable'); END")


def _protect_validated_lists():
    if engine.dialect.name == "sqlite":
        with engine.begin() as connection:
            for table in ("validated_lists", "list_finalizations", "payout_arrangements", "arrangement_revisions", "household_concerns", "concern_revisions", "damage_claims", "claim_revisions", "amount_rule_versions", "payout_sessions", "session_revisions"):
                for operation in ("UPDATE", "DELETE"):
                    connection.exec_driver_sql(f"CREATE TRIGGER IF NOT EXISTS {table}_no_{operation.lower()} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT, 'Validated list history is immutable'); END")
