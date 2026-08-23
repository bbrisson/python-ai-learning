"""API FastAPI exposant la logique métier et le workflow pédagogique."""

from __future__ import annotations

from fastapi import FastAPI, status

from .planner import build_local_plan
from .schemas import HealthResponse, StudyPlan, StudyRequest, WorkflowResult
from .workflow import run_workflow


app = FastAPI(
    title="Assistant d'apprentissage IA",
    version="0.1.0",
    description=(
        "Projet pédagogique pour Pydantic, FastAPI, Outlines, LangChain et "
        "LangGraph."
    ),
)


@app.get("/health", response_model=HealthResponse, tags=["supervision"])
def health() -> HealthResponse:
    """Vérifier que le processus web répond, sans dépendance externe."""

    return HealthResponse()


@app.post(
    "/study-plans",
    response_model=StudyPlan,
    status_code=status.HTTP_201_CREATED,
    tags=["apprentissage"],
)
def create_study_plan(request: StudyRequest) -> StudyPlan:
    """Valider la requête HTTP puis appeler une fonction métier pure."""

    return build_local_plan(request)


@app.post(
    "/study-workflows",
    response_model=WorkflowResult,
    status_code=status.HTTP_200_OK,
    tags=["apprentissage"],
)
def execute_study_workflow(request: StudyRequest) -> WorkflowResult:
    """Exécuter le graphe déterministe et retourner son état public validé."""

    return run_workflow(request)
