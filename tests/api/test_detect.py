from fastapi.testclient import TestClient

from pii_detector.api.app import create_app

client = TestClient(create_app())


def test_detect_returns_entities_list():
    response = client.post("/detect", json={"text": "dm me at a@b.com"})
    assert response.status_code == 200
    # Pipeline is a stub today, so no entities yet — but the shape is stable.
    assert response.json() == {"entities": []}


def test_detect_rejects_empty_text():
    response = client.post("/detect", json={"text": ""})
    assert response.status_code == 422


def test_detect_rejects_missing_text():
    response = client.post("/detect", json={})
    assert response.status_code == 422
