"""Basic tests for AI Travel Planner."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert data["version"] == "2.0.0"


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_planner_page():
    response = client.get("/planner")
    assert response.status_code == 200


def test_about_page():
    response = client.get("/about")
    assert response.status_code == 200


def test_saved_page():
    response = client.get("/saved-page")
    assert response.status_code == 200


def test_settings_page():
    response = client.get("/settings-page")
    assert response.status_code == 200


def test_history_page():
    response = client.get("/history-page")
    assert response.status_code == 200


def test_static_css():
    response = client.get("/static/css/style.css")
    assert response.status_code == 200


def test_static_api_js():
    response = client.get("/static/js/api.js")
    assert response.status_code == 200


def test_get_preferences():
    response = client.get("/api/preferences?user_id=test_user")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test_user"


def test_get_history_empty():
    response = client.get("/api/history?user_id=nonexistent_user_xyz")
    assert response.status_code == 200
    data = response.json()
    assert "trips" in data


def test_get_analytics():
    response = client.get("/api/analytics?user_id=test_user")
    assert response.status_code == 200
    data = response.json()
    assert "total_trips" in data


def test_plan_trip_validation():
    response = client.post("/api/plan-trip", json={"query": "ab"})
    assert response.status_code == 422


def test_trip_not_found():
    response = client.get("/api/trip/nonexistent-trip-id")
    assert response.status_code == 404
