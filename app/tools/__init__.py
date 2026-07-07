"""Modular LangChain tools for travel search."""

from app.tools.flight_tool import flight_search_tool
from app.tools.hotel_tool import hotel_search_tool
from app.tools.attractions_tool import attractions_search_tool
from app.tools.restaurant_tool import restaurant_search_tool
from app.tools.travel_tips_tool import travel_tips_search_tool
from app.tools.budget_tool import budget_search_tool
from app.tools.weather_tool import weather_search_tool

ALL_TOOLS = [
    flight_search_tool,
    hotel_search_tool,
    attractions_search_tool,
    restaurant_search_tool,
    travel_tips_search_tool,
    budget_search_tool,
    weather_search_tool,
]

__all__ = [
    "flight_search_tool",
    "hotel_search_tool",
    "attractions_search_tool",
    "restaurant_search_tool",
    "travel_tips_search_tool",
    "budget_search_tool",
    "weather_search_tool",
    "ALL_TOOLS",
]
