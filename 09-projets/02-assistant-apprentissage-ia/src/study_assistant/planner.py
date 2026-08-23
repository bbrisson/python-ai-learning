"""Logique métier déterministe, indépendante du web et des LLM."""

from __future__ import annotations

from .schemas import Level, StudyPlan, StudyRequest, StudyStep


LEVEL_LABELS = {
    Level.BEGINNER: "les fondations et le vocabulaire",
    Level.INTERMEDIATE: "les mécanismes et les compromis d'architecture",
    Level.ADVANCED: "les limites, la performance et l'industrialisation",
}


def build_local_plan(request: StudyRequest) -> StudyPlan:
    """Construire un plan reproductible sans effectuer d'appel réseau.

    Cette fonction sert de référence testable. Une implémentation LLM doit
    respecter exactement le même contrat ``StudyPlan``.
    """

    introduction_minutes = max(5, request.available_minutes // 4)
    validation_minutes = max(5, request.available_minutes // 4)
    practice_minutes = (
        request.available_minutes - introduction_minutes - validation_minutes
    )
    emphasis = LEVEL_LABELS[request.level]

    return StudyPlan(
        topic=request.topic,
        level=request.level,
        summary=(
            f"Plan consacré à {request.topic}, centré sur {emphasis}, "
            "avec une progression théorie-pratique-validation."
        ),
        steps=[
            StudyStep(
                title="Comprendre le modèle mental",
                objective=(
                    f"Expliquer pourquoi {request.topic} existe et identifier "
                    "ses responsabilités principales."
                ),
                duration_minutes=introduction_minutes,
            ),
            StudyStep(
                title="Construire un exemple minimal",
                objective=(
                    f"Implémenter un cas simple avec {request.topic} et observer "
                    "les données à chaque frontière."
                ),
                duration_minutes=practice_minutes,
            ),
            StudyStep(
                title="Vérifier les invariants",
                objective=(
                    "Tester le chemin nominal, une entrée invalide et expliquer "
                    "le comportement obtenu."
                ),
                duration_minutes=validation_minutes,
            ),
        ],
        total_minutes=request.available_minutes,
        next_action=(
            "Exécuter les tests associés, puis reformuler le rôle de chaque "
            "couche sans consulter le cours."
        ),
    )
