"""Hotel search tool using Tavily."""

from langchain_core.tools import tool

from app.tools.tavily_base import tavily_search


@tool
def hotel_search_tool(query: str) -> str:
    """Search for hotels and accommodation options. Input should describe destination and preferences."""
    return tavily_search(f"Best hotels and accommodation for {query}", max_results=5)
