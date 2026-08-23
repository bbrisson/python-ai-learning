from fastapi.testclient import TestClient

from study_assistant.api import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "study-assistant"}


def test_create_study_plan() -> None:
    response = client.post(
        "/study-plans",
        json={
            "topic": "FastAPI",
            "level": "debutant",
            "available_minutes": 40,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["topic"] == "FastAPI"
    assert body["total_minutes"] == 40
    assert len(body["steps"]) == 3


def test_fastapi_translates_validation_error_to_422() -> None:
    response = client.post(
        "/study-plans",
        json={"topic": "FastAPI", "available_minutes": 5},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "available_minutes"


def test_workflow_endpoint_exposes_branch_result() -> None:
    response = client.post(
        "/study-workflows",
        json={
            "topic": "LangGraph",
            "available_minutes": 45,
            "quiz_score": 82,
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "progression"
    assert response.json()["history"][-1] == "progression_preparee"
