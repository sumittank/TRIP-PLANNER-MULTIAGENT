"""Travel planning business logic."""

import logging
from uuid import uuid4

from sqlalchemy.orm import Session

from app.graph.builder import create_initial_state, get_compiled_graph
from app.memory.summary import retrieve_memories, summarize_and_store
from app.schemas.travel import PlanTripRequest, PlanTripResponse

logger = logging.getLogger(__name__)


class TravelService:
    def __init__(self, db: Session):
        self.db = db
        self.graph = get_compiled_graph()

    def plan_trip(self, request: PlanTripRequest) -> PlanTripResponse:
        thread_id = request.thread_id or f"{request.user_id}_{uuid4().hex[:8]}"
        memories = retrieve_memories(self.db, request.user_id)

        initial_state = create_initial_state(
            user_query=request.query,
            user_id=request.user_id,
            thread_id=thread_id,
            memories=memories,
        )

        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(initial_state, config=config)

        trip_id = str(uuid4())
        response = PlanTripResponse(
            trip_id=trip_id,
            final_response=result.get("final_response", ""),
            confidence_score=result.get("confidence_score", 0.0),
            agents_run=result.get("agents_completed", result.get("active_agents", [])),
            structured_output=result.get("structured_output", {}),
            flight_results=result.get("flight_results", ""),
            hotel_results=result.get("hotel_results", ""),
            budget_results=result.get("budget_results", ""),
            attraction_results=result.get("attraction_results", ""),
            travel_tips_results=result.get("travel_tips_results", ""),
            itinerary=result.get("itinerary", ""),
            llm_calls=result.get("llm_calls", 0),
            packing_checklist=result.get("packing_checklist", ""),
            travel_checklist=result.get("travel_checklist", ""),
        )

        from app.database.repositories import SearchHistoryRepository, TripRepository

        trip_repo = TripRepository(self.db)
        trip_repo.create({
            "trip_id": trip_id,
            "user_id": request.user_id,
            "thread_id": thread_id,
            "user_query": request.query,
            "destination": result.get("destination", ""),
            "flight_results": response.flight_results,
            "hotel_results": response.hotel_results,
            "budget_results": response.budget_results,
            "attraction_results": response.attraction_results,
            "travel_tips_results": response.travel_tips_results,
            "itinerary": response.itinerary,
            "final_response": response.final_response,
            "structured_output": response.structured_output,
            "confidence_score": response.confidence_score,
            "llm_calls": response.llm_calls,
            "agents_run": response.agents_run,
        })

        search_repo = SearchHistoryRepository(self.db)
        search_repo.add(request.user_id, request.query)

        try:
            summarize_and_store(
                self.db,
                request.user_id,
                thread_id,
                request.query,
                response.final_response,
            )
        except Exception as exc:
            logger.warning("Memory summary failed: %s", exc)

        return response

    def stream_trip(self, request: PlanTripRequest):
        thread_id = request.thread_id or f"{request.user_id}_{uuid4().hex[:8]}"
        memories = retrieve_memories(self.db, request.user_id)
        initial_state = create_initial_state(
            user_query=request.query,
            user_id=request.user_id,
            thread_id=thread_id,
            memories=memories,
        )
        config = {"configurable": {"thread_id": thread_id}}
        for chunk in self.graph.stream(initial_state, config=config, stream_mode="updates"):
            yield chunk
