from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..models import GenSupply, GenIssue, GenInspect

router = APIRouter(prefix="/generators", tags=["generators"])

# ====== التوريد ======
@router.post("/supply", response_model=GenSupply)
def create_gen_supply(rec: GenSupply, session: Session = Depends(get_session)) -> GenSupply:
    session.add(rec); session.commit(); session.refresh(rec); return rec

@router.get("/supply", response_model=List[GenSupply])
def list_gen_supply(session: Session = Depends(get_session)) -> List[GenSupply]:
    return session.exec(select(GenSupply)).all()

# ====== الصرف ======
@router.post("/issue", response_model=GenIssue)
def create_gen_issue(rec: GenIssue, session: Session = Depends(get_session)) -> GenIssue:
    session.add(rec); session.commit(); session.refresh(rec); return rec

@router.get("/issue", response_model=List[GenIssue])
def list_gen_issue(session: Session = Depends(get_session)) -> List[GenIssue]:
    return session.exec(select(GenIssue)).all()

# ====== الرفع والفحص ======
@router.post("/inspect", response_model=GenInspect)
def create_gen_inspect(rec: GenInspect, session: Session = Depends(get_session)) -> GenInspect:
    # ملاحظة: هنا نتعامل JSON فقط (بدون ملفات) ليتطابق مع الواجهة الحالية
    # إذا كان rehab_date نص تاريخ فقط (YYYY-MM-DD) نحوله لـ datetime
    if isinstance(rec.rehab_date, str):
        try:
            rec.rehab_date = datetime.fromisoformat(rec.rehab_date)
        except Exception:
            rec.rehab_date = None
    session.add(rec); session.commit(); session.refresh(rec); return rec

@router.get("/inspect", response_model=List[GenInspect])
def list_gen_inspect(session: Session = Depends(get_session)) -> List[GenInspect]:
    return session.exec(select(GenInspect)).all()
from sqlmodel import select

@router.get("/last3")
def last_three_generators(session: Session = Depends(get_session)):
    rows = session.exec(select(GenSupply).order_by(GenSupply.date.desc(), GenSupply.id.desc())).all()
    rows = rows[:3]
    return [{"code": r.code, "prev_site": r.prev_site} for r in rows]
