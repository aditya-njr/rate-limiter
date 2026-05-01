import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_simulate_token_bucket(client: TestClient):
    body = {
        "algorithm": "tokenBucket",
        "clientId": "c1",
        "requestCount": 3,
        "intervalMs": 0,
        "config": {"capacity": 2, "refillPerSecond": 1},
    }
    r = client.post("/api/simulate", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["summary"]["total"] == 3
    assert data["summary"]["allowed"] == 2
    assert data["summary"]["rejected"] == 1


def test_try_then_429(client: TestClient):
    body = {
        "algorithm": "fixedWindow",
        "clientId": "c2",
        "config": {"windowMs": 1000, "maxRequests": 1},
        "nowMs": 0,
    }
    r1 = client.post("/api/try", json=body)
    assert r1.status_code == 200
    r2 = client.post("/api/try", json=body)
    assert r2.status_code == 429


def test_reset(client: TestClient):
    body_try = {
        "algorithm": "fixedWindow",
        "clientId": "c3",
        "config": {"windowMs": 1000, "maxRequests": 1},
        "nowMs": 0,
    }
    client.post("/api/try", json=body_try)
    r = client.post("/api/reset", json={"clientId": "c3"})
    assert r.status_code == 200
    assert r.json()["removed"] >= 1


def test_validation_error_shape(client: TestClient):
    r = client.post(
        "/api/simulate",
        json={"algorithm": "tokenBucket", "clientId": "x", "requestCount": 1},
    )
    assert r.status_code == 400
    err = r.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert err["message"] == "Invalid request body"
    assert "details" in err
