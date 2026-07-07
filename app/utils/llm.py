"""Shared LLM instance factory."""

from functools import lru_cache

from langchain_groq import ChatGroq

from app.config.settings import get_settings


@lru_cache
def get_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key or None,
        temperature=0.3,
    )
