"""Client Ollama minimal, partagé par tous les exemples de loop engineering.

Volontairement en standard library seulement (`urllib`), comme
`07-llm/01-ollama-model-tuning/test_model.py`. Aucune dépendance à installer,
et surtout : rien ne cache la mécanique. Tu vois exactement l'objet JSON qui
part sur le réseau et celui qui revient.

Architecture (identique au dossier 01) :

    Python sur Windows
        -> requête HTTP POST
        -> serveur Ollama 192.168.18.5:11434
        -> modèle qwen3.8:27b
        -> réponse JSON

Analogie C/C++ : considère ce module comme le `.c` qui encapsule l'appel
système. Les boucles des exemples 01 à 04 sont la logique applicative ; ici
c'est le driver.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any


# --- Configuration -------------------------------------------------------

# La variable d'environnement OLLAMA_HOST est déjà définie sur ta machine
# (http://192.168.18.5:11434). On la lit, avec une valeur de repli explicite
# pour que le script reste lisible même sans environnement configuré.
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.18.5:11434").rstrip("/")
CHAT_URL = f"{OLLAMA_HOST}/api/chat"

MODEL = "qwen3.8:27b"

# Timeout généreux : 27 milliards de paramètres, et le premier appel doit
# charger ~32 GB de poids en VRAM. Un timeout court est LA première cause de
# "ma boucle ne marche pas" alors que le serveur allait très bien.
TIMEOUT_S = 300


def setup_console() -> None:
    """Forcer la console Windows en UTF-8.

    Sans ça, `print("−12 °C")` affiche `-12 �C` (ou lève UnicodeEncodeError)
    parce que la console hérite de la codepage cp1252. Bug classique et
    déroutant : le modèle a bien répondu, c'est l'affichage qui ment.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def chat(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    *,
    model: str = MODEL,
    think: bool = False,
    temperature: float = 0.0,
    fmt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Un aller-retour avec `/api/chat`. Retourne le message de l'assistant.

    Args:
        messages: L'historique COMPLET. Le serveur ne mémorise rien entre deux
            appels — voir `01_boucle_nue.py`.
        tools: Schémas JSON des outils disponibles, ou None.
        model: Nom du modèle Ollama.
        think: Mode raisonnement de qwen3. False = réponse directe, plus
            rapide et plus prévisible dans une boucle automatisée.
        temperature: 0.0 pour rendre les boucles reproductibles pendant
            l'apprentissage.
        fmt: Schéma JSON pour forcer une sortie structurée (`format`).

    Returns:
        Le dict `message` de la réponse : `{"role": "assistant",
        "content": str, "tool_calls": [...] | absent}`.
    """
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "think": think,
        "options": {"temperature": temperature},
    }
    if tools:
        body["tools"] = tools
    if fmt:
        body["format"] = fmt

    request = urllib.request.Request(
        CHAT_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama a répondu HTTP {exc.code} : {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Serveur Ollama injoignable sur {OLLAMA_HOST} : {exc.reason}"
        ) from exc

    return payload["message"]


def timed_chat(*args: Any, **kwargs: Any) -> tuple[dict[str, Any], float]:
    """Comme `chat`, mais retourne aussi la durée en secondes.

    Utile pour rendre visible le coût réel d'un tour de boucle : c'est la
    grandeur que le loop engineering cherche à contrôler.
    """
    start = time.monotonic()
    message = chat(*args, **kwargs)
    return message, time.monotonic() - start
