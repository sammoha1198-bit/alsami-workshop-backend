from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# ======================= 🛠️ المحركات =======================
class EngineSupply(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    engine_type: Optional[str] = None
    model: Optional[str] = None
    prev_site: Optional[str] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class EngineIssue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    current_site: Optional[str] = None
    receiver: Optional[str] = None
    requester: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


class EngineRehab(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    rehab_by: Optional[str] = None
    rehab_type: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None


class EngineCheck(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    inspector: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None


class EngineUpload(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    rehab_file: Optional[str] = None  # نعم / لا
    check_file: Optional[str] = None  # نعم / لا
    rehab_date: Optional[datetime] = None
    check_date: Optional[datetime] = None
    notes: Optional[str] = None


class EngineLathe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    lathe_rehab: Optional[str] = None
    lathe_supply_date: Optional[datetime] = None
    notes: Optional[str] = None


class EnginePump(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    pump_serial: Optional[str] = None
    pump_rehab: Optional[str] = None
    notes: Optional[str] = None


class EngineElectrical(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    kind: Optional[str] = None
    has_starter: Optional[bool] = False
    has_dynamo: Optional[bool] = False
    date: Optional[datetime] = None


# ======================= ⚡ المولدات =======================
class GenSupply(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    gen_type: Optional[str] = None
    model: Optional[str] = None
    prev_site: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_entity: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class GenIssue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    receiver: Optional[str] = None
    requester: Optional[str] = None
    current_site: Optional[str] = None
    notes: Optional[str] = None


class GenInspect(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    inspector: Optional[str] = None
    electrical_rehab_by: Optional[str] = None
    rehab_date: Optional[datetime] = None
    notes: Optional[str] = None


# ======================= 🧩 قطع الغيار =======================
class SparePart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_kind: str  # محرك أو مولد
    serial_or_code: Optional[str] = None
    model: Optional[str] = None
    part_name: Optional[str] = None
    qty: Optional[int] = 1
    condition: Optional[str] = None
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
