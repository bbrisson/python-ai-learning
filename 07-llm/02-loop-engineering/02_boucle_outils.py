"""Exemple 2 — La boucle agentique : le modèle décide, ton code exécute.

POURQUOI
--------
C'est ici que « loop engineering » prend son sens. Un LLM ne peut rien faire
d'autre que produire du texte. Il ne lit pas un fichier, il ne calcule pas.
Ce qu'il sait faire, c'est demander : « appelle `taille_fichier` avec ce
chemin ». L'exécution, c'est TOI.

La boucle agentique est donc un protocole en trois temps qui tourne jusqu'à
stabilisation :

    1. envoyer l'état (messages + outils disponibles)
    2. si la réponse contient des `tool_calls` : les exécuter, ajouter les
       résultats à l'état, RECOMMENCER
    3. sinon : le modèle a produit du texte final -> sortir

Analogie LabVIEW : c'est exactement une boucle While avec un registre à
décalage (`messages`) et une structure Case pilotée par un enum reçu de
l'extérieur. Analogie C : une boucle d'événements avec dispatch sur un
`switch`, où le producteur d'événements est le modèle.

Point de vocabulaire important : le modèle n'a AUCUN pouvoir d'exécution.
`tool_calls` est une demande, pas un ordre. Tout ce que ta table de dispatch
refuse de faire n'arrivera jamais. C'est là que se place la sécurité.

Détail Ollama (piège) : `arguments` arrive déjà décodé en dict Python. Avec
l'API OpenAI c'est une *string* JSON qu'il faut passer à `json.loads`. Un
copier-coller entre les deux écosystèmes plante ici.

Exécution :
    python 02_boucle_outils.py
"""

from __future__ import annotations

import ast
import json
import operator
from pathlib import Path
from typing import Any, Callable

from ollama_client import setup_console, timed_chat


# Racine autorisée : le repo. Aucun outil ne sortira de cet arbre.
RACINE = Path(__file__).resolve().parents[2]


# --- Implémentation réelle des outils ------------------------------------

def _resoudre(chemin: str) -> Path:
    """Résoudre un chemin en refusant toute sortie du repo.

    Sans ce garde-fou, un modèle qui hallucine `../../../etc/passwd` (ou
    `C:/Users/benoi/.ssh/`) serait servi docilement. La règle : on valide
    APRÈS résolution des `..`, jamais avant.
    """
    cible = (RACINE / chemin).resolve()
    if not cible.is_relative_to(RACINE):
        raise ValueError(f"Chemin hors du repo, refusé : {chemin}")
    return cible


def lister_fichiers(dossier: str, extension: str = "") -> str:
    """Lister les fichiers d'un dossier du repo, filtrés par extension."""
    cible = _resoudre(dossier)
    if not cible.is_dir():
        return json.dumps({"erreur": f"{dossier} n'est pas un dossier"})

    motif = f"*{extension}" if extension else "*"
    noms = sorted(p.name for p in cible.glob(motif) if p.is_file())
    return json.dumps({"dossier": dossier, "fichiers": noms}, ensure_ascii=False)


def taille_fichier(chemin: str) -> str:
    """Retourner la taille d'un fichier du repo, en octets."""
    cible = _resoudre(chemin)
    if not cible.is_file():
        return json.dumps({"erreur": f"{chemin} introuvable"})
    return json.dumps({"chemin": chemin, "octets": cible.stat().st_size})


_OPERATEURS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.Pow: operator.pow,
}


def calculer(expression: str) -> str:
    """Évaluer une expression arithmétique, sans `eval`.

    `eval()` sur une chaîne produite par un LLM est une exécution de code
    arbitraire. On parcourt l'AST et on n'autorise que des nombres et cinq
    opérateurs — tout le reste lève.
    """

    def evaluer(noeud: ast.AST) -> float:
        if isinstance(noeud, ast.Constant) and isinstance(noeud.value, (int, float)):
            return noeud.value
        if isinstance(noeud, ast.BinOp) and type(noeud.op) in _OPERATEURS:
            return _OPERATEURS[type(noeud.op)](evaluer(noeud.left), evaluer(noeud.right))
        if isinstance(noeud, ast.UnaryOp) and type(noeud.op) in _OPERATEURS:
            return _OPERATEURS[type(noeud.op)](evaluer(noeud.operand))
        raise ValueError("Expression non autorisée")

    try:
        resultat = evaluer(ast.parse(expression, mode="eval").body)
    except (ValueError, SyntaxError, ZeroDivisionError, TypeError) as exc:
        return json.dumps({"erreur": f"{expression} : {exc}"}, ensure_ascii=False)
    return json.dumps({"expression": expression, "resultat": resultat})


# La table de dispatch : le `switch` de la boucle d'événements.
DISPATCH: dict[str, Callable[..., str]] = {
    "lister_fichiers": lister_fichiers,
    "taille_fichier": taille_fichier,
    "calculer": calculer,
}


# --- Déclaration des outils envoyée au modèle ----------------------------
#
# Ces schémas JSON sont injectés dans le prompt par le template du modèle.
# Ils coûtent des tokens à CHAQUE tour de boucle : une description bavarde
# se paye N fois. Mais une description trop vague fait choisir le mauvais
# outil, ce qui coûte un tour entier. C'est l'arbitrage central du métier.

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "lister_fichiers",
            "description": "Liste les fichiers d'un dossier du repo d'apprentissage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dossier": {
                        "type": "string",
                        "description": "Chemin relatif à la racine du repo, ex: '01-environnement'.",
                    },
                    "extension": {
                        "type": "string",
                        "description": "Filtre optionnel, ex: '.ipynb'.",
                    },
                },
                "required": ["dossier"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "taille_fichier",
            "description": "Retourne la taille en octets d'un fichier du repo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chemin": {
                        "type": "string",
                        "description": "Chemin relatif, ex: '01-environnement/01-setup.ipynb'.",
                    },
                },
                "required": ["chemin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Évalue une expression arithmétique, ex: '(120+340)/1024'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                },
                "required": ["expression"],
            },
        },
    },
]


SYSTEME = {
    "role": "system",
    "content": (
        "Tu es un assistant qui inspecte un repo d'apprentissage Python/IA. "
        "Utilise les outils pour obtenir des faits — n'invente jamais un nom "
        "de fichier ni une taille. Quand tu as assez d'informations, donne "
        "une réponse finale courte, en français."
    ),
}

TACHE = (
    "Combien de notebooks Jupyter (.ipynb) y a-t-il dans le dossier "
    "01-environnement, et quelle est leur taille totale en kilooctets ?"
)

MAX_TOURS = 8


def executer_outil(appel: dict[str, Any]) -> str:
    """Exécuter un `tool_call` et retourner son résultat en texte.

    Une exception d'outil n'est PAS une panne de la boucle : on la renvoie
    au modèle comme observation. Il corrige souvent son appel tout seul au
    tour suivant. C'est le cœur du sujet — voir l'exemple 03.
    """
    nom = appel["function"]["name"]
    arguments = appel["function"]["arguments"]  # déjà un dict côté Ollama

    fonction = DISPATCH.get(nom)
    if fonction is None:
        return json.dumps({"erreur": f"outil inconnu : {nom}"})

    try:
        return fonction(**arguments)
    except Exception as exc:  # noqa: BLE001 — on veut tout renvoyer au modèle
        return json.dumps({"erreur": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False)


def boucle_agentique(tache: str) -> str | None:
    """La boucle. Une quarantaine de lignes, et c'est tout un agent."""
    messages: list[dict[str, Any]] = [SYSTEME, {"role": "user", "content": tache}]

    for tour in range(1, MAX_TOURS + 1):
        reponse, duree = timed_chat(messages, TOOLS)
        messages.append(reponse)

        appels = reponse.get("tool_calls")
        if not appels:
            # Condition d'arrêt : plus aucune demande d'outil.
            print(f"\n--- Tour {tour} ({duree:.1f}s) : réponse finale ---")
            return reponse["content"].strip()

        print(f"\n--- Tour {tour} ({duree:.1f}s) : {len(appels)} appel(s) d'outil ---")
        for appel in appels:
            nom = appel["function"]["name"]
            resultat = executer_outil(appel)
            print(f"  -> {nom}({appel['function']['arguments']})")
            print(f"     <- {resultat[:160]}")

            # Le résultat retourne dans l'état, avec le rôle `tool`.
            messages.append({"role": "tool", "tool_name": nom, "content": resultat})

    # Budget épuisé sans convergence : c'est un échec, il doit se voir.
    print(f"\n[ARRÊT] {MAX_TOURS} tours atteints sans réponse finale.")
    return None


def main() -> None:
    setup_console()
    print("=" * 70)
    print("BOUCLE AGENTIQUE — qwen3.8:27b avec 3 outils")
    print("=" * 70)
    print(f"Tâche : {TACHE}")

    resultat = boucle_agentique(TACHE)

    print("\n" + "=" * 70)
    print("RÉSULTAT")
    print("=" * 70)
    print(resultat if resultat else "(aucune réponse finale — budget épuisé)")


if __name__ == "__main__":
    main()
