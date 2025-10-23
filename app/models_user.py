# C:\Workshop-System\backend\app\database.py
import os
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/ws.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    # استيراد كل الموديلات هنا فقط لتفادي الاستيراد الدائري
    from .models_user import User  # مهم: كي تُسجَّل طاولة users
    # إن أردت إنشاء بقية الجداول لاحقًا، ضع استيراداتها هنا أيضًا.
    SQLModel.metadata.create_all(engine)
