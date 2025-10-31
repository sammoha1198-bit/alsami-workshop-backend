# app/main.py
from __future__ import annotations

import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

from fastapi import Body, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from sqlmodel import Session, select, SQLModel
from sqlalchemy import Column, Text  # noqa: F401  (مطلوب لتصريح sa_column في models)
from sqlalchemy import text as sqla_text

from .database import init_db, get_session, engine
from . import models

# محاولـة استيراد سكريبت البذور (اختياري)
try:
    from .seed_demo_data import main as seed_main  # type: ignore
except Exception:  # pragma: no cover
    seed_main = None

# =====================================================================
# تهيئة التطبيق و CORS
# =====================================================================

app = FastAPI(title="Alsami Workshop Backend", version="3.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # افتحها حالياً
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# أدوات مساعدة عامة
# =====================================================================

def obj2dict(o: Any) -> Dict[str, Any]:
    """يدعم SQLModel .model_dump() أو .dict()."""
    if hasattr(o, "model_dump"):
        return o.model_dump()  # type: ignore[attr-defined]
    if hasattr(o, "dict"):
        return o.dict()        # type: ignore[attr-defined]
    return dict(o)


# ----------------- إصلاح المخطط (SQLite) -----------------

def _table_columns(table_name: str) -> set[str]:
    with engine.connect() as conn:
        rows = conn.exec_driver_sql(f"PRAGMA table_info({table_name});").fetchall()
        # ترتيب قيم PRAGMA: (cid, name, type, notnull, dflt_value, pk)
        return {r[1] for r in rows}

def add_column_if_missing(table: str, column: str, coltype: str):
    with engine.connect() as conn:
        cols = _table_columns(table)
        if column not in cols:
            conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {coltype};")

def repair_sqlite():
    """
    يصلّح أعمدة ناقصة في الجداول المعروفة.
    حالياً: يضمن وجود enginecheck.desc TEXT.
    """
    init_db()  # تأكد أن الجداول الأساسية منشأة
    # أهم حالة ظهرت:
    add_column_if_missing("enginecheck", "desc", "TEXT")

# =====================================================================
# تشغيل وقت الإقلاع
# =====================================================================

@app.on_event("startup")
def on_startup():
    init_db()
    repair_sqlite()

# =====================================================================
# المسارات الأساسية
# =====================================================================

@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "time": datetime.datetime.utcnow().isoformat()}

# ----------------- البحث -----------------

@app.get("/api/search/{key}")
def search_item(key: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "engines": {
            "supply": [], "issue": [], "rehab": [], "check": [],
            "upload": [], "lathe": [], "pump": [], "electrical": [],
        },
        "generators": {
            "supply": [], "issue": [], "inspect": [],
        },
    }

    # محركات
    result["engines"]["supply"] = [obj2dict(r) for r in session.exec(
        select(models.EngineSupply).where(models.EngineSupply.serial == key)
    ).all()]

    result["engines"]["issue"] = [obj2dict(r) for r in session.exec(
        select(models.EngineIssue).where(models.EngineIssue.serial == key)
    ).all()]

    result["engines"]["rehab"] = [obj2dict(r) for r in session.exec(
        select(models.EngineRehab).where(models.EngineRehab.serial == key)
    ).all()]

    result["engines"]["check"] = [obj2dict(r) for r in session.exec(
        select(models.EngineCheck).where(models.EngineCheck.serial == key)
    ).all()]

    result["engines"]["upload"] = [obj2dict(r) for r in session.exec(
        select(models.EngineUpload).where(models.EngineUpload.serial == key)
    ).all()]

    result["engines"]["lathe"] = [obj2dict(r) for r in session.exec(
        select(models.EngineLathe).where(models.EngineLathe.serial == key)
    ).all()]

    result["engines"]["pump"] = [obj2dict(r) for r in session.exec(
        select(models.EnginePump).where(models.EnginePump.serial == key)
    ).all()]

    result["engines"]["electrical"] = [obj2dict(r) for r in session.exec(
        select(models.EngineElectrical).where(models.EngineElectrical.serial == key)
    ).all()]

    # مولدات (المفتاح هو code)
    result["generators"]["supply"] = [obj2dict(r) for r in session.exec(
        select(models.GeneratorSupply).where(models.GeneratorSupply.code == key)
    ).all()]

    result["generators"]["issue"] = [obj2dict(r) for r in session.exec(
        select(models.GeneratorIssue).where(models.GeneratorIssue.code == key)
    ).all()]

    result["generators"]["inspect"] = [obj2dict(r) for r in session.exec(
        select(models.GeneratorInspect).where(models.GeneratorInspect.code == key)
    ).all()]

    return result


# ----------------- مزامنة دفعات IndexedDB -----------------

@app.post("/api/sync/batch")
async def sync_batch(
    payload: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = payload.get("items", []) or []
    saved = 0

    for item in items:
        store = item.get("store")
        data: Dict[str, Any] = item.get("payload", {}) or {}

        def add(obj):
            nonlocal saved
            session.add(obj)
            saved += 1

        if store == "eng_supply":
            add(models.EngineSupply(
                serial=data.get("serial", ""),
                engineType=data.get("engineType"),
                model=data.get("model"),
                prevSite=data.get("prevSite"),
                supDate=data.get("supDate"),
                supplier=data.get("supplier"),
                notes=data.get("notes"),
            ))

        elif store == "eng_issue":
            add(models.EngineIssue(
                serial=data.get("serial", ""),
                currSite=data.get("currSite"),
                receiver=data.get("receiver"),
                requester=data.get("requester"),
                issueDate=data.get("issueDate"),
                notes=data.get("notes"),
            ))

        elif store == "eng_rehab":
            add(models.EngineRehab(
                serial=data.get("serial", ""),
                rehabber=data.get("rehabber"),
                rehabType=data.get("rehabType"),
                rehabDate=data.get("rehabDate"),
                notes=data.get("notes"),
            ))

        elif store == "eng_check":
            # لاحظ: العمود في DB اسمه "desc" لكن الموديل يعرّف الحقل كـ description
            add(models.EngineCheck(
                serial=data.get("serial", ""),
                inspector=data.get("inspector"),
                description=data.get("description") or data.get("desc"),
                checkDate=data.get("checkDate"),
                notes=data.get("notes"),
            ))

        elif store == "eng_upload":
            add(models.EngineUpload(
                serial=data.get("serial", ""),
                rehabUp=data.get("rehabUp"),
                checkUp=data.get("checkUp"),
                rehabUpDate=data.get("rehabUpDate"),
                checkUpDate=data.get("checkUpDate"),
                notes=data.get("notes"),
            ))

        elif store == "eng_lathe":
            add(models.EngineLathe(
                serial=data.get("serial", ""),
                lathe=data.get("lathe"),
                latheDate=data.get("latheDate"),
                notes=data.get("notes"),
            ))

        elif store == "eng_pump":
            add(models.EnginePump(
                serial=data.get("serial", ""),
                pumpSerial=data.get("pumpSerial"),
                pumpRehab=data.get("pumpRehab"),
                notes=data.get("notes"),
            ))

        elif store == "eng_electrical":
            add(models.EngineElectrical(
                serial=data.get("serial", ""),
                etype=data.get("etype"),
                starter=data.get("starter"),
                alternator=data.get("alternator"),
                edate=data.get("edate"),
                notes=data.get("notes"),
            ))

        # -------- مولدات --------
        elif store == "gen_supply":
            add(models.GeneratorSupply(
                code=data.get("code", ""),
                gType=data.get("gType"),
                model=data.get("model"),
                prevSite=data.get("prevSite"),
                supDate=data.get("supDate"),
                supplier=data.get("supplier"),
                vendor=data.get("vendor"),
                notes=data.get("notes"),
            ))

        elif store == "gen_issue":
            add(models.GeneratorIssue(
                code=data.get("code", ""),
                issueDate=data.get("issueDate"),
                receiver=data.get("receiver"),
                requester=data.get("requester"),
                currSite=data.get("currSite"),
                notes=data.get("notes"),
            ))

        elif store == "gen_inspect":
            add(models.GeneratorInspect(
                code=data.get("code", ""),
                inspector=data.get("inspector"),
                elecRehab=data.get("elecRehab"),
                rehabDate=data.get("rehabDate"),
                rehabUp=data.get("rehabUp"),
                checkUp=data.get("checkUp"),
                notes=data.get("notes"),
            ))

    session.commit()
    return {"ok": True, "saved": saved}


# ----------------- آخر 3 عناصر -----------------

@app.get("/api/last3/engines")
def last3_engines(session: Session = Depends(get_session)) -> Dict[str, Any]:
    rows = session.exec(
        select(models.EngineSupply).order_by(models.EngineSupply.id.desc()).limit(3)
    ).all()
    return {"items": [{"serial": r.serial, "prevSite": r.prevSite or ""} for r in rows]}

@app.get("/api/last3/generators")
def last3_generators(session: Session = Depends(get_session)) -> Dict[str, Any]:
    rows = session.exec(
        select(models.GeneratorSupply).order_by(models.GeneratorSupply.id.desc()).limit(3)
    ).all()
    return {"items": [{"code": r.code, "prevSite": r.prevSite or ""} for r in rows]}


# ----------------- تصدير Excel -----------------

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

@app.post("/api/export/xlsx")
async def export_xlsx(payload: Dict[str, Any] = Body(...)):
    original_filename: str = payload.get("filename") or "تقرير.xlsx"
    safe_ascii_name = "report.xlsx"  # اسم ASCII احتياطي للرؤوس
    sheet_name: str = payload.get("sheet") or "تقرير"
    headers: List[str] = payload.get("headers") or []
    raw_rows: List[Union[Dict[str, Any], List[Any]]] = payload.get("rows") or []

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.sheet_view.rightToLeft = True

    header_fill = PatternFill("solid", fgColor="10b981")
    alt_fill    = PatternFill("solid", fgColor="ecfdf3")
    white_fill  = PatternFill("solid", fgColor="FFFFFF")
    header_font = Font(bold=True, color="FFFFFF", name="Arial")
    normal_font = Font(name="Arial")
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin", color="DDDDDD"),
        right=Side(style="thin", color="DDDDDD"),
        top=Side(style="thin", color="DDDDDD"),
        bottom=Side(style="thin", color="DDDDDD"),
    )

    if headers:
        ws.append(headers)
        for col_idx, _ in enumerate(headers, start=1):
            c = ws.cell(row=1, column=col_idx)
            c.fill = header_fill
            c.font = header_font
            c.alignment = align_right
            c.border = thin_border
            ws.column_dimensions[c.column_letter].width = 28

    current_row = 2
    for row in raw_rows:
        if isinstance(row, dict):
            ordered = [row.get(h, "") for h in headers] if headers else list(row.values())
        elif isinstance(row, (list, tuple)):
            ordered = list(row)
        else:
            ordered = [str(row)]

        ws.append(ordered)
        for col_idx in range(1, len(ordered) + 1):
            c = ws.cell(row=current_row, column=col_idx)
            c.font = normal_font
            c.alignment = align_right
            c.border = thin_border
            c.fill = alt_fill if current_row % 2 else white_fill
        current_row += 1

    ws.append([])
    sig_cell = ws.cell(row=current_row + 1, column=1)
    sig_cell.value = f"تم توليد التقرير في: {datetime.datetime.utcnow().isoformat()}"
    sig_cell.alignment = align_right
    sig_cell.font = Font(italic=True, color="555555", name="Arial")

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    # Content-Disposition يدعم اسم ملف عربي عبر filename*
    encoded_name = quote(original_filename)
    headers_resp = {
        "Content-Disposition": (
            f"attachment; filename={safe_ascii_name}; "
            f"filename*=UTF-8''{encoded_name}"
        )
    }

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_resp,
    )

# ----------------- البذور (اختياري) -----------------

@app.get("/api/seed")
def seed_endpoint():
    if seed_main is None:
        return {"ok": False, "error": "seed_demo_data.py غير متوفر"}
    try:
        # دالة main في ملف البذور تُنادي init_db بنفسها عادةً
        seed_main()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ----------------- إصلاح يدوي للمخطط -----------------

@app.post("/api/admin/repair", tags=["admin"])
def admin_repair():
    try:
        repair_sqlite()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# =====================================================================
# نقطة تشغيل محلية
# =====================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=9000, reload=True)
