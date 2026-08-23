# 03 — Outlines : produire une sortie structurée

## Objectif

À la fin de ce chapitre, tu dois comprendre la différence entre :

- demander du JSON dans un prompt ;
- extraire du JSON d'un texte libre ;
- contraindre la génération par un schéma ;
- valider les règles métier après la génération.

Le fichier étudié est `src/study_assistant/outlines_adapter.py`.

## Pourquoi « réponds en JSON » ne suffit pas

Un LLM prédit des tokens. Une instruction textuelle n'est pas un système de
types : le modèle peut ajouter du Markdown, oublier une clé ou produire un type
incorrect.

Trois stratégies doivent être distinguées :

```text
prompt seulement       -> convention probabiliste
parse après génération -> détection tardive d'une erreur
génération contrainte  -> espace de sorties limité par un schéma
```

Outlines fournit une interface uniforme pour associer un type de sortie à un
modèle. Le mécanisme réel dépend du backend : pour un modèle local directement
pilotable, la contrainte peut agir sur les tokens admissibles ; pour un service
dit « black box », Outlines transmet le format au mécanisme structuré offert
par ce service.

Avec l'adaptateur Ollama utilisé ici, la contrainte disponible est un JSON
Schema. Le modèle Pydantic `StudyPlan` devient donc à la fois le contrat Python
et la description de sortie envoyée au serveur.

## Deux protections complémentaires

```text
StudyPlan (Pydantic)
    |
    +--> JSON Schema envoyé par Outlines/Ollama
    |
    +--> validation Pydantic de la valeur reçue
```

La première protection réduit les sorties syntaxiquement invalides. La seconde
reste indispensable pour les invariants métier. Un JSON peut respecter ses
types tout en étant absurde : trois durées valides peuvent ne pas totaliser la
durée demandée.

## Lecture guidée du code

`create_ollama_generator()` effectue quatre opérations explicites :

```python
client = ollama.Client(host=base_url, timeout=120.0)
model = outlines.from_ollama(client, model_name)
generator = outlines.Generator(model, StudyPlan)
```

1. créer le client du fournisseur ;
2. l'adapter à l'interface Outlines ;
3. associer le modèle de sortie Pydantic ;
4. retourner un générateur appelable.

La création est dans une fonction. Importer le module ne contacte donc pas le
serveur et ne charge pas de modèle.

`normalize_generated_plan()` accepte volontairement trois représentations :
objet `StudyPlan`, JSON texte ou objet Python. Elle ramène ensuite chaque chemin
vers une seule représentation interne validée.

## Expérience hors ligne

Le test injecte un faux générateur. Il vérifie la frontière sans GPU, sans
réseau et sans sortie probabiliste :

```powershell
python -m pytest tests/test_outlines_adapter.py -v
```

L'injection de `fake_generator` est importante : un test unitaire doit vérifier
notre code, pas la disponibilité du serveur `192.168.18.5`.

## Expérience avec Ollama

Cette expérience contacte explicitement le serveur du laboratoire et utilise
le modèle `prof-python-ai`. Depuis un interpréteur Python lancé dans
l'environnement du projet :

```python
from study_assistant.outlines_adapter import generate_structured_plan
from study_assistant.schemas import StudyRequest

request = StudyRequest(
    topic="Outlines",
    level="debutant",
    available_minutes=45,
)
plan = generate_structured_plan(request)
print(plan.model_dump_json(indent=2))
```

Si le serveur est inaccessible, l'erreur réseau est normale et distincte d'une
`ValidationError`. Si le serveur retourne une structure incohérente, Pydantic
doit la refuser : ce comportement est voulu.

## Exercice

Crée un modèle `QuizQuestion` avec une question, quatre choix, l'index de la
bonne réponse et une explication. Ajoute un invariant garantissant que l'index
pointe vers un choix existant, puis utilise-le comme `output_type` d'un second
générateur Outlines.

Teste d'abord la normalisation avec un faux JSON avant tout appel au modèle.

## Critère de réussite

Tu dois pouvoir expliquer pourquoi « JSON valide » ne signifie ni « donnée
métier valide » ni « réponse factuellement vraie », et situer exactement le
rôle d'Outlines par rapport à Pydantic.

## Référence officielle

- [Outlines — Architecture](https://dottxt-ai.github.io/outlines/main/guide/architecture/)
- [Outlines — Ollama](https://dottxt-ai.github.io/outlines/main/features/models/ollama/)
- [Outlines — Generator](https://dottxt-ai.github.io/outlines/main/features/core/generator/)
