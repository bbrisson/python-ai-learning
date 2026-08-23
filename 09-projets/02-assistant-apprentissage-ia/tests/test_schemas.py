import pytest
from pydantic import ValidationError

from study_assistant.planner import build_local_plan
from study_assistant.schemas import Level, StudyPlan, StudyRequest


def test_request_normalizes_and_validates_input() -> None:
    request = StudyRequest(
        topic="  Pydantic  ",
        level="intermediaire",
        available_minutes="45",
    )

    assert request.topic == "Pydantic"
    assert request.level is Level.INTERMEDIATE
    assert request.available_minutes == 45


@pytest.mark.parametrize(
    "payload",
    [
        {"topic": "--", "available_minutes": 30},
        {"topic": "FastAPI", "available_minutes": 10},
        {"topic": "FastAPI", "unknown_field": True},
    ],
)
def test_request_rejects_invalid_boundaries(payload: dict) -> None:
    with pytest.raises(ValidationError):
        StudyRequest.model_validate(payload)


def test_plan_serialization_round_trip_preserves_contract() -> None:
    plan = build_local_plan(
        StudyRequest(topic="LangGraph", level="avance", available_minutes=60)
    )

    restored = StudyPlan.model_validate_json(plan.model_dump_json())

    assert restored == plan
    assert sum(step.duration_minutes for step in restored.steps) == 60


def test_plan_rejects_an_incoherent_total() -> None:
    plan = build_local_plan(StudyRequest(topic="Outlines", available_minutes=30))
    invalid_data = plan.model_dump()
    invalid_data["total_minutes"] = 31

    with pytest.raises(ValidationError, match="somme des durées"):
        StudyPlan.model_validate(invalid_data)
