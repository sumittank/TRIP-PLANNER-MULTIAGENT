"""Conditional routing logic for LangGraph."""

from app.graph.state import TravelState

AGENT_NODE_MAP = {
    "flight": "flight_agent",
    "hotel": "hotel_agent",
    "budget": "budget_agent",
    "attraction": "attraction_agent",
    "travel_tips": "travel_tips_agent",
}


def route_after_supervisor(state: TravelState) -> str:
    active = state.get("active_agents", [])
    if not active:
        return "parallel_executor"
    return "parallel_executor"


def route_after_critic(state: TravelState) -> str:
    confidence = state.get("confidence_score", 0.0)
    needs_reflection = state.get("needs_reflection", False)
    retry_count = state.get("retry_count", 0)

    if needs_reflection and retry_count < 2 and confidence < 0.7:
        return "reflection"
    return "response_formatter"


def route_after_reflection(state: TravelState) -> str:
    return "response_formatter"


def validate_state(state: TravelState) -> TravelState:
    """Ensure required state fields have defaults."""
    defaults: dict = {
        "user_query": "",
        "user_id": "default_user",
        "thread_id": "default_thread",
        "memories": "",
        "active_agents": [],
        "destination": "",
        "flight_results": "",
        "hotel_results": "",
        "budget_results": "",
        "attraction_results": "",
        "restaurant_results": "",
        "travel_tips_results": "",
        "weather_results": "",
        "itinerary": "",
        "critic_feedback": "",
        "reflection_notes": "",
        "confidence_score": 0.0,
        "final_response": "",
        "structured_output": {},
        "packing_checklist": "",
        "travel_checklist": "",
        "llm_calls": 0,
        "errors": [],
        "retry_count": 0,
        "needs_reflection": False,
        "agents_completed": [],
    }
    for key, default in defaults.items():
        if key not in state or state[key] is None:
            state[key] = default
    if "messages" not in state:
        state["messages"] = []
    return state
