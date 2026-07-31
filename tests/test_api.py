"""
Integration tests for the FastAPI endpoints. These hit the real
app (and real database) using FastAPI's TestClient -- make sure
Postgres is running and reachable before running these.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_transactions_returns_paginated_results():
    response = client.get("/transactions?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert len(data["results"]) <= 5


def test_transaction_stats_summary_has_expected_fields():
    response = client.get("/transactions/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_transactions" in data
    assert "fraud_count" in data
    assert "fraud_rate_percent" in data


def test_score_endpoint_returns_valid_response():
    payload = {
        "card_id": "test_card_001",
        "merchant": "Test Merchant",
        "merchant_category": "crypto_exchange",
        "amount": 5000.0,
        "currency": "USD",
        "country": "RU",
    }
    response = client.post("/transactions/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "fraud_score" in data
    assert "predicted_fraud" in data
    assert "explanation" in data
    assert isinstance(data["explanation"], list)


def test_get_nonexistent_transaction_returns_404():
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/transactions/{fake_id}")
    assert response.status_code == 404