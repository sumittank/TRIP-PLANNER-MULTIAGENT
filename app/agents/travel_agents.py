"""Travel planning agent nodes."""

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.graph.state import TravelState
from app.prompts.templates import (
    CRITIC_PROMPT,
    ITINERARY_PROMPT,
    REFLECTION_PROMPT,
    RESPONSE_FORMATTER_PROMPT,
    STRUCTURED_OUTPUT_PROMPT,
    SUPERVISOR_PROMPT,
)
from app.tools import (
    attractions_search_tool,
    budget_search_tool,
    flight_search_tool,
    hotel_search_tool,
    restaurant_search_tool,
    travel_tips_search_tool,
    weather_search_tool,
)
from app.utils.llm import get_llm

logger = logging.getLogger(__name__)
llm = get_llm()


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


def _safe_tool_call(tool, query: str) -> str:
    try:
        return tool.invoke(query)
    except Exception as exc:
        logger.error("Tool %s failed: %s", tool.name, exc)
        return f"Error fetching data: {exc}"


def memory_retrieval_node(state: TravelState) -> dict:
    return {"messages": [AIMessage(content="Retrieved user travel memories")]}


def supervisor_agent(state: TravelState) -> dict:
    query = state["user_query"]
    memories = state.get("memories", "")

    prompt = f"{SUPERVISOR_PROMPT}\n\nUser memories:\n{memories}\n\nUser request:\n{query}"
    response = llm.invoke([SystemMessage(content="Route to appropriate agents."), HumanMessage(content=prompt)])
    data = _extract_json(response.content)

    agents = data.get("agents", [])
    if not agents:
        query_lower = query.lower()
        agents = []
        if any(w in query_lower for w in ["flight", "fly", "airline", "airport"]):
            agents.append("flight")
        if any(w in query_lower for w in ["hotel", "stay", "accommodation", "resort"]):
            agents.append("hotel")
        if any(w in query_lower for w in ["budget", "cost", "price", "₹", "$", "under"]):
            agents.append("budget")
        if any(w in query_lower for w in ["attraction", "sightseeing", "visit", "place", "tourist"]):
            agents.append("attraction")
        if any(w in query_lower for w in ["tip", "advice", "pack", "safety", "custom"]):
            agents.append("travel_tips")
        if not agents:
            agents = ["flight", "hotel", "budget", "attraction", "travel_tips"]

    destination = data.get("destination", "")
    reasoning = data.get("reasoning", "Routing based on query analysis")

    return {
        "active_agents": agents,
        "destination": destination,
        "messages": [AIMessage(content=f"Supervisor activated: {', '.join(agents)}. {reasoning}")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def _run_agent(name: str, state: TravelState) -> tuple[str, str, str]:
    query = state["user_query"]
    destination = state.get("destination") or query

    tool_map = {
        "flight": (flight_search_tool, "flight_results"),
        "hotel": (hotel_search_tool, "hotel_results"),
        "budget": (budget_search_tool, "budget_results"),
        "attraction": (attractions_search_tool, "attraction_results"),
        "travel_tips": (travel_tips_search_tool, "travel_tips_results"),
    }

    if name not in tool_map:
        return name, "", f"Unknown agent: {name}"

    tool, field = tool_map[name]
    result = _safe_tool_call(tool, query if name == "flight" else destination)

    extras = {}
    if name == "attraction":
        extras["restaurant_results"] = _safe_tool_call(restaurant_search_tool, destination)
        extras["weather_results"] = _safe_tool_call(weather_search_tool, destination)

    return name, result, field, extras


def parallel_executor(state: TravelState) -> dict:
    active = state.get("active_agents", [])
    updates: dict = {"agents_completed": [], "llm_calls": state.get("llm_calls", 0)}
    messages = []

    def run_single(agent_name: str) -> dict:
        query = state["user_query"]
        destination = state.get("destination") or query
        result_dict: dict = {"agents_completed": [agent_name]}

        if agent_name == "flight":
            result_dict["flight_results"] = _safe_tool_call(flight_search_tool, query)
        elif agent_name == "hotel":
            result_dict["hotel_results"] = _safe_tool_call(hotel_search_tool, destination)
        elif agent_name == "budget":
            result_dict["budget_results"] = _safe_tool_call(budget_search_tool, destination)
        elif agent_name == "attraction":
            result_dict["attraction_results"] = _safe_tool_call(attractions_search_tool, destination)
            result_dict["restaurant_results"] = _safe_tool_call(restaurant_search_tool, destination)
            result_dict["weather_results"] = _safe_tool_call(weather_search_tool, destination)
        elif agent_name == "travel_tips":
            result_dict["travel_tips_results"] = _safe_tool_call(travel_tips_search_tool, destination)

        return result_dict

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_single, name): name for name in active}
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                updates["agents_completed"].extend(result.pop("agents_completed", []))
                updates.update({k: v for k, v in result.items() if v})
                messages.append(AIMessage(content=f"{name} agent completed"))
            except Exception as exc:
                logger.error("Agent %s failed: %s", name, exc)
                updates.setdefault("errors", [])
                updates["errors"].append(f"{name}: {exc}")

    itinerary_prompt = f"""
    {ITINERARY_PROMPT}

    User Query: {state['user_query']}
    Memories: {state.get('memories', '')}
    Flights: {updates.get('flight_results', state.get('flight_results', ''))}
    Hotels: {updates.get('hotel_results', state.get('hotel_results', ''))}
    Budget: {updates.get('budget_results', state.get('budget_results', ''))}
    Attractions: {updates.get('attraction_results', state.get('attraction_results', ''))}
    Restaurants: {updates.get('restaurant_results', state.get('restaurant_results', ''))}
    Weather: {updates.get('weather_results', state.get('weather_results', ''))}
    Tips: {updates.get('travel_tips_results', state.get('travel_tips_results', ''))}
    """
    itinerary_response = llm.invoke([
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=itinerary_prompt),
    ])
    updates["itinerary"] = itinerary_response.content
    updates["llm_calls"] = updates["llm_calls"] + 1
    messages.append(AIMessage(content="Itinerary generated"))

    updates["messages"] = messages
    return updates


def critic_agent(state: TravelState) -> dict:
    collected = {
        "flights": state.get("flight_results", ""),
        "hotels": state.get("hotel_results", ""),
        "budget": state.get("budget_results", ""),
        "attractions": state.get("attraction_results", ""),
        "restaurants": state.get("restaurant_results", ""),
        "tips": state.get("travel_tips_results", ""),
        "weather": state.get("weather_results", ""),
        "itinerary": state.get("itinerary", ""),
    }

    prompt = f"{CRITIC_PROMPT}\n\nCollected data:\n{json.dumps(collected, indent=2)}"
    response = llm.invoke([SystemMessage(content="Critique the travel plan."), HumanMessage(content=prompt)])
    data = _extract_json(response.content)

    confidence = float(data.get("confidence_score", 0.75))
    approved = data.get("approved", confidence >= 0.6)
    issues = data.get("issues", [])
    suggestions = data.get("suggestions", [])

    feedback = f"Issues: {issues}. Suggestions: {suggestions}"

    return {
        "confidence_score": confidence,
        "critic_feedback": feedback,
        "needs_reflection": not approved,
        "messages": [AIMessage(content=f"Critic review complete. Confidence: {confidence:.2f}")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def reflection_agent(state: TravelState) -> dict:
    prompt = f"""
    {REFLECTION_PROMPT}

    Original query: {state['user_query']}
    Critic feedback: {state.get('critic_feedback', '')}
    Current itinerary: {state.get('itinerary', '')[:1500]}
    """
    response = llm.invoke([SystemMessage(content="Improve the travel plan."), HumanMessage(content=prompt)])
    data = _extract_json(response.content)

    improvements = data.get("improvements", [])
    revised = data.get("revised_sections", {})
    itinerary = state.get("itinerary", "")

    if revised.get("itinerary"):
        itinerary = revised["itinerary"]
    elif improvements:
        improve_prompt = f"Improve this itinerary based on: {improvements}\n\n{itinerary}"
        improved = llm.invoke([HumanMessage(content=improve_prompt)])
        itinerary = improved.content

    return {
        "itinerary": itinerary,
        "reflection_notes": "; ".join(improvements) if improvements else "Plan refined",
        "retry_count": state.get("retry_count", 0) + 1,
        "confidence_score": min(state.get("confidence_score", 0.5) + 0.15, 0.95),
        "needs_reflection": False,
        "messages": [AIMessage(content="Reflection and self-correction applied")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def response_formatter(state: TravelState) -> dict:
    prompt = f"""
    {RESPONSE_FORMATTER_PROMPT}

    User Query: {state['user_query']}
    User Memories: {state.get('memories', '')}
    Destination: {state.get('destination', '')}

    Flights:
    {state.get('flight_results', 'N/A')}

    Hotels:
    {state.get('hotel_results', 'N/A')}

    Budget:
    {state.get('budget_results', 'N/A')}

    Attractions:
    {state.get('attraction_results', 'N/A')}

    Restaurants:
    {state.get('restaurant_results', 'N/A')}

    Weather:
    {state.get('weather_results', 'N/A')}

    Travel Tips:
    {state.get('travel_tips_results', 'N/A')}

    Itinerary:
    {state.get('itinerary', 'N/A')}

    Critic Feedback:
    {state.get('critic_feedback', 'N/A')}

    Confidence Score: {state.get('confidence_score', 0.75)}
    """

    response = llm.invoke([
        SystemMessage(content="Format a comprehensive travel plan."),
        HumanMessage(content=prompt),
    ])

    structured_prompt = f"""
    {STRUCTURED_OUTPUT_PROMPT}

    Formatted response:
    {response.content[:3000]}
    """
    structured_response = llm.invoke([HumanMessage(content=structured_prompt)])
    structured = _extract_json(structured_response.content)

    if not structured:
        structured = {
            "destination": state.get("destination", ""),
            "confidence_score": state.get("confidence_score", 0.75),
            "flights": state.get("flight_results", ""),
            "hotels": state.get("hotel_results", ""),
            "budget_breakdown": state.get("budget_results", ""),
            "attractions": state.get("attraction_results", ""),
            "restaurants": state.get("restaurant_results", ""),
            "itinerary": state.get("itinerary", ""),
        }

    packing = structured.get("packing_checklist", "")
    if isinstance(packing, list):
        packing = "\n".join(f"- {item}" for item in packing)
    travel = structured.get("travel_checklist", "")
    if isinstance(travel, list):
        travel = "\n".join(f"- {item}" for item in travel)

    if not packing:
        packing = "- Passport/ID\n- Weather-appropriate clothing\n- Chargers and adapters\n- Medications\n- Travel insurance documents"
    if not travel:
        travel = "- Confirm flight bookings\n- Hotel reservation confirmation\n- Local currency/cards\n- Emergency contacts\n- Download offline maps"

    return {
        "final_response": response.content,
        "structured_output": structured,
        "packing_checklist": packing,
        "travel_checklist": travel,
        "messages": [AIMessage(content=response.content)],
        "llm_calls": state.get("llm_calls", 0) + 2,
    }


def error_recovery_node(state: TravelState) -> dict:
    errors = state.get("errors", [])
    if not errors:
        return {}
    recovery_msg = f"Recovered from errors: {'; '.join(errors)}. Proceeding with available data."
    return {
        "messages": [AIMessage(content=recovery_msg)],
        "errors": [],
    }
