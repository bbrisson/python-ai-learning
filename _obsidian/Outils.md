---
type: reference
title: Inventaire des outils
updated: 2026-04-12
---

# Inventaire des outils

[[Index|← Index]]

---

## Conda

| | GX10 | Windows |
|---|---|---|
| Version | 26.1.1 | 26.1.1 |
| Distribution | Miniconda | Miniconda (mode utilisateur) |
| Chemin | `/home/bbrisson/miniconda3/` | `C:\Users\benoi\miniconda3\` |
| Env créés dans | `~/miniconda3/envs/` | `C:\Users\benoi\.conda\envs\` |
| Init shell | `.bashrc` | PowerShell |

### Environnement `ai_learning`

```
Python 3.11
ipykernel
```

Commande pour recréer depuis le fichier `environment.yml` (fichier à la racine du repo) :
```bash
conda env create -f environment.yml
```

---

## Git

| | GX10 | Windows |
|---|---|---|
| Version | 2.43.0 | 2.52.0 |
| User | Benoit Brisson | Benoit Brisson |
| Email | benoit@fbrisson.com | benoit@fbrisson.com |

---

## GitHub CLI (`gh`)

| | GX10 | Windows |
|---|---|---|
| Version | 2.45.0 | — |
| Authentifié | Oui (`bbrisson`) | — |

---

## JupyterLab

| | GX10 | Windows |
|---|---|---|
| Installé dans | Dashboard GX10 (`.venv` Python 3.12) | Env conda `base` |
| Port | 11002 | 8888 |
| Working dir | `/home/bbrisson` | — |

---

## VSCode

| Attribut | Valeur |
|---|---|
| Version | 1.113.0 |
| Extension | Jupyter |
| Machine | Laptop Windows uniquement |

---

## Quarto

Outil de publication scientifique — produit des rapports HTML, PDF, slides à partir de fichiers `.qmd` (Markdown + code Python/R).

- Appris dans `06-quarto.ipynb` (EN COURS)
- Exercices présents dans `01-environnement/` : `ex1_cell_options.qmd`, `ex2_figures.qmd`, `ex3_params.qmd`
- Commande de rendu : `quarto render <fichier>.qmd` (fichier)
