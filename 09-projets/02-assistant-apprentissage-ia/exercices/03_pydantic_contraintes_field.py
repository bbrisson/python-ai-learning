"""Ajouter des contraintes et des métadonnées avec ``pydantic.Field``.

Ce script montre que :
    - l'annotation définit le type général d'un champ ;
    - ``Field`` précise les valeurs autorisées ;
    - une valeur par défaut rend un champ facultatif à l'entrée ;
    - les contraintes sont exportées dans le JSON Schema du modèle.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class LearningGoal(BaseModel):
    """Objectif d'apprentissage avec contraintes explicites."""

    topic: str = Field(
        min_length=2,
        max_length=80,
        description="Technologie ou concept à étudier",
    )
    hours_per_week: int = Field(
        default=5,
        ge=1,
        le=40,
        description="Nombre d'heures disponibles chaque semaine",
    )


def validate_case(label: str, raw_data: dict[str, Any]) -> None:
    """Construire un objectif ou afficher les contraintes non respectées."""

    print(f"\n--- {label} ---")
    print(f"Entrée : {raw_data}")

    try:
        # POINT D'ARRÊT 2 : F10 applique le type et les contraintes Field.
        goal = LearningGoal.model_validate(raw_data)
    except ValidationError as error:
        # POINT D'ARRÊT 3 : inspecte error.errors() pour localiser la règle.
        print("Validation refusée")
        for detail in error.errors():
            print(
                f"Champ={detail['loc']} | "
                f"Type={detail['type']} | "
                f"Message={detail['msg']}"
            )
        return

    print(f"Objet validé : {goal}")
    print(f"Champs fournis explicitement : {goal.model_fields_set}")


def display_json_schema() -> None:
    """Afficher comment Field est traduit en contraintes JSON Schema."""

    schema = LearningGoal.model_json_schema()

    # POINT D'ARRÊT 4 : développe schema['properties'] dans le débogueur.
    print("\n--- Contraintes exportées en JSON Schema ---")
    print(json.dumps(schema["properties"], indent=2, ensure_ascii=False))


def main() -> None:
    """Comparer valeurs explicites, valeur par défaut et entrées interdites."""

    valid = {"topic": "Pydantic", "hours_per_week": 8}
    uses_default = {"topic": "FastAPI"}
    topic_too_short = {"topic": "P", "hours_per_week": 5}
    too_many_hours = {"topic": "LangGraph", "hours_per_week": 60}

    # POINT D'ARRÊT 1 : inspecte les quatre dictionnaires avant validation.
    validate_case("Valeurs explicites valides", valid)
    validate_case("Valeur par défaut", uses_default)
    validate_case("Sujet trop court", topic_too_short)
    validate_case("Durée trop grande", too_many_hours)
    display_json_schema()


if __name__ == "__main__":
    main()
