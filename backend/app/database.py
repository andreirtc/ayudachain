from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from app.models.entities import Base

# Use check_same_thread=False for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    columns = {c["name"] for c in inspect(engine).get_columns("distributions")} if inspect(engine).has_table("distributions") else None
    if columns is not None and "amount_centavos" not in columns:
        raise RuntimeError(
            "The database uses the old peso amount format. Delete backend/ayudachain.db and "
            "restart the chain and backend (see docs/WINDOWS_LOCAL.md, Reset)."
        )
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
