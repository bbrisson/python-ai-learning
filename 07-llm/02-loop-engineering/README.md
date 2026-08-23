# 02 — Loop engineering avec Ollama et qwen3.8:27b

## 1. De quoi on parle, et pourquoi c'est un métier distinct

Le **prompt engineering** consiste à bien formuler *un* appel. Le **loop
engineering** consiste à concevoir le système bouclé qui enchaîne *N* appels
jusqu'à un état terminal acceptable.

La différence est la même qu'entre écrire une fonction et concevoir un
asservissement. Une fonction, tu la vérifies avec un jeu d'entrées/sorties.
Un système bouclé, tu dois te demander : est-ce qu'il converge ? en combien
de temps ? que se passe-t-il s'il ne converge pas ? qu'est-ce qui le sature ?
comment je l'arrête ?

C'est là que se trouvent 90 % des problèmes des agents en production, et
quasiment aucun d'entre eux ne se règle en améliorant le prompt.

Une formulation qui aide, venant du C : le modèle est une fonction pure,
sans état, potentiellement lente et parfois fausse. La boucle est le
programme. Ton travail n'est pas d'améliorer la fonction — tu ne peux pas,
elle est figée dans 32 Go de poids — mais d'écrire un programme correct
autour d'un appelé non fiable.

## 2. Audit de l'environnement (fait avant d'écrire une ligne)

Serveur Ollama interrogé sur `http://192.168.18.5:11434` (déjà présent dans
ta variable d'environnement `OLLAMA_HOST`) :

| Élément | Valeur |
|---|---|
| Modèle | `qwen3.8:27b` — 26,9 milliards de paramètres, 32,4 Go |
| Capacités | `tools`, `thinking`, `vision`, `completion` |
| Fenêtre de contexte | 262 144 tokens |
| Famille de template | `qwen35` |

Le point décisif est **`tools`**. Sans cette capacité, il faudrait faire du
*tool calling* à la main : décrire les outils en texte dans le prompt système,
demander au modèle de répondre en JSON, et parser sa réponse en espérant
qu'elle soit bien formée. C'est faisable, c'est ce qu'on faisait avant, et
c'est fragile. Ici le template du modèle sait sérialiser les outils et Ollama
sait re-parser les appels : on récupère du JSON structuré, pas du texte à
deviner.

Les 262 k tokens de contexte sont confortables mais ne dispensent pas de
gérer l'accumulation : chaque tour de boucle **relit tout l'historique depuis
le début**. Le coût d'une boucle est quadratique en nombre de tours, pas
linéaire.

## 3. Anatomie d'une boucle

Toute boucle agentique, quelle que soit la bibliothèque qui l'enrobe, se
ramène à cinq composants. LangChain, LangGraph et les autres ne font
qu'emballer ça — d'où l'intérêt de l'écrire une fois à la main.

```
        ┌─────────────────────────────────────────┐
        │                                         │
        v                                         │
   ┌─────────┐   messages    ┌────────┐  tool_calls   ┌──────────┐
   │  ÉTAT   │ ────────────> │ MODÈLE │ ───────────>  │ DISPATCH │
   │ (list)  │               └────────┘               └──────────┘
   └─────────┘                    │                        │
        ^                         │ pas de tool_calls      │ résultats
        │                         v                        │
        │                   ┌──────────┐                   │
        └───────────────────│  ARRÊT   │<──────────────────┘
          observations      └──────────┘   BUDGET (tours, temps, tokens)
```

1. **L'état** — une `list[dict]`. Le serveur ne mémorise rien : voir
   l'exemple 01.
2. **L'appel au modèle** — non déterministe, lent, faillible.
3. **Le dispatch** — ta table nom → fonction Python. C'est ici, et nulle
   part ailleurs, que se décide ce que l'agent a le droit de faire.
4. **La condition d'arrêt** — la partie que les débutants oublient de
   concevoir.
5. **Le budget** — le watchdog. Non négociable.

## 4. Les deux familles de boucles

| | Boucle à outils (ex. 02, 03) | Boucle de réflexion (ex. 04) |
|---|---|---|
| Ce qui boucle | l'acquisition de faits | la qualité d'un artefact |
| Signal d'arrêt | `tool_calls` vide | un juge dit « accepté » |
| Arrêt naturel ? | oui, le modèle s'arrête | **non**, il faut le fabriquer |
| Risque principal | boucle stérile, outil mal choisi | complaisance du juge, plafonnement |
| Analogie | boucle d'événements + `switch` | asservissement avec correcteur |

## 5. Les invariants à ne jamais violer

1. **Réinjecter l'historique complet, les deux rôles.** Oublier d'ajouter la
   réponse de l'assistant est le bug le plus courant : le modèle revoit ses
   questions mais jamais ses réponses, et se contredit.
2. **Une exception d'outil est une observation, pas une panne.** Tu
   l'attrapes, tu la sérialises, tu la renvoies au modèle. Il se corrige
   souvent tout seul (démontré en section 7).
3. **Tout ce qu'un contrôle déterministe peut trancher ne va pas au
   modèle.** `compile()` coûte 0,1 ms et ne se trompe jamais ; un juge LLM
   coûte 30 s et hésite.
4. **Toute sortie de boucle est étiquetée.** `convergence`, `budget épuisé`,
   `boucle stérile` — jamais un `None` muet. « Ça n'a rien renvoyé » n'est
   pas un diagnostic.
5. **Le modèle n'exécute rien.** `tool_calls` est une demande. La sécurité
   se place dans le dispatch, pas dans le prompt : un prompt système qui dit
   « ne lis pas de fichiers sensibles » n'est pas un contrôle d'accès.

## 6. Modes de défaillance et parades

| Défaillance | Symptôme | Parade | Où |
|---|---|---|---|
| Divergence | l'agent ne s'arrête jamais | `max_tours` | ex. 03 |
| Boucle stérile | même appel, mêmes arguments, en boucle | signature d'appel dédupliquée | ex. 03 |
| Coût qui s'emballe | 40 s par tour, contexte qui gonfle | budget temps + tokens | ex. 03 |
| Outil qui échoue | crash de la boucle | renvoyer l'erreur comme observation | ex. 03 |
| Amnésie | l'agent oublie le début | réinjection de l'historique | ex. 01 |
| Complaisance du juge | tout est accepté du premier coup | contexte séparé pour le juge | ex. 04 |
| Plafonnement | le score stagne ou régresse | garder la meilleure version | ex. 04 |
| Chemin halluciné | `../../../etc/passwd` | validation après résolution | ex. 02 |
| `eval` déguisé | outil « calculatrice » | parcours d'AST, liste blanche | ex. 02 |

## 7. Les fichiers

| Fichier | Ce qu'il démontre |
|---|---|
| `ollama_client.py` | client HTTP minimal, stdlib seule — aucune magie cachée |
| `01_boucle_nue.py` | où vit l'état : deux boucles côte à côte, l'une amnésique |
| `02_boucle_outils.py` | la boucle agentique complète avec 3 outils réels |
| `03_garde_fous.py` | budget, détection de cycle, erreur-comme-observation |
| `04_boucle_reflexion.py` | générateur + juge, condition d'arrêt fabriquée |
| `test_boucles.py` | 17 tests hors ligne, sans serveur (faux modèle injecté) |

Exécution :

```powershell
conda activate ai_learning
cd C:\Users\benoi\work\python-ai-learning\07-llm\02-loop-engineering
python 01_boucle_nue.py
python test_boucles.py
```

Aucune dépendance à installer : tout est en `urllib`, comme
`07-llm/01-ollama-model-tuning/test_model.py`.

## 8. Traces réelles observées sur ton serveur

Ces sorties viennent de vraies exécutions contre `qwen3.8:27b`, pas d'un
exemple inventé.

**Exemple 02 — convergence en 4 tours.** À noter le tour 2 : le modèle a
demandé **cinq appels d'outil d'un coup**. Une boucle écrite avec `if
tool_calls[0]` au lieu d'une itération sur toute la liste perdrait quatre
résultats sur cinq et partirait en vrille. Le parallélisme d'outils n'est
pas une option avancée, c'est le comportement par défaut.

```
--- Tour 1 (4.2s) : 1 appel(s) d'outil ---
  -> lister_fichiers({'dossier': '01-environnement', 'extension': '.ipynb'})
--- Tour 2 (8.3s) : 5 appel(s) d'outil ---
  -> taille_fichier(...)  x5
--- Tour 3 (3.0s) : 1 appel(s) d'outil ---
  -> calculer({'expression': '(28318+12895+51348+13686+21589)/1024'})
--- Tour 4 (6.4s) : réponse finale ---
```

**Exemple 03 — auto-correction sur erreur d'outil.** L'outil refuse `'Conda'`
(majuscule) et renvoie la correction dans le message d'erreur. Au tour
suivant, le modèle appelle `'conda'`. Il a aussi déduit de `sujets_valides`
que « Génie logiciel » n'existait pas, sans gaspiller un appel pour le
vérifier :

```
Tour 1 : chercher_note({'sujet': 'Conda'})  -> [ERREUR] ... Réessaie avec 'conda'.
Tour 2 : chercher_note({'sujet': 'conda'})  -> [ok] ...
Tour 3 : réponse finale         (3 tours | 9.0s | ~366 tokens)
```

La leçon est directement actionnable : **écris tes messages d'erreur d'outil
pour qu'ils soient lus par le modèle**, avec la valeur corrigée et la liste
des valeurs valides. Un `ValueError: invalid input` coûte plusieurs tours ; un
message qui dit quoi faire en coûte un.

**Exemple 04 — convergence en 2 révisions** (7/10 puis 10/10), et un défaut
instructif : le juge a rempli le champ `problemes` avec des lignes du genre
« Le code le fait. OK. ». Le schéma JSON a bien contraint la **forme** — un
tableau de chaînes — mais rien ne contraint la **sémantique** : le modèle a
mis des non-problèmes dans la liste des problèmes. Ces faux reproches
repartent ensuite dans le prompt du générateur.

C'est un vrai piège de conception, et la parade n'est pas de mieux formuler
la consigne. Elle est structurelle : demander un tableau d'objets
`{"exigence": ..., "respectee": bool, "correction": ...}` et **filtrer côté
Python** sur `respectee == false`. Là encore : ce que le code peut trancher,
le code le tranche.

## 9. Pièges spécifiques à Ollama et qwen3

- **`arguments` est déjà un dict**, pas une chaîne JSON. L'API OpenAI renvoie
  une *string* qu'il faut passer à `json.loads`. Tout code copié d'un tutoriel
  OpenAI plante ici — ou pire, marche par accident.
- **Le message de résultat utilise `{"role": "tool", "tool_name": ...,
  "content": ...}`.** Le `content` doit être une chaîne : sérialise ton dict
  avec `json.dumps`.
- **`think`** : qwen3 sait raisonner avant de répondre. Dans une boucle
  automatisée, `think: False` donne des tours plus rapides et plus
  prévisibles. Le mode raisonnement se justifie sur la planification, pas sur
  chaque appel d'outil.
- **Premier appel lent** : charger 32 Go en VRAM prend une dizaine de
  secondes. Un timeout court fait croire à une panne serveur — d'où
  `TIMEOUT_S = 300` dans le client.
- **Encodage console Windows** : sans `reconfigure(encoding="utf-8")`, la
  console affiche `-12 �C` pour `-12 °C`. Le modèle a bien répondu, c'est
  l'affichage qui ment. `setup_console()` dans `ollama_client.py` règle ça.
- **`format`** accepte un schéma JSON complet et contraint le décodage. C'est
  ce qui rend une condition d'arrêt exploitable par un `if`.

## 10. Où ça se raccroche dans le repo

- `07-llm/01-ollama-model-tuning/` — le Modelfile et la personnalisation d'un
  modèle. Ce dossier-ci suppose acquis le fait qu'Ollama est un serveur
  distant qu'on interroge en HTTP.
- `09-projets/02-assistant-apprentissage-ia/cours/05-langgraph.md` — LangGraph
  est exactement l'industrialisation de ce qui est écrit ici à la main :
  l'état devient un graphe typé, les transitions deviennent des arêtes, et
  les garde-fous deviennent des paramètres. Avoir écrit la boucle nue rend ce
  cours-là lisible au lieu de magique.
