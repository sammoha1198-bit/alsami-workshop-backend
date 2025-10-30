from sqlmodel import SQLModel, Field
from typing import Optional


# =====================================================
# 🛠️ المحركات (Engines)
# =====================================================

class EngineSupply(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    engineType: Optional[str] = None
    model: Optional[str] = None
    prevSite: Optional[str] = None
    supDate: Optional[str] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None


class EngineIssue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    currSite: Optional[str] = None
    receiver: Optional[str] = None
    requester: Optional[str] = None
    issueDate: Optional[str] = None
    notes: Optional[str] = None


class EngineRehab(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    rehabber: Optional[str] = None
    rehabType: Optional[str] = None
    rehabDate: Optional[str] = None
    notes: Optional[str] = None


class EngineCheck(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    inspector: Optional[str] = None
    desc: Optional[str] = None
    checkDate: Optional[str] = None
    notes: Optional[str] = None


class EngineUpload(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    rehabUp: Optional[str] = None
    checkUp: Optional[str] = None
    rehabUpDate: Optional[str] = None
    checkUpDate: Optional[str] = None
    notes: Optional[str] = None


class EngineLathe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    lathe: Optional[str] = None
    latheDate: Optional[str] = None
    notes: Optional[str] = None


class EnginePump(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    pumpSerial: Optional[str] = None
    pumpRehab: Optional[str] = None
    notes: Optional[str] = None


class EngineElectrical(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str
    etype: Optional[str] = None
    starter: Optional[str] = None
    alternator: Optional[str] = None
    edate: Optional[str] = None
    notes: Optional[str] = None


# =====================================================
# ⚡ المولدات (Generators)
# =====================================================

class GeneratorSupply(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    gType: Optional[str] = None
    model: Optional[str] = None
    prevSite: Optional[str] = None
    supDate: Optional[str] = None
    supplier: Optional[str] = None
    vendor: Optional[str] = None
    notes: Optional[str] = None


class GeneratorIssue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    issueDate: Optional[str] = None
    receiver: Optional[str] = None
    requester: Optional[str] = None
    currSite: Optional[str] = None
    notes: Optional[str] = None


class GeneratorInspect(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    inspector: Optional[str] = None
    elecRehab: Optional[str] = None
    rehabDate: Optional[str] = None
    rehabUp: Optional[str] = None
    checkUp: Optional[str] = None
    notes: Optional[str] = None
