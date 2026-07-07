"""Trip history and export endpoints."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.travel import ComparePlansRequest, HistoryResponse, TripDetail
from app.services.trip_service import ExportService, TripService

router = APIRouter(prefix="/api", tags=["History"])


@router.get("/history", response_model=HistoryResponse)
def get_history(user_id: str = Query(default="default_user"), db: Session = Depends(get_db)):
    return TripService(db).get_history(user_id)


@router.get("/trip/{trip_id}", response_model=TripDetail)
def get_trip(trip_id: str, db: Session = Depends(get_db)):
    return TripService(db).get_trip(trip_id)


@router.delete("/history/{trip_id}")
def delete_trip(trip_id: str, db: Session = Depends(get_db)):
    TripService(db).delete_trip(trip_id)
    return {"message": "Trip deleted successfully"}


@router.get("/saved", response_model=HistoryResponse)
def get_saved_trips(user_id: str = Query(default="default_user"), db: Session = Depends(get_db)):
    return TripService(db).get_favourites(user_id)


@router.post("/trip/{trip_id}/favourite", response_model=TripDetail)
def toggle_favourite(trip_id: str, db: Session = Depends(get_db)):
    return TripService(db).toggle_favourite(trip_id)


@router.get("/trip/{trip_id}/export/json")
def export_json(trip_id: str, db: Session = Depends(get_db)):
    trip = TripService(db).get_trip(trip_id)
    content = ExportService.to_json(trip)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=trip_{trip_id}.json"},
    )


@router.get("/trip/{trip_id}/export/markdown")
def export_markdown(trip_id: str, db: Session = Depends(get_db)):
    trip = TripService(db).get_trip(trip_id)
    content = ExportService.to_markdown(trip)
    return PlainTextResponse(
        content=content,
        headers={"Content-Disposition": f"attachment; filename=trip_{trip_id}.md"},
    )


@router.post("/compare")
def compare_plans(request: ComparePlansRequest, db: Session = Depends(get_db)):
    service = TripService(db)
    trip_a = service.get_trip(request.trip_id_a)
    trip_b = service.get_trip(request.trip_id_b)
    return ExportService.compare_plans(trip_a, trip_b)
