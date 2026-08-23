"""Workflow LangGraph déterministe avec branchement selon le résultat du quiz."""

from __future__ import annotations

import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from .planner import build_local_plan
from .schemas import StudyPlan, StudyRequest, WorkflowResult


class StudyState(TypedDict, total=False):
    """État partagé; chaque nœud retourne uniquement ses mises à jour."""

    topic: str
    level: str
    available_minutes: int
    quiz_score: int | None
    plan: StudyPlan
    decision: Literal["revision", "progression"]
    feedback: str
    history: Annotated[list[str], operator.add]


def _request_from_state(state: StudyState) -> StudyRequest:
    return StudyRequest.model_validate(
        {
            "topic": state["topic"],
            "level": state["level"],
            "available_minutes": state["available_minutes"],
            "quiz_score": state.get("quiz_score"),
        }
    )


def create_plan(state: StudyState) -> StudyState:
    """Nœud 1 : construire le plan à partir d'une entrée déjà validable."""

    return {
        "plan": build_local_plan(_request_from_state(state)),
        "history": ["plan_cree"],
    }


def assess_progress(state: StudyState) -> StudyState:
    """Nœud 2 : transformer le score brut en décision de routage."""

    score = state.get("quiz_score")
    decision: Literal["revision", "progression"]
    decision = "progression" if score is not None and score >= 70 else "revision"
    return {"decision": decision, "history": ["progression_evaluee"]}


def route_after_assessment(
    state: StudyState,
) -> Literal["prepare_revision", "prepare_progression"]:
    """Arête conditionnelle : choisir le prochain nœud sans modifier l'état."""

    if state["decision"] == "progression":
        return "prepare_progression"
    return "prepare_revision"


def prepare_revision(state: StudyState) -> StudyState:
    return {
        "feedback": (
            "Reprendre l'exemple minimal et expliquer chaque frontière de données "
            "avant de refaire le quiz."
        ),
        "history": ["revision_preparee"],
    }


def prepare_progression(state: StudyState) -> StudyState:
    return {
        "feedback": (
            "Les fondations sont acquises; appliquer maintenant le concept dans "
            "le mini-projet intégrateur."
        ),
        "history": ["progression_preparee"],
    }


def build_workflow():
    """Assembler et compiler le graphe avant son invocation."""

    builder = StateGraph(StudyState)
    builder.add_node("create_plan", create_plan)
    builder.add_node("assess_progress", assess_progress)
    builder.add_node("prepare_revision", prepare_revision)
    builder.add_node("prepare_progression", prepare_progression)
    builder.add_edge(START, "create_plan")
    builder.add_edge("create_plan", "assess_progress")
    builder.add_conditional_edges(
        "assess_progress",
        route_after_assessment,
        {
            "prepare_revision": "prepare_revision",
            "prepare_progression": "prepare_progression",
        },
    )
    builder.add_edge("prepare_revision", END)
    builder.add_edge("prepare_progression", END)
    return builder.compile()


learning_workflow = build_workflow()


def run_workflow(request: StudyRequest) -> WorkflowResult:
    """Valider l'entrée et la sortie autour de l'exécution LangGraph."""

    result = learning_workflow.invoke(
        {
            **request.model_dump(mode="json"),
            "history": [],
        }
    )
    return WorkflowResult.model_validate(
        {
            "plan": result["plan"],
            "decision": result["decision"],
            "feedback": result["feedback"],
            "history": result["history"],
        }
    )
