# app/seed_demo_data.py
from sqlmodel import Session, select
from .database import engine, init_db
from . import models


def seed() -> None:
    """زرع بيانات تجريبية لو قاعدة البيانات فاضية."""
    init_db()

    with Session(engine) as s:
        exists = s.exec(select(models.EngineSupply)).first()
        if exists:
            # في بيانات، ما نضيف
            print("⚠️ يوجد بيانات مسبقة، لم أضف بيانات جديدة.")
            return

        # ------------------- المحركات -------------------
        engines_supply = [
            models.EngineSupply(
                serial="111",
                engineType="Deutz",
                model="F4L912",
                prevSite="المخزن الرئيسي",
                supDate="2025-10-30",
                supplier="Yemen Mobile",
                notes="توريد جديد",
            ),
            models.EngineSupply(
                serial="222",
                engineType="Perkins",
                model="404D-22",
                prevSite="فرع الحديدة",
                supDate="2025-10-29",
                supplier="PowerTech",
                notes="محرك جاهز للاستخدام",
            ),
            models.EngineSupply(
                serial="333",
                engineType="Kubota",
                model="V2203",
                prevSite="فرع صنعاء",
                supDate="2025-10-28",
                supplier="DieselPro",
                notes="محرك تم إعادة تأهيله",
            ),
        ]

        engines_issue = [
            models.EngineIssue(
                serial="111",
                currSite="محطة تعز",
                receiver="المهندس سامي",
                requester="قسم التشغيل",
                issueDate="2025-11-01",
                notes="تم صرفه للموقع",
            )
        ]

        engines_rehab = [
            models.EngineRehab(
                serial="333",
                rehabber="فريق التأهيل",
                rehabType="إصلاح كامل",
                rehabDate="2025-11-02",
                notes="تم تغيير حلقات ومضخة",
            )
        ]

        engines_check = [
           EngineCheck(
    serial="222",
    inspector="فريق الفحص",
    description="فحص حرارة وضغط زيت",  # ← بدلاً من desc="..."
    checkDate="2025-11-03",
    notes="الفحص ممتاز"
)

        ]

        engines_upload = [
            models.EngineUpload(
                serial="111",
                rehabUp="نعم",
                checkUp="لا",
                rehabUpDate="2025-11-04",
                notes="تم رفع المؤهل فقط",
            )
        ]

        engines_lathe = [
            models.EngineLathe(
                serial="333",
                lathe="تشغيل عمود + جلنبر",
                latheDate="2025-11-05",
                notes="مخرطة خارجية",
            )
        ]

        engines_pump = [
            models.EnginePump(
                serial="111",
                pumpSerial="P-111-A",
                pumpRehab="تنظيف ورش",
                notes="بمب جاهز",
            )
        ]

        engines_electrical = [
            models.EngineElectrical(
                serial="222",
                etype="كهرباء كاملة",
                starter="نعم",
                alternator="نعم",
                edate="2025-11-06",
                notes="تم فحص الدينمو",
            )
        ]

        # ------------------- المولدات -------------------
        gens_supply = [
            models.GeneratorSupply(
                code="GEN001",
                gType="30kVA",
                model="FG Wilson",
                prevSite="المستودع المركزي",
                supDate="2025-10-30",
                supplier="Yemen Mobile",
                vendor="PowerMax",
                notes="مولد جديد",
            ),
            models.GeneratorSupply(
                code="GEN002",
                gType="20kVA",
                model="Perkins",
                prevSite="فرع إب",
                supDate="2025-10-29",
                supplier="Yemen Mobile",
                vendor="EnergyTech",
                notes="مولد مستخدم",
            ),
            models.GeneratorSupply(
                code="GEN003",
                gType="15kVA",
                model="Deutz",
                prevSite="فرع تعز",
                supDate="2025-10-27",
                supplier="Yemen Mobile",
                vendor="DieselPro",
                notes="مولد مؤهل",
            ),
        ]

        gens_issue = [
            models.GeneratorIssue(
                code="GEN001",
                issueDate="2025-11-01",
                receiver="موقع ذمار",
                requester="قسم الطاقة",
                currSite="ذمار",
                notes="سليم",
            )
        ]

        gens_inspect = [
            models.GeneratorInspect(
                code="GEN002",
                inspector="فريق الفحص",
                elecRehab="نعم",
                rehabDate="2025-11-02",
                rehabUp="نعم",
                checkUp="نعم",
                notes="تم الرفع للنظام",
            )
        ]

        s.add_all(engines_supply)
        s.add_all(engines_issue)
        s.add_all(engines_rehab)
        s.add_all(engines_check)
        s.add_all(engines_upload)
        s.add_all(engines_lathe)
        s.add_all(engines_pump)
        s.add_all(engines_electrical)

        s.add_all(gens_supply)
        s.add_all(gens_issue)
        s.add_all(gens_inspect)

        s.commit()
        print("✅ تم إدخال بيانات تجريبية بنجاح.")


if __name__ == "__main__":
    # تشغيل يدوي: python -m app.seed_demo_data
    seed()
