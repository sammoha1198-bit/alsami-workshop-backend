from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import spares, engines, generators, search_export, exporter
from . import auth


# ===== إنشاء التطبيق أولاً =====
app = FastAPI(
    title="Workshop Management API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Startup =====
@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/api/health")
def health():
    return {"ok": True}

# ===== تضمين الراوترات (بعد إنشاء app) =====
app.include_router(spares.router,       prefix="/api")
app.include_router(engines.router,      prefix="/api")
app.include_router(generators.router,   prefix="/api")
app.include_router(search_export.router, prefix="/api")
app.include_router(exporter.router,     prefix="/api")
app.include_router(auth.router, prefix="/api")