from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..models import EngineSupply

router = APIRouter(prefix="/engines", tags=["engines"])

@router.post("/supply", response_model=EngineSupply)
def create_engine_supply(record: EngineSupply, session: Session = Depends(get_session)):
    """
    إنشاء سجل توريد جديد للمحرك
    """
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("/supply", response_model=List[EngineSupply])
def list_engine_supplies(session: Session = Depends(get_session)):
    """
    عرض جميع سجلات التوريد للمحركات
    """
    result = session.exec(select(EngineSupply)).all()
    return result
from sqlmodel import select

@router.get("/last3")
def last_three_engines(session: Session = Depends(get_session)):
    # آخر 3 من جدول التوريد بحسب التاريخ أو id
    rows = session.exec(select(EngineSupply).order_by(EngineSupply.date.desc(), EngineSupply.id.desc())).all()
    rows = rows[:3]
    return [{"serial": r.serial, "prev_site": r.prev_site} for r in rows]
