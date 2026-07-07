"""LangGraph travel planning state definition."""

import operator
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage


class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    user_id: str
    thread_id: str
    memories: str
    active_agents: list[str]
    destination: str
    flight_results: str
    hotel_results: str
    budget_results: str
    attraction_results: str
    restaurant_results: str
    travel_tips_results: str
    weather_results: str
    itinerary: str
    critic_feedback: str
    reflection_notes: str
    confidence_score: float
    final_response: str
    structured_output: dict[str, Any]
    packing_checklist: str
    travel_checklist: str
    llm_calls: int
    errors: Annotated[list[str], operator.add]
    retry_count: int
    needs_reflection: bool
    agents_completed: Annotated[list[str], operator.add]
