# app/models.py
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text

# ============ محركات ============
class EngineSupply(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    serial: str = Field(index=True)
    engineType: Optional[str] = None
    model: Optional[str] = None
    prevSite: Optional[str] = None
    supDate: Optional[str] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None


class EngineIssue(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    serial: str = Field(index=True)
    currSite: Optional[str] = None
    receiver: Optional[str] = None
    requester: Optional[str] = None
    issueDate: Optional[str] = None
    notes: Optional[str] = None


class EngineRehab(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    serial: str = Field(index=True)
    rehabber: Optional[str] = None
    rehabType: Optional[str] = None
    rehabDate: Optional[str] = None
    notes: Optional[str] = None



class EngineCheck(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial: str = Field(index=True)
    inspector: Optional[str] = None
    # 🔧 نخزن الخاصية باسم 'description' في بايثون، لكن في قاعدة البيانات عمودها اسمه "desc"
    description: Optional[str] = Field(
        default=None,
        sa_column=Column("desc", Text, nullable=True)
    )
    checkDate: Optional[str] = None
    notes: Optional[str] = None



class EngineUpload(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    serial: str = Field(index=True)
    rehabUp: Optional[str] = None
    checkUp: Optional[str] = None
    rehabUpDate: Optional[str] = None
    checkUpDate: Optional[str] = None
    notes: Optional[str] = None


class EngineLathe(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    serial: str = Field(index=True)
    lathe: Optional[str] = None
    latheDate: Optional[str] = None
    notes: Optional[str] = None


class EnginePump(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    serial: str = Field(index=True)
    pumpSerial: Optional[str] = None
    pumpRehab: Optional[str] = None
    notes: Optional[str] = None


class EngineElectrical(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    serial: str = Field(index=True)
    etype: Optional[str] = None
    starter: Optional[str] = None
    alternator: Optional[str] = None
    edate: Optional[str] = None
    notes: Optional[str] = None


# ============ مولدات ============
class GeneratorSupply(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    gType: Optional[str] = None
    model: Optional[str] = None
    prevSite: Optional[str] = None
    supDate: Optional[str] = None
    supplier: Optional[str] = None
    vendor: Optional[str] = None
    notes: Optional[str] = None


class GeneratorIssue(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    issueDate: Optional[str] = None
    receiver: Optional[str] = None
    requester: Optional[str] = None
    currSite: Optional[str] = None
    notes: Optional[str] = None


class GeneratorInspect(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    inspector: Optional[str] = None
    elecRehab: Optional[str] = None
    rehabDate: Optional[str] = None
    rehabUp: Optional[str] = None
    checkUp: Optional[str] = None
    notes: Optional[str] = None
