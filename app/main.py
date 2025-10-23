# C:\Workshop-System\backend\app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from . import auth

# إن كانت هذه الراوترات موجودة لديك، سيعمل الاستيراد.
# لو لم تكن موجودة بعد، اتركها كما هي وسنضيفها لاحقًا.
from .routers import spares, engines, generators, search_export, exporter

app = FastAPI(
    title="Workshop Management API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS (اسمح من كل المصادر حالياً)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # ينشئ جدول users وباقي الجداول المسجّلة في الموديلات
    init_db()

@app.get("/")
def root():
    return {"ok": True, "service": "workshop-backend"}

@app.get("/api/health")
def health():
    return {"ok": True}

# تجميع المسارات تحت /api
app.include_router(auth.router,          prefix="/api")
app.include_router(spares.router,        prefix="/api")
app.include_router(engines.router,       prefix="/api")
app.include_router(generators.router,    prefix="/api")
app.include_router(search_export.router, prefix="/api")
app.include_router(exporter.router,      prefix="/api")
