from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_actuator_index():
    response = client.get("/actuator")
    assert response.status_code == 200
    data = response.json()
    assert "links" in data
    assert "self" in data["links"]
    assert "health" in data["links"]
    assert "info" in data["links"]
    assert "metrics" in data["links"]


def test_actuator_health():
    response = client.get("/actuator/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["components"]["ping"]["status"] == "UP"
    assert data["components"]["diskSpace"]["status"] == "UP"


def test_actuator_liveness_and_readiness():
    liveness = client.get("/actuator/health/liveness")
    readiness = client.get("/actuator/health/readiness")
    assert liveness.status_code == 200
    assert liveness.json() == {"status": "UP"}
    assert readiness.status_code == 200
    assert readiness.json() == {"status": "UP"}


def test_actuator_info():
    response = client.get("/actuator/info")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "python_version" in data["app"]


def test_actuator_metrics():
    response = client.get("/actuator/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "process.uptime" in data["names"]
    assert len(data["measurements"]) == 1