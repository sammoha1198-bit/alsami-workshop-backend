from datetime import datetime, timedelta
from typing import Optional, List
import os, jwt
from fastapi import APIRouter, HTTPException, Depends, Header
from passlib.context import CryptContext
from sqlmodel import SQLModel, Field, Session, select

from .database import get_session

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_EXPIRE_MINUTES = 24*60
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/auth", tags=["auth"])

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    role: str = Field(default="viewer")  # admin | tech | viewer
    password_hash: str

def hash_pw(p): return pwd.hash(p)
def verify_pw(p, h): return pwd.verify(p, h)

def create_token(uid: int, role: str, name: str):
    payload = {"uid": uid, "role": role, "name": name, "exp": datetime.utcnow()+timedelta(minutes=JWT_EXPIRE_MINUTES)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

@router.post("/register")
def register(email: str, name: str, password: str, role: str = "viewer",
             admin_secret: Optional[str] = None,
             session: Session = Depends(get_session)):
    # للسماح بإنشاء المستخدمين فقط عبر مشرف أو عبر SECRET أولي
    MASTER = os.getenv("ADMIN_CREATE_SECRET", "")
    if not admin_secret or admin_secret != MASTER:
        raise HTTPException(status_code=403, detail="not allowed")
    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(status_code=409, detail="exists")
    u = User(email=email, name=name, role=role, password_hash=hash_pw(password))
    session.add(u); session.commit(); session.refresh(u)
    return {"ok": True, "id": u.id}

@router.post("/login")
def login(email: str, password: str, session: Session = Depends(get_session)):
    u = session.exec(select(User).where(User.email == email)).first()
    if not u or not verify_pw(password, u.password_hash):
        raise HTTPException(status_code=401, detail="bad creds")
    return {"token": create_token(u.id, u.role, u.name), "role": u.role, "name": u.name}

# ===== dependencies =====
def get_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="no token")
    token = authorization.split(" ",1)[1]
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return data  # {"uid","role","name"}
    except Exception:
        raise HTTPException(status_code=401, detail="bad token")

def role_required(roles: List[str]):
    def dep(user=Depends(get_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="forbidden")
        return user
    return dep
