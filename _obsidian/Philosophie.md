---
type: reference
title: Philosophie et règles pédagogiques
updated: 2026-04-12
---

# Philosophie et règles pédagogiques

[[Index|← Index]]

---

## Philosophie du projet

| Principe | Détail |
|---|---|
| Un kernel par projet | Via `ipykernel` — chaque env conda a son kernel isolé |
| JupyterLab dans `base` | Les kernels sont dans des envs séparés — pas dans `base` |
| Tout versionner | Tout le code et les notebooks vont sur GitHub |
| Auditer avant d'installer | Vérifier ce qui existe avant d'ajouter quoi que ce soit |
| Documenter au fur et à mesure | Les how-to sont documentés dans les notebooks au moment où on les découvre |

---

## Profil apprenant

- Background **C/C++ et LabVIEW** — expertise systèmes bas niveau
- Nouveau à **Python** et à l'écosystème **AI/ML**
- Préfère les **explications techniques et profondes** — pas superficielles
- Les analogies avec des concepts de programmation (POO, pointeurs, ABI) sont bienvenues

---

## Règles pédagogiques (avec Claude Code)

- **Auditer d'abord** : avant toute installation ou configuration, vérifier ce qui existe
- **Adapter à l'environnement réel** : conseils spécifiques à GX10 / Windows, pas génériques
- **POURQUOI avant COMMENT** : la raison précède la commande
- **Signaler les approches pro** : toujours mentionner s'il existe une meilleure pratique
- **Être descriptif** : expliquer ce que la commande fait, ce qu'on voit, ce qu'on répond
- **Corriger ouvertement** : si une approche précédente n'était pas optimale, le dire clairement
- **Explications complètes** : pas de réponses superficielles
- **Pas de prochaine étape proposée** : c'est l'apprenant qui décide quand avancer
- **Ordre d'apprentissage strict** : ne pas sauter d'étapes
- **Fichier vs dossier** : toujours préciser si un pattern/nom cible un fichier ou un dossier

---

## Accomplissements à ce jour

- ✅ Conda configuré — env `ai_learning` sur GX10 et Windows
- ✅ Git et GitHub CLI configurés et authentifiés sur les deux machines
- ✅ Repo `python-ai-learning` créé sur GitHub, cloné sur GX10 et Windows
- ✅ Kernel `ai_learning` enregistré dans JupyterLab et VSCode
- ✅ JupyterLab installé dans `base` sur Windows (port 8888)
- ✅ `.gitignore` ajouté (exclut `.ipynb_checkpoints/`)
- ✅ `environment.yml` nettoyé (prefix Linux supprimé pour portabilité)
