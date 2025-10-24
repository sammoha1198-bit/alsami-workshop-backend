from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ✅ الاستيراد الصحيح للدالة الموجودة في database.py
from .database import init_db

# الراوترات
from .routers import engines, generators, search_export, exporter

app = FastAPI(title="Workshop System", version="1.0")

# CORS للواجهة
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ إنشاء الجداول مرة واحدة
init_db()

# ✅ ربط الراوترات
app.include_router(engines.router)
app.include_router(generators.router)
app.include_router(search_export.router)
app.include_router(exporter.router)

# ✅ خدمة الواجهة الثابتة: افتح http://127.0.0.1:2000/static/index.html
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return {"service": "Workshop API", "status": "running", "static": "/static/index.html"}
