"""Attractions search tool using Tavily."""

from langchain_core.tools import tool

from app.tools.tavily_base import tavily_search


@tool
def attractions_search_tool(query: str) -> str:
    """Search for tourist attractions and sightseeing spots near a destination."""
    return tavily_search(f"Top tourist attractions and sightseeing in {query}", max_results=5)
