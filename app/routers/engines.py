from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import datetime
from app.database import get_session
from app.models import (
    EngineSupply, EngineIssue, EngineRehab, EngineCheck, EngineUpload,
    EngineLathe, EnginePump, EngineElectrical
)

router = APIRouter(prefix="/api/engines", tags=["Engines"])

# 🟢 1) التوريد
@router.post("/supply")
def create_supply(data: EngineSupply, session: Session = Depends(get_session)):
    if isinstance(data.date, str):
        try: data.date = datetime.fromisoformat(data.date)
        except: data.date = datetime.utcnow()
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 2) الصرف
@router.post("/issue")
def create_issue(data: EngineIssue, session: Session = Depends(get_session)):
    if isinstance(data.date, str):
        try: data.date = datetime.fromisoformat(data.date)
        except: data.date = datetime.utcnow()
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 3) التأهيل
@router.post("/rehab")
def create_rehab(data: EngineRehab, session: Session = Depends(get_session)):
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 4) الفحص
@router.post("/check")
def create_check(data: EngineCheck, session: Session = Depends(get_session)):
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 5) الرفع
@router.post("/upload")
def create_upload(data: EngineUpload, session: Session = Depends(get_session)):
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 6) المخرطة
@router.post("/lathe")
def create_lathe(data: EngineLathe, session: Session = Depends(get_session)):
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 7) البمبات والنوزلات
@router.post("/pump")
def create_pump(data: EnginePump, session: Session = Depends(get_session)):
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 8) الصريمي
@router.post("/electrical")
def create_electrical(data: EngineElectrical, session: Session = Depends(get_session)):
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 9) آخر 3 محركات (للعرض في الواجهة)
@router.get("/last3")
def last_three(session: Session = Depends(get_session)):
    q = session.exec(select(EngineSupply).order_by(EngineSupply.id.desc()).limit(3)).all()
    return [{"serial": e.serial, "prev_site": e.prev_site} for e in q]
