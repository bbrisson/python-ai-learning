"""Deux chaînes LangChain : une simulation locale et un vrai client Ollama."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_ollama import ChatOllama

from .outlines_adapter import DEFAULT_MODEL, DEFAULT_OLLAMA_URL
from .schemas import StudyRequest


def build_teacher_prompt() -> ChatPromptTemplate:
    """Créer un template réutilisable, distinct du modèle d'inférence."""

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Tu es un professeur Python/IA précis. Explique le pourquoi avant "
                "le comment et distingue toujours contrat, orchestration et I/O.",
            ),
            (
                "human",
                "Explique {topic} au niveau {level} dans une séance de "
                "{available_minutes} minutes.",
            ),
        ]
    )


def _offline_model(prompt_value: Any) -> AIMessage:
    """Simuler un chat model pour apprendre et tester LCEL hors ligne."""

    messages = prompt_value.to_messages()
    return AIMessage(
        content=(
            "Simulation LangChain hors ligne. Le modèle recevrait ce message :\n"
            f"{messages[-1].content}"
        )
    )


def build_offline_chain() -> Runnable:
    """Composer prompt -> faux modèle -> conversion en chaîne de caractères."""

    return build_teacher_prompt() | RunnableLambda(_offline_model) | StrOutputParser()


def build_ollama_chain(
    base_url: str = DEFAULT_OLLAMA_URL,
    model_name: str = DEFAULT_MODEL,
) -> Runnable:
    """Composer la même chaîne avec le vrai fournisseur Ollama."""

    model = ChatOllama(
        base_url=base_url,
        model=model_name,
        temperature=0,
    )
    return build_teacher_prompt() | model | StrOutputParser()


def explain_topic(request: StudyRequest, chain: Runnable | None = None) -> str:
    """Exécuter une chaîne injectée; la simulation est la valeur sûre par défaut."""

    active_chain = chain or build_offline_chain()
    return active_chain.invoke(
        {
            "topic": request.topic,
            "level": request.level.value,
            "available_minutes": request.available_minutes,
        }
    )
