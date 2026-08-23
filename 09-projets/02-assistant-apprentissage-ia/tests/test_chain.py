from study_assistant.chain import build_offline_chain, explain_topic
from study_assistant.schemas import StudyRequest


def test_langchain_composition_runs_without_external_model() -> None:
    request = StudyRequest(topic="LCEL", available_minutes=30)

    answer = explain_topic(request, chain=build_offline_chain())

    assert "Simulation LangChain hors ligne" in answer
    assert "LCEL" in answer
    assert "30 minutes" in answer
