"""Comparer un modèle Ollama de base avec un modèle personnalisé.

Ce script utilise volontairement seulement la standard library Python.

Objectif débutant :
    Poser exactement la même question à deux modèles :

    1. `llama3.2:3b`, le modèle de base ;
    2. `prof-python-ai`, le modèle personnalisé avec notre `Modelfile`.

    Ensuite, le script affiche les deux réponses et une petite grille
    d'observation pour analyser les changements provoqués par le Modelfile.

Architecture :
    Python sur Windows
        -> requête HTTP POST
        -> serveur Ollama 192.168.18.5:11434
        -> modèle demandé
        -> réponse texte
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


OLLAMA_URL = "http://192.168.18.5:11434/api/generate"

BASE_MODEL = "llama3.2:3b"
CUSTOM_MODEL = "prof-python-ai"

QUESTION = (
    "Explique en français, pour un débutant, la différence entre "
    "un environnement conda et un kernel Jupyter. "
    "Si possible, fais un lien avec une personne qui connaît déjà C/C++ ou LabVIEW."
)


def ask_ollama(model_name: str, prompt: str) -> str:
    """Envoyer une question à un modèle Ollama et retourner la réponse texte.

    Args:
        model_name: Le nom du modèle Ollama à utiliser.
        prompt: La question envoyée au modèle.

    Returns:
        Le texte généré par le modèle.

    Raises:
        RuntimeError: Si le serveur ne répond pas, retourne une erreur,
            ou si la réponse JSON ne contient pas le champ attendu.
    """

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Impossible de joindre le serveur Ollama à {OLLAMA_URL}. "
            f"Modèle demandé: {model_name}. Détail: {error}"
        ) from error

    data = json.loads(response_body)

    if "response" not in data:
        raise RuntimeError(
            f"Réponse Ollama inattendue pour le modèle {model_name}: {data}"
        )

    return data["response"]


def print_separator(title: str) -> None:
    """Afficher un séparateur lisible dans le terminal."""

    line = "=" * 80
    print(f"\n{line}\n{title}\n{line}\n")


def print_analysis_grid() -> None:
    """Afficher une grille d'analyse manuelle des différences à observer."""

    print_separator("Grille d'analyse manuelle")
    print(
        "Compare les deux réponses avec ces critères :\n\n"
        "1. Langue\n"
        "   - Les deux réponses sont-elles bien en français ?\n\n"
        "2. Niveau débutant\n"
        "   - La réponse est-elle compréhensible pour quelqu'un qui débute en Python ?\n\n"
        "3. Structure pédagogique\n"
        "   - La réponse est-elle organisée étape par étape ?\n"
        "   - Y a-t-il des titres, des listes ou une progression logique ?\n\n"
        "4. Précision technique\n"
        "   - La distinction entre environnement conda et kernel Jupyter est-elle exacte ?\n\n"
        "5. Adaptation au profil C/C++ ou LabVIEW\n"
        "   - Le modèle fait-il un lien utile avec un profil venant de C/C++ ou LabVIEW ?\n\n"
        "6. Effet du Modelfile\n"
        "   - Le modèle `prof-python-ai` semble-t-il plus patient, précis et pédagogique ?\n"
    )


def main() -> None:
    """Point d'entrée du script."""

    print_separator("Configuration du test")
    print(f"Serveur Ollama : {OLLAMA_URL}")
    print(f"Modèle de base : {BASE_MODEL}")
    print(f"Modèle personnalisé : {CUSTOM_MODEL}")
    print("\nQuestion commune :")
    print(QUESTION)

    print_separator(f"Réponse du modèle de base — {BASE_MODEL}")
    base_answer = ask_ollama(BASE_MODEL, QUESTION)
    print(base_answer)

    print_separator(f"Réponse du modèle personnalisé — {CUSTOM_MODEL}")
    custom_answer = ask_ollama(CUSTOM_MODEL, QUESTION)
    print(custom_answer)

    print_analysis_grid()


if __name__ == "__main__":
    main()