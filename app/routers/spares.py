from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..database import get_session
from ..models import SparePart

router = APIRouter(prefix="/spares", tags=["spares"])

@router.post("", response_model=SparePart)
def create_spare(sp: SparePart, session: Session = Depends(get_session)) -> SparePart:
    """
    إنشاء سجل قطع غيار جديد.
    الحقول المطلوبة:
    - item_kind: "محرك" أو "مولد"
    - serial_or_code: الرقم التسلسلي للمحرك أو ترميز المولد
    - part_name: اسم القطعة
    - qty: العدد
    - condition: "جديد" أو "مؤهل"
    - (اختياري) model, notes
    """
    session.add(sp)
    session.commit()
    session.refresh(sp)
    return sp

@router.get("", response_model=List[SparePart])
def list_spares(
    item_kind: Optional[str] = None,
    serial_or_code: Optional[str] = None,
    date_from: Optional[str] = None,  # ISO format: YYYY-MM-DD أو YYYY-MM-DDTHH:MM:SS
    date_to: Optional[str] = None,
    session: Session = Depends(get_session),
) -> List[SparePart]:
    """
    استعلام عن سجلات قطع الغيار مع فلاتر اختيارية:
    - item_kind: "محرك" أو "مولد"
    - serial_or_code: نفس رقم التسلسلي/الترميز المستخدم في البحث
    - date_from / date_to: مدى زمني
    """
    stmt = select(SparePart)
    if item_kind:
        stmt = stmt.where(SparePart.item_kind == item_kind)
    if serial_or_code:
        stmt = stmt.where(SparePart.serial_or_code == serial_or_code)

    rows = session.exec(stmt).all()

    # تصفية زمنية اختيارية
    d1 = datetime.fromisoformat(date_from) if date_from else None
    d2 = datetime.fromisoformat(date_to) if date_to else None

    def in_range(dt: datetime) -> bool:
        if not isinstance(dt, datetime):
            return False
        if d1 and dt < d1:
            return False
        if d2 and dt > d2:
            return False
        return True

    return [r for r in rows if in_range(r.date)]
