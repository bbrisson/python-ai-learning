"""Exemple 1 — La boucle nue : où vit l'état ?

POURQUOI cet exemple d'abord
----------------------------
Avant de parler d'agents et d'outils, il faut avoir compris UNE chose, et
elle est contre-intuitive quand on vient du C/C++ ou de LabVIEW :

    Le serveur Ollama ne se souvient de RIEN entre deux requêtes.

`/api/chat` est une fonction pure : `f(historique) -> message`. Il n'y a pas
de session, pas de handle, pas de contexte persistant côté serveur. La
"mémoire" de ton assistant, c'est une `list` Python dans TON processus, que
tu renvoies en entier à chaque tour.

Analogie : ce n'est pas un objet avec des attributs privés qui accumulent
l'état entre les appels de méthode. C'est une fonction `static` sans variable
locale statique — tout ce dont elle a besoin arrive par ses arguments. Le
`while` est ta pile d'appel, et `messages` est ton pointeur d'état.

Ce script démontre la différence en la RENDANT VISIBLE : on pose les mêmes
trois questions à deux boucles, l'une amnésique, l'autre avec état.

Exécution :
    python 01_boucle_nue.py
"""

from __future__ import annotations

from ollama_client import setup_console, timed_chat


SYSTEME = {
    "role": "system",
    "content": "Tu es concis. Réponds en français, en une seule phrase courte.",
}

TOURS = [
    "Je m'appelle Benoît et je programme en C++ depuis 15 ans.",
    "Quel langage est-ce que je connais déjà ?",
    "Et comment je m'appelle ?",
]


def boucle_amnesique(tours: list[str]) -> None:
    """Chaque tour renvoie UNIQUEMENT la question courante.

    C'est l'erreur numéro un des débuts. Le code paraît juste, le serveur
    répond sans erreur, et pourtant l'assistant a un poisson rouge à la
    place du cerveau.
    """
    print("\n" + "=" * 70)
    print("BOUCLE A — sans état (on n'envoie que la dernière question)")
    print("=" * 70)

    for question in tours:
        # L'historique est reconstruit à zéro à chaque itération :
        # tout ce qui précède est perdu.
        messages = [SYSTEME, {"role": "user", "content": question}]
        reponse, duree = timed_chat(messages)

        print(f"\n[{len(messages)} messages envoyés | {duree:.1f}s]")
        print(f"  USER      : {question}")
        print(f"  ASSISTANT : {reponse['content'].strip()}")


def boucle_avec_etat(tours: list[str]) -> None:
    """L'historique s'accumule : c'est la boucle qui porte la mémoire.

    Noter les deux `append` par itération. Oublier de réinjecter la réponse
    de l'assistant est l'autre erreur classique : le modèle revoit ses
    questions mais jamais ses propres réponses, et se contredit.
    """
    print("\n" + "=" * 70)
    print("BOUCLE B — avec état (l'historique complet repart à chaque tour)")
    print("=" * 70)

    messages: list[dict[str, object]] = [SYSTEME]

    for question in tours:
        messages.append({"role": "user", "content": question})
        reponse, duree = timed_chat(messages)
        # Sans cette ligne, la mémoire est trouée.
        messages.append({"role": "assistant", "content": reponse["content"]})

        print(f"\n[{len(messages) - 1} messages envoyés | {duree:.1f}s]")
        print(f"  USER      : {question}")
        print(f"  ASSISTANT : {reponse['content'].strip()}")

    print(f"\n→ État final : {len(messages)} messages accumulés en mémoire Python.")
    print("  C'est CE tableau qui grossit à chaque tour, et c'est lui qui")
    print("  finira par saturer la fenêtre de contexte (exemple 03).")


def main() -> None:
    setup_console()
    print("Modèle : qwen3.8:27b — le premier appel charge ~32 GB, sois patient.")
    boucle_amnesique(TOURS)
    boucle_avec_etat(TOURS)

    print("\n" + "=" * 70)
    print("CE QU'IL FAUT RETENIR")
    print("=" * 70)
    print("1. Le serveur est sans état. L'état vit dans ta liste `messages`.")
    print("2. Il faut réinjecter les DEUX rôles : user ET assistant.")
    print("3. Le coût d'un tour croît avec l'historique — la boucle n'est pas")
    print("   gratuite, chaque itération relit tout depuis le début.")


if __name__ == "__main__":
    main()
