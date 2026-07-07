"""Flight search tool using AviationStack API."""

import re

import requests
from langchain_core.tools import tool

from app.config.settings import get_settings
from app.utils.retry import retry_call


def _parse_flight_query(query: str) -> dict[str, str]:
    """Extract origin/destination hints from natural language query."""
    patterns = [
        r"from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+)",
        r"([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)\s+(?:trip|travel|flight)",
    ]
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return {"dep_iata": match.group(1).strip()[:3].upper(), "arr_iata": match.group(2).strip()[:3].upper()}
    return {}


def _search_flights_api(query: str) -> str:
    settings = get_settings()
    url = "https://api.aviationstack.com/v1/flights"
    params: dict[str, str | int] = {"access_key": settings.aviationstack_api_key, "limit": 5}

    parsed = _parse_flight_query(query)
    if parsed.get("dep_iata") and len(parsed["dep_iata"]) == 3:
        params["dep_iata"] = parsed["dep_iata"]
    if parsed.get("arr_iata") and len(parsed["arr_iata"]) == 3:
        params["arr_iata"] = parsed["arr_iata"]

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    flights = []
    for flight in data.get("data", [])[:5]:
        airline = flight.get("airline", {}).get("name", "Unknown")
        flight_num = flight.get("flight", {}).get("iata", "N/A")
        departure = flight.get("departure", {})
        arrival = flight.get("arrival", {})
        dep_airport = departure.get("airport", "Unknown")
        arr_airport = arrival.get("airport", "Unknown")
        dep_iata = departure.get("iata", "")
        arr_iata = arrival.get("iata", "")
        status = flight.get("flight_status", "Unknown")
        flights.append(
            f"Airline: {airline} ({flight_num})\n"
            f"Route: {dep_airport} ({dep_iata}) → {arr_airport} ({arr_iata})\n"
            f"Status: {status}"
        )

    if not flights:
        return "No flights found. Try specifying origin and destination (e.g., 'flights from DEL to BOM')."
    return "\n\n".join(flights)


@tool
def flight_search_tool(query: str) -> str:
    """Search for flights using AviationStack. Input should describe route or travel request."""
    return retry_call(lambda: _search_flights_api(query), max_retries=3)
