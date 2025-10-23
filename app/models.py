from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


# ========== قواعد مشتركة ==========
class EngineBase(SQLModel):
    serial: str = Field(index=True, description="الرقم التسلسلي للمحرك")


class GeneratorBase(SQLModel):
    code: str = Field(index=True, description="ترميز المولد")


# ========== جداول المحركات ==========
class EngineSupply(EngineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_name: str = "محرك"
    engine_type: Optional[str] = None
    model: Optional[str] = None
    prev_site: Optional[str] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class EngineIssue(EngineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    current_site: Optional[str] = None
    receiver: Optional[str] = None
    requester: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class EngineRehab(EngineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rehab_by: Optional[str] = None
    rehab_type: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class EngineCheck(EngineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    inspector: Optional[str] = None
    description: Optional[str] = None
    check_notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class EngineUpload(EngineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rehab_file: Optional[str] = None
    check_file: Optional[str] = None
    check_date: Optional[datetime] = None
    rehab_date: Optional[datetime] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class EngineLathe(EngineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lathe_rehab: Optional[str] = None
    notes: Optional[str] = None
    lathe_supply_date: Optional[datetime] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class EnginePump(EngineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pump_serial: Optional[str] = None
    pump_rehab: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class EngineElectrical(EngineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    kind: Optional[str] = None
    has_starter: Optional[bool] = None
    has_dynamo: Optional[bool] = None
    date: datetime = Field(default_factory=datetime.utcnow)


# ========== جداول المولدات ==========
class GenSupply(GeneratorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_name: str = "مولد"
    gen_type: Optional[str] = None
    model: Optional[str] = None
    prev_site: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_entity: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class GenIssue(GeneratorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    issue_date: Optional[datetime] = None
    receiver: Optional[str] = None
    requester: Optional[str] = None
    current_site: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class GenInspect(GeneratorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    inspector: Optional[str] = None
    electrical_rehab_by: Optional[str] = None
    rehab_date: Optional[datetime] = None
    rehab_file: Optional[str] = None
    check_file: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


# ========== قطع الغيار (جديد) ==========
class SparePart(SQLModel, table=True):
    """
    أيقونة "قطع الغيار" — تدعم محرك/مولد.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    item_kind: str = Field(description="نوع الصنف (محرك/مولد)")  # values: "محرك" أو "مولد"
    serial_or_code: str = Field(index=True, description="الرقم التسلسلي للمحرك أو ترميز المولد")
    model: Optional[str] = Field(default=None, description="مودل المحرك/المولد")
    part_name: str = Field(description="اسم القطعة المصروفة")
    qty: int = Field(default=1, description="العدد")
    condition: str = Field(description="حالة القطعة (جديد/مؤهل)")
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
