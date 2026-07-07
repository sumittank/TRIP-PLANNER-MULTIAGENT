"""LangGraph workflow builder."""

import logging
from functools import lru_cache

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from app.agents.travel_agents import (
    critic_agent,
    error_recovery_node,
    memory_retrieval_node,
    parallel_executor,
    reflection_agent,
    response_formatter,
    supervisor_agent,
)
from app.graph.routing import route_after_critic, route_after_supervisor, validate_state
from app.graph.state import TravelState
from app.memory.checkpointer import get_checkpointer

logger = logging.getLogger(__name__)


def _validate_node(state: TravelState) -> dict:
    validate_state(state)
    return {}


def build_travel_graph() -> StateGraph:
    graph = StateGraph(TravelState)

    graph.add_node("validate", _validate_node)
    graph.add_node("memory_retrieval", memory_retrieval_node)
    graph.add_node("supervisor", supervisor_agent)
    graph.add_node("parallel_executor", parallel_executor)
    graph.add_node("error_recovery", error_recovery_node)
    graph.add_node("critic", critic_agent)
    graph.add_node("reflection", reflection_agent)
    graph.add_node("response_formatter", response_formatter)

    graph.add_edge(START, "validate")
    graph.add_edge("validate", "memory_retrieval")
    graph.add_edge("memory_retrieval", "supervisor")
    graph.add_conditional_edges("supervisor", route_after_supervisor, {"parallel_executor": "parallel_executor"})
    graph.add_edge("parallel_executor", "error_recovery")
    graph.add_edge("error_recovery", "critic")
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {"reflection": "reflection", "response_formatter": "response_formatter"},
    )
    graph.add_edge("reflection", "response_formatter")
    graph.add_edge("response_formatter", END)

    return graph


@lru_cache
def get_compiled_graph():
    graph = build_travel_graph()
    checkpointer = get_checkpointer()
    compiled = graph.compile(checkpointer=checkpointer)
    logger.info("Travel planning graph compiled with checkpointing")
    return compiled


def create_initial_state(
    user_query: str,
    user_id: str = "default_user",
    thread_id: str = "default_thread",
    memories: str = "",
) -> dict:
    return {
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "user_id": user_id,
        "thread_id": thread_id,
        "memories": memories,
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
