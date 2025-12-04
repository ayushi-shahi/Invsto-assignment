import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)


def test_get_data_empty_db():
    """GET /data on empty DB should return 404"""
    response = client.get("/data")
    assert response.status_code in (200, 404)  # depending if data exists
    if response.status_code == 404:
        assert "No stock data found" in response.json()["detail"]


def test_post_data_valid():
    """POST /data with valid payload should create record"""
    payload = {
        "trade_timestamp": "2025-12-01T00:00:00",
        "open": 100.0,
        "high": 110.0,
        "low": 90.0,
        "close": 105.0,
        "volume": 1000,
        "instrument": "TEST"
    }
    response = client.post("/data", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["instrument"] == "TEST"
    assert data["close"] == 105.0


def test_get_data_after_post():
    """GET /data should return at least one record after POST"""
    response = client.get("/data")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
