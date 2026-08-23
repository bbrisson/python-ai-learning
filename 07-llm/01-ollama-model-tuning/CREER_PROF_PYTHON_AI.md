# Préparer la création du modèle `prof-python-ai`

## 1. Objectif de ce fichier

Ce fichier prépare la création du modèle personnalisé :

```text
prof-python-ai
```

Ce modèle sera créé à partir du fichier :

```text
Modelfile
```

Le but est de transformer le modèle de base `llama3.2:3b` en assistant spécialisé pour apprendre Python et l'intelligence artificielle en français.

Important : ce fichier prépare les commandes. Il ne les exécute pas automatiquement.

## 2. Ce qu'on a déjà validé

Avant de créer `prof-python-ai`, nous avons déjà validé plusieurs choses.

### Le serveur Ollama répond

Adresse du serveur :

```text
http://192.168.18.5:11434
```

La commande suivante a fonctionné :

```bash
curl http://192.168.18.5:11434/api/tags
```

### Le modèle de base existe

Nous avons listé les modèles disponibles avec :

```powershell
powershell -NoProfile -Command "(Invoke-RestMethod -Uri 'http://192.168.18.5:11434/api/tags').models | Select-Object -ExpandProperty name"
```

Le modèle suivant est disponible :

```text
llama3.2:3b
```

### Python peut appeler Ollama

Le script suivant a été exécuté avec succès :

```bash
python 07-llm\01-ollama-model-tuning\test_model.py
```

Il a appelé :

```text
http://192.168.18.5:11434/api/generate
```

avec le modèle :

```text
llama3.2:3b
```

Conclusion : la chaîne suivante fonctionne déjà.

```text
Python sur Windows -> serveur Ollama -> llama3.2:3b -> réponse
```

## 3. Ce qu'on veut faire maintenant

Maintenant, on veut créer une couche de personnalisation au-dessus de `llama3.2:3b`.

Le nouveau modèle s'appellera :

```text
prof-python-ai
```

Il utilisera comme base :

```text
llama3.2:3b
```

et il suivra les instructions du fichier :

```text
07-llm/01-ollama-model-tuning/Modelfile
```

## 4. Rappel du contenu du Modelfile

Le fichier `Modelfile` commence par :

```text
FROM llama3.2:3b
```

Cela signifie :

```text
Utilise llama3.2:3b comme modèle de base.
```

Il contient aussi :

```text
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
```

Ces paramètres rendent le modèle plus stable et adapté à des réponses pédagogiques.

Enfin, le bloc `SYSTEM` explique le rôle du modèle :

```text
Tu es un professeur patient, précis et pédagogique spécialisé en Python et en intelligence artificielle.
```

## 5. Pré-requis avant d'exécuter la commande

Avant de lancer `ollama create`, il faut être sur la machine qui héberge Ollama.

Dans notre cas, c'est probablement :

```text
192.168.18.5
```

Il faut aussi que le fichier `Modelfile` soit disponible sur cette machine.

Deux scénarios fréquents :

### Scénario A — Le dépôt existe déjà sur le serveur

Dans ce cas, il suffit de se connecter par SSH, puis d'aller dans le bon dossier.

### Scénario B — Le dépôt n'existe pas sur le serveur

Dans ce cas, il faut copier le fichier `Modelfile` sur le serveur avant de lancer `ollama create`.

Ce fichier documente d'abord le scénario A, car c'est le plus propre si le projet est versionné avec Git.

## 6. Commandes SSH génériques — scénario A

### Étape 1 — Se connecter au serveur

Commande générique :

```bash
ssh <user>@192.168.18.5
```

À remplacer :

- `<user>` par le nom d'utilisateur SSH réel.

Exemple fictif :

```bash
ssh mon_utilisateur@192.168.18.5
```

### Étape 2 — Aller dans le dossier du Modelfile

Une fois connecté au serveur :

```bash
cd <chemin-du-repo>/07-llm/01-ollama-model-tuning
```

À remplacer :

- `<chemin-du-repo>` par le chemin réel du dépôt sur le serveur.

Exemple fictif :

```bash
cd ~/work/python-ai-learning/07-llm/01-ollama-model-tuning
```

### Étape 3 — Vérifier qu'on est au bon endroit

Commande :

```bash
ls
```

On doit voir au minimum :

```text
Modelfile
README.md
COMMANDES.md
test_model.py
```

Le fichier le plus important pour la création du modèle est :

```text
Modelfile
```

### Étape 4 — Vérifier que Ollama est disponible

Commande :

```bash
ollama --version
```

Si Ollama est installé et accessible, cette commande affiche une version.

### Étape 5 — Vérifier que le modèle de base existe

Commande :

```bash
ollama list
```

On veut confirmer la présence de :

```text
llama3.2:3b
```

Si `llama3.2:3b` n'apparaît pas, il faudra le télécharger :

```bash
ollama pull llama3.2:3b
```

Mais selon notre vérification HTTP, il est déjà présent sur le serveur.

## 7. Créer le modèle personnalisé

Depuis le dossier qui contient `Modelfile`, lancer :

```bash
ollama create prof-python-ai -f Modelfile
```

Décomposition :

- `ollama` : programme en ligne de commande ;
- `create` : demande la création d'un modèle personnalisé ;
- `prof-python-ai` : nom du nouveau modèle ;
- `-f Modelfile` : utilise le fichier `Modelfile` comme configuration.

Si tout fonctionne, Ollama crée un modèle local nommé :

```text
prof-python-ai
```

## 8. Vérifier que le modèle a été créé

Après la création, lancer :

```bash
ollama list
```

On doit voir apparaître :

```text
prof-python-ai
```

Si le modèle apparaît dans la liste, la création a réussi.

## 9. Tester rapidement le modèle sur le serveur

Commande :

```bash
ollama run prof-python-ai
```

Question de test :

```text
Explique la différence entre un environnement conda et un kernel Jupyter pour un débutant.
```

Ce qu'on veut observer :

- la réponse est en français ;
- la réponse est pédagogique ;
- la réponse explique progressivement ;
- la réponse évite les formulations trop vagues ;
- si possible, elle fait le lien avec un profil C/C++ ou LabVIEW.

Pour quitter la session interactive :

```text
/bye
```

## 10. Tester le modèle depuis Windows plus tard

Une fois `prof-python-ai` créé sur le serveur, on pourra modifier `test_model.py`.

Actuellement, il contient :

```python
MODEL_NAME = "llama3.2:3b"
```

Plus tard, on pourra remplacer par :

```python
MODEL_NAME = "prof-python-ai"
```

Puis relancer :

```bash
python 07-llm\01-ollama-model-tuning\test_model.py
```

Cela permettra de comparer :

```text
llama3.2:3b brut
```

avec :

```text
prof-python-ai personnalisé
```

## 11. Checklist avant exécution réelle

Avant d'exécuter `ollama create`, vérifier :

- [ ] Je peux me connecter au serveur `192.168.18.5` par SSH.
- [ ] Je connais le nom d'utilisateur SSH.
- [ ] Je connais le chemin du dépôt sur le serveur, ou je sais où copier le `Modelfile`.
- [ ] Le fichier `Modelfile` est présent sur le serveur.
- [ ] `ollama --version` fonctionne sur le serveur.
- [ ] `ollama list` montre `llama3.2:3b`.
- [ ] Je suis prêt à créer le modèle `prof-python-ai`.

## 12. Commandes résumées

Version générique :

```bash
ssh <user>@192.168.18.5
cd <chemin-du-repo>/07-llm/01-ollama-model-tuning
ls
ollama --version
ollama list
ollama create prof-python-ai -f Modelfile
ollama list
ollama run prof-python-ai
```

Important : remplacer :

- `<user>` par le nom d'utilisateur SSH réel ;
- `<chemin-du-repo>` par le chemin réel du dépôt sur le serveur.

## 13. Commandes exactes pour ton serveur

Dans ton cas, les valeurs exactes sont :

```text
Utilisateur SSH : bbrisson
Serveur Ollama  : 192.168.18.5
Chemin du dépôt : /home/bbrisson/work/python-ai-learning
```

Donc les commandes prêtes à copier-coller sont les suivantes.

### Étape 1 — Se connecter au serveur

Depuis ton terminal Windows :

```bash
ssh bbrisson@192.168.18.5
```

Cette commande ouvre une session sur la machine qui héberge Ollama.

### Étape 2 — Aller dans le dossier de l'exemple

Une fois connecté au serveur :

```bash
cd /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning
```

Cette commande place le terminal dans le dossier où se trouve le fichier `Modelfile`.

### Étape 3 — Vérifier les fichiers présents

```bash
ls
```

On veut voir au minimum :

```text
Modelfile
README.md
COMMANDES.md
CREER_PROF_PYTHON_AI.md
test_model.py
```

Si `CREER_PROF_PYTHON_AI.md` n'apparaît pas encore, ce n'est pas bloquant pour Ollama. Le fichier essentiel est :

```text
Modelfile
```

### Étape 4 — Vérifier Ollama

```bash
ollama --version
```

Cette commande confirme que le CLI Ollama est accessible sur le serveur.

### Étape 5 — Vérifier le modèle de base

```bash
ollama list
```

On veut voir :

```text
llama3.2:3b
```

### Étape 6 — Créer le modèle personnalisé

```bash
ollama create prof-python-ai -f Modelfile
```

Cette commande crée le modèle personnalisé `prof-python-ai` à partir du `Modelfile`.

### Étape 7 — Vérifier que le modèle existe

```bash
ollama list
```

On veut maintenant voir :

```text
prof-python-ai
```

### Étape 8 — Tester le modèle dans le terminal du serveur

```bash
ollama run prof-python-ai
```

Question de test recommandée :

```text
Explique la différence entre un environnement conda et un kernel Jupyter pour un débutant.
```

Pour quitter :

```text
/bye
```

## 14. Bloc complet à copier-coller avec prudence

Si tu veux faire les étapes manuellement une par une, utilise plutôt les sections précédentes.

Si tu veux un bloc compact après connexion SSH, tu peux utiliser :

```bash
cd /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning
ls
ollama --version
ollama list
ollama create prof-python-ai -f Modelfile
ollama list
```

Je recommande de ne pas inclure `ollama run prof-python-ai` dans ce bloc compact, car cette commande ouvre une session interactive.

## 15. Prochaine décision

La prochaine étape n'est pas technique, elle est pratique :

```text
Veut-on exécuter ces commandes maintenant, ou compléter d'abord la documentation ?
```

Les informations nécessaires sont maintenant connues :

```text
ssh bbrisson@192.168.18.5
cd /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning
```

Il reste à décider si on exécute réellement la création du modèle `prof-python-ai`.

## 16. Variante SSH interactive avec mot de passe

Une vérification SSH non interactive a été tentée avec une option du type :

```bash
ssh -o BatchMode=yes bbrisson@192.168.18.5 "..."
```

Elle a échoué avec :

```text
Permission denied (publickey,password).
```

Ce message indique que le serveur SSH répond, mais que l'authentification automatique par clé SSH n'a pas fonctionné depuis ce terminal Windows.

L'option importante est :

```text
BatchMode=yes
```

Elle signifie :

```text
N'ouvre pas de prompt interactif pour demander un mot de passe.
```

Donc si aucune clé SSH valide n'est disponible, la commande échoue immédiatement.

Pour permettre à SSH de demander le mot de passe, il faut enlever `BatchMode=yes`.

### Commande interactive simple

Depuis un terminal Windows interactif :

```bash
ssh bbrisson@192.168.18.5
```

Si le serveur accepte l'authentification par mot de passe, SSH demandera :

```text
bbrisson@192.168.18.5's password:
```

Après connexion, lancer les commandes une par une :

```bash
cd /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning
ls
ollama --version
ollama list
```

Ces commandes sont non destructives.

Elles vérifient seulement :

- qu'on est connecté au bon serveur ;
- que le dossier existe ;
- que le fichier `Modelfile` est présent ;
- que Ollama est disponible ;
- que le modèle `llama3.2:3b` est présent.

### Commande interactive en une seule ligne

On peut aussi demander à SSH d'exécuter une commande distante après authentification :

```bash
ssh bbrisson@192.168.18.5 "cd /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning && pwd && ls && ollama --version && ollama list"
```

Cette commande peut demander le mot de passe, puis exécuter les vérifications.

Elle ne crée pas encore le modèle.

### Commande de création à lancer seulement après validation

Quand les vérifications sont bonnes, la commande de création sera :

```bash
ssh bbrisson@192.168.18.5 "cd /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning && ollama create prof-python-ai -f Modelfile && ollama list"
```

Cette commande est plus importante, car elle crée réellement le modèle `prof-python-ai` sur le serveur Ollama.

Il faut donc la lancer seulement après validation explicite.

## 17. Diagnostic réel après vérification SSH

Nous avons lancé une vérification SSH interactive.

Résultat : l'authentification SSH fonctionne, mais le dossier de l'exemple n'existe pas encore sur le serveur.

Le dépôt existe bien ici :

```text
/home/bbrisson/work/python-ai-learning
```

Mais ce dossier n'existe pas encore côté serveur :

```text
/home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning
```

Le serveur contient seulement :

```text
07-llm/.gitkeep
```

Conclusion : le `Modelfile` créé sur Windows n'est pas encore présent sur le serveur.

Donc on ne peut pas encore lancer :

```bash
ollama create prof-python-ai -f Modelfile
```

depuis le serveur, car Ollama ne trouverait pas le fichier `Modelfile`.

## 18. Deux façons propres de synchroniser le Modelfile

Avant de créer `prof-python-ai`, il faut transférer les fichiers vers le serveur.

### Option A — Synchroniser avec Git

C'est l'approche la plus propre si on veut garder le projet versionné.

Principe :

1. commit les fichiers sur Windows ;
2. push vers GitHub ;
3. pull depuis le serveur.

Workflow conceptuel :

```text
Windows -> git commit -> git push -> serveur -> git pull
```

Avantage :

- garde l'historique ;
- évite les copies manuelles ;
- permet de reproduire l'exemple plus tard.

Inconvénient :

- demande de faire un commit avant de tester sur le serveur.

### Option B — Copier seulement le dossier avec scp

C'est l'approche rapide si on veut tester avant de committer.

Depuis Windows, on peut copier le dossier vers le serveur avec `scp`.

Commande proposée :

```bash
scp -r 07-llm/01-ollama-model-tuning bbrisson@192.168.18.5:/home/bbrisson/work/python-ai-learning/07-llm/
```

Cette commande signifie :

```text
Copie récursivement le dossier local 07-llm/01-ollama-model-tuning
vers le dossier 07-llm du dépôt situé sur le serveur.
```

Décomposition :

- `scp` : copie de fichiers via SSH ;
- `-r` : récursif, nécessaire pour copier un dossier ;
- `07-llm/01-ollama-model-tuning` : dossier local à copier ;
- `bbrisson@192.168.18.5` : utilisateur et serveur ;
- `/home/bbrisson/work/python-ai-learning/07-llm/` : destination sur le serveur.

Après la copie, on pourra vérifier :

```bash
ssh bbrisson@192.168.18.5 "ls /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning"
```

On devra voir :

```text
COMMANDES.md
CREER_PROF_PYTHON_AI.md
Modelfile
README.md
test_model.py
```

## 19. Commandes après synchronisation

Une fois le dossier présent sur le serveur, les commandes de création deviennent valides :

```bash
ssh bbrisson@192.168.18.5 "cd /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning && ollama create prof-python-ai -f Modelfile && ollama list"
```

Puis, pour tester interactivement :

```bash
ssh bbrisson@192.168.18.5
cd /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning
ollama run prof-python-ai
```

## 20. Prochaine décision mise à jour

La prochaine décision est maintenant :

```text
Comment veut-on envoyer le dossier 01-ollama-model-tuning sur le serveur ?
```

Options recommandées :

1. utiliser Git, si on veut un workflow propre et versionné ;
2. utiliser `scp`, si on veut tester rapidement avant de committer.

## 21. Création réelle effectuée avec succès

La synchronisation par Git a été utilisée.

Depuis Windows :

```text
git add ...
git commit -m "Add Ollama model tuning example"
git push
```

Le commit créé est :

```text
d96cae4 Add Ollama model tuning example
```

Puis, sur le serveur `192.168.18.5`, un `git pull` a été exécuté depuis :

```text
/home/bbrisson/work/python-ai-learning
```

Le dossier suivant est maintenant présent sur le serveur :

```text
/home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning
```

Le fichier `Modelfile` a été vérifié sur le serveur.

La création du modèle a ensuite été lancée avec :

```bash
ssh bbrisson@192.168.18.5 "cd /home/bbrisson/work/python-ai-learning/07-llm/01-ollama-model-tuning && ollama create prof-python-ai -f Modelfile && echo '--- modèles après création ---' && ollama list"
```

Résultat important :

```text
success
```

Puis `ollama list` a confirmé la présence du nouveau modèle :

```text
prof-python-ai:latest    603845aa5f89    2.0 GB    Less than a second ago
```

Conclusion :

```text
Le modèle prof-python-ai a été créé avec succès sur le serveur Ollama.
```

## 22. État actuel

À ce stade :

- le serveur Ollama répond ;
- le modèle de base `llama3.2:3b` existe ;
- le script Python `test_model.py` fonctionne avec `llama3.2:3b` ;
- le `Modelfile` est présent sur le serveur ;
- le modèle personnalisé `prof-python-ai` existe maintenant dans Ollama.

Aucun test de génération avec `prof-python-ai` n'a encore été lancé dans cette étape.

La prochaine étape possible sera de comparer :

```text
llama3.2:3b
```

avec :

```text
prof-python-ai
```

mais ce sera fait seulement après validation explicite.