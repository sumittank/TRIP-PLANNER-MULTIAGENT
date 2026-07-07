"""Restaurant search tool using Tavily."""

from langchain_core.tools import tool

from app.tools.tavily_base import tavily_search


@tool
def restaurant_search_tool(query: str) -> str:
    """Search for restaurant recommendations and local cuisine at a destination."""
    return tavily_search(f"Best restaurants and local food in {query}", max_results=5)
