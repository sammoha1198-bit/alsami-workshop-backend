# app/routers/exporter.py

from io import BytesIO
from typing import Optional, Iterable, List, Tuple
from datetime import datetime, date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from ..database import get_session
from ..models import (
    EngineSupply, EngineIssue, EngineRehab, EngineCheck, EngineUpload,
    EngineLathe, EnginePump, EngineElectrical,
    GenSupply, GenIssue, GenInspect
)

router = APIRouter(prefix="/api/export", tags=["Export"])

# ======================= أدوات مساعدة عامة =======================

def _parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        # دعم صيغة yyyy-mm-dd
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

def _wb() -> Workbook:
    wb = Workbook()
    return wb

def _ws(wb: Workbook, title: str):
    ws = wb.create_sheet(title=title[:31])  # حد العنوان في Excel
    # RTL
    ws.sheet_view.rightToLeft = True
    return ws

def _style_header(ws, row: int, cols_count: int):
    fill = PatternFill(start_color="D6EAF8", end_color="D6EAF8", fill_type="solid")
    font = Font(bold=True)
    align = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )
    for c in range(1, cols_count + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = fill
        cell.font = font
        cell.alignment = align
        cell.border = border

def _style_table(ws, start_row: int, rows_count: int, cols_count: int):
    # حدود وخلايا عامة
    align = Alignment(horizontal="right", vertical="center", wrap_text=True)
    border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )
    for r in range(start_row, start_row + rows_count):
        for c in range(1, cols_count + 1):
            cell = ws.cell(row=r, column=c)
            cell.alignment = align
            cell.border = border

def _autosize(ws, upto_col: int):
    for c in range(1, upto_col + 1):
        letter = get_column_letter(c)
        ws.column_dimensions[letter].width = 18

def _date_fmt(d: Optional[datetime]) -> str:
    if not d:
        return ""
    if isinstance(d, date) and not isinstance(d, datetime):
        return d.isoformat()
    return str(d)[:10]

# فلترة بالتاريخ داخل الاستعلام عندما يتوفر عمود تاريخ
def _range_filter(q, col, d_from: Optional[date], d_to: Optional[date]):
    if d_from:
        q = q.where(col >= datetime.combine(d_from, datetime.min.time()))
    if d_to:
        q = q.where(col <= datetime.combine(d_to, datetime.max.time()))
    return q

# ======================= إنشاء شيتات الأنواع =======================

def sheet_engine_supply(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "توريد المحركات")
    headers = ["الرقم التسلسلي", "نوع المحرك", "المودل", "الموقع السابق", "المورد", "تاريخ التوريد", "ملاحظات"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(EngineSupply)
    q = _range_filter(q, EngineSupply.date, d_from, d_to)
    rows = session.exec(q).all()
    for r in rows:
        ws.append([
            r.serial or "", r.engine_type or "", r.model or "", r.prev_site or "",
            r.supplier or "", _date_fmt(r.date), r.notes or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_engine_issue(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "صرف المحركات")
    headers = ["الرقم التسلسلي", "الموقع الحالي", "المستلم", "الجهة الطالبة", "تاريخ الصرف", "ملاحظات"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(EngineIssue)
    q = _range_filter(q, EngineIssue.date, d_from, d_to)
    rows = session.exec(q).all()
    for r in rows:
        ws.append([
            r.serial or "", r.current_site or "", r.receiver or "",
            r.requester or "", _date_fmt(r.date), r.notes or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_engine_rehab(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "تأهيل المحركات")
    headers = ["الرقم التسلسلي", "المؤهل", "نوع التأهيل", "تاريخ التأهيل", "ملاحظات"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(EngineRehab)
    q = _range_filter(q, EngineRehab.date, d_from, d_to)
    rows = session.exec(q).all()
    for r in rows:
        ws.append([
            r.serial or "", r.rehab_by or "", r.rehab_type or "",
            _date_fmt(r.date), r.notes or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_engine_check(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "فحص المحركات")
    headers = ["الرقم التسلسلي", "الفاحص", "الوصف", "تاريخ الفحص", "ملاحظات الفحص"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(EngineCheck)
    q = _range_filter(q, EngineCheck.date, d_from, d_to)
    rows = session.exec(q).all()
    for r in rows:
        ws.append([
            r.serial or "", r.inspector or "", r.description or "",
            _date_fmt(r.date), getattr(r, "check_notes", None) or getattr(r, "notes", "") or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_engine_upload(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "رفع المحركات")
    headers = ["الرقم التسلسلي", "ملف المؤهل (نعم/لا)", "ملف الفحص (نعم/لا)", "تاريخ رفع المؤهل", "تاريخ رفع الفحص", "ملاحظات"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(EngineUpload)
    # لا يوجد عمود تاريخ واحد؛ نستخدم rehab_date و check_date (فلترة واسعة: أي منهما يقع داخل المدى)
    all_rows = session.exec(q).all()
    def in_range(u: EngineUpload) -> bool:
        def ok(dv: Optional[datetime]) -> bool:
            if not (d_from or d_to):
                return True
            if not dv:
                return False
            d = dv.date()
            if d_from and d < d_from:
                return False
            if d_to and d > d_to:
                return False
            return True
        return ok(u.rehab_date) or ok(u.check_date)

    rows = [r for r in all_rows if in_range(r)]
    for r in rows:
        ws.append([
            r.serial or "",
            (r.rehab_file or ""), (r.check_file or ""),
            _date_fmt(r.rehab_date), _date_fmt(r.check_date),
            r.notes or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_engine_lathe(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "المخرطة (محركات)")
    headers = ["الرقم التسلسلي", "تأهيل المخرطة", "تاريخ توريد للمخرطة", "ملاحظات"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(EngineLathe)
    q = _range_filter(q, EngineLathe.lathe_supply_date, d_from, d_to)
    rows = session.exec(q).all()
    for r in rows:
        ws.append([
            r.serial or "", r.lathe_rehab or "", _date_fmt(r.lathe_supply_date), r.notes or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_engine_pump(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "البمبات والنوزلات")
    headers = ["الرقم التسلسلي للمحرك", "الرقم التسلسلي للبمب", "تأهيل البمب", "ملاحظات"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    # لا يوجد تاريخ في النموذج => نتجاهل الفلترة الزمنية
    rows = session.exec(select(EnginePump)).all()
    for r in rows:
        ws.append([
            r.serial or "", r.pump_serial or "", r.pump_rehab or "", r.notes or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_engine_electrical(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "الصريمي (كهرباء)")
    headers = ["الرقم التسلسلي", "النوع", "سلف", "دينمو", "تاريخ"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(EngineElectrical)
    q = _range_filter(q, EngineElectrical.date, d_from, d_to)
    rows = session.exec(q).all()
    for r in rows:
        ws.append([
            r.serial or "", r.kind or "",
            "نعم" if r.has_starter else "لا",
            "نعم" if r.has_dynamo else "لا",
            _date_fmt(r.date)
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_gen_supply(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "توريد المولدات")
    headers = ["الترميز", "نوع المولد", "المودل", "الموقع السابق", "اسم المورد", "الجهة الموردة", "تاريخ التوريد", "ملاحظات"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(GenSupply)
    q = _range_filter(q, GenSupply.date, d_from, d_to)
    rows = session.exec(q).all()
    for r in rows:
        ws.append([
            r.code or "", r.gen_type or "", r.model or "", r.prev_site or "",
            r.supplier_name or "", r.supplier_entity or "", _date_fmt(r.date), r.notes or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_gen_issue(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "صرف المولدات")
    headers = ["الترميز", "تاريخ الصرف", "المستلم", "الجهة الطالبة", "الموقع الحالي", "ملاحظات"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(GenIssue)
    q = _range_filter(q, GenIssue.issue_date, d_from, d_to)
    rows = session.exec(q).all()
    for r in rows:
        ws.append([
            r.code or "", _date_fmt(r.issue_date), r.receiver or "", r.requester or "",
            r.current_site or "", r.notes or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

def sheet_gen_inspect(session: Session, wb: Workbook, d_from: Optional[date], d_to: Optional[date]):
    ws = _ws(wb, "الرفع والفحص (مولدات)")
    headers = ["الترميز", "الفاحص", "المؤهل الكهربائي", "تاريخ التأهيل", "ملاحظات"]
    ws.append(headers)
    _style_header(ws, 1, len(headers))

    q = select(GenInspect)
    q = _range_filter(q, GenInspect.rehab_date, d_from, d_to)
    rows = session.exec(q).all()
    for r in rows:
        ws.append([
            r.code or "", r.inspector or "", r.electrical_rehab_by or "",
            _date_fmt(r.rehab_date), r.notes or ""
        ])
    _style_table(ws, 2, len(rows), len(headers))
    _autosize(ws, len(headers))

# ======================= الراوت الرئيسي للتصدير =======================

@router.get("/{kind}")
def export_kind(
    kind: str,
    date_from: Optional[str] = Query(None, alias="from"),
    date_to: Optional[str]   = Query(None, alias="to"),
    session: Session = Depends(get_session)
):
    """
    kinds:
      - engines, generators
      - engines/issue, generators/issue
      - engines/rehab, engines/check, engines/upload
      - engines/lathe, engines/electrical, engines/pump
      - generators/inspect
      - all  -> ملف واحد يحتوي شيتات منفصلة لجميع ما سبق
    """
    d_from = _parse_date(date_from)
    d_to   = _parse_date(date_to)

    wb = _wb()
    # احذف الشيت الافتراضي الذي ينشئه openpyxl
    if wb.active and wb.active.max_row == 1 and wb.active.max_column == 1 and wb.active["A1"].value is None:
        wb.remove(wb.active)

    def add_one(_kind: str):
        if _kind == "engines":
            sheet_engine_supply(session, wb, d_from, d_to)
        elif _kind == "engines/issue":
            sheet_engine_issue(session, wb, d_from, d_to)
        elif _kind == "engines/rehab":
            sheet_engine_rehab(session, wb, d_from, d_to)
        elif _kind == "engines/check":
            sheet_engine_check(session, wb, d_from, d_to)
        elif _kind == "engines/upload":
            sheet_engine_upload(session, wb, d_from, d_to)
        elif _kind == "engines/lathe":
            sheet_engine_lathe(session, wb, d_from, d_to)
        elif _kind == "engines/electrical":
            sheet_engine_electrical(session, wb, d_from, d_to)
        elif _kind == "engines/pump":
            sheet_engine_pump(session, wb, d_from, d_to)
        elif _kind == "generators":
            sheet_gen_supply(session, wb, d_from, d_to)
        elif _kind == "generators/issue":
            sheet_gen_issue(session, wb, d_from, d_to)
        elif _kind == "generators/inspect":
            sheet_gen_inspect(session, wb, d_from, d_to)
        else:
            # نوع غير معروف؛ نتجاهله بصمت
            pass

    if kind == "all":
        kinds = [
            "engines", "engines/issue", "engines/rehab", "engines/check", "engines/upload",
            "engines/lathe", "engines/electrical", "engines/pump",
            "generators", "generators/issue", "generators/inspect"
        ]
        for k in kinds:
            add_one(k)
        filename = "تقرير-الورشة-شامل.xlsx"
    else:
        add_one(kind)
        safe = kind.replace("/", "-")
        filename = f"تقرير-{safe}.xlsx"

    # إذا لم تُنشأ أي شيت (نوع خاطئ مثلاً) أضف شيتًا فارغًا لتجنب خطأ الحفظ
    if not wb.worksheets:
        ws = _ws(wb, "فارغ")
        ws.append(["لا توجد بيانات"])

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    # ترميز الاسم RFC5987 لتجنب UnicodeEncodeError
    from urllib.parse import quote
    encoded_filename = quote(filename.encode("utf-8"))

    return StreamingResponse(
        bio,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )
