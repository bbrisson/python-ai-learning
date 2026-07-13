# Commandes utilisées — Ollama depuis Windows et SSH

## 1. But de ce fichier

Ce fichier explique les commandes utilisées ou proposées dans cet exercice.

L'objectif est de comprendre :

- ce que fait chaque commande ;
- pourquoi elle est utilisée ;
- quelles parties sont spécifiques à Windows, PowerShell, Ollama ou SSH ;
- ce qu'il faut regarder dans la sortie.

Ce fichier est volontairement écrit pour un débutant.

## 2. Contexte de l'exercice

Le serveur Ollama est à l'adresse :

```text
192.168.18.5
```

Le port standard de l'API Ollama est :

```text
11434
```

Donc l'adresse de base du serveur est :

```text
http://192.168.18.5:11434
```

Quand on veut parler à Ollama depuis Windows, on envoie une requête HTTP vers cette adresse.

## 3. Commande simple pour vérifier le serveur

Commande utilisée :

```bash
curl http://192.168.18.5:11434/api/tags
```

### Ce que fait cette commande

Elle demande au serveur Ollama :

```text
Quels modèles sont disponibles chez toi ?
```

L'endpoint appelé est :

```text
/api/tags
```

Dans Ollama, cet endpoint retourne la liste des modèles installés.

### Détail de la commande

```text
curl
```

`curl` est un outil en ligne de commande pour faire des requêtes HTTP.

```text
http://192.168.18.5:11434
```

C'est l'adresse du serveur Ollama.

```text
/api/tags
```

C'est la route de l'API qui liste les modèles.

### Attention sous Windows PowerShell

Sous PowerShell, `curl` peut être un alias vers :

```text
Invoke-WebRequest
```

Ce n'est pas exactement le même comportement que le vrai programme `curl` Linux.

C'est pour cela que la sortie peut être plus verbeuse, avec des champs comme :

```text
StatusCode
StatusDescription
Content
Headers
RawContent
```

### Résultat attendu

Un résultat correct contient :

```text
StatusCode : 200
```

ou :

```text
200 OK
```

Cela veut dire :

```text
Le serveur répond correctement.
```

## 4. Commande PowerShell pour lister seulement les noms des modèles

Commande utilisée :

```powershell
powershell -NoProfile -Command "(Invoke-RestMethod -Uri 'http://192.168.18.5:11434/api/tags').models | Select-Object -ExpandProperty name"
```

Cette commande est plus avancée, mais elle donne une sortie beaucoup plus lisible.

Elle affiche seulement les noms des modèles disponibles.

## 5. Décomposition de la commande PowerShell

### Partie 1 — Lancer PowerShell

```powershell
powershell
```

Lance PowerShell depuis le terminal courant.

Dans notre environnement, le shell par défaut est `cmd.exe`, donc on appelle explicitement PowerShell pour utiliser ses commandes.

### Partie 2 — Ne pas charger le profil utilisateur

```powershell
-NoProfile
```

Cette option dit à PowerShell :

```text
Ne charge pas les scripts de configuration personnels au démarrage.
```

Pourquoi c'est utile ?

- la commande démarre plus vite ;
- le résultat est plus prévisible ;
- on évite qu'un alias ou une configuration personnelle change le comportement.

### Partie 3 — Exécuter une commande PowerShell inline

```powershell
-Command "..."
```

Cette option dit à PowerShell :

```text
Exécute le code placé entre guillemets.
```

Tout ce qui est entre les guillemets est donc du code PowerShell.

## 6. Décomposition de la commande interne

La partie interne est :

```powershell
(Invoke-RestMethod -Uri 'http://192.168.18.5:11434/api/tags').models | Select-Object -ExpandProperty name
```

### Partie 1 — Appeler une API HTTP

```powershell
Invoke-RestMethod -Uri 'http://192.168.18.5:11434/api/tags'
```

`Invoke-RestMethod` appelle une API HTTP et convertit automatiquement la réponse JSON en objet PowerShell.

Dans notre cas, Ollama retourne une réponse JSON qui ressemble conceptuellement à ceci :

```json
{
  "models": [
    {
      "name": "llama3.2:3b",
      "modified_at": "...",
      "size": 2019393189
    }
  ]
}
```

### Partie 2 — Les parenthèses

```powershell
(Invoke-RestMethod -Uri 'http://192.168.18.5:11434/api/tags')
```

Les parenthèses forcent PowerShell à exécuter cette partie en premier.

C'est comparable à une expression en C/C++ :

```cpp
result = function_call();
```

On veut d'abord obtenir le résultat de la requête HTTP.

### Partie 3 — Accéder à la propriété `.models`

```powershell
.models
```

La réponse JSON contient une propriété appelée `models`.

Cette propriété contient la liste des modèles disponibles.

Donc cette partie signifie :

```text
Prends seulement la liste models dans la réponse.
```

### Partie 4 — Le pipe PowerShell

```powershell
|
```

Le symbole `|` envoie le résultat de gauche vers la commande de droite.

C'est semblable au pipe dans Linux ou dans un terminal Unix.

Conceptuellement :

```text
liste des modèles -> Select-Object
```

### Partie 5 — Extraire seulement le nom

```powershell
Select-Object -ExpandProperty name
```

Chaque modèle contient plusieurs propriétés :

- `name` ;
- `model` ;
- `modified_at` ;
- `size` ;
- `digest` ;
- etc.

Nous ne voulons afficher que le nom.

Donc :

```powershell
Select-Object -ExpandProperty name
```

signifie :

```text
Pour chaque modèle, affiche seulement la valeur de la propriété name.
```

## 7. Résultat obtenu

La commande a listé plusieurs modèles, dont :

```text
llama3.2:3b
```

C'est le modèle que nous avons choisi comme base pour le premier `Modelfile`.

Pourquoi lui ?

- il est déjà installé ;
- il est relativement léger ;
- il est suffisant pour apprendre le workflow ;
- il évite de commencer avec un très gros modèle.

## 8. Commandes SSH génériques

Si on veut créer le modèle personnalisé directement sur le serveur Ollama, il faut se connecter au serveur.

Commande générique :

```bash
ssh <user>@192.168.18.5
```

À remplacer :

```text
<user>
```

par le nom d'utilisateur réel sur le serveur.

Une fois connecté, il faut aller dans le dossier du projet :

```bash
cd <chemin-du-repo>/07-llm/01-ollama-model-tuning
```

À remplacer :

```text
<chemin-du-repo>
```

par le chemin réel du dépôt sur le serveur.

Exemple fictif :

```bash
cd ~/work/python-ai-learning/07-llm/01-ollama-model-tuning
```

## 9. Commande pour créer le modèle personnalisé

Commande prévue :

```bash
ollama create prof-python-ai -f Modelfile
```

### Ce que fait cette commande

Elle demande à Ollama de créer un nouveau modèle nommé :

```text
prof-python-ai
```

en utilisant les instructions contenues dans le fichier :

```text
Modelfile
```

### Décomposition

```text
ollama
```

Programme en ligne de commande d'Ollama.

```text
create
```

Sous-commande qui crée un modèle personnalisé.

```text
prof-python-ai
```

Nom du nouveau modèle.

```text
-f Modelfile
```

Indique le fichier de configuration à utiliser.

## 10. Commande pour tester le modèle personnalisé

Après création, on pourra tester avec :

```bash
ollama run prof-python-ai
```

Cette commande ouvre une conversation interactive avec le modèle.

Question de test possible :

```text
Explique la différence entre un environnement conda et un kernel Jupyter pour un débutant.
```

Pour quitter :

```text
/bye
```

## 11. Commande Python utilisée pour tester le modèle de base

Après avoir créé `test_model.py`, nous avons exécuté cette commande depuis la racine du projet :

```bash
python 07-llm\01-ollama-model-tuning\test_model.py
```

### Ce que fait cette commande

Elle lance le script Python :

```text
07-llm/01-ollama-model-tuning/test_model.py
```

Ce script envoie une requête HTTP `POST` à Ollama :

```text
http://192.168.18.5:11434/api/generate
```

avec le modèle :

```text
llama3.2:3b
```

### Pourquoi utiliser d'abord le modèle de base ?

On teste d'abord `llama3.2:3b` directement pour valider la chaîne simple :

```text
Python -> serveur Ollama -> modèle de base -> réponse
```

Avant d'ajouter le modèle personnalisé `prof-python-ai`, on veut s'assurer que :

- Python fonctionne ;
- le serveur Ollama est accessible ;
- l'API `/api/generate` répond ;
- le modèle `llama3.2:3b` peut générer une réponse.

### Résultat obtenu

Le script a bien affiché :

```text
Modèle utilisé : llama3.2:3b
Serveur Ollama : http://192.168.18.5:11434/api/generate
```

puis une réponse générée par le modèle.

Conclusion :

```text
Le test Python vers Ollama fonctionne.
```

### Observation sur la qualité de la réponse

La réponse du modèle de base était utilisable, mais pas parfaite.

Elle contenait quelques formulations maladroites et des explications parfois approximatives.

C'est une bonne observation pédagogique : le modèle de base répond, mais il n'a pas encore reçu nos instructions spécialisées de professeur Python/AI.

Cela motive la prochaine étape : créer le modèle personnalisé `prof-python-ai` avec le `Modelfile`.

## 12. Résumé du workflow complet

Le workflow prévu est :

```text
1. Vérifier que le serveur Ollama répond.
2. Lister les modèles disponibles.
3. Choisir un modèle de base.
4. Écrire un Modelfile.
5. Se connecter au serveur par SSH.
6. Aller dans le dossier du Modelfile.
7. Exécuter ollama create.
8. Tester avec ollama run.
9. Appeler le modèle de base depuis Python.
10. Plus tard : créer et tester le modèle personnalisé.
```

## 13. Ce qu'il faut retenir

Pour cet exercice, les idées importantes sont :

- Ollama expose une API HTTP ;
- le serveur est sur `192.168.18.5:11434` ;
- `/api/tags` liste les modèles disponibles ;
- PowerShell peut lire le JSON et extraire seulement les noms ;
- `Modelfile` décrit le comportement du modèle personnalisé ;
- `test_model.py` valide l'appel Python vers Ollama ;
- `ollama create` crée le modèle personnalisé ;
- `ollama run` permet de le tester dans le terminal.