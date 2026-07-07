"""Repository pattern for database access."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.database.models import ConversationSummary, SearchHistory, TripRecord, UserPreference


class PreferenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> UserPreference | None:
        return self.db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    def get_or_create(self, user_id: str) -> UserPreference:
        pref = self.get_by_user_id(user_id)
        if pref:
            return pref
        pref = UserPreference(user_id=user_id)
        self.db.add(pref)
        self.db.commit()
        self.db.refresh(pref)
        return pref

    def update(self, user_id: str, data: dict[str, Any]) -> UserPreference:
        pref = self.get_or_create(user_id)
        for key, value in data.items():
            if hasattr(pref, key) and value is not None:
                setattr(pref, key, value)
        pref.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(pref)
        return pref


class TripRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict[str, Any]) -> TripRecord:
        payload = dict(data)
        trip_id = payload.pop("trip_id", None) or str(uuid4())
        trip = TripRecord(trip_id=trip_id, **payload)
        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)
        return trip

    def get_by_trip_id(self, trip_id: str) -> TripRecord | None:
        return self.db.query(TripRecord).filter(TripRecord.trip_id == trip_id).first()

    def list_by_user(self, user_id: str, limit: int = 50) -> list[TripRecord]:
        return (
            self.db.query(TripRecord)
            .filter(TripRecord.user_id == user_id)
            .order_by(TripRecord.created_at.desc())
            .limit(limit)
            .all()
        )

    def list_favourites(self, user_id: str) -> list[TripRecord]:
        return (
            self.db.query(TripRecord)
            .filter(TripRecord.user_id == user_id, TripRecord.is_favourite.is_(True))
            .order_by(TripRecord.created_at.desc())
            .all()
        )

    def delete(self, trip_id: str) -> bool:
        trip = self.get_by_trip_id(trip_id)
        if not trip:
            return False
        self.db.delete(trip)
        self.db.commit()
        return True

    def toggle_favourite(self, trip_id: str) -> TripRecord | None:
        trip = self.get_by_trip_id(trip_id)
        if not trip:
            return None
        trip.is_favourite = not trip.is_favourite
        self.db.commit()
        self.db.refresh(trip)
        return trip

    def count_by_user(self, user_id: str) -> int:
        return self.db.query(TripRecord).filter(TripRecord.user_id == user_id).count()


class MemoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_summary(
        self,
        user_id: str,
        thread_id: str,
        summary: str,
        destinations: list[str] | None = None,
        topics: list[str] | None = None,
    ) -> ConversationSummary:
        record = ConversationSummary(
            user_id=user_id,
            thread_id=thread_id,
            summary=summary,
            destinations=destinations or [],
            topics=topics or [],
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_recent_summaries(self, user_id: str, limit: int = 5) -> list[ConversationSummary]:
        return (
            self.db.query(ConversationSummary)
            .filter(ConversationSummary.user_id == user_id)
            .order_by(ConversationSummary.created_at.desc())
            .limit(limit)
            .all()
        )


class SearchHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, user_id: str, query: str) -> SearchHistory:
        record = SearchHistory(user_id=user_id, query=query)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_by_user(self, user_id: str, limit: int = 20) -> list[SearchHistory]:
        return (
            self.db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
            .all()
        )
