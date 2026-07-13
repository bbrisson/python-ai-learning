# Plan débutant — Personnaliser un modèle avec Ollama

## 1. But de cet exercice

Le but est de créer progressivement un exemple très simple pour comprendre comment personnaliser le comportement d'un modèle de langage avec **Ollama**.

Dans cet exercice, on ne va pas encore entraîner un modèle à partir de zéro. On va plutôt apprendre à dire à un modèle existant :

> « Réponds comme un professeur de Python et d'intelligence artificielle, en français, avec des explications claires pour un débutant. »

C'est une bonne première étape avant de parler de vrai fine-tuning.

## 2. Où placer cet exemple dans le projet

Le bon dossier est :

```text
07-llm/
```

Pourquoi ?

Parce que Ollama sert à utiliser des **LLM locaux** ou hébergés sur une machine de ton réseau.

LLM signifie :

```text
Large Language Model
```

En français :

```text
grand modèle de langage
```

Comme cet exemple concerne l'utilisation pratique d'un modèle de langage, il appartient au dossier `07-llm`.

## 3. Information importante sur ton serveur Ollama

Dans ton cas, le serveur Ollama n'est pas sur la machine locale Windows.

Il est à l'adresse :

```text
192.168.18.5
```

L'API Ollama utilise normalement le port :

```text
11434
```

Donc l'adresse complète de l'API sera probablement :

```text
http://192.168.18.5:11434
```

Pour générer une réponse avec un modèle, le script Python appellera plus tard :

```text
http://192.168.18.5:11434/api/generate
```

## 4. Ce qu'on appelle ici « model tuning »

Le mot **tuning** peut vouloir dire plusieurs choses.

Pour un débutant, il faut distinguer deux niveaux.

### Niveau 1 — Personnalisation simple avec Ollama

Avec Ollama, on peut créer un modèle personnalisé à partir d'un modèle existant.

On peut définir :

- le modèle de base ;
- le rôle du modèle ;
- le style de réponse ;
- la température ;
- la taille du contexte ;
- les instructions système.

Cette personnalisation se fait avec un fichier appelé :

```text
Modelfile
```

C'est ce que nous allons faire dans cet exemple.

### Niveau 2 — Fine-tuning réel

Le vrai fine-tuning est plus avancé.

Il consiste à modifier les poids internes du modèle avec des données d'entraînement.

Exemples de techniques :

- SFT, pour Supervised Fine-Tuning ;
- LoRA ;
- QLoRA.

Ce n'est pas l'objectif de cette première étape.

Ici, on commence par la personnalisation Ollama, car elle est plus simple et plus utile pour apprendre les bases.

## 5. Structure prévue pour l'exemple

À terme, on créera ce dossier :

```text
07-llm/01-ollama-model-tuning/
```

Il contiendra probablement :

```text
07-llm/01-ollama-model-tuning/
├── README.md
├── Modelfile
└── test_model.py
```

Chaque fichier aura un rôle précis.

## 6. Rôle de chaque fichier

### README.md

Le fichier `README.md` expliquera l'exercice étape par étape.

Il répondra à des questions simples :

- Qu'est-ce que Ollama ?
- Qu'est-ce qu'un modèle de base ?
- Qu'est-ce qu'un `Modelfile` ?
- Comment créer un modèle personnalisé ?
- Comment tester le modèle ?
- Comment appeler le modèle depuis Python ?

### Modelfile

Le fichier `Modelfile` décrira le modèle personnalisé.

Il pourra contenir quelque chose comme :

```text
FROM llama3.2:3b

PARAMETER temperature 0.3
PARAMETER num_ctx 4096

SYSTEM """
Tu es un professeur patient et précis spécialisé en Python et en intelligence artificielle.
Tu expliques les concepts pour un débutant, en français.
Tu évites les réponses superficielles.
"""
```

Explication rapide :

- `FROM` choisit le modèle de base ;
- `PARAMETER` ajuste le comportement ;
- `SYSTEM` donne les instructions générales au modèle.

### test_model.py

Le fichier `test_model.py` servira à appeler le serveur Ollama depuis Python.

Comme ton serveur est à l'adresse `192.168.18.5`, le script devra utiliser :

```python
OLLAMA_URL = "http://192.168.18.5:11434/api/generate"
```

L'idée sera de poser une question au modèle personnalisé et d'afficher sa réponse.

## 7. Plan d'apprentissage étape par étape

### Étape 1 — Comprendre l'architecture

Avant d'écrire du code, il faut comprendre les rôles :

```text
Windows / VSCode / Python
        |
        | requête HTTP
        v
Serveur Ollama : 192.168.18.5:11434
        |
        v
Modèle de langage
```

Ton script Python ne contient pas le modèle.

Il envoie une requête au serveur Ollama.

Le serveur Ollama exécute le modèle et retourne une réponse.

### Étape 2 — Vérifier que le serveur répond

On vérifiera plus tard que l'adresse suivante est accessible :

```text
http://192.168.18.5:11434
```

On pourra le faire avec une commande comme :

```bash
curl http://192.168.18.5:11434/api/tags
```

Cette commande devrait lister les modèles disponibles sur le serveur Ollama.

### Étape 3 — Choisir un modèle de base

Il faudra choisir un modèle déjà disponible sur le serveur Ollama, par exemple :

```text
llama3.2:3b
```

ou un autre modèle installé sur la machine `192.168.18.5`.

### Étape 4 — Créer le Modelfile

Le `Modelfile` définira le comportement du modèle personnalisé.

Exemple d'objectif :

```text
Créer un assistant qui enseigne Python et l'AI à un débutant francophone.
```

### Étape 5 — Créer le modèle personnalisé

Sur la machine où Ollama est installé, on utilisera une commande du genre :

```bash
ollama create prof-python-ai -f Modelfile
```

Cette commande dira à Ollama :

> Crée un nouveau modèle nommé `prof-python-ai` à partir des instructions du fichier `Modelfile`.

### Étape 6 — Tester dans le terminal

On pourra ensuite tester le modèle avec :

```bash
ollama run prof-python-ai
```

Puis poser une question comme :

```text
Explique la différence entre un environnement conda et un kernel Jupyter.
```

### Étape 7 — Tester depuis Python

Enfin, on créera un script Python pour envoyer une requête HTTP au serveur Ollama.

Le script utilisera l'adresse :

```text
http://192.168.18.5:11434/api/generate
```

## 8. Critères de réussite

L'exemple sera réussi si :

- le plan est clair pour un débutant ;
- on comprend la différence entre personnaliser un modèle et faire un vrai fine-tuning ;
- on comprend que le serveur Ollama est sur `192.168.18.5` ;
- on sait que Python communiquera avec Ollama par HTTP ;
- la prochaine étape est claire : créer le dossier d'exemple avec `README.md`, `Modelfile` et `test_model.py`.

## 9. Ce que cette première étape ne fait pas encore

Cette première étape ne crée pas encore le modèle personnalisé.

Elle ne lance pas Ollama.

Elle ne télécharge aucun modèle.

Elle ne modifie pas l'environnement Python.

Elle sert seulement à poser un plan clair avant d'écrire les fichiers opérationnels.