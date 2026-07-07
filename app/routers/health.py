"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.database.connection import get_db
from app.schemas.travel import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    settings = get_settings()
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.app_version,
        database=db_status,
        services={
            "groq": "configured" if settings.groq_api_key else "missing_key",
            "tavily": "configured" if settings.tavily_api_key else "missing_key",
            "aviationstack": "configured" if settings.aviationstack_api_key else "missing_key",
        },
    )
