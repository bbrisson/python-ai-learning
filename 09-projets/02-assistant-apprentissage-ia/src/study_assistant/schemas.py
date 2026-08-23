"""Contrats de données partagés par toutes les couches de l'application.

Pydantic joue ici le rôle d'une frontière d'exécution : les annotations Python
décrivent la forme attendue et Pydantic valide les données non fiables qui
entrent dans le système (HTTP, JSON ou sortie d'un LLM).
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    """Configuration commune : espaces nettoyés et champs inconnus refusés."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Level(str, Enum):
    """Niveaux acceptés par l'API et sérialisables directement en JSON."""

    BEGINNER = "debutant"
    INTERMEDIATE = "intermediaire"
    ADVANCED = "avance"


class StudyRequest(StrictModel):
    """Entrée utilisateur validée avant d'atteindre la logique métier."""

    topic: str = Field(min_length=2, max_length=120)
    level: Level = Level.BEGINNER
    available_minutes: int = Field(default=30, ge=20, le=240)
    quiz_score: int | None = Field(default=None, ge=0, le=100)

    @field_validator("topic")
    @classmethod
    def topic_must_contain_text(cls, value: str) -> str:
        """Refuser un sujet qui ne contient aucun caractère alphanumérique."""

        if not any(character.isalnum() for character in value):
            raise ValueError("le sujet doit contenir au moins une lettre ou un chiffre")
        return value


class StudyStep(StrictModel):
    """Une étape atomique et mesurable du plan d'étude."""

    title: str = Field(min_length=3, max_length=80)
    objective: str = Field(min_length=10, max_length=300)
    duration_minutes: int = Field(ge=5, le=180)


class StudyPlan(StrictModel):
    """Sortie structurée commune au code déterministe et au LLM."""

    topic: str = Field(min_length=2, max_length=120)
    level: Level
    summary: str = Field(min_length=10, max_length=500)
    steps: list[StudyStep] = Field(min_length=3, max_length=3)
    total_minutes: int = Field(ge=20, le=240)
    next_action: str = Field(min_length=10, max_length=300)

    @model_validator(mode="after")
    def durations_must_match_total(self) -> StudyPlan:
        """Garantir un invariant métier entre les étapes et le total."""

        computed_total = sum(step.duration_minutes for step in self.steps)
        if computed_total != self.total_minutes:
            raise ValueError(
                "la somme des durées doit être égale à total_minutes "
                f"({computed_total} != {self.total_minutes})"
            )
        return self


class WorkflowResult(StrictModel):
    """Résultat public du workflow LangGraph."""

    plan: StudyPlan
    decision: Literal["revision", "progression"]
    feedback: str = Field(min_length=10)
    history: list[str] = Field(min_length=3)


class HealthResponse(StrictModel):
    """Réponse minimale de supervision de l'API."""

    status: Literal["ok"] = "ok"
    service: str = "study-assistant"
