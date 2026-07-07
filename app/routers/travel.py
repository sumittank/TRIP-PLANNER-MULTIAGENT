"""Travel planning API endpoints."""

import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.travel import ChatRequest, ChatResponse, PlanTripRequest, PlanTripResponse
from app.services.travel_service import TravelService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Travel"])


@router.post("/plan-trip", response_model=PlanTripResponse)
def plan_trip(request: PlanTripRequest, db: Session = Depends(get_db)):
    service = TravelService(db)
    return service.plan_trip(request)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    service = TravelService(db)
    plan_request = PlanTripRequest(
        query=request.message,
        user_id=request.user_id,
        thread_id=request.thread_id,
    )
    result = service.plan_trip(plan_request)
    return ChatResponse(
        response=result.final_response,
        trip_id=result.trip_id,
        confidence_score=result.confidence_score,
    )


@router.post("/plan-trip/stream")
def plan_trip_stream(request: PlanTripRequest, db: Session = Depends(get_db)):
    service = TravelService(db)

    def event_generator():
        for chunk in service.stream_trip(request):
            yield f"data: {json.dumps(chunk, default=str)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
