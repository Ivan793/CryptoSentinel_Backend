from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.api.routes import projects, rules, scans, findings, crypto_keys, security_events

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(projects.router)
app.include_router(rules.router)
app.include_router(scans.router)
app.include_router(findings.router)
app.include_router(crypto_keys.router)
app.include_router(security_events.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}