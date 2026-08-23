from study_assistant.schemas import StudyRequest
from study_assistant.workflow import run_workflow


def test_low_score_routes_to_revision() -> None:
    result = run_workflow(
        StudyRequest(topic="LangGraph", available_minutes=30, quiz_score=45)
    )

    assert result.decision == "revision"
    assert result.history == [
        "plan_cree",
        "progression_evaluee",
        "revision_preparee",
    ]


def test_high_score_routes_to_progression() -> None:
    result = run_workflow(
        StudyRequest(topic="LangGraph", available_minutes=30, quiz_score=90)
    )

    assert result.decision == "progression"
    assert result.history[-1] == "progression_preparee"


def test_missing_score_uses_safe_revision_branch() -> None:
    result = run_workflow(StudyRequest(topic="LangGraph", available_minutes=30))

    assert result.decision == "revision"
