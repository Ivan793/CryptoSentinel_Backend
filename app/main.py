from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes import (
    crypto_keys,
    findings,
    projects,
    reports,
    rules,
    scans,
    security_events,
)
from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.services.rule_sync import sync_rules


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Al arrancar, deja el catálogo de reglas del código reflejado en la tabla rules.
    with SessionLocal() as db:
        sync_rules(db)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

for router in (
    projects.router,
    rules.router,
    scans.router,
    findings.router,
    crypto_keys.router,
    security_events.router,
    reports.router,
):
    app.include_router(router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}