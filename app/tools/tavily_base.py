"""Shared Tavily search helper."""

from app.config.settings import get_settings
from app.utils.cache import search_cache
from app.utils.retry import retry_call
from tavily import TavilyClient


def _get_client() -> TavilyClient:
    settings = get_settings()
    return TavilyClient(api_key=settings.tavily_api_key)


def tavily_search(query: str, max_results: int = 5) -> str:
    cache_key = f"tavily:{query}:{max_results}"
    cached = search_cache.get(cache_key)
    if cached:
        return cached

    def _search() -> str:
        client = _get_client()
        response = client.search(query=query, max_results=max_results)
        results = []
        for i, item in enumerate(response.get("results", []), 1):
            title = item.get("title", "Unknown")
            url = item.get("url", "")
            snippet = item.get("content", "").strip()
            if len(snippet) > 300:
                snippet = snippet[:300].rsplit(" ", 1)[0] + "..."
            results.append(f"{i}. **{title}**\n   {url}\n   {snippet}")
        return "\n\n".join(results) if results else "No results found."

    result = retry_call(_search, max_retries=3)
    search_cache.set(cache_key, result)
    return result
