"""Travel tips search tool using Tavily."""

from langchain_core.tools import tool

from app.tools.tavily_base import tavily_search


@tool
def travel_tips_search_tool(query: str) -> str:
    """Search for travel tips, local customs, safety advice, and practical information."""
    return tavily_search(f"Travel tips safety customs practical advice for {query}", max_results=5)
