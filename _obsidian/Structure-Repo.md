---
type: reference
title: Structure du repo
updated: 2026-04-12
---

# Structure du repo

[[Index|← Index]]

Repo GitHub : `bbrisson/python-ai-learning`

---

## Arborescence

```
python-ai-learning/
├── _obsidian/              ← notes Obsidian (ce vault)
├── 01-environnement/       ← outils : conda, jupyter, git, vscode/cursor, quarto
├── 02-python/              ← langage : bases, POO, librairies standard
├── 03-data/                ← données : numpy, pandas, visualisation
├── 04-machine-learning/    ← ML classique : scikit-learn, régression, classification
├── 05-deep-learning/       ← réseaux de neurones : pytorch, CNN, RNN
├── 06-nlp/                 ← texte : transformers, embeddings, fine-tuning
├── 07-llm/                 ← modèles de langage : API, prompt engineering
├── 08-rag/                 ← RAG : vector DB, langchain/llamaindex, agents
├── 09-projets/             ← projets intégrateurs
├── CLAUDE.md               ← instructions pour Claude Code (contexte pédagogique)
└── environment.yml         ← définition de l'env conda ai_learning
```

---

## Fichiers clés à la racine

### `environment.yml` (fichier)

Définit l'environnement conda `ai_learning` :

```yaml
name: ai_learning
channels:
  - defaults
dependencies:
  - python=3.11
  - ipykernel
```

Le `prefix` Linux a été supprimé pour assurer la portabilité GX10 ↔ Windows.

### `.gitignore` (fichier)

Exclut notamment :
- Le dossier `.ipynb_checkpoints/` (généré automatiquement par Jupyter)

---

## Contenu de `01-environnement/`

En plus des notebooks `.ipynb`, ce dossier contient des fichiers Quarto générés :

| Fichier/Dossier | Type | Description |
|---|---|---|
| `ex1_cell_options.qmd` | fichier | Exercice Quarto — cell options |
| `ex1_cell_options.html` | fichier | Rendu HTML de l'exercice |
| `ex1_cell_options_files/` | dossier | Assets bootstrap/quarto pour le HTML |
| `ex2_figures.qmd` | fichier | Exercice Quarto — figures |
| `ex2_figures.html` | fichier | Rendu HTML avec figure sinus |
| `ex3_params.qmd` | fichier | Exercice Quarto — rapport paramétré |
| `ex3_params.html` | fichier | Rendu HTML paramétré |
