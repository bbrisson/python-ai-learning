"""Génération structurée avec Outlines et le serveur Ollama du laboratoire."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .schemas import StudyPlan, StudyRequest


DEFAULT_OLLAMA_URL = "http://192.168.18.5:11434"
DEFAULT_MODEL = "prof-python-ai"


def normalize_generated_plan(value: Any) -> StudyPlan:
    """Ramener les formats possibles d'un fournisseur vers un modèle Pydantic."""

    if isinstance(value, StudyPlan):
        return value
    if isinstance(value, (str, bytes, bytearray)):
        return StudyPlan.model_validate_json(value)
    return StudyPlan.model_validate(value)


def create_ollama_generator(
    base_url: str = DEFAULT_OLLAMA_URL,
    model_name: str = DEFAULT_MODEL,
) -> Callable[[str], Any]:
    """Configurer Outlines sans lancer de génération pendant l'import du module."""

    import ollama
    import outlines

    client = ollama.Client(host=base_url, timeout=120.0)
    model = outlines.from_ollama(client, model_name)
    return outlines.Generator(model, StudyPlan)


def generate_structured_plan(
    request: StudyRequest,
    generator: Callable[[str], Any] | None = None,
) -> StudyPlan:
    """Demander un plan conforme au schéma, puis le valider à la frontière."""

    active_generator = generator or create_ollama_generator()
    prompt = (
        "Crée un plan d'étude en français. Respecte exactement le sujet, le "
        "niveau, la durée totale et produis exactement trois étapes. Les durées "
        "des étapes doivent totaliser la durée demandée. Entrée JSON :\n"
        f"{request.model_dump_json()}"
    )
    return normalize_generated_plan(active_generator(prompt))
