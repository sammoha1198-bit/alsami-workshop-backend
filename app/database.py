from sqlmodel import SQLModel, create_engine, Session
from .auth import User  # مهم: حتى تُسجَّل طاولة User داخل metadata

import os

DB_URL = os.getenv("DATABASE_URL", "sqlite:///workshop.db")
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, echo=False, connect_args=connect_args)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
