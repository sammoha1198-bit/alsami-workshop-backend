# app/main.py
from fastapi import FastAPI, Body, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Union
from io import BytesIO
from urllib.parse import quote
import datetime

from sqlmodel import Session, select, desc

from .database import init_db, get_session
from . import models  # مهم عشان الجداول تتسجل
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side


app = FastAPI(
    title="Alsami Workshop Backend",
    version="3.1",
    description="Backend for engines / generators / spares forms",
)

# ===================== CORS =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # افتحها الآن لأن الفرونت يشتغل من file:// أو localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== STARTUP =====================
@app.on_event("startup")
def on_startup():
    # إنشاء الجداول لو غير موجودة
    init_db()


# ===================== HEALTH =====================
@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {
        "ok": True,
        "time": datetime.datetime.utcnow().isoformat(),
    }


# =======================================================
# 1) البحث الحقيقي
# =======================================================
@app.get("/api/search/{key}")
def search_item(key: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    الـ frontend يتوقع بنية محددة:
    {
      "engines": {...},
      "generators": {...}
    }
    """

    # محركات
    eng_sup = session.exec(
        select(models.EngineSupply).where(models.EngineSupply.serial == key)
    ).all()
    eng_issue = session.exec(
        select(models.EngineIssue).where(models.EngineIssue.serial == key)
    ).all()
    eng_rehab = session.exec(
        select(models.EngineRehab).where(models.EngineRehab.serial == key)
    ).all()
    eng_check = session.exec(
        select(models.EngineCheck).where(models.EngineCheck.serial == key)
    ).all()
    eng_upload = session.exec(
        select(models.EngineUpload).where(models.EngineUpload.serial == key)
    ).all()
    eng_lathe = session.exec(
        select(models.EngineLathe).where(models.EngineLathe.serial == key)
    ).all()
    eng_pump = session.exec(
        select(models.EnginePump).where(models.EnginePump.serial == key)
    ).all()
    eng_elec = session.exec(
        select(models.EngineElectrical).where(models.EngineElectrical.serial == key)
    ).all()

    # مولدات
    gen_sup = session.exec(
        select(models.GeneratorSupply).where(models.GeneratorSupply.code == key)
    ).all()
    gen_issue = session.exec(
        select(models.GeneratorIssue).where(models.GeneratorIssue.code == key)
    ).all()
    gen_inspect = session.exec(
        select(models.GeneratorInspect).where(models.GeneratorInspect.code == key)
    ).all()

    return {
        "engines": {
            "supply": [r.dict() for r in eng_sup],
            "issue": [r.dict() for r in eng_issue],
            "rehab": [r.dict() for r in eng_rehab],
            "check": [r.dict() for r in eng_check],
            "upload": [r.dict() for r in eng_upload],
            "lathe": [r.dict() for r in eng_lathe],
            "pump": [r.dict() for r in eng_pump],
            "electrical": [r.dict() for r in eng_elec],
        },
        "generators": {
            "supply": [r.dict() for r in gen_sup],
            "issue": [r.dict() for r in gen_issue],
            "inspect": [r.dict() for r in gen_inspect],
        },
    }


# =======================================================
# 2) مزامنة الدُفعات من الفرونت (IndexedDB → سيرفر)
# =======================================================
@app.post("/api/sync/batch")
async def sync_batch(
    payload: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = payload.get("items", [])
    saved = 0

    for item in items:
        store = item.get("store")
        data = item.get("payload", {}) or {}

        # -------- محركات --------
        if store == "eng_supply":
            obj = models.EngineSupply(
                serial=data.get("serial", ""),
                engineType=data.get("engineType"),
                model=data.get("model"),
                prevSite=data.get("prevSite"),
                supDate=data.get("supDate"),
                supplier=data.get("supplier"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        elif store == "eng_issue":
            obj = models.EngineIssue(
                serial=data.get("serial", ""),
                currSite=data.get("currSite"),
                receiver=data.get("receiver"),
                requester=data.get("requester"),
                issueDate=data.get("issueDate"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        elif store == "eng_rehab":
            obj = models.EngineRehab(
                serial=data.get("serial", ""),
                rehabber=data.get("rehabber"),
                rehabType=data.get("rehabType"),
                rehabDate=data.get("rehabDate"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        elif store == "eng_check":
            obj = models.EngineCheck(
                serial=data.get("serial", ""),
                inspector=data.get("inspector"),
                desc=data.get("desc"),
                checkDate=data.get("checkDate"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        elif store == "eng_upload":
            obj = models.EngineUpload(
                serial=data.get("serial", ""),
                rehabUp=data.get("rehabUp"),
                checkUp=data.get("checkUp"),
                rehabUpDate=data.get("rehabUpDate"),
                checkUpDate=data.get("checkUpDate"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        elif store == "eng_lathe":
            obj = models.EngineLathe(
                serial=data.get("serial", ""),
                lathe=data.get("lathe"),
                latheDate=data.get("latheDate"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        elif store == "eng_pump":
            obj = models.EnginePump(
                serial=data.get("serial", ""),
                pumpSerial=data.get("pumpSerial"),
                pumpRehab=data.get("pumpRehab"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        elif store == "eng_electrical":
            obj = models.EngineElectrical(
                serial=data.get("serial", ""),
                etype=data.get("etype"),
                starter=data.get("starter"),
                alternator=data.get("alternator"),
                edate=data.get("edate"),
            )
            session.add(obj)
            saved += 1

        # -------- مولدات --------
        elif store == "gen_supply":
            obj = models.GeneratorSupply(
                code=data.get("code", ""),
                gType=data.get("gType"),
                model=data.get("model"),
                prevSite=data.get("prevSite"),
                supDate=data.get("supDate"),
                supplier=data.get("supplier"),
                vendor=data.get("vendor"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        elif store == "gen_issue":
            obj = models.GeneratorIssue(
                code=data.get("code", ""),
                issueDate=data.get("issueDate"),
                receiver=data.get("receiver"),
                requester=data.get("requester"),
                currSite=data.get("currSite"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        elif store == "gen_inspect":
            obj = models.GeneratorInspect(
                code=data.get("code", ""),
                inspector=data.get("inspector"),
                elecRehab=data.get("elecRehab"),
                rehabDate=data.get("rehabDate"),
                rehabUp=data.get("rehabUp"),
                checkUp=data.get("checkUp"),
                notes=data.get("notes"),
            )
            session.add(obj)
            saved += 1

        else:
            # لو جالك ستور غير معروف تجاهله
            continue

    session.commit()
    return {"ok": True, "saved": saved}


# =======================================================
# 3) آخر 3 محركات / مولدات
# =======================================================
@app.get("/api/last3/engines")
def last3_engines(session: Session = Depends(get_session)) -> Dict[str, Any]:
    rows = session.exec(
        select(models.EngineSupply).order_by(desc(models.EngineSupply.id)).limit(3)
    ).all()
    return {
        "items": [
            {
                "serial": r.serial,
                "prevSite": r.prevSite or "",
            }
            for r in rows
        ]
    }


@app.get("/api/last3/generators")
def last3_generators(session: Session = Depends(get_session)) -> Dict[str, Any]:
    rows = session.exec(
        select(models.GeneratorSupply).order_by(desc(models.GeneratorSupply.id)).limit(3)
    ).all()
    return {
        "items": [
            {
                "code": r.code,
                "prevSite": r.prevSite or "",
            }
            for r in rows
        ]
    }


# =======================================================
# 4) التصدير إلى Excel (ملوّن + RTL)
# =======================================================
@app.post("/api/export/xlsx")
async def export_xlsx(payload: Dict[str, Any] = Body(...)):
    """
    يتوقع الفرونت:
    {
      "filename": "...",
      "sheet": "...",
      "headers": [...],
      "rows": [ {...} or [...] ]
    }
    """
    original_filename: str = payload.get("filename") or "alsami.xlsx"
    # مهم: اسم الملف في الهيدر لازم يكون إنجليزي عشان windows ما ينهار
    safe_filename = "alsami_report.xlsx"

    sheet_name: str = payload.get("sheet") or "تقرير"
    headers: List[str] = payload.get("headers") or []
    raw_rows: List[Union[Dict[str, Any], List[Any]]] = payload.get("rows") or []

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    # RTL
    ws.sheet_view.rightToLeft = True

    header_fill = PatternFill("solid", fgColor="0EA5E9")  # أزرق
    alt_fill = PatternFill("solid", fgColor="EFF6FF")
    white_fill = PatternFill("solid", fgColor="FFFFFF")
    header_font = Font(bold=True, color="FFFFFF", name="Tahoma")
    normal_font = Font(name="Tahoma")
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB"),
    )

    # رأس الجدول
    if headers:
      ws.append(headers)
      for col_idx, _ in enumerate(headers, start=1):
          cell = ws.cell(row=1, column=col_idx)
          cell.fill = header_fill
          cell.font = header_font
          cell.alignment = align_right
          cell.border = thin_border
          ws.column_dimensions[cell.column_letter].width = 28

    # البيانات
    current_row = 2
    for row in raw_rows:
        if isinstance(row, dict):
            # رتب حسب رؤوس الأعمدة
            if headers:
                ordered = [row.get(h, "") for h in headers]
            else:
                ordered = list(row.values())
        elif isinstance(row, (list, tuple)):
            ordered = list(row)
        else:
            ordered = [str(row)]

        ws.append(ordered)
        for col_idx in range(1, len(ordered) + 1):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.font = normal_font
            cell.alignment = align_right
            cell.border = thin_border
            cell.fill = alt_fill if current_row % 2 else white_fill
        current_row += 1

    # توقيع
    ws.append([])
    sig_cell = ws.cell(row=current_row + 1, column=1)
    sig_cell.value = f"تم توليد التقرير في: {datetime.datetime.utcnow().isoformat()}"
    sig_cell.alignment = align_right
    sig_cell.font = Font(italic=True, color="6B7280", name="Tahoma")

    # اكتب إلى بافر
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    # نحط الاسم العربي في filename* فقط
    encoded_name = quote(original_filename)

    headers_resp = {
        "Content-Disposition": (
            f"attachment; filename={safe_filename}; filename*=UTF-8''{encoded_name}"
        )
    }

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_resp,
    )


# =======================================================
# للتشغيل المباشر
# =======================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=9000, reload=True)
