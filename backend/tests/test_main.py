from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home_returns_running_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "SmartLearn AI Backend is running"}


def test_db_endpoint_responds():
    response = client.get("/test-db")
    assert response.status_code == 200
    assert "message" in response.json()
