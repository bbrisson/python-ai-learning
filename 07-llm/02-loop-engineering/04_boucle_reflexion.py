"""Exemple 4 — Boucle de réflexion : générer, juger, corriger.

POURQUOI
--------
Les exemples 2 et 3 bouclent sur des *outils*. Ici on boucle sur la
*qualité*. C'est la deuxième grande famille de boucles, et sa condition
d'arrêt ne tombe pas toute seule : il n'y a pas de `tool_calls` vide pour
te dire que c'est fini. Tu dois la fabriquer.

Le schéma est celui d'une régulation en boucle fermée :

    générateur -> artefact -> juge -> écart -> générateur -> ...

Deux décisions d'ingénierie font toute la différence entre un truc qui
s'améliore et un truc qui tourne en rond :

1. LE JUGE DOIT AVOIR UN CONTEXTE PROPRE.
   Si tu demandes au même fil de conversation « critique ta réponse », il
   voit son propre raisonnement et le défend. Il faut une conversation
   neuve, qui ne reçoit que le cahier des charges et l'artefact — pas
   l'historique du générateur. On instancie deux listes `messages`
   distinctes. C'est de l'isolation d'état, exactement comme on ne partage
   pas un buffer entre deux threads pour éviter qu'ils se corrompent.

2. LA CONDITION D'ARRÊT DOIT ÊTRE LISIBLE PAR MACHINE.
   Un juge qui répond « c'est plutôt bien, mais on pourrait améliorer la
   gestion d'erreur » n'est pas exploitable par un `if`. On force donc une
   sortie JSON avec le paramètre `format` d'Ollama, qui contraint le
   décodage au schéma fourni. On obtient `{"accepte": bool, "score": int,
   "problemes": [...]}` — et là on peut brancher un `while`.

Troisième garde-fou, spécifique à cette famille : le PLAFONNEMENT. Si le
score ne progresse plus d'une itération à l'autre, continuer ne sert à rien
et fait souvent régresser. On garde alors la meilleure version vue, pas la
dernière produite — nuance qui compte.

Exécution :
    python 04_boucle_reflexion.py
"""

from __future__ import annotations

import json
from typing import Any

from ollama_client import setup_console, timed_chat


CAHIER_DES_CHARGES = """\
Écris une fonction Python `formater_octets(n)` qui convertit un nombre
d'octets en chaîne lisible (ex: 1536 -> '1.5 Kio').

Exigences :
- unités binaires : o, Kio, Mio, Gio, Tio (1024) ;
- une décimale, sauf pour les octets bruts qui restent entiers ;
- refuser les valeurs négatives avec une ValueError explicite ;
- accepter les entiers ET les flottants ;
- docstring en français, annotations de type ;
- aucune dépendance externe.
"""

# Le schéma qui rend le verdict exploitable par du code.
SCHEMA_VERDICT: dict[str, Any] = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 10},
        "accepte": {"type": "boolean"},
        "problemes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["score", "accepte", "problemes"],
}

SEUIL_ACCEPTATION = 9
MAX_REVISIONS = 4


def generer(consigne: str, retours: list[str]) -> str:
    """Produire (ou corriger) le code.

    Le générateur reçoit un contexte MINIMAL : le cahier des charges et la
    liste des reproches. Pas l'historique complet des versions précédentes.
    Réinjecter tous les brouillons ratés fait dériver le modèle vers ses
    propres erreurs — il les a sous les yeux, il les recopie.
    """
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "Tu es un développeur Python senior. Tu réponds UNIQUEMENT "
                "avec le code de la fonction, sans texte autour, sans bloc "
                "markdown."
            ),
        },
        {"role": "user", "content": consigne},
    ]

    if retours:
        reproches = "\n".join(f"- {r}" for r in retours)
        messages.append(
            {
                "role": "user",
                "content": (
                    f"La version précédente a été refusée pour ces raisons :\n"
                    f"{reproches}\n\nRéécris la fonction COMPLÈTE en corrigeant "
                    f"tout ce qui précède."
                ),
            }
        )

    reponse, duree = timed_chat(messages, temperature=0.2)
    print(f"    [générateur : {duree:.1f}s]")
    return nettoyer_code(reponse["content"])


def nettoyer_code(texte: str) -> str:
    """Retirer les clôtures markdown que le modèle ajoute malgré la consigne.

    Un modèle obéit aux instructions de format « la plupart du temps ». Une
    boucle robuste ne suppose jamais qu'une consigne de format a été suivie :
    elle normalise. C'est moins cher qu'un tour de boucle supplémentaire.
    """
    texte = texte.strip()
    if texte.startswith("```"):
        lignes = texte.splitlines()
        lignes = lignes[1:]  # retire ```python
        if lignes and lignes[-1].strip() == "```":
            lignes = lignes[:-1]
        texte = "\n".join(lignes)
    return texte.strip()


def juger(consigne: str, code: str) -> dict[str, Any]:
    """Évaluer le code dans une conversation NEUVE, avec sortie contrainte.

    Noter qu'aucun message du générateur n'entre ici. Le juge ne sait pas
    qui a écrit le code ni combien de fois il a été repris — donc il ne
    s'auto-congratule pas et ne s'acharne pas.
    """
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "Tu es un relecteur de code sévère mais juste. Tu vérifies "
                "point par point le cahier des charges. Tu réponds en JSON."
            ),
        },
        {
            "role": "user",
            "content": (
                f"CAHIER DES CHARGES :\n{consigne}\n\n"
                f"CODE À ÉVALUER :\n{code}\n\n"
                f"Donne un score sur 10, la liste précise des exigences non "
                f"respectées, et accepte=true seulement si le code respecte "
                f"TOUT le cahier des charges."
            ),
        },
    ]

    reponse, duree = timed_chat(messages, fmt=SCHEMA_VERDICT)
    print(f"    [juge : {duree:.1f}s]")

    try:
        return json.loads(reponse["content"])
    except json.JSONDecodeError:
        # `format` contraint le décodage, mais on ne parie jamais là-dessus :
        # un verdict illisible doit dégrader proprement, pas planter la boucle.
        return {"score": 0, "accepte": False, "problemes": ["verdict illisible"]}


def verifier_syntaxe(code: str) -> str | None:
    """Vérification déterministe AVANT d'appeler le juge.

    Un LLM juge coûte 10 secondes ; `compile()` coûte 0,1 milliseconde et ne
    se trompe jamais sur une SyntaxError. Règle générale du loop engineering :
    tout ce qu'un contrôle déterministe peut trancher ne doit jamais être
    confié au modèle.
    """
    try:
        compile(code, "<artefact>", "exec")
    except SyntaxError as exc:
        return f"le code ne compile pas : ligne {exc.lineno}, {exc.msg}"
    return None


def boucle_de_reflexion(consigne: str) -> tuple[str, dict[str, Any], str]:
    """Générer/juger/corriger jusqu'à acceptation, plafonnement ou budget.

    Returns:
        (meilleur code, meilleur verdict, raison d'arrêt).
    """
    retours: list[str] = []
    meilleur_code = ""
    meilleur_verdict: dict[str, Any] = {"score": -1, "accepte": False, "problemes": []}

    for revision in range(1, MAX_REVISIONS + 1):
        print(f"\n--- Révision {revision}/{MAX_REVISIONS} ---")

        code = generer(consigne, retours)

        erreur_syntaxe = verifier_syntaxe(code)
        if erreur_syntaxe:
            print(f"    [syntaxe] REFUS immédiat : {erreur_syntaxe}")
            retours = [erreur_syntaxe]
            continue

        verdict = juger(consigne, code)
        score = verdict["score"]
        print(f"    score {score}/10, accepté={verdict['accepte']}")
        for probleme in verdict["problemes"]:
            print(f"      - {probleme}")

        # On mémorise la MEILLEURE version, pas la dernière.
        if score > meilleur_verdict["score"]:
            meilleur_code, meilleur_verdict = code, verdict
        elif score <= meilleur_verdict["score"]:
            # Plafonnement : une révision qui n'améliore plus rien.
            print("    [plafond] le score ne progresse plus.")
            return meilleur_code, meilleur_verdict, "plafonnement du score"

        if verdict["accepte"] and score >= SEUIL_ACCEPTATION:
            return code, verdict, "accepté par le juge"

        retours = verdict["problemes"]

    return meilleur_code, meilleur_verdict, f"budget de {MAX_REVISIONS} révisions épuisé"


def main() -> None:
    setup_console()
    print("=" * 70)
    print("BOUCLE DE RÉFLEXION — générateur + juge (qwen3.8:27b)")
    print("=" * 70)
    print(CAHIER_DES_CHARGES)

    code, verdict, raison = boucle_de_reflexion(CAHIER_DES_CHARGES)

    print("\n" + "=" * 70)
    print(f"ARRÊT : {raison} — meilleur score {verdict['score']}/10")
    print("=" * 70)
    print(code)

    print("\n" + "=" * 70)
    print("CE QU'IL FAUT RETENIR")
    print("=" * 70)
    print("- Juge et générateur = deux contextes séparés, sinon complaisance.")
    print("- Une condition d'arrêt doit être un booléen, pas une phrase :")
    print("  d'où la sortie JSON contrainte par `format`.")
    print("- Ce qu'un contrôle déterministe peut trancher (compile, tests,")
    print("  linter), ne le demande pas au modèle : c'est plus sûr et gratuit.")
    print("- Garde la meilleure version, pas la dernière.")


if __name__ == "__main__":
    main()
