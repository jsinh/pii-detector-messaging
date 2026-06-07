from fastapi.testclient import TestClient

from pii_detector.api.app import create_app

client = TestClient(create_app())


def test_healthz_reports_ok():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_reports_ready():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
