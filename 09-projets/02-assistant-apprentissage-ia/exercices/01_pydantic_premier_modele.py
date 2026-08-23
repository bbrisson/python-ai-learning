"""Premier modèle Pydantic à parcourir pas à pas avec le débogueur.

Dans VS Code :
    1. Place un point d'arrêt sur l'appel à ``create_learning_goal`` dans main.
    2. Lance « Python Debugger: Python File » avec F5.
    3. Utilise F11 pour entrer dans ``create_learning_goal``.
    4. Sur la construction ``LearningGoal(...)``, utilise F10 pour ne pas
       entrer tout de suite dans les mécanismes internes de Pydantic.
"""

from pydantic import BaseModel


class LearningGoal(BaseModel):
    """Contrat minimal décrivant un objectif d'apprentissage."""

    topic: str
    hours_per_week: int


def create_learning_goal(topic: str, hours_per_week: int) -> LearningGoal:
    """Construire un objet validé à partir de valeurs Python ordinaires."""

    # POINT D'ARRÊT 2 : inspecte topic et hours_per_week avant la validation.
    goal = LearningGoal(
        topic=topic,
        hours_per_week=hours_per_week,
    )

    # Inspecte goal après la construction : c'est maintenant un LearningGoal.
    return goal


def display_learning_goal(goal: LearningGoal) -> None:
    """Afficher l'objet et sa représentation sérialisée."""

    print(goal)
    print(goal.topic)
    print(type(goal.hours_per_week))
    print(LearningGoal.model_fields.keys())
    print(goal.model_dump())


def main() -> None:
    """Préparer les données, construire le modèle, puis l'afficher."""

    raw_topic = "Pydantic"
    raw_hours_per_week = 5

    # POINT D'ARRÊT 1 : F11 entre dans notre fonction de construction.
    goal = create_learning_goal(raw_topic, raw_hours_per_week)

    # POINT D'ARRÊT 3 : inspecte goal, puis F11 entre dans l'affichage.
    display_learning_goal(goal)


if __name__ == "__main__":
    main()
