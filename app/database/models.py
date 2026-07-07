"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.database.connection import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), unique=True, index=True, nullable=False)
    preferred_airline = Column(String(128), default="")
    favourite_hotel_type = Column(String(128), default="")
    travel_style = Column(String(128), default="")
    budget_range = Column(String(64), default="")
    previous_destinations = Column(JSONB, default=list)
    budget_history = Column(JSONB, default=list)
    extra_preferences = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), index=True, nullable=False)
    thread_id = Column(String(128), index=True, nullable=False)
    summary = Column(Text, nullable=False)
    destinations = Column(JSONB, default=list)
    topics = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class TripRecord(Base):
    __tablename__ = "trip_records"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(String(128), index=True, nullable=False)
    thread_id = Column(String(128), index=True, nullable=False)
    user_query = Column(Text, nullable=False)
    destination = Column(String(256), default="")
    flight_results = Column(Text, default="")
    hotel_results = Column(Text, default="")
    budget_results = Column(Text, default="")
    attraction_results = Column(Text, default="")
    travel_tips_results = Column(Text, default="")
    itinerary = Column(Text, default="")
    final_response = Column(Text, default="")
    structured_output = Column(JSONB, default=dict)
    confidence_score = Column(Float, default=0.0)
    is_favourite = Column(Boolean, default=False)
    llm_calls = Column(Integer, default=0)
    agents_run = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), index=True, nullable=False)
    query = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
