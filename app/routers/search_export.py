from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import (
    EngineSupply, EngineIssue, EngineRehab, EngineCheck, EngineUpload,
    EngineLathe, EnginePump, EngineElectrical,
    GenSupply, GenIssue, GenInspect
)

router = APIRouter(prefix="/api/search", tags=["Search & Reports"])

@router.get("/summary")
def search_summary(q: str, session: Session = Depends(get_session)):
    q = q.strip()

    engines = session.exec(select(EngineSupply).where(EngineSupply.serial.contains(q))).all()
    gens = session.exec(select(GenSupply).where(GenSupply.code.contains(q))).all()

    rows = []

    # 🛠️ المحركات
    for e in engines:
        issue = session.exec(select(EngineIssue).where(EngineIssue.serial == e.serial)).first()
        rehab = session.exec(select(EngineRehab).where(EngineRehab.serial == e.serial)).first()
        check = session.exec(select(EngineCheck).where(EngineCheck.serial == e.serial)).first()
        upload = session.exec(select(EngineUpload).where(EngineUpload.serial == e.serial)).first()
        lathe = session.exec(select(EngineLathe).where(EngineLathe.serial == e.serial)).first()
        pump = session.exec(select(EnginePump).where(EnginePump.serial == e.serial)).first()
        elect = session.exec(select(EngineElectrical).where(EngineElectrical.serial == e.serial)).first()

        rows.append({
            "kind": "محرك",
            "key": e.serial,
            "supply_type": e.engine_type,
            "supply_model": e.model,
            "supply_supplier": e.supplier,
            "supply_prev_site": e.prev_site,
            "supply_date": str(e.date.date()),

            "issue_current_site": issue.current_site if issue else "",
            "issue_receiver": issue.receiver if issue else "",
            "issue_requester": issue.requester if issue else "",
            "issue_date": str(issue.date.date()) if issue else "",

            "rehab_by": rehab.rehab_by if rehab else "",
            "rehab_type": rehab.rehab_type if rehab else "",
            "rehab_date": str(rehab.date.date()) if rehab else "",

            "check_inspector": check.inspector if check else "",
            "check_desc": check.description if check else "",
            "check_date": str(check.date.date()) if check else "",

            "upload_rehab_file": upload.rehab_file if upload else "",
            "upload_check_file": upload.check_file if upload else "",
            "upload_rehab_date": str(upload.rehab_date.date()) if upload and upload.rehab_date else "",
            "upload_check_date": str(upload.check_date.date()) if upload and upload.check_date else "",

            "lathe_rehab": lathe.lathe_rehab if lathe else "",
            "lathe_supply_date": str(lathe.lathe_supply_date.date()) if lathe and lathe.lathe_supply_date else "",

            "pump_serial": pump.pump_serial if pump else "",
            "pump_rehab": pump.pump_rehab if pump else "",

            "elect_kind": elect.kind if elect else "",
            "elect_starter": "نعم" if elect and elect.has_starter else "لا",
            "elect_dynamo": "نعم" if elect and elect.has_dynamo else "لا",
        })

    # ⚡ المولدات
    for g in gens:
        issue = session.exec(select(GenIssue).where(GenIssue.code == g.code)).first()
        inspect = session.exec(select(GenInspect).where(GenInspect.code == g.code)).first()

        rows.append({
            "kind": "مولد",
            "key": g.code,
            "supply_type": g.gen_type,
            "supply_model": g.model,
            "supply_supplier": g.supplier_name,
            "supply_prev_site": g.prev_site,
            "supply_date": str(g.date.date()),

            "issue_current_site": issue.current_site if issue else "",
            "issue_receiver": issue.receiver if issue else "",
            "issue_requester": issue.requester if issue else "",
            "issue_date": str(issue.issue_date.date()) if issue else "",

            "check_inspector": inspect.inspector if inspect else "",
            "rehab_by": inspect.electrical_rehab_by if inspect else "",
            "rehab_date": str(inspect.rehab_date.date()) if inspect and inspect.rehab_date else "",
        })

    return {"rows": rows}
