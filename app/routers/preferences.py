"""User preferences endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.travel import AnalyticsResponse, PreferencesResponse, PreferencesUpdate
from app.services.preference_service import PreferenceService
from app.services.trip_service import AnalyticsService

router = APIRouter(prefix="/api", tags=["Preferences"])


@router.get("/preferences", response_model=PreferencesResponse)
def get_preferences(user_id: str = Query(default="default_user"), db: Session = Depends(get_db)):
    return PreferenceService(db).get_preferences(user_id)


@router.post("/preferences", response_model=PreferencesResponse)
def update_preferences(
    data: PreferencesUpdate,
    user_id: str = Query(default="default_user"),
    db: Session = Depends(get_db),
):
    return PreferenceService(db).update_preferences(user_id, data)


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(user_id: str = Query(default="default_user"), db: Session = Depends(get_db)):
    return AnalyticsService(db).get_analytics(user_id)
