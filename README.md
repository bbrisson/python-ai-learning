# Python AI Learning

Parcours personnel d'apprentissage de Python, de l'IA et de la construction
d'applications autour des modèles de langage.

Le dépôt suit deux règles simples : comprendre le **pourquoi** avant le
**comment**, puis vérifier chaque concept avec du code exécutable.

## État actuel

- environnement Conda : `ai_learning`, Python 3.11 ;
- module actif : `01-environnement/06-quarto.ipynb` ;
- bases Python : `02-python/01-bases.ipynb`, créé mais non complété ;
- laboratoire LLM : personnalisation et comparaison de modèles avec Ollama ;
- nouveau parcours préparé : Pydantic, FastAPI, Outlines, LangChain et
  LangGraph.

Le nouveau matériel est disponible dès maintenant, mais reste marqué **à
étudier**. Cela préserve l'ordre d'apprentissage existant : ajouter un cours au
dépôt ne signifie pas qu'il a déjà été suivi.

## Travaux déjà présents

- [Laboratoire Ollama](07-llm/01-ollama-model-tuning/README.md) — modèle
  personnalisé et comparaison avec Streamlit ;
- [Choix d'architecture pour les outils internes](09-projets/architecture-outils-internes/CHOIX_ARCHITECTURE_OUTILS_INTERNES.md)
  — analyse FastAPI/HTMX, sécurité et déploiement ;
- [Assistant d'apprentissage IA](09-projets/02-assistant-apprentissage-ia/README.md)
  — mise en pratique des cinq nouvelles technologies.

## Carte du dépôt

| Dossier | Rôle |
|---|---|
| `01-environnement/` | Conda, Git, Jupyter, VS Code et Quarto |
| `02-python/` | Langage Python et bibliothèque standard |
| `03-data/` | NumPy, pandas et visualisation |
| `04-machine-learning/` | Apprentissage automatique classique |
| `05-deep-learning/` | Réseaux de neurones et PyTorch |
| `06-nlp/` | Traitement du langage et transformers |
| `07-llm/` | Modèles de langage, Ollama et sorties structurées |
| `08-rag/` | RAG, chaînes et workflows avec état |
| `09-projets/` | Architecture et projets intégrateurs |
| `_obsidian/` | Index, progression et références du parcours |

## Parcours applications IA modernes

Le projet
[`09-projets/02-assistant-apprentissage-ia/`](09-projets/02-assistant-apprentissage-ia/README.md)
enseigne les technologies dans cet ordre :

1. **Pydantic** — définir et valider les contrats de données ;
2. **FastAPI** — exposer ces contrats sur une frontière HTTP ;
3. **Outlines** — contraindre une sortie de LLM avec le même schéma ;
4. **LangChain** — composer un prompt, un modèle et un parseur ;
5. **LangGraph** — orchestrer un workflow avec état et branchements.

L'exemple final est un assistant qui fabrique un plan d'étude et choisit une
branche de révision ou de progression selon un score. Les tests normaux ne
contactent aucun service externe ; l'appel au serveur Ollama est un exercice
explicite et séparé.

## Reproduire l'environnement

Depuis la racine du dépôt, le fichier `environment.yml` est le manifeste
portable Windows/GX10 :

```powershell
conda env update -n ai_learning -f environment.yml
conda activate ai_learning
```

Pour exécuter uniquement les tests du nouveau projet :

```powershell
cd 09-projets/02-assistant-apprentissage-ia
python -m pytest
```

Les commandes et les résultats attendus propres à chaque technologie sont
documentés dans les chapitres du projet.
