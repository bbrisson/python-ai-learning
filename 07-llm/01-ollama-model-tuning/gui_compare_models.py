"""GUI Streamlit pour comparer un modèle Ollama de base et un modèle personnalisé.

Cette interface permet de :
    - poser la même question à deux modèles Ollama ;
    - visualiser les réponses côte à côte ;
    - afficher une configuration de référence pour le modèle de base ;
    - éditer le `Modelfile` du modèle personnalisé ;
    - sauvegarder localement le `Modelfile` ;
    - afficher les commandes pour mettre à jour `prof-python-ai` sur le serveur.

Important : cette première version n'exécute pas automatiquement `ssh`, `scp`
ou `ollama create`. Elle affiche les commandes à lancer pour garder l'exercice
sûr et pédagogique.
"""

from __future__ import annotations

import json
from pathlib import Path
import urllib.error
import urllib.request

try:
    import streamlit as st
except ModuleNotFoundError as exc:  # pragma: no cover - message utile au lancement
    raise SystemExit(
        "Streamlit n'est pas installé dans cet environnement.\n\n"
        "Commande d'installation proposée :\n"
        "    pip install streamlit\n\n"
        "Commande de lancement ensuite :\n"
        "    streamlit run 07-llm/01-ollama-model-tuning/gui_compare_models.py"
    ) from exc


OLLAMA_URL = "http://192.168.18.5:11434/api/generate"
BASE_MODEL = "llama3.2:3b"
CUSTOM_MODEL = "prof-python-ai"

PROJECT_PATH_ON_SERVER = "/home/bbrisson/work/python-ai-learning"
EXAMPLE_PATH_ON_SERVER = f"{PROJECT_PATH_ON_SERVER}/07-llm/01-ollama-model-tuning"
SSH_TARGET = "bbrisson@192.168.18.5"

CURRENT_DIR = Path(__file__).resolve().parent
MODELFILE_PATH = CURRENT_DIR / "Modelfile"

BASE_MODEL_REFERENCE = """FROM llama3.2:3b

# Modèle de base utilisé tel quel.
# Il n'a pas de SYSTEM prompt spécialisé dans cet exemple.
# Il sert de point de comparaison avec prof-python-ai.
"""

DEFAULT_QUESTION = (
    "Explique en français, pour un débutant, la différence entre "
    "un environnement conda et un kernel Jupyter. "
    "Si possible, fais un lien avec une personne qui connaît déjà C/C++ ou LabVIEW."
)


def read_modelfile() -> str:
    """Lire le Modelfile local."""

    return MODELFILE_PATH.read_text(encoding="utf-8")


def write_modelfile(content: str) -> None:
    """Sauvegarder le Modelfile local."""

    MODELFILE_PATH.write_text(content, encoding="utf-8")


def ask_ollama(model_name: str, prompt: str) -> str:
    """Envoyer un prompt à un modèle Ollama."""

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
        with urllib.request.urlopen(request, timeout=180) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Impossible de joindre Ollama à {OLLAMA_URL} pour {model_name}. "
            f"Détail: {error}"
        ) from error

    data = json.loads(response_body)
    if "response" not in data:
        raise RuntimeError(f"Réponse inattendue de Ollama pour {model_name}: {data}")

    return data["response"]


def update_commands() -> tuple[str, str]:
    """Retourner les commandes de synchronisation et recréation du modèle."""

    git_workflow = f"""# Depuis Windows, après avoir modifié le Modelfile local :
git add 07-llm/01-ollama-model-tuning/Modelfile
git commit -m "Update prof-python-ai Modelfile"
git push

# Sur le serveur Ollama :
ssh {SSH_TARGET} "cd {PROJECT_PATH_ON_SERVER} && git pull && cd {EXAMPLE_PATH_ON_SERVER} && ollama create {CUSTOM_MODEL} -f Modelfile && ollama list"
"""

    scp_workflow = f"""# Copier seulement le Modelfile local vers le serveur :
scp 07-llm/01-ollama-model-tuning/Modelfile {SSH_TARGET}:{EXAMPLE_PATH_ON_SERVER}/Modelfile

# Recréer le modèle personnalisé sur le serveur :
ssh {SSH_TARGET} "cd {EXAMPLE_PATH_ON_SERVER} && ollama create {CUSTOM_MODEL} -f Modelfile && ollama list"
"""

    return git_workflow, scp_workflow


def render_analysis_help() -> None:
    """Afficher une grille d'analyse des différences."""

    with st.expander("Grille d'analyse des différences", expanded=True):
        st.markdown(
            """
Compare les deux réponses avec ces critères :

1. **Langue** — Les deux réponses sont-elles bien en français ?
2. **Niveau débutant** — La réponse est-elle compréhensible pour quelqu'un qui débute en Python ?
3. **Structure pédagogique** — Y a-t-il une progression logique, des étapes, des titres ?
4. **Précision technique** — La différence conda/kernel Jupyter est-elle exacte ?
5. **Adaptation au profil** — Le lien avec C/C++ ou LabVIEW est-il utile ?
6. **Effet du Modelfile** — `prof-python-ai` est-il plus patient, précis et pédagogique ?

Point important : un `Modelfile` influence le **comportement** du modèle,
mais ne garantit pas automatiquement la vérité technique.
"""
        )


def main() -> None:
    """Construire la GUI Streamlit."""

    st.set_page_config(
        page_title="Ollama model tuning — comparaison",
        layout="wide",
    )

    st.title("Ollama model tuning — comparaison côte à côte")
    st.caption("Comparaison entre le modèle de base et le modèle personnalisé.")

    st.info(
        "Cette GUI sauvegarde le `Modelfile` localement et affiche les commandes "
        "pour mettre à jour le modèle sur le serveur. Elle n'exécute pas `ssh`, "
        "`scp` ou `ollama create` automatiquement."
    )

    question = st.text_area(
        "Question commune aux deux modèles",
        value=DEFAULT_QUESTION,
        height=120,
    )

    left, right = st.columns(2)

    with left:
        st.subheader(f"Modèle de base — `{BASE_MODEL}`")
        st.text_area(
            "Configuration de référence du modèle de base",
            value=BASE_MODEL_REFERENCE,
            height=260,
            disabled=True,
        )

    with right:
        st.subheader(f"Modèle personnalisé — `{CUSTOM_MODEL}`")
        modelfile_content = st.text_area(
            "Modelfile éditable du modèle personnalisé",
            value=read_modelfile(),
            height=260,
        )

        if st.button("Sauvegarder le Modelfile local", type="secondary"):
            write_modelfile(modelfile_content)
            st.success(f"Modelfile sauvegardé : {MODELFILE_PATH}")

    generate = st.button("Générer les réponses des deux modèles", type="primary")

    if generate:
        response_left, response_right = st.columns(2)

        with st.spinner("Appel des modèles Ollama en cours..."):
            try:
                base_answer = ask_ollama(BASE_MODEL, question)
                custom_answer = ask_ollama(CUSTOM_MODEL, question)
            except RuntimeError as error:
                st.error(str(error))
                return

        with response_left:
            st.subheader(f"Réponse — `{BASE_MODEL}`")
            st.markdown(base_answer)

        with response_right:
            st.subheader(f"Réponse — `{CUSTOM_MODEL}`")
            st.markdown(custom_answer)

        render_analysis_help()

    st.divider()
    st.subheader("Mettre à jour le modèle personnalisé")
    st.markdown(
        "Après modification du `Modelfile`, il faut recréer `prof-python-ai` "
        "sur le serveur Ollama pour que les changements prennent effet."
    )

    git_commands, scp_commands = update_commands()
    update_tab_git, update_tab_scp = st.tabs(["Workflow Git", "Workflow scp rapide"])

    with update_tab_git:
        st.code(git_commands, language="bash")

    with update_tab_scp:
        st.code(scp_commands, language="bash")


if __name__ == "__main__":
    main()