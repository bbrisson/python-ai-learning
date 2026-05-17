---
type: reference
title: Jupyter — Pièges par environnement
updated: 2026-04-12
---

# Jupyter — Pièges par environnement

[[Index|← Index]] | [[Environnements]]

---

## GX10 (Ubuntu)

| Situation | Problème | Solution |
|---|---|---|
| `!conda` dans une cellule | Échoue — JupyterLab tourne dans `.venv` Python 3.12, indépendant de conda | Utiliser le chemin absolu : `!/home/bbrisson/miniconda3/bin/conda` |
| `%%bash` avec conda | Échoue — nouveau processus sans `.bashrc` | Même solution : chemin absolu de conda |
| `%%bash` avec git | Fonctionne | `git` est dans le PATH système |
| Commandes `git` | Fonctionnent avec `!` ou `%%bash` | Pas de problème |
| Commandes multi-lignes | `!` ne supporte qu'une ligne | Utiliser `%%bash` |
| Commit depuis Jupyter | Risque d'erreurs | Utiliser le terminal SSH — plus fiable |

**Raison fondamentale** : JupyterLab sur le GX10 tourne dans son propre `.venv` Python 3.12, entièrement séparé de l'installation Miniconda. Le sous-processus `!` hérite du PATH de ce `.venv`, pas du `.bashrc` de l'utilisateur.

---

## Windows (VSCode)

| Situation | Comportement | Note |
|---|---|---|
| `!conda` dans une cellule | **Fonctionne** | conda est dans le PATH de `cmd.exe` après `conda init` |
| `conda activate` dans une cellule | **Ne fonctionne pas** | Exécuter dans PowerShell directement |
| Après `ipykernel install` | Le nouveau kernel n'est pas visible immédiatement | `Ctrl+Shift+P` → `Jupyter: Restart Kernel` |

---

## Analogie pour comprendre

Pense à `!` dans Jupyter comme à un `system()` en C — il lance un sous-processus avec l'environnement hérité du processus Jupyter lui-même, pas de ton shell interactif. Sur le GX10, le processus Jupyter est dans un `.venv` isolé → il n'a pas `conda` dans son `PATH`. Sur Windows, `conda init` a modifié `cmd.exe` (le shell par défaut de VSCode pour les `!`) → `conda` est accessible.
