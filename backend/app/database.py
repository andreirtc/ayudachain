from sqlalchemy import create_engine, inspect
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
            "The database was created by an older version of AyudaChain. Delete backend/ayudachain.db and "
            "restart the chain and backend (see docs/WINDOWS_LOCAL.md, Reset)."
        )
    Base.metadata.create_all(bind=engine)

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
