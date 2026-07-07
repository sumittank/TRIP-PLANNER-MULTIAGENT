"""Pydantic request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PlanTripRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    user_id: str = Field(default="default_user", max_length=128)
    thread_id: str | None = Field(default=None, max_length=128)
    regenerate: bool = False


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    user_id: str = Field(default="default_user", max_length=128)
    thread_id: str | None = Field(default=None, max_length=128)


class ComparePlansRequest(BaseModel):
    trip_id_a: str
    trip_id_b: str


class PreferencesUpdate(BaseModel):
    preferred_airline: str | None = None
    favourite_hotel_type: str | None = None
    travel_style: str | None = None
    budget_range: str | None = None
    previous_destinations: list[str] | None = None
    budget_history: list[str] | None = None
    extra_preferences: dict[str, Any] | None = None


class PreferencesResponse(BaseModel):
    user_id: str
    preferred_airline: str = ""
    favourite_hotel_type: str = ""
    travel_style: str = ""
    budget_range: str = ""
    previous_destinations: list[str] = Field(default_factory=list)
    budget_history: list[str] = Field(default_factory=list)
    extra_preferences: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime | None = None


class TripSummary(BaseModel):
    trip_id: str
    user_id: str
    user_query: str
    destination: str = ""
    confidence_score: float = 0.0
    is_favourite: bool = False
    agents_run: list[str] = Field(default_factory=list)
    created_at: datetime


class TripDetail(TripSummary):
    flight_results: str = ""
    hotel_results: str = ""
    budget_results: str = ""
    attraction_results: str = ""
    travel_tips_results: str = ""
    itinerary: str = ""
    final_response: str = ""
    structured_output: dict[str, Any] = Field(default_factory=dict)
    llm_calls: int = 0


class PlanTripResponse(BaseModel):
    trip_id: str
    final_response: str
    confidence_score: float
    agents_run: list[str]
    structured_output: dict[str, Any]
    flight_results: str = ""
    hotel_results: str = ""
    budget_results: str = ""
    attraction_results: str = ""
    travel_tips_results: str = ""
    itinerary: str = ""
    llm_calls: int = 0
    packing_checklist: str = ""
    travel_checklist: str = ""


class ChatResponse(BaseModel):
    response: str
    trip_id: str | None = None
    confidence_score: float = 0.0


class HistoryResponse(BaseModel):
    trips: list[TripSummary]
    total: int


class AnalyticsResponse(BaseModel):
    total_trips: int
    favourite_trips: int
    total_searches: int
    recent_destinations: list[str]
    average_confidence: float


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    services: dict[str, str]


class ErrorResponse(BaseModel):
    detail: str
    status_code: int = 500
