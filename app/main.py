from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import spares, engines, generators, search_export, exporter

app = FastAPI(
    title="Workshop Management API (No Auth Mode)",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# السماح بالوصول من أي مصدر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def home():
    return {"ok": True, "mode": "no-auth", "msg": "Workshop system running without login"}

@app.get("/api/health")
def health():
    return {"ok": True}

# تضمين جميع المسارات الأخرى
app.include_router(spares.router,       prefix="/api")
app.include_router(engines.router,      prefix="/api")
app.include_router(generators.router,   prefix="/api")
app.include_router(search_export.router, prefix="/api")
app.include_router(exporter.router,     prefix="/api")
