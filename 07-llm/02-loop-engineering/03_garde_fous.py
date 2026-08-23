"""Exemple 3 — Les garde-fous : c'est ça, le vrai métier.

POURQUOI
--------
Écrire la boucle de l'exemple 2 prend vingt minutes. La rendre sûre à laisser
tourner sans surveillance prend le reste de la semaine. Une boucle agentique
est un système bouclé non déterministe : elle peut ne jamais converger, et
elle dépense de l'argent et du temps à chaque itération.

Analogie régulation / LabVIEW : tu ne mets pas un PID en production sans
saturation de la commande, sans anti-windup et sans watchdog. Ici c'est
pareil. Le modèle est le correcteur, tes outils sont l'actionneur, et sans
limites la boucle diverge.

Les quatre modes de défaillance à couvrir, et leur parade :

    1. Divergence            -> budget de tours (`max_tours`)
    2. Boucle stérile        -> détection de signature d'appel répétée
    3. Coût qui s'emballe    -> budget de temps et de tokens
    4. Erreur d'outil        -> renvoyer l'erreur au modèle, PAS lever

Le point 4 est le plus contre-intuitif quand on vient du C++ : ici, une
exception n'est pas une condition d'échec, c'est une *observation*. Le
modèle lit le message d'erreur et corrige son appel au tour suivant. Ta
boucle transforme une exception en donnée d'entrée. Ce script le démontre
avec un outil volontairement pointilleux sur le format de ses arguments.

Exécution :
    python 03_garde_fous.py
"""

from __future__ import annotations

import json
import time
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from ollama_client import setup_console, timed_chat


# --- 1 à 3 : le budget ---------------------------------------------------


@dataclass
class Budget:
    """Enveloppe de ressources d'une boucle. Le watchdog.

    Trois limites indépendantes, parce qu'elles ne saturent pas en même
    temps : une boucle peut faire 3 tours et brûler 200 secondes, ou faire
    20 tours instantanés sur un cache.
    """

    max_tours: int = 8
    max_secondes: float = 240.0
    max_tokens: int = 20_000

    tours: int = 0
    tokens: int = 0
    debut: float = field(default_factory=time.monotonic)

    def epuise(self) -> str | None:
        """Retourner la raison d'arrêt, ou None si on peut continuer."""
        if self.tours >= self.max_tours:
            return f"budget de tours atteint ({self.max_tours})"
        if time.monotonic() - self.debut >= self.max_secondes:
            return f"budget de temps atteint ({self.max_secondes:.0f}s)"
        if self.tokens >= self.max_tokens:
            return f"budget de tokens atteint ({self.max_tokens})"
        return None

    def resume(self) -> str:
        ecoule = time.monotonic() - self.debut
        return f"{self.tours} tours | {ecoule:.1f}s | ~{self.tokens} tokens"


class DetecteurDeBoucle:
    """Repère un agent qui tourne en rond.

    Signature = nom de l'outil + arguments normalisés. Si la même signature
    revient deux fois, le modèle n'apprend plus rien de ses observations :
    continuer ne fera que payer les mêmes tokens.

    C'est l'équivalent de la détection de cycle dans une machine à états :
    si l'état suivant égale l'état courant et que l'entrée n'a pas changé,
    tu ne sortiras jamais.
    """

    def __init__(self) -> None:
        self._vues: set[str] = set()

    def signature(self, appel: dict[str, Any]) -> str:
        fonction = appel["function"]
        return json.dumps(
            [fonction["name"], fonction["arguments"]], sort_keys=True, ensure_ascii=False
        )

    def est_repetition(self, appel: dict[str, Any]) -> bool:
        signature = self.signature(appel)
        if signature in self._vues:
            return True
        self._vues.add(signature)
        return False


# --- 4 : un outil pointilleux, pour voir l'auto-correction ---------------

NOTES = {
    "conda": "Un environnement conda isole interpréteur ET bibliothèques natives.",
    "kernel": "Un kernel Jupyter est un processus Python déclaré dans un kernel.json.",
    "git": "Git stocke des snapshots complets, pas des deltas.",
}


def chercher_note(sujet: str) -> str:
    """Chercher une note de cours. Exige une clé en minuscules sans accent.

    La contrainte est artificielle mais représentative : la moitié des
    outils réels d'entreprise ont un format d'identifiant strict (numéro de
    pièce, code projet, clé d'API interne). Le modèle ne peut pas le
    deviner — il doit l'apprendre du message d'erreur.
    """
    normalise = "".join(
        c
        for c in unicodedata.normalize("NFD", sujet)
        if unicodedata.category(c) != "Mn"
    ).lower()

    if normalise != sujet:
        return json.dumps(
            {
                "erreur": "format invalide",
                "detail": (
                    f"'{sujet}' doit être en minuscules et sans accent. "
                    f"Réessaie avec '{normalise}'."
                ),
                "sujets_valides": sorted(NOTES),
            },
            ensure_ascii=False,
        )

    if sujet not in NOTES:
        return json.dumps(
            {"erreur": "sujet inconnu", "sujets_valides": sorted(NOTES)},
            ensure_ascii=False,
        )

    return json.dumps({"sujet": sujet, "note": NOTES[sujet]}, ensure_ascii=False)


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "chercher_note",
            "description": "Cherche une note de cours par sujet.",
            "parameters": {
                "type": "object",
                "properties": {"sujet": {"type": "string"}},
                "required": ["sujet"],
            },
        },
    }
]

SYSTEME = {
    "role": "system",
    "content": (
        "Tu réponds à partir des notes de cours, via l'outil `chercher_note`. "
        "Si l'outil retourne une erreur, lis-la et corrige ton appel. "
        "Réponse finale courte, en français."
    ),
}

# Formulée avec majuscule et accent, pour provoquer l'erreur de format.
TACHE = "Que disent mes notes sur les sujets « Conda » et « Génie logiciel » ?"


def boucle_gardee(tache: str, budget: Budget) -> tuple[str | None, str]:
    """La boucle de l'exemple 2, plus les quatre garde-fous.

    Returns:
        (réponse finale ou None, raison d'arrêt).
    """
    messages: list[dict[str, Any]] = [SYSTEME, {"role": "user", "content": tache}]
    detecteur = DetecteurDeBoucle()

    while True:
        raison = budget.epuise()
        if raison:
            return None, raison

        reponse, duree = timed_chat(messages, TOOLS)
        budget.tours += 1
        # Approximation volontairement grossière (~4 caractères par token).
        # Suffisant pour un plafond : on veut un ordre de grandeur, pas une
        # facturation exacte.
        budget.tokens += sum(len(str(m.get("content", ""))) for m in messages) // 4
        messages.append(reponse)

        appels = reponse.get("tool_calls")
        if not appels:
            print(f"\n--- Tour {budget.tours} ({duree:.1f}s) : réponse finale ---")
            return reponse["content"].strip(), "convergence"

        print(f"\n--- Tour {budget.tours} ({duree:.1f}s) ---")
        for appel in appels:
            nom = appel["function"]["name"]
            arguments = appel["function"]["arguments"]

            # Garde-fou 2 : le même appel une deuxième fois n'apportera rien.
            if detecteur.est_repetition(appel):
                print(f"  [BOUCLE] {nom}({arguments}) déjà tenté — on arrête.")
                return None, "boucle stérile détectée"

            # Garde-fou 4 : l'erreur devient une observation.
            resultat = chercher_note(**arguments) if nom == "chercher_note" else json.dumps(
                {"erreur": f"outil inconnu : {nom}"}
            )
            marque = "ERREUR" if '"erreur"' in resultat else "ok"
            print(f"  -> {nom}({arguments})")
            print(f"     <- [{marque}] {resultat[:180]}")

            messages.append({"role": "tool", "tool_name": nom, "content": resultat})


def main() -> None:
    setup_console()
    print("=" * 70)
    print("BOUCLE SOUS GARDE-FOUS — qwen3.8:27b")
    print("=" * 70)
    print(f"Tâche : {TACHE}")
    print("\nÀ observer : le premier appel échoue sur le format, le modèle lit")
    print("le message d'erreur et se corrige seul au tour suivant. Puis il")
    print("bute sur un sujet qui n'existe pas — et doit l'admettre.\n")

    budget = Budget()
    resultat, raison = boucle_gardee(TACHE, budget)

    print("\n" + "=" * 70)
    print(f"ARRÊT : {raison}")
    print(f"CONSOMMÉ : {budget.resume()}")
    print("=" * 70)
    print(resultat if resultat else "(pas de réponse finale)")

    print("\nCE QU'IL FAUT RETENIR")
    print("- Une boucle sans budget est un bug qui attend son heure.")
    print("- Un message d'erreur d'outil est de la PÉDAGOGIE pour le modèle :")
    print("  écris-le pour être lu, avec la correction suggérée.")
    print("- Toute sortie de boucle doit être étiquetée : convergence, budget,")
    print("  ou boucle stérile. « Ça n'a rien renvoyé » n'est pas un diagnostic.")


if __name__ == "__main__":
    main()
