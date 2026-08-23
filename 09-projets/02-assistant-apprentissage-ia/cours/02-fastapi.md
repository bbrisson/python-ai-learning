# 02 — FastAPI : la frontière HTTP

## Objectif

À la fin de ce chapitre, tu dois comprendre comment une fonction Python
devient une opération HTTP documentée et pourquoi la logique métier ne devrait
pas vivre dans la route.

Les fichiers étudiés sont :

- `src/study_assistant/api.py` — transport HTTP ;
- `src/study_assistant/planner.py` — logique métier pure ;
- `tests/test_api.py` — tests de la frontière.

## Pourquoi une couche web séparée

Le client connaît HTTP et JSON. La logique métier devrait connaître
`StudyRequest` et `StudyPlan`, pas les en-têtes, les sockets ou les codes de
statut.

```text
HTTP/JSON -> route FastAPI -> objets Pydantic -> fonction métier
```

Cette séparation permet d'appeler `build_local_plan()` depuis un test, une CLI,
un worker ou une autre API sans simuler une requête web.

## FastAPI, Starlette et Uvicorn

Ces noms correspondent à trois couches distinctes :

- **FastAPI** déclare les routes, dépendances, contrats et OpenAPI ;
- **Starlette**, utilisée par FastAPI, fournit les primitives web ASGI ;
- **Uvicorn** est le serveur ASGI qui écoute sur un port et appelle
  l'application.

Analogie systèmes : Uvicorn joue le rôle de la boucle serveur, Starlette offre
les primitives de protocole et FastAPI ajoute une interface déclarative basée
sur les annotations.

## Cycle d'une requête

Pour `POST /study-plans` :

1. Uvicorn reçoit les octets HTTP ;
2. Starlette construit la requête ASGI ;
3. FastAPI lit le corps JSON ;
4. Pydantic construit `StudyRequest` ou produit les détails d'erreur ;
5. la route appelle `build_local_plan()` ;
6. FastAPI valide le retour avec `StudyPlan` ;
7. la réponse est sérialisée en JSON avec le statut 201.

Une durée inférieure à 20 n'atteint donc jamais la logique métier : FastAPI
retourne 422 avec un chemin précis vers `available_minutes`.

## Lire les signatures

```python
@app.post(
    "/study-plans",
    response_model=StudyPlan,
    status_code=status.HTTP_201_CREATED,
)
def create_study_plan(request: StudyRequest) -> StudyPlan:
    return build_local_plan(request)
```

- le décorateur décrit le protocole ;
- `request: StudyRequest` décrit le corps entrant ;
- `response_model=StudyPlan` impose le contrat sortant ;
- `-> StudyPlan` aide le lecteur et les outils statiques.

Garder le modèle de réponse explicite est important : il documente l'API et
évite d'exposer accidentellement un champ interne.

## `def` ou `async def` ?

`async def` est utile lorsque la route attend des bibliothèques I/O elles-mêmes
asynchrones. Il ne rend pas un calcul CPU plus rapide et ne transforme pas une
bibliothèque bloquante en bibliothèque asynchrone.

Les routes de ce projet utilisent `def` parce que leur logique est synchrone et
rapide. Un appel LLM long devrait avoir des timeouts et, selon les contraintes,
être asynchrone ou confié à une file de tâches.

## Expérience

Lance l'API depuis le dossier du projet :

```powershell
python -m uvicorn study_assistant.api:app --app-dir src --reload
```

Ouvre `http://127.0.0.1:8000/docs`, puis exécute avec l'interface Swagger :

- `GET /health` ;
- `POST /study-plans` avec une durée de 40 ;
- le même POST avec une durée de 5.

Dans un autre terminal, exécute les tests :

```powershell
python -m pytest tests/test_api.py -v
```

Compare la réponse 422 avec les contraintes du modèle Pydantic.

## Exercice

Ajoute `GET /study-levels` qui retourne les valeurs acceptées par l'énumération
`Level`. Déclare un modèle de réponse, puis teste le code 200 et le JSON exact.

## Critère de réussite

Tu dois pouvoir tracer une requête invalide sans dire vaguement « FastAPI fait
la validation » : précise quelle annotation sélectionne le corps, quel modèle
effectue la validation et pourquoi la fonction métier n'est pas appelée.

## Référence officielle

- [FastAPI — Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI — Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI — Testing](https://fastapi.tiangolo.com/tutorial/testing/)
