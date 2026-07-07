"""Conversation summary generation and memory retrieval."""

import json
import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session

from app.database.repositories import MemoryRepository, PreferenceRepository
from app.prompts.templates import MEMORY_SUMMARY_PROMPT
from app.utils.llm import get_llm

logger = logging.getLogger(__name__)


def retrieve_memories(db: Session, user_id: str) -> str:
    """Build context string from user preferences and recent conversation summaries."""
    pref_repo = PreferenceRepository(db)
    mem_repo = MemoryRepository(db)

    pref = pref_repo.get_by_user_id(user_id)
    summaries = mem_repo.get_recent_summaries(user_id, limit=5)

    parts = []
    if pref:
        if pref.preferred_airline:
            parts.append(f"Preferred airline: {pref.preferred_airline}")
        if pref.favourite_hotel_type:
            parts.append(f"Favourite hotel type: {pref.favourite_hotel_type}")
        if pref.travel_style:
            parts.append(f"Travel style: {pref.travel_style}")
        if pref.budget_range:
            parts.append(f"Budget range: {pref.budget_range}")
        if pref.previous_destinations:
            parts.append(f"Previous destinations: {', '.join(pref.previous_destinations[:10])}")
        if pref.budget_history:
            parts.append(f"Budget history: {', '.join(str(b) for b in pref.budget_history[:5])}")

    for summary in summaries:
        parts.append(f"Past conversation: {summary.summary}")

    return "\n".join(parts) if parts else "No prior preferences stored."


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


def summarize_and_store(
    db: Session,
    user_id: str,
    thread_id: str,
    user_query: str,
    final_response: str,
) -> None:
    """Generate conversation summary and update user preferences."""
    llm = get_llm()
    prompt = f"{MEMORY_SUMMARY_PROMPT}\n\nUser query: {user_query}\n\nResponse: {final_response[:2000]}"
    response = llm.invoke([SystemMessage(content="Extract travel memory as JSON."), HumanMessage(content=prompt)])
    data = _extract_json(response.content)

    summary = data.get("summary", f"User planned: {user_query[:200]}")
    destinations = data.get("destinations", [])
    topics = data.get("topics", [])
    preferences = data.get("preferences", {})

    mem_repo = MemoryRepository(db)
    mem_repo.save_summary(user_id, thread_id, summary, destinations, topics)

    pref_repo = PreferenceRepository(db)
    pref = pref_repo.get_or_create(user_id)
    update_data: dict = {}

    if preferences.get("travel_style"):
        update_data["travel_style"] = preferences["travel_style"]
    if preferences.get("budget"):
        update_data["budget_range"] = preferences["budget"]
        history = list(pref.budget_history or [])
        history.append(preferences["budget"])
        update_data["budget_history"] = history[-10:]
    if preferences.get("hotel_type"):
        update_data["favourite_hotel_type"] = preferences["hotel_type"]
    if preferences.get("airline"):
        update_data["preferred_airline"] = preferences["airline"]
    if destinations:
        prev = list(pref.previous_destinations or [])
        for dest in destinations:
            if dest not in prev:
                prev.append(dest)
        update_data["previous_destinations"] = prev[-20:]

    if update_data:
        pref_repo.update(user_id, update_data)

    logger.info("Stored conversation summary for user %s", user_id)
