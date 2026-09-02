import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.entities import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ayudachain.db")

# Use check_same_thread=False for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
