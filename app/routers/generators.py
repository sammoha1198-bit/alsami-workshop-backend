from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import datetime
from app.database import get_session
from app.models import GenSupply, GenIssue, GenInspect

router = APIRouter(prefix="/api/generators", tags=["Generators"])

# 🟢 1) التوريد
@router.post("/supply")
def create_supply(data: GenSupply, session: Session = Depends(get_session)):
    if isinstance(data.date, str):
        try: data.date = datetime.fromisoformat(data.date)
        except: data.date = datetime.utcnow()
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 2) الصرف
@router.post("/issue")
def create_issue(data: GenIssue, session: Session = Depends(get_session)):
    if isinstance(data.issue_date, str):
        try: data.issue_date = datetime.fromisoformat(data.issue_date)
        except: data.issue_date = datetime.utcnow()
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 3) الفحص والرفع
@router.post("/inspect")
def create_inspect(data: GenInspect, session: Session = Depends(get_session)):
    session.add(data); session.commit(); session.refresh(data)
    return data

# 🟢 4) آخر 3 مولدات
@router.get("/last3")
def last_three(session: Session = Depends(get_session)):
    q = session.exec(select(GenSupply).order_by(GenSupply.id.desc()).limit(3)).all()
    return [{"code": g.code, "prev_site": g.prev_site} for g in q]
