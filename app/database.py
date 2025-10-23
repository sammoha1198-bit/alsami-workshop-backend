import os
from sqlmodel import SQLModel, Session, create_engine

# استخدم DATABASE_URL من البيئة، وإلا SQLite مؤقت على Render
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/ws.db")

# إعدادات خاصة لـ SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# إنشاء المحرك مرة واحدة للتطبيق كله
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def get_session():
    """Dependency للـ FastAPI يعيد Session موحّدة."""
    with Session(engine) as session:
        yield session

def init_db():
    """
    مهم جدًا: استيراد النماذج قبل create_all حتى تُسجَّل داخل metadata.
    يكفي User الآن لإصلاح تسجيل الدخول/التسجيل.
    """
    from .auth import User  # ← هذا يضمن إنشاء جدول المستخدمين
    # إذا أردت إنشاء باقي الجداول أيضًا، اترك الراوترات تستورد models أثناء التشغيل.
    SQLModel.metadata.create_all(engine)
