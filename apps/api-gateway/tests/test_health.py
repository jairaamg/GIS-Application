from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_live() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_project() -> None:
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Demo",
            "description": "Skeleton project",
            "organization_id": "11111111-1111-1111-1111-111111111111",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Demo"
