from fastapi import FastAPI, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict, Any, List, Union
from io import BytesIO
from urllib.parse import quote
import datetime

from sqlmodel import Session, select

# ملفاتنا
from .database import init_db, get_session
from . import models

# Excel
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side


# =========================================================
# إنشاء التطبيق
# =========================================================
app = FastAPI(
    title="Alsami Workshop Backend",
    version="4.0",
    description="Backend for Alsami mobile workshop app (engines + generators + spares)",
)

# =========================================================
# CORS
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # أثناء التطوير افتحها
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Startup
# =========================================================
@app.on_event("startup")
def on_startup() -> None:
    # إنشاء الجداول لو مش موجودة
    init_db()


# =========================================================
# Root (للاختبار من Render)
# =========================================================
@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": "Workshop API",
        "status": "running",
        "endpoints": [
            "/api/health",
            "/api/search/{key}",
            "/api/last3/engines",
            "/api/last3/generators",
            "/api/export/xlsx",
        ],
    }


# =========================================================
# Health
# =========================================================
@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "time": datetime.datetime.utcnow().isoformat()}


# =========================================================
# 1) البحث: يرجّع كل السجلات لنفس الرقم
# =========================================================
@app.get("/api/search/{key}")
def search_item(key: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    هذا المسار هو المهم للـ frontend
    لازم يرجع بنفس الشكل اللي يتوقعه app.js
    """
    # نجهز الشكل الفارغ أول
    result: Dict[str, Any] = {
        "engines": {
            "supply": [],
            "issue": [],
            "rehab": [],
            "check": [],
            "upload": [],
            "lathe": [],
            "pump": [],
            "electrical": [],
        },
        "generators": {
            "supply": [],
            "issue": [],
            "inspect": [],
        },
    }

    # ---------- محركات ----------
    eng_supply = session.exec(
        select(models.EngineSupply).where(models.EngineSupply.serial == key)
    ).all()
    result["engines"]["supply"] = [row.dict() for row in eng_supply]

    eng_issue = session.exec(
        select(models.EngineIssue).where(models.EngineIssue.serial == key)
    ).all()
    result["engines"]["issue"] = [row.dict() for row in eng_issue]

    eng_rehab = session.exec(
        select(models.EngineRehab).where(models.EngineRehab.serial == key)
    ).all()
    result["engines"]["rehab"] = [row.dict() for row in eng_rehab]

    eng_check = session.exec(
        select(models.EngineCheck).where(models.EngineCheck.serial == key)
    ).all()
    result["engines"]["check"] = [row.dict() for row in eng_check]

    eng_upload = session.exec(
        select(models.EngineUpload).where(models.EngineUpload.serial == key)
    ).all()
    result["engines"]["upload"] = [row.dict() for row in eng_upload]

    eng_lathe = session.exec(
        select(models.EngineLathe).where(models.EngineLathe.serial == key)
    ).all()
    result["engines"]["lathe"] = [row.dict() for row in eng_lathe]

    eng_pump = session.exec(
        select(models.EnginePump).where(models.EnginePump.serial == key)
    ).all()
    result["engines"]["pump"] = [row.dict() for row in eng_pump]

    eng_elec = session.exec(
        select(models.EngineElectrical).where(models.EngineElectrical.serial == key)
    ).all()
    result["engines"]["electrical"] = [row.dict() for row in eng_elec]

    # ---------- مولدات ----------
    gen_supply = session.exec(
        select(models.GeneratorSupply).where(models.GeneratorSupply.code == key)
    ).all()
    result["generators"]["supply"] = [row.dict() for row in gen_supply]

    gen_issue = session.exec(
        select(models.GeneratorIssue).where(models.GeneratorIssue.code == key)
    ).all()
    result["generators"]["issue"] = [row.dict() for row in gen_issue]

    gen_inspect = session.exec(
        select(models.GeneratorInspect).where(models.GeneratorInspect.code == key)
    ).all()
    result["generators"]["inspect"] = [row.dict() for row in gen_inspect]

    return result


# =========================================================
# 2) مزامنة الدُفعات من الفرونت (IndexedDB → backend)
# =========================================================
@app.post("/api/sync/batch")
def sync_batch(
    body: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = body.get("items", [])
    saved = 0

    for item in items:
        store = item.get("store")
        data = item.get("payload", {})

        # محركات
        if store == "eng_supply":
            session.add(
                models.EngineSupply(
                    serial=data.get("serial", ""),
                    engineType=data.get("engineType"),
                    model=data.get("model"),
                    prevSite=data.get("prevSite"),
                    supDate=data.get("supDate"),
                    supplier=data.get("supplier"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

        elif store == "eng_issue":
            session.add(
                models.EngineIssue(
                    serial=data.get("serial", ""),
                    currSite=data.get("currSite"),
                    receiver=data.get("receiver"),
                    requester=data.get("requester"),
                    issueDate=data.get("issueDate"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

        elif store == "eng_rehab":
            session.add(
                models.EngineRehab(
                    serial=data.get("serial", ""),
                    rehabber=data.get("rehabber"),
                    rehabType=data.get("rehabType"),
                    rehabDate=data.get("rehabDate"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

        elif store == "eng_check":
            session.add(
                models.EngineCheck(
                    serial=data.get("serial", ""),
                    inspector=data.get("inspector"),
                    desc=data.get("desc"),
                    checkDate=data.get("checkDate"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

        elif store == "eng_upload":
            session.add(
                models.EngineUpload(
                    serial=data.get("serial", ""),
                    rehabUp=data.get("rehabUp"),
                    checkUp=data.get("checkUp"),
                    rehabUpDate=data.get("rehabUpDate"),
                    checkUpDate=data.get("checkUpDate"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

        elif store == "eng_lathe":
            session.add(
                models.EngineLathe(
                    serial=data.get("serial", ""),
                    lathe=data.get("lathe"),
                    latheDate=data.get("latheDate"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

        elif store == "eng_pump":
            session.add(
                models.EnginePump(
                    serial=data.get("serial", ""),
                    pumpSerial=data.get("pumpSerial"),
                    pumpRehab=data.get("pumpRehab"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

        elif store == "eng_electrical":
            session.add(
                models.EngineElectrical(
                    serial=data.get("serial", ""),
                    etype=data.get("etype"),
                    starter=data.get("starter"),
                    alternator=data.get("alternator"),
                    edate=data.get("edate"),
                )
            )
            saved += 1

        # مولدات
        elif store == "gen_supply":
            session.add(
                models.GeneratorSupply(
                    code=data.get("code", ""),
                    gType=data.get("gType"),
                    model=data.get("model"),
                    prevSite=data.get("prevSite"),
                    supDate=data.get("supDate"),
                    supplier=data.get("supplier"),
                    vendor=data.get("vendor"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

        elif store == "gen_issue":
            session.add(
                models.GeneratorIssue(
                    code=data.get("code", ""),
                    issueDate=data.get("issueDate"),
                    receiver=data.get("receiver"),
                    requester=data.get("requester"),
                    currSite=data.get("currSite"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

        elif store == "gen_inspect":
            session.add(
                models.GeneratorInspect(
                    code=data.get("code", ""),
                    inspector=data.get("inspector"),
                    elecRehab=data.get("elecRehab"),
                    rehabDate=data.get("rehabDate"),
                    rehabUp=data.get("rehabUp"),
                    checkUp=data.get("checkUp"),
                    notes=data.get("notes"),
                )
            )
            saved += 1

    session.commit()
    return {"ok": True, "saved": saved}


# =========================================================
# 3) آخر 3 محركات / مولدات
# =========================================================
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


# =========================================================
# 4) التصدير إلى إكسل (عربي + RTL + ألوان)
# =========================================================
@app.post("/api/export/xlsx")
def export_xlsx(payload: Dict[str, Any] = Body(...)):
    original_filename: str = payload.get("filename") or "report.xlsx"
    sheet_name: str = payload.get("sheet") or "تقرير"
    headers: List[str] = payload.get("headers") or []
    raw_rows: List[Union[Dict[str, Any], List[Any]]] = payload.get("rows") or []

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.sheet_view.rightToLeft = True

    header_fill = PatternFill("solid", fgColor="0EA5E9")
    alt_fill = PatternFill("solid", fgColor="E2F3FF")
    white_fill = PatternFill("solid", fgColor="FFFFFF")
    header_font = Font(bold=True, color="FFFFFF", name="Arial")
    normal_font = Font(name="Arial")
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin", color="DDDDDD"),
        right=Side(style="thin", color="DDDDDD"),
        top=Side(style="thin", color="DDDDDD"),
        bottom=Side(style="thin", color="DDDDDD"),
    )

    # رأس الجدول
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
        if isinstance(row, dict) and headers:
            ordered = [row.get(h, "") for h in headers]
        elif isinstance(row, dict):
            ordered = list(row.values())
        else:
            ordered = list(row)
        ws.append(ordered)
        for col_idx in range(1, len(ordered) + 1):
            c = ws.cell(row=current_row, column=col_idx)
            c.font = normal_font
            c.alignment = align_right
            c.border = thin_border
            c.fill = alt_fill if current_row % 2 else white_fill
        current_row += 1

    ws.append([])
    sig = ws.cell(row=current_row + 1, column=1)
    sig.value = f"تم توليد التقرير في: {datetime.datetime.utcnow().isoformat()}"
    sig.alignment = align_right
    sig.font = Font(italic=True, color="555555", name="Arial")

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    safe = "report.xlsx"
    encoded = quote(original_filename)

    headers_resp = {
        "Content-Disposition": f"attachment; filename={safe}; filename*=UTF-8''{encoded}"
    }

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_resp,
    )


# =========================================================
# للتشغيل المحلي
# =========================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=9000, reload=True)
