"""Weather search tool using Tavily."""

from langchain_core.tools import tool

from app.tools.tavily_base import tavily_search


@tool
def weather_search_tool(query: str) -> str:
    """Search for weather forecasts and seasonal climate information for a destination."""
    return tavily_search(f"Weather forecast climate best time to visit {query}", max_results=5)
