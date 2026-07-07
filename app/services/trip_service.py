"""Trip history and export services."""

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.database.repositories import SearchHistoryRepository, TripRepository
from app.schemas.travel import AnalyticsResponse, HistoryResponse, TripDetail, TripSummary
from app.utils.exceptions import NotFoundError


class TripService:
    def __init__(self, db: Session):
        self.db = db
        self.trip_repo = TripRepository(db)

    def get_history(self, user_id: str, limit: int = 50) -> HistoryResponse:
        trips = self.trip_repo.list_by_user(user_id, limit)
        summaries = [
            TripSummary(
                trip_id=t.trip_id,
                user_id=t.user_id,
                user_query=t.user_query,
                destination=t.destination or "",
                confidence_score=t.confidence_score or 0.0,
                is_favourite=t.is_favourite or False,
                agents_run=t.agents_run or [],
                created_at=t.created_at,
            )
            for t in trips
        ]
        return HistoryResponse(trips=summaries, total=len(summaries))

    def get_trip(self, trip_id: str) -> TripDetail:
        trip = self.trip_repo.get_by_trip_id(trip_id)
        if not trip:
            raise NotFoundError(f"Trip {trip_id} not found")
        return TripDetail(
            trip_id=trip.trip_id,
            user_id=trip.user_id,
            user_query=trip.user_query,
            destination=trip.destination or "",
            confidence_score=trip.confidence_score or 0.0,
            is_favourite=trip.is_favourite or False,
            agents_run=trip.agents_run or [],
            created_at=trip.created_at,
            flight_results=trip.flight_results or "",
            hotel_results=trip.hotel_results or "",
            budget_results=trip.budget_results or "",
            attraction_results=trip.attraction_results or "",
            travel_tips_results=trip.travel_tips_results or "",
            itinerary=trip.itinerary or "",
            final_response=trip.final_response or "",
            structured_output=trip.structured_output or {},
            llm_calls=trip.llm_calls or 0,
        )

    def delete_trip(self, trip_id: str) -> bool:
        if not self.trip_repo.delete(trip_id):
            raise NotFoundError(f"Trip {trip_id} not found")
        return True

    def toggle_favourite(self, trip_id: str) -> TripDetail:
        trip = self.trip_repo.toggle_favourite(trip_id)
        if not trip:
            raise NotFoundError(f"Trip {trip_id} not found")
        return self.get_trip(trip_id)

    def get_favourites(self, user_id: str) -> HistoryResponse:
        trips = self.trip_repo.list_favourites(user_id)
        summaries = [
            TripSummary(
                trip_id=t.trip_id,
                user_id=t.user_id,
                user_query=t.user_query,
                destination=t.destination or "",
                confidence_score=t.confidence_score or 0.0,
                is_favourite=True,
                agents_run=t.agents_run or [],
                created_at=t.created_at,
            )
            for t in trips
        ]
        return HistoryResponse(trips=summaries, total=len(summaries))


class ExportService:
    @staticmethod
    def to_json(trip: TripDetail) -> str:
        return json.dumps(trip.model_dump(), indent=2, default=str)

    @staticmethod
    def to_markdown(trip: TripDetail) -> str:
        return f"""# Travel Plan — {trip.destination or 'Trip'}

**Query:** {trip.user_query}
**Generated:** {trip.created_at}
**Confidence:** {trip.confidence_score:.0%}
**Trip ID:** {trip.trip_id}

---

## Flights
{trip.flight_results or 'N/A'}

## Hotels
{trip.hotel_results or 'N/A'}

## Budget
{trip.budget_results or 'N/A'}

## Attractions
{trip.attraction_results or 'N/A'}

## Travel Tips
{trip.travel_tips_results or 'N/A'}

## Itinerary
{trip.itinerary or 'N/A'}

---

## Final Plan
{trip.final_response or 'N/A'}

---
*LLM Calls: {trip.llm_calls} | Agents: {', '.join(trip.agents_run)}*
"""

    @staticmethod
    def compare_plans(trip_a: TripDetail, trip_b: TripDetail) -> dict:
        return {
            "trip_a": {"id": trip_a.trip_id, "destination": trip_a.destination, "confidence": trip_a.confidence_score},
            "trip_b": {"id": trip_b.trip_id, "destination": trip_b.destination, "confidence": trip_b.confidence_score},
            "comparison": {
                "confidence_diff": trip_a.confidence_score - trip_b.confidence_score,
                "same_destination": trip_a.destination == trip_b.destination,
                "recommended": trip_a.trip_id if trip_a.confidence_score >= trip_b.confidence_score else trip_b.trip_id,
            },
        }


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.trip_repo = TripRepository(db)
        self.search_repo = SearchHistoryRepository(db)

    def get_analytics(self, user_id: str) -> AnalyticsResponse:
        trips = self.trip_repo.list_by_user(user_id, limit=100)
        favourites = self.trip_repo.list_favourites(user_id)
        searches = self.search_repo.list_by_user(user_id, limit=100)

        destinations = []
        confidences = []
        for trip in trips:
            if trip.destination:
                destinations.append(trip.destination)
            if trip.confidence_score:
                confidences.append(trip.confidence_score)

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        return AnalyticsResponse(
            total_trips=len(trips),
            favourite_trips=len(favourites),
            total_searches=len(searches),
            recent_destinations=list(dict.fromkeys(destinations))[:10],
            average_confidence=round(avg_conf, 2),
        )
