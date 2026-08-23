"""Observer la validation et la conversion de types avec Pydantic.

Points importants à observer dans le débogueur :
    - ``raw_data`` contient des données ordinaires potentiellement non fiables ;
    - ``model_validate`` construit un objet seulement si les données peuvent
      respecter le contrat ``LearningGoal`` ;
    - une erreur est un objet ``ValidationError`` contenant des détails
      structurés, pas seulement un message destiné à l'écran.
"""

from typing import Any

from pydantic import BaseModel, ValidationError


class LearningGoal(BaseModel):
    """Le même contrat minimal que dans le premier exercice."""

    topic: str
    hours_per_week: int


def validate_learning_goal(label: str, raw_data: dict[str, Any]) -> None:
    """Valider un dictionnaire et afficher le résultat ou les erreurs."""

    print(f"\n--- {label} ---")
    print(f"Entrée : {raw_data}")
    print(f"Type avant validation : {type(raw_data['hours_per_week'])}")

    try:
        # POINT D'ARRÊT 2 : inspecte raw_data, puis exécute cette ligne avec F10.
        goal = LearningGoal.model_validate(raw_data)
    except ValidationError as error:
        # POINT D'ARRÊT 3 : inspecte error et développe error.errors().
        print("Validation refusée")
        for detail in error.errors():
            print(f"Champ : {detail['loc']}")
            print(f"Message : {detail['msg']}")
            print(f"Valeur reçue : {detail['input']!r}")
        return

    print(f"Objet validé : {goal}")
    print(f"Type après validation : {type(goal.hours_per_week)}")


def main() -> None:
    """Comparer un entier, une chaîne convertible et une chaîne invalide."""

    already_typed = {
        "topic": "Pydantic",
        "hours_per_week": 5,
    }
    convertible = {
        "topic": "Pydantic",
        "hours_per_week": "5",
    }
    invalid = {
        "topic": "Pydantic",
        "hours_per_week": "cinq",
    }

    # POINT D'ARRÊT 1 : inspecte les trois dictionnaires avant leur validation.
    validate_learning_goal("Valeur déjà typée", already_typed)
    validate_learning_goal("Valeur convertible", convertible)
    validate_learning_goal("Valeur invalide", invalid)


if __name__ == "__main__":
    main()
