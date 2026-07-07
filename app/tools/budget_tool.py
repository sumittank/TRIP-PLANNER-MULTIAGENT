"""Budget estimation tool using Tavily."""

from langchain_core.tools import tool

from app.tools.tavily_base import tavily_search


@tool
def budget_search_tool(query: str) -> str:
    """Search for trip cost estimates, budget breakdowns, and price information."""
    return tavily_search(f"Trip cost budget breakdown travel expenses for {query}", max_results=5)
