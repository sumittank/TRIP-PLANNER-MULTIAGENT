"""User preferences service."""

from sqlalchemy.orm import Session

from app.database.repositories import PreferenceRepository
from app.schemas.travel import PreferencesResponse, PreferencesUpdate


class PreferenceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PreferenceRepository(db)

    def get_preferences(self, user_id: str) -> PreferencesResponse:
        pref = self.repo.get_or_create(user_id)
        return PreferencesResponse(
            user_id=pref.user_id,
            preferred_airline=pref.preferred_airline or "",
            favourite_hotel_type=pref.favourite_hotel_type or "",
            travel_style=pref.travel_style or "",
            budget_range=pref.budget_range or "",
            previous_destinations=pref.previous_destinations or [],
            budget_history=[str(b) for b in (pref.budget_history or [])],
            extra_preferences=pref.extra_preferences or {},
            updated_at=pref.updated_at,
        )

    def update_preferences(self, user_id: str, data: PreferencesUpdate) -> PreferencesResponse:
        update_dict = data.model_dump(exclude_none=True)
        self.repo.update(user_id, update_dict)
        return self.get_preferences(user_id)
