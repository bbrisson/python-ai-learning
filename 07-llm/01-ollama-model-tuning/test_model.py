"""Tester un appel Python vers le serveur Ollama.

Ce script utilise volontairement seulement la standard library Python.

Objectif débutant :
    Vérifier que Python peut envoyer une question au serveur Ollama situé sur
    le réseau local et afficher la réponse du modèle `llama3.2:3b`.

Architecture :
    Python sur Windows
        -> requête HTTP POST
        -> serveur Ollama 192.168.18.5:11434
        -> modèle llama3.2:3b
        -> réponse texte
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


OLLAMA_URL = "http://192.168.18.5:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def ask_ollama(prompt: str) -> str:
    """Envoyer une question à Ollama et retourner la réponse texte.

    Args:
        prompt: La question envoyée au modèle.

    Returns:
        Le texte généré par le modèle.

    Raises:
        RuntimeError: Si le serveur ne répond pas ou retourne une erreur.
    """

    payload = {
        "model": MODEL_NAME,
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
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Impossible de joindre le serveur Ollama à {OLLAMA_URL}. "
            f"Détail: {error}"
        ) from error

    data = json.loads(response_body)
    return data["response"]


def main() -> None:
    """Point d'entrée du script."""

    question = (
        "Explique en français, pour un débutant, la différence entre "
        "un environnement conda et un kernel Jupyter."
    )

    print(f"Modèle utilisé : {MODEL_NAME}")
    print(f"Serveur Ollama : {OLLAMA_URL}")
    print("Question :")
    print(question)
    print("\nRéponse du modèle :\n")

    answer = ask_ollama(question)
    print(answer)


if __name__ == "__main__":
    main()