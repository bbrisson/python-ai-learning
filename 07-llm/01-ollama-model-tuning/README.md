# Ollama model tuning — première étape débutant

## 1. Objectif de ce dossier

Ce dossier servira à construire un exemple simple de personnalisation d'un modèle avec **Ollama**.

L'objectif n'est pas encore de faire du fine-tuning avancé.

Pour commencer, on veut comprendre comment prendre un modèle déjà disponible dans Ollama et lui donner un comportement plus spécialisé.

Exemple d'objectif :

> Créer un assistant local qui répond comme un professeur de Python et d'intelligence artificielle, en français, pour un débutant.

## 2. Ce que tu dois comprendre avant de coder

Ollama fonctionne comme un serveur de modèles.

Dans ton environnement, ce serveur est à l'adresse :

```text
192.168.18.5
```

Le port habituel de l'API Ollama est :

```text
11434
```

Donc l'adresse de base de ton serveur Ollama est probablement :

```text
http://192.168.18.5:11434
```

Ton PC Windows avec VSCode et Python ne contient pas directement le modèle.

Il enverra des requêtes au serveur Ollama.

Schéma mental :

```text
Python sur Windows
        |
        | requête HTTP
        v
Serveur Ollama : 192.168.18.5:11434
        |
        v
Modèle de langage
        |
        | réponse
        v
Python sur Windows
```

## 3. Personnalisation Ollama vs vrai fine-tuning

Il faut être précis avec les mots.

### Personnalisation Ollama

Avec Ollama, on peut créer un modèle personnalisé à partir d'un modèle existant.

On peut configurer :

- le modèle de base ;
- les instructions générales ;
- le style de réponse ;
- certains paramètres comme la température ;
- le contexte disponible.

Cette personnalisation se fait avec un fichier appelé :

```text
Modelfile
```

### Vrai fine-tuning

Le vrai fine-tuning est différent.

Il modifie les poids internes du modèle avec des données d'entraînement.

C'est plus avancé et ce n'est pas notre première étape.

Techniques associées :

- SFT ;
- LoRA ;
- QLoRA.

Dans ce dossier, on commence par la personnalisation Ollama, parce que c'est plus simple et plus concret.

## 4. Fichiers dans ce dossier

Pour l'instant, ce dossier contient :

```text
07-llm/01-ollama-model-tuning/
├── README.md
├── COMMANDES.md
├── Modelfile
└── test_model.py
```

Rôle de chaque fichier :

- `README.md` : explique l'exercice étape par étape ;
- `COMMANDES.md` : explique les commandes utilisées ;
- `Modelfile` : décrit le futur modèle personnalisé `prof-python-ai` ;
- `test_model.py` : teste un appel Python vers le serveur Ollama.

## 5. Vérification déjà faite : le serveur répond

Nous avons vérifié que le serveur Ollama répond à cette adresse :

```text
http://192.168.18.5:11434
```

Commande utilisée depuis Windows :

```bash
curl http://192.168.18.5:11434/api/tags
```

Le serveur a répondu avec un code :

```text
200 OK
```

Cela veut dire que le serveur est accessible depuis cette machine.

Nous avons aussi listé les modèles disponibles. Le modèle choisi pour commencer est :

```text
llama3.2:3b
```

Pourquoi ce choix ?

- il est déjà présent sur le serveur ;
- il est plus léger que les très gros modèles ;
- il est suffisant pour apprendre le mécanisme de personnalisation ;
- il évite de mélanger apprentissage du workflow et problèmes de performance.

## 6. Le Modelfile actuel

Le fichier `Modelfile` utilise ce modèle de base :

```text
FROM llama3.2:3b
```

Il définit ensuite quelques paramètres :

```text
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
```

Explication débutant :

- `temperature 0.3` : rend les réponses plus stables et moins aléatoires ;
- `top_p 0.9` : limite un peu le choix des mots possibles ;
- `num_ctx 4096` : indique la taille approximative du contexte que le modèle peut utiliser.

Le `SYSTEM` prompt donne le rôle du modèle :

```text
professeur francophone, patient et précis, spécialisé en Python et en AI
```

## 7. Test Python réussi avec le modèle de base

Nous avons créé le fichier :

```text
test_model.py
```

Ce script utilise Python pour envoyer une question au serveur Ollama.

Il utilise :

```python
OLLAMA_URL = "http://192.168.18.5:11434/api/generate"
MODEL_NAME = "llama3.2:3b"
```

Commande exécutée depuis la racine du projet :

```bash
python 07-llm\01-ollama-model-tuning\test_model.py
```

Résultat : le script a bien reçu une réponse du modèle `llama3.2:3b`.

Cela valide la chaîne technique suivante :

```text
Python sur Windows
        |
        | requête HTTP POST
        v
Serveur Ollama : 192.168.18.5:11434
        |
        v
Modèle llama3.2:3b
        |
        | réponse texte
        v
Python sur Windows
```

Observation importante : la réponse du modèle de base était correcte globalement, mais pas parfaite. Elle contenait quelques formulations maladroites et certains détails approximatifs.

C'est normal : `llama3.2:3b` est utilisé ici sans instruction spécialisée.

Cette observation justifie la prochaine étape : créer le modèle personnalisé `prof-python-ai` avec le `Modelfile`.

## 8. Prochaine étape proposée : préparer la création du modèle

Pour créer le modèle personnalisé dans Ollama, la commande sera :

```bash
ollama create prof-python-ai -f Modelfile
```

Cette commande signifie :

```text
Crée un nouveau modèle nommé prof-python-ai en utilisant les instructions du fichier Modelfile.
```

Important : cette commande doit être exécutée sur la machine où le serveur Ollama est installé, donc probablement sur :

```text
192.168.18.5
```

Elle ne sera pas lancée automatiquement depuis ce README.

Avant de l'exécuter, il faut décider comment envoyer ou placer le fichier `Modelfile` sur la machine serveur.

Options possibles :

1. copier manuellement le contenu du `Modelfile` sur la machine `192.168.18.5` ;
2. utiliser Git si le dépôt est aussi présent sur cette machine ;
3. utiliser `scp` ou un autre mécanisme de copie de fichier.

## 9. Commandes SSH génériques pour créer le modèle

Si tu as accès au serveur par SSH, le workflow général est :

1. se connecter au serveur ;
2. aller dans le dossier qui contient le `Modelfile` ;
3. vérifier que Ollama voit le modèle de base ;
4. créer le modèle personnalisé.

### Étape 1 — Se connecter au serveur

Commande générique :

```bash
ssh <user>@192.168.18.5
```

À remplacer :

- `<user>` par ton nom d'utilisateur sur le serveur.

Exemple fictif :

```bash
ssh mon_utilisateur@192.168.18.5
```

### Étape 2 — Aller dans le dossier du projet

Une fois connecté au serveur :

```bash
cd <chemin-du-repo>/07-llm/01-ollama-model-tuning
```

À remplacer :

- `<chemin-du-repo>` par le chemin réel du dépôt `python-ai-learning` sur le serveur.

Exemple fictif :

```bash
cd ~/work/python-ai-learning/07-llm/01-ollama-model-tuning
```

### Étape 3 — Vérifier que le modèle de base existe

Commande :

```bash
ollama list
```

On veut voir un modèle nommé :

```text
llama3.2:3b
```

Si le modèle n'existe pas sur le serveur, il faudra le télécharger avec :

```bash
ollama pull llama3.2:3b
```

Mais dans notre vérification depuis Windows, ce modèle semblait déjà présent sur le serveur.

### Étape 4 — Créer le modèle personnalisé

Depuis le dossier qui contient le `Modelfile` :

```bash
ollama create prof-python-ai -f Modelfile
```

Si la commande réussit, Ollama créera un nouveau modèle local nommé :

```text
prof-python-ai
```

### Étape 5 — Tester rapidement dans le terminal du serveur

Commande :

```bash
ollama run prof-python-ai
```

Question de test possible :

```text
Explique la différence entre un environnement conda et un kernel Jupyter pour un débutant.
```

Pour quitter la session interactive Ollama, utiliser :

```text
/bye
```

## 10. Ce qu'on ne fait pas encore

On ne lance pas encore `ollama create`.

On ne teste pas encore le modèle personnalisé.

On prépare seulement la commande et on valide la compréhension.

## 11. Questions avant la prochaine étape

Avant d'aller plus loin, il faut répondre à une question pratique :

```text
Est-ce qu'on exécute maintenant ces commandes SSH, ou est-ce qu'on les garde seulement comme documentation ?
```

La réponse dépend de ce que tu veux faire ensuite :

- exécuter les commandes SSH toi-même ;
- me donner les informations exactes pour préparer des commandes non génériques ;
- créer d'abord le script Python qui appellera le serveur Ollama ;
- modifier le `Modelfile` avant de créer le modèle.

## 12. Critère de réussite de cette étape

Cette étape est réussie si :

- le dossier `07-llm/01-ollama-model-tuning/` existe ;
- ce fichier `README.md` explique clairement le but ;
- l'adresse du serveur Ollama `192.168.18.5` est documentée ;
- le fichier `Modelfile` existe ;
- le fichier `test_model.py` existe et a été exécuté avec succès ;
- la commande `ollama create` est documentée ;
- les commandes SSH génériques sont documentées ;
- aucune commande de création de modèle n'a été lancée sans validation ;
- la suite se fait seulement après validation.