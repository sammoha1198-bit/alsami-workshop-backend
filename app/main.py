# app/main.py  — header & app creation MUST come before any @app.get/@app.post

from fastapi import FastAPI, Depends, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Union
from io import BytesIO
from urllib.parse import quote
import datetime

from sqlalchemy import text
from sqlmodel import Session, select

from .database import init_db, get_session, engine
from . import models

# -------------------- create app FIRST --------------------
app = FastAPI(title="Alsami Workshop Backend", version="3.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup: ensure tables exist
@app.on_event("startup")
def on_startup():
    init_db()

# -------------------- schema repair helpers --------------------
def _table_has_column(conn, table: str, col: str) -> bool:
    rows = conn.execute(text(f'PRAGMA table_info("{table}")')).fetchall()
    cols = {r[1] for r in rows}  # column name is index 1
    return col in cols

def _safe_exec(conn, sql: str):
    conn.execute(text(sql))

def repair_schema() -> dict:
    fixed = []
    with engine.begin() as conn:
        # enginesupply.engineType
        if not _table_has_column(conn, "enginesupply", "engineType"):
            _safe_exec(conn, """
                CREATE TABLE IF NOT EXISTS enginesupply_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    serial TEXT NOT NULL,
                    engineType TEXT,
                    model TEXT,
                    prevSite TEXT,
                    supDate TEXT,
                    supplier TEXT,
                    notes TEXT
                );
            """)
            # move old data if table exists
            if conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='enginesupply'")).fetchone():
                _safe_exec(conn, """
                    INSERT INTO enginesupply_new (id, serial, engineType, model, prevSite, supDate, supplier, notes)
                    SELECT id, serial, '' as engineType, model, prevSite, supDate, supplier, notes
                    FROM enginesupply;
                """)
                _safe_exec(conn, "DROP TABLE enginesupply;")
            _safe_exec(conn, "ALTER TABLE enginesupply_new RENAME TO enginesupply;")
            fixed.append("enginesupply.engineType")

        # enginecheck.desc
        if not _table_has_column(conn, "enginecheck", "desc"):
            _safe_exec(conn, 'ALTER TABLE enginecheck ADD COLUMN "desc" TEXT;')
            fixed.append("enginecheck.desc")

    # ensure any missing tables are created
    init_db()
    return {"fixed": fixed}

# -------------------- admin/repair & seed routes --------------------
@app.post("/api/admin/repair")
def admin_repair():
    try:
        info = repair_schema()
        return {"ok": True, **info}
    except Exception as e:
        return Response(
            content=f'{{"ok": false, "error": "{str(e)}"}}',
            media_type="application/json",
            status_code=500,
        )

@app.get("/api/seed")
def seed():
    try:
        with Session(engine) as s:
            if s.exec(select(models.EngineSupply)).first():
                return {"ok": True, "note": "data already exists"}

            # Engines supply
            s.add_all([
                models.EngineSupply(serial="111", engineType="Deutz",  model="F4L912",  prevSite="المخزن الرئيسي", supDate="2025-10-30", supplier="Yemen Mobile", notes="توريد جديد"),
                models.EngineSupply(serial="222", engineType="Perkins",model="404D-22", prevSite="فرع الحديدة",   supDate="2025-10-29", supplier="PowerTech",   notes="محرك جاهز"),
                models.EngineSupply(serial="333", engineType="Kubota", model="V2203",   prevSite="فرع صنعاء",     supDate="2025-10-28", supplier="DieselPro",    notes="تم إعادة تأهيله"),
            ])
            # Other engine tables
            s.add_all([
                models.EngineIssue(serial="111", currSite="محطة تعز", receiver="المهندس سامي", requester="قسم التشغيل", issueDate="2025-11-01", notes="تم صرفه للموقع"),
                models.EngineRehab(serial="333", rehabber="فريق التأهيل", rehabType="إصلاح كامل", rehabDate="2025-11-02", notes="تغيير حلقات ومضخة"),
                models.EngineCheck(serial="222", inspector="فريق الفحص", desc="فحص حرارة وضغط زيت", checkDate="2025-11-03", notes="الفحص ممتاز"),
                models.EngineUpload(serial="111", rehabUp="نعم", checkUp="لا", rehabUpDate="2025-11-04", notes="تم رفع المؤهل فقط"),
                models.EngineLathe(serial="333", lathe="تشغيل عمود + جلنبر", latheDate="2025-11-05", notes="مخرطة خارجية"),
                models.EnginePump(serial="111", pumpSerial="P-111-A", pumpRehab="تنظيف ورش", notes="بمب جاهز"),
                models.EngineElectrical(serial="222", etype="كهرباء كاملة", starter="نعم", alternator="نعم", edate="2025-11-06", notes="تم فحص الدينمو"),
            ])
            # Generators
            s.add_all([
                models.GeneratorSupply(code="GEN001", gType="30kVA", model="FG Wilson", prevSite="المستودع المركزي", supDate="2025-10-30", supplier="Yemen Mobile", vendor="PowerMax",   notes="مولد جديد"),
                models.GeneratorSupply(code="GEN002", gType="20kVA", model="Perkins",   prevSite="فرع إب",          supDate="2025-10-29", supplier="Yemen Mobile", vendor="EnergyTech", notes="مولد مستخدم"),
                models.GeneratorSupply(code="GEN003", gType="15kVA", model="Deutz",     prevSite="فرع تعز",         supDate="2025-10-27", supplier="Yemen Mobile", vendor="DieselPro",  notes="مولد مؤهل"),
            ])
            s.add_all([
                models.GeneratorIssue(code="GEN001", issueDate="2025-11-01", receiver="موقع ذمار", requester="قسم الطاقة", currSite="ذمار", notes="سليم"),
                models.GeneratorInspect(code="GEN002", inspector="فريق الفحص", elecRehab="نعم", rehabDate="2025-11-02", rehabUp="نعم", checkUp="نعم", notes="تم الرفع للنظام"),
            ])
            s.commit()
        return {"ok": True, "seeded": True}
    except Exception as e:
        return Response(
            content=f'{{"ok": false, "error": "{str(e)}"}}',
            media_type="application/json",
            status_code=500,
        )

# -------------- your other routes (health/search/export/last3/...) go BELOW this line --------------
