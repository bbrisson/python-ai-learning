---
type: reference
title: Environnements de travail
updated: 2026-04-12
---

# Environnements de travail

[[Index|← Index]]

---

## GX10 — Machine principale (calcul AI)

| Attribut | Valeur |
|---|---|
| Machine | Asus Ascent GX10, ARM64 |
| OS | Ubuntu |
| Accès | SSH depuis le laptop Windows |
| Conda | 26.1.1 (Miniconda) |
| Conda bin | `/home/bbrisson/miniconda3/bin/conda` |
| Env actif | `ai_learning` (Python 3.11, ipykernel) |
| JupyterLab | Installé via dashboard GX10, port **11002** |
| Working dir Jupyter | `/home/bbrisson` |
| Repo | `~/work/python-ai-learning` |
| Git | 2.43.0 — Benoit Brisson, benoit@fbrisson.com |
| GitHub CLI | 2.45.0, authentifié (`bbrisson`) |

### Particularités GX10

- JupyterLab tourne dans son propre `.venv` Python 3.12 — **indépendant de conda**
- `!conda` **échoue** dans les cellules → toujours utiliser le chemin absolu
- `%%bash` **échoue** aussi pour conda (nouveau processus sans `.bashrc`)
- Les commandes `git` fonctionnent avec `!` ou `%%bash` (git est dans le PATH système)
- Commandes multi-lignes dans Jupyter : utiliser `%%bash`
- **Commiter depuis Jupyter** : utiliser le terminal SSH (plus fiable)

> Voir aussi [[Jupyter-Gotchas]]

---

## Laptop Windows — Développement / Notebooks

| Attribut | Valeur |
|---|---|
| Machine | Windows 11, x64 |
| VSCode | 1.113.0 avec extension Jupyter |
| Conda | 26.1.1 (Miniconda, mode utilisateur) |
| Conda path | `C:\Users\benoi\miniconda3` |
| Conda init | Configuré pour PowerShell |
| Envs conda | `C:\Users\benoi\.conda\envs\` |
| Env actif | `ai_learning` (Python 3.11, ipykernel) |
| Kernel enregistré | `C:\Users\benoi\AppData\Roaming\jupyter\kernels\ai_learning` |
| JupyterLab | Installé dans l'env `base`, port **8888** |
| Repo | `C:\Users\benoi\work\python-ai-learning` |
| Git | 2.52.0 |

### Particularités Windows

- `!conda` **fonctionne** dans les cellules (conda dans le PATH de `cmd.exe`)
- `conda activate` **ne fonctionne pas** dans les cellules → exécuter dans PowerShell
- Après `ipykernel install` : `Ctrl+Shift+P` → `Jupyter: Restart Kernel` pour recharger le kernel

> Voir aussi [[Jupyter-Gotchas]]
