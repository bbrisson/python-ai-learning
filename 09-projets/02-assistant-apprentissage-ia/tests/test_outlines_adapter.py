from study_assistant.outlines_adapter import (
    generate_structured_plan,
    normalize_generated_plan,
)
from study_assistant.planner import build_local_plan
from study_assistant.schemas import StudyRequest


def test_normalize_generated_plan_accepts_json() -> None:
    expected = build_local_plan(StudyRequest(topic="Outlines", available_minutes=35))

    actual = normalize_generated_plan(expected.model_dump_json())

    assert actual == expected


def test_generation_boundary_can_be_tested_without_ollama() -> None:
    request = StudyRequest(topic="sorties structurées", available_minutes=50)
    expected = build_local_plan(request)
    received_prompts: list[str] = []

    def fake_generator(prompt: str) -> str:
        received_prompts.append(prompt)
        return expected.model_dump_json()

    actual = generate_structured_plan(request, generator=fake_generator)

    assert actual == expected
    assert "sorties structurées" in received_prompts[0]
