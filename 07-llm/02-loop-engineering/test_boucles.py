"""Tests hors ligne des boucles — aucun serveur Ollama requis.

POURQUOI DES TESTS SANS MODÈLE
------------------------------
Une boucle agentique mélange deux natures de code :

- du code déterministe : budget, dispatch, validation de chemins, détection
  de cycle, nettoyage de sortie ;
- un appel non déterministe : le modèle.

Presque tous tes bugs seront dans la première catégorie, et elle se teste
comme n'importe quel code C++ : entrées connues, sorties attendues. La
technique est d'injecter un faux modèle — un script de réponses préenregistré
qui joue le rôle du serveur.

Analogie : c'est un banc de test avec un simulateur à la place de l'instrument.
Tu ne débranches pas le vrai modèle parce qu'il est mauvais, mais parce qu'un
test doit être reproductible, instantané et gratuit.

Exécution :
    python test_boucles.py          # sans dépendance
    pytest test_boucles.py -v       # si pytest est disponible
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

DOSSIER = Path(__file__).resolve().parent
sys.path.insert(0, str(DOSSIER))

from ollama_client import setup_console  # noqa: E402  (après ajustement du sys.path)


def charger(nom_fichier: str) -> Any:
    """Importer un module dont le nom commence par un chiffre.

    `import 02_boucle_outils` est une SyntaxError : un identifiant Python ne
    peut pas commencer par un chiffre. Les fichiers numérotés se chargent
    donc par leur chemin, via importlib.
    """
    chemin = DOSSIER / nom_fichier
    nom_module = chemin.stem.lstrip("0123456789_") or chemin.stem
    spec = importlib.util.spec_from_file_location(nom_module, chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom_module] = module
    spec.loader.exec_module(module)
    return module


outils = charger("02_boucle_outils.py")
gardes = charger("03_garde_fous.py")
reflexion = charger("04_boucle_reflexion.py")


# --- Sécurité des outils -------------------------------------------------


def test_chemin_hors_repo_refuse() -> None:
    """Un modèle qui hallucine `../..` ne doit pas sortir du repo."""
    for tentative in ("../../../etc/passwd", "../../.ssh/id_rsa", "..\\..\\secret"):
        try:
            outils._resoudre(tentative)
        except ValueError:
            continue
        raise AssertionError(f"chemin accepté alors qu'il sort du repo : {tentative}")


def test_chemin_dans_repo_accepte() -> None:
    assert outils._resoudre("01-environnement").name == "01-environnement"


def test_calculer_refuse_le_code() -> None:
    """`calculer` ne doit jamais devenir un `eval` déguisé."""
    for charge in ("__import__('os').system('dir')", "open('x').read()", "1 if 1 else 2"):
        resultat = json.loads(outils.calculer(charge))
        assert "erreur" in resultat, f"expression dangereuse acceptée : {charge}"


def test_calculer_arithmetique() -> None:
    assert json.loads(outils.calculer("(28318+12895)/1024"))["resultat"] == 40.24707031250
    assert "erreur" in json.loads(outils.calculer("1/0"))


def test_outil_inconnu_ne_leve_pas() -> None:
    """Un outil halluciné doit produire une observation, pas un crash."""
    appel = {"function": {"name": "outil_qui_nexiste_pas", "arguments": {}}}
    assert "erreur" in json.loads(outils.executer_outil(appel))


def test_mauvais_arguments_ne_levent_pas() -> None:
    appel = {"function": {"name": "taille_fichier", "arguments": {"mauvais": "x"}}}
    resultat = json.loads(outils.executer_outil(appel))
    assert "erreur" in resultat and "TypeError" in resultat["erreur"]


# --- Garde-fous ----------------------------------------------------------


def test_budget_tours() -> None:
    budget = gardes.Budget(max_tours=2)
    assert budget.epuise() is None
    budget.tours = 2
    assert "tours" in budget.epuise()


def test_budget_tokens() -> None:
    budget = gardes.Budget(max_tokens=100)
    budget.tokens = 100
    assert "tokens" in budget.epuise()


def test_detecteur_de_boucle() -> None:
    detecteur = gardes.DetecteurDeBoucle()
    appel = {"function": {"name": "chercher_note", "arguments": {"sujet": "conda"}}}
    autre = {"function": {"name": "chercher_note", "arguments": {"sujet": "git"}}}

    assert detecteur.est_repetition(appel) is False
    assert detecteur.est_repetition(autre) is False
    assert detecteur.est_repetition(appel) is True, "répétition non détectée"


def test_signature_insensible_a_l_ordre_des_cles() -> None:
    """Deux appels identiques aux clés près sont le MÊME appel.

    Sans `sort_keys`, `{'a':1,'b':2}` et `{'b':2,'a':1}` produiraient deux
    signatures différentes et le détecteur laisserait passer le cycle.
    """
    detecteur = gardes.DetecteurDeBoucle()
    un = {"function": {"name": "f", "arguments": {"a": 1, "b": 2}}}
    deux = {"function": {"name": "f", "arguments": {"b": 2, "a": 1}}}
    detecteur.est_repetition(un)
    assert detecteur.est_repetition(deux) is True


def test_chercher_note_erreur_pedagogique() -> None:
    """Le message d'erreur doit contenir la correction à appliquer."""
    resultat = json.loads(gardes.chercher_note("Conda"))
    assert resultat["erreur"] == "format invalide"
    assert "conda" in resultat["detail"], "l'erreur n'indique pas la correction"
    assert resultat["sujets_valides"] == ["conda", "git", "kernel"]


# --- Boucle de réflexion -------------------------------------------------


def test_nettoyer_code_retire_les_clotures() -> None:
    brut = "```python\ndef f():\n    return 1\n```"
    assert reflexion.nettoyer_code(brut) == "def f():\n    return 1"


def test_nettoyer_code_laisse_le_code_nu() -> None:
    assert reflexion.nettoyer_code("def f():\n    return 1") == "def f():\n    return 1"


def test_verifier_syntaxe() -> None:
    assert reflexion.verifier_syntaxe("def f():\n    return 1") is None
    assert "compile pas" in reflexion.verifier_syntaxe("def f(:\n  pass")


# --- La boucle complète, avec un faux modèle -----------------------------


class FauxModele:
    """Rejoue une séquence de réponses préenregistrées.

    Signature compatible avec `timed_chat` : retourne `(message, duree)`.
    """

    def __init__(self, reponses: list[dict[str, Any]]) -> None:
        self.reponses = list(reponses)
        self.appels: list[list[dict[str, Any]]] = []

    def __call__(self, messages, tools=None, **kwargs):  # noqa: ANN001
        # On mémorise une copie : c'est ce qui permet de vérifier que la
        # boucle a bien réinjecté l'historique.
        self.appels.append([dict(m) for m in messages])
        if not self.reponses:
            raise AssertionError("la boucle a fait plus d'appels que prévu")
        return self.reponses.pop(0), 0.0


def _tool_call(nom: str, **arguments: Any) -> dict[str, Any]:
    return {"function": {"name": nom, "arguments": arguments}}


def test_boucle_agentique_converge(monkeypatch: Any = None) -> None:
    """Deux tours d'outil puis une réponse finale."""
    faux = FauxModele(
        [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [_tool_call("lister_fichiers", dossier="01-environnement", extension=".ipynb")],
            },
            {"role": "assistant", "content": "Il y a 5 notebooks."},
        ]
    )
    original = outils.timed_chat
    outils.timed_chat = faux
    try:
        resultat = outils.boucle_agentique("combien de notebooks ?")
    finally:
        outils.timed_chat = original

    assert resultat == "Il y a 5 notebooks."
    # Le deuxième appel doit contenir système + user + assistant + tool.
    assert len(faux.appels[1]) == 4
    assert faux.appels[1][-1]["role"] == "tool"
    assert "01-setup.ipynb" in faux.appels[1][-1]["content"]


def test_boucle_agentique_respecte_le_budget() -> None:
    """Un modèle qui ne s'arrête jamais doit être coupé, pas subi."""
    boucle_infinie = [
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [_tool_call("calculer", expression=f"1+{i}")],
        }
        for i in range(outils.MAX_TOURS)
    ]
    faux = FauxModele(boucle_infinie)
    original = outils.timed_chat
    outils.timed_chat = faux
    try:
        resultat = outils.boucle_agentique("boucle sans fin")
    finally:
        outils.timed_chat = original

    assert resultat is None, "la boucle aurait dû être coupée par le budget"
    assert len(faux.appels) == outils.MAX_TOURS


def test_boucle_gardee_detecte_le_cycle() -> None:
    """Le même appel deux fois de suite : arrêt immédiat, raison explicite."""
    repete = {
        "role": "assistant",
        "content": "",
        "tool_calls": [_tool_call("chercher_note", sujet="Conda")],
    }
    faux = FauxModele([repete, dict(repete)])
    original = gardes.timed_chat
    gardes.timed_chat = faux
    try:
        resultat, raison = gardes.boucle_gardee("test", gardes.Budget())
    finally:
        gardes.timed_chat = original

    assert resultat is None
    assert raison == "boucle stérile détectée"


# --- Exécution sans pytest ----------------------------------------------


def main() -> int:
    setup_console()
    tests = [
        (nom, objet)
        for nom, objet in sorted(globals().items())
        if nom.startswith("test_") and callable(objet)
    ]
    echecs = 0

    for nom, test in tests:
        try:
            test()
        except AssertionError as exc:
            echecs += 1
            print(f"ECHEC  {nom}\n       {exc}")
        except Exception as exc:  # noqa: BLE001
            echecs += 1
            print(f"ERREUR {nom}\n       {type(exc).__name__}: {exc}")
        else:
            print(f"ok     {nom}")

    print(f"\n{len(tests) - echecs}/{len(tests)} tests passés.")
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
