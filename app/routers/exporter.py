from typing import Dict, Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from ..auth import role_required  # ← أضِف هذا

import io

from ..database import get_session
from ..models import (
    EngineSupply, EngineIssue, EngineRehab, EngineCheck, EngineUpload, EngineLathe, EnginePump, EngineElectrical,
    GenSupply, GenIssue, GenInspect
)

router = APIRouter(prefix="/export", tags=["export"])

# ...

def _style_ws(ws, headers):
    ws.sheet_view.rightToLeft = True
    fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
    thin = Side(style="thin", color="CCCCCC")
    ws.append(headers)
    for c in ws[1]:
        c.font = Font(bold=True); c.alignment = Alignment(horizontal="center")
        c.fill = fill; c.border = Border(top=thin, left=thin, right=thin, bottom=thin)
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 22

def _date_of(rec, *names):
    for n in names:
        v = getattr(rec, n, None)
        if v: return v
    return None

# --------- Helpers ----------
def parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def in_range(dt: Optional[datetime], d1: Optional[datetime], d2: Optional[datetime]) -> bool:
    if not dt:
        return False
    if d1 and dt < d1:
        return False
    if d2 and dt > d2:
        return False
    return True

def latest(rows: List, date_field: str = "date"):
    """أعد أحدث سجل (أكبر تاريخ) من قائمة سجلات، وإلا None"""
    if not rows:
        return None
    rows = [r for r in rows if getattr(r, date_field, None)]
    if not rows:
        return None
    return sorted(rows, key=lambda r: getattr(r, date_field))[ -1 ]

def style_header(ws, labels):
    ws.sheet_view.rightToLeft = True
    fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
    thin = Side(style="thin", color="CCCCCC")
    ws.append(labels)
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")
        c.fill = fill
        c.border = Border(top=thin, left=thin, right=thin, bottom=thin)
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 18

def yn(v: Optional[bool]) -> str:
    return "نعم" if v is True else "لا" if v is False else ""

# ========= صرف المحركات =========
@router.get("/engines/issue")
def export_engines_issue(date_from: str | None = Query(None, alias="from"),
                         date_to: str | None = Query(None, alias="to"),
                         session: Session = Depends(get_session)):
    d1, d2 = parse_date(date_from), parse_date(date_to)
    rows = [r for r in session.exec(select(EngineIssue)).all()
            if in_range(_date_of(r, "date"), d1, d2)]
    wb = Workbook(); ws = wb.active; ws.title = "صرف المحركات"
    _style_ws(ws, ["الرقم التسلسلي","الموقع الحالي","المستلم","الجهة الطالبة","تاريخ الصرف","ملاحظات"])
    for r in rows:
        ws.append([r.serial, r.current_site, r.receiver, r.requester, r.date, getattr(r,"notes", "")])
    bio = io.BytesIO(); wb.save(bio); bio.seek(0)
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=engines_issue.xlsx"})
user=Depends(role_required(["admin"]))  # ← يمنع غير الـadmin
# ========= صرف المولدات =========
@router.get("/generators/issue")
def export_generators_issue(date_from: str | None = Query(None, alias="from"),
                            date_to: str | None = Query(None, alias="to"),
                            session: Session = Depends(get_session)):
    d1, d2 = parse_date(date_from), parse_date(date_to)
    rows = [r for r in session.exec(select(GenIssue)).all()
            if in_range(_date_of(r, "date", "issue_date"), d1, d2)]
    wb = Workbook(); ws = wb.active; ws.title = "صرف المولدات"
    _style_ws(ws, ["الترميز","تاريخ الصرف","المستلم","الجهة الطالبة","الموقع الحالي","ملاحظات"])
    for r in rows:
        ws.append([r.code, r.issue_date, r.receiver, r.requester, r.current_site, getattr(r,"notes","")])
    bio = io.BytesIO(); wb.save(bio); bio.seek(0)
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=generators_issue.xlsx"})
user=Depends(role_required(["admin"]))  # ← يمنع غير الـadmin
# ========= المخرطة =========
@router.get("/engines/lathe")
def export_engines_lathe(date_from: str | None = Query(None, alias="from"),
                         date_to: str | None = Query(None, alias="to"),
                         session: Session = Depends(get_session)):
    d1, d2 = parse_date(date_from), parse_date(date_to)
    rows = [r for r in session.exec(select(EngineLathe)).all()
            if in_range(_date_of(r, "date", "lathe_supply_date"), d1, d2)]
    wb = Workbook(); ws = wb.active; ws.title = "المخرطة"
    _style_ws(ws, ["الرقم التسلسلي","تأهيل المخرطة","ملاحظات","تاريخ التوريد للمخرطة"])
    for r in rows:
        ws.append([r.serial, r.lathe_rehab, getattr(r,"notes",""), getattr(r,"lathe_supply_date", "")])
    bio = io.BytesIO(); wb.save(bio); bio.seek(0)
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=engines_lathe.xlsx"})
user=Depends(role_required(["admin"]))  # ← يمنع غير الـadmin
# ========= الصريمي =========
@router.get("/engines/electrical")
def export_engines_electrical(date_from: str | None = Query(None, alias="from"),
                              date_to: str | None = Query(None, alias="to"),
                              session: Session = Depends(get_session)):
    d1, d2 = parse_date(date_from), parse_date(date_to)
    rows = [r for r in session.exec(select(EngineElectrical)).all()
            if in_range(_date_of(r, "date"), d1, d2)]
    wb = Workbook(); ws = wb.active; ws.title = "الصريمي"
    _style_ws(ws, ["الرقم التسلسلي","النوع","سلف","دينمو","تاريخ"])
    def yn(v): return "نعم" if v else "لا" if v is False else ""
    for r in rows:
        ws.append([r.serial, r.kind, yn(getattr(r,"has_starter",None)), yn(getattr(r,"has_dynamo",None)), getattr(r,"date","")])
    bio = io.BytesIO(); wb.save(bio); bio.seek(0)
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=engines_electrical.xlsx"})
user=Depends(role_required(["admin"]))  # ← يمنع غير الـadmin
# ========= البمبات والنوزلات =========
@router.get("/engines/pump")
def export_engines_pump(date_from: str | None = Query(None, alias="from"),
                        date_to: str | None = Query(None, alias="to"),
                        session: Session = Depends(get_session)):
    d1, d2 = parse_date(date_from), parse_date(date_to)
    rows = [r for r in session.exec(select(EnginePump)).all()
            if in_range(_date_of(r, "date"), d1, d2)]
    wb = Workbook(); ws = wb.active; ws.title = "البمبات والنوزلات"
    _style_ws(ws, ["الرقم التسلسلي للمحرك","الرقم التسلسلي للبمب","تأهيل البمب","ملاحظات","تاريخ"])
    for r in rows:
        ws.append([r.serial, r.pump_serial, r.pump_rehab, getattr(r,"notes",""), getattr(r,"date","")])
    bio = io.BytesIO(); wb.save(bio); bio.seek(0)
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=engines_pump.xlsx"})
user=Depends(role_required(["admin"]))  # ← يمنع غير الـadmin
# ===================== محركات — أعمدة مفصلة =====================
@router.get("/engines")
def export_engines_columns(
    date_from: Optional[str] = Query(None, alias="from"),
    date_to: Optional[str]   = Query(None, alias="to"),
    session: Session = Depends(get_session),
    user=Depends(role_required(["admin"]))  # ← يمنع غير الـadmin
):

    d1, d2 = parse_date(date_from), parse_date(date_to)

    # اجمع حسب serial
    groups: Dict[str, Dict[str, List]] = {}
    def put(key: str, row):
        if not in_range(getattr(row, "date", None), d1, d2):
            return
        g = groups.setdefault(row.serial, {"supply":[], "issue":[], "rehab":[], "check":[], "upload":[], "lathe":[], "pump":[], "electrical":[]})
        g[key].append(row)

    for r in session.exec(select(EngineSupply)).all():    put("supply", r)
    for r in session.exec(select(EngineIssue)).all():     put("issue", r)
    for r in session.exec(select(EngineRehab)).all():     put("rehab", r)
    for r in session.exec(select(EngineCheck)).all():     put("check", r)
    for r in session.exec(select(EngineUpload)).all():    put("upload", r)
    for r in session.exec(select(EngineLathe)).all():     put("lathe", r)
    for r in session.exec(select(EnginePump)).all():      put("pump", r)
    for r in session.exec(select(EngineElectrical)).all():put("electrical", r)

    wb = Workbook()
    ws = wb.active
    ws.title = "المحركات (أعمدة)"
    style_header(ws, [
        # أساسي
        "الرقم التسلسلي",
        # توريد
        "توريد/نوع", "توريد/مودل", "توريد/مورد", "توريد/الموقع السابق", "توريد/تاريخ",
        # صرف
        "صرف/الموقع الحالي", "صرف/المستلم", "صرف/الجهة الطالبة", "صرف/تاريخ",
        # تأهيل
        "تأهيل/المؤهل", "تأهيل/نوع التأهيل", "تأهيل/ملاحظات", "تأهيل/تاريخ",
        # فحص
        "فحص/الفاحص", "فحص/الوصف", "فحص/ملاحظات", "فحص/تاريخ",
        # رفع
        "رفع/ملف المؤهل", "رفع/ملف الفحص", "رفع/تاريخ المؤهل", "رفع/تاريخ الفحص", "رفع/ملاحظات",
        # مخرطة
        "مخرطة/تأهيل", "مخرطة/ملاحظات", "مخرطة/تاريخ توريد للمخرطة",
        # بمبات
        "بمبات/رقم بمب", "بمبات/تأهيل", "بمبات/ملاحظات",
        # صريمي
        "صريمي/النوع", "صريمي/سلف", "صريمي/دينمو",
    ])

    for serial, g in groups.items():
        s  = latest(g["supply"])
        isr = latest(g["issue"])
        rh = latest(g["rehab"])
        ch = latest(g["check"])
        up = latest(g["upload"])
        lt = latest(g["lathe"])
        pm = latest(g["pump"])
        el = latest(g["electrical"])

        ws.append([
            serial,
            # توريد
            getattr(s, "engine_type", None) or "",
            getattr(s, "model", None) or "",
            getattr(s, "supplier", None) or "",
            getattr(s, "prev_site", None) or "",
            getattr(s, "date", None) or "",
            # صرف
            getattr(isr, "current_site", None) or "",
            getattr(isr, "receiver", None) or "",
            getattr(isr, "requester", None) or "",
            getattr(isr, "date", None) or "",
            # تأهيل
            getattr(rh, "rehab_by", None) or "",
            getattr(rh, "rehab_type", None) or "",
            getattr(rh, "notes", None) or "",
            getattr(rh, "date", None) or "",
            # فحص
            getattr(ch, "inspector", None) or "",
            getattr(ch, "description", None) or "",
            getattr(ch, "check_notes", None) or "",
            getattr(ch, "date", None) or "",
            # رفع
            getattr(up, "rehab_file", None) or "",
            getattr(up, "check_file", None) or "",
            getattr(up, "rehab_date", None) or "",
            getattr(up, "check_date", None) or "",
            getattr(up, "notes", None) or "",
            # مخرطة
            getattr(lt, "lathe_rehab", None) or "",
            getattr(lt, "notes", None) or "",
            getattr(lt, "lathe_supply_date", None) or "",
            # بمبات
            getattr(pm, "pump_serial", None) or "",
            getattr(pm, "pump_rehab", None) or "",
            getattr(pm, "notes", None) or "",
            # صريمي
            getattr(el, "kind", None) or "",
            yn(getattr(el, "has_starter", None)),
            yn(getattr(el, "has_dynamo", None)),
        ])

    out = io.BytesIO()
    wb.save(out); out.seek(0)
    filename = f"engines_columns_{date_from or 'all'}_{date_to or 'all'}.xlsx"
    return StreamingResponse(out,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

user=Depends(role_required(["admin"]))  # ← يمنع غير الـadmin
# ===================== مولدات — أعمدة مفصلة =====================
@router.get("/generators")
def export_generators_columns(
    date_from: Optional[str] = Query(None, alias="from"),
    date_to: Optional[str]   = Query(None, alias="to"),
    session: Session = Depends(get_session),
):
    d1, d2 = parse_date(date_from), parse_date(date_to)

    groups: Dict[str, Dict[str, List]] = {}
    def put(key: str, row):
        if not in_range(getattr(row, "date", None), d1, d2):
            return
        g = groups.setdefault(row.code, {"supply":[], "issue":[], "inspect":[]})
        g[key].append(row)

    for r in session.exec(select(GenSupply)).all():  put("supply", r)
    for r in session.exec(select(GenIssue)).all():   put("issue", r)
    for r in session.exec(select(GenInspect)).all(): put("inspect", r)

    wb = Workbook()
    ws = wb.active
    ws.title = "المولدات (أعمدة)"
    style_header(ws, [
        "الترميز",
        # توريد
        "توريد/نوع", "توريد/مودل", "توريد/المورد", "توريد/الجهة الموردة", "توريد/الموقع السابق", "توريد/تاريخ",
        # صرف
        "صرف/تاريخ", "صرف/المستلم", "صرف/الجهة الطالبة", "صرف/الموقع الحالي", "صرف/ملاحظات",
        # الرفع والفحص
        "فحص/الفاحص", "فحص/المؤهل الكهربائي", "فحص/تاريخ التأهيل", "فحص/ملاحظات",
    ])

    for code, g in groups.items():
        s  = latest(g["supply"])
        isr = latest(g["issue"], date_field="date")  # (يوجد حقل issue_date أيضًا)
        ins = latest(g["inspect"])

        ws.append([
            code,
            # توريد
            getattr(s, "gen_type", None) or "",
            getattr(s, "model", None) or "",
            getattr(s, "supplier_name", None) or "",
            getattr(s, "supplier_entity", None) or "",
            getattr(s, "prev_site", None) or "",
            getattr(s, "date", None) or "",
            # صرف
            getattr(isr, "issue_date", None) or "",
            getattr(isr, "receiver", None) or "",
            getattr(isr, "requester", None) or "",
            getattr(isr, "current_site", None) or "",
            getattr(isr, "notes", None) or "",
            # فحص
            getattr(ins, "inspector", None) or "",
            getattr(ins, "electrical_rehab_by", None) or "",
            getattr(ins, "rehab_date", None) or "",
            getattr(ins, "notes", None) or "",
        ])

    out = io.BytesIO()
    wb.save(out); out.seek(0)
    filename = f"generators_columns_{date_from or 'all'}_{date_to or 'all'}.xlsx"
    return StreamingResponse(out,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
user=Depends(role_required(["admin"]))  # ← يمنع غير الـadmin