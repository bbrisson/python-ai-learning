# 01 — Pydantic : les contrats à l'exécution

## Objectif

À la fin de ce chapitre, tu dois pouvoir distinguer :

- une annotation de type Python ;
- une validation à l'exécution ;
- une conversion contrôlée ;
- une sérialisation ;
- un invariant portant sur plusieurs champs.

Le fichier étudié est `src/study_assistant/schemas.py`.

## Pourquoi Pydantic est nécessaire

En C++, le compilateur vérifie une grande partie des types avant l'exécution.
En Python, ceci :

```python
def double(value: int) -> int:
    return value * 2
```

n'empêche pas un appel `double("ab")`. L'annotation `int` est une information
pour les humains et les outils statiques ; l'interpréteur ne l'impose pas.

Une API reçoit pourtant des données non fiables : JSON, variables
d'environnement, fichiers ou sorties de modèle. Pydantic transforme une
annotation en **frontière d'exécution**. On peut comparer un modèle Pydantic à
une `struct` enrichie d'un parseur, de contrôles d'invariants et d'un
sérialiseur JSON.

## Le flux exact

```text
dict/JSON non fiable
        |
        v
validation + conversion Pydantic
        |
        +---- erreur impossible à convertir -> ValidationError
        |
        v
objet Python dont les champs respectent le contrat
```

Pydantic garantit la forme de l'objet **après** validation. Il peut convertir
une valeur compatible : la chaîne `"45"` devient par exemple l'entier `45`.
Lorsque cette conversion est indésirable, le mode strict est disponible.

## Lecture guidée du code

### 1. Une politique commune

`StrictModel` contient :

```python
model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
```

- `extra="forbid"` empêche une faute de frappe de disparaître silencieusement ;
- `str_strip_whitespace=True` nettoie les chaînes avant les autres contrôles.

Le nom `StrictModel` désigne ici la politique du projet sur les champs
inconnus. Il ne faut pas le confondre avec le **strict mode** de Pydantic, qui
désactive aussi certaines conversions de types.

### 2. Contraintes locales

Dans `StudyRequest`, `Field(ge=20, le=240)` borne la durée. Ce contrôle dépend
d'un seul champ. Le validateur `topic_must_contain_text`, lui, ajoute une règle
qui n'est pas exprimable par le simple type `str`.

### 3. Invariant global

Dans `StudyPlan`, `durations_must_match_total` est un `model_validator` exécuté
après la validation des champs. Il compare plusieurs valeurs déjà converties :

```text
sum(steps[*].duration_minutes) == total_minutes
```

C'est un invariant métier, comparable à une condition qui doit rester vraie
pour toute instance valide d'une classe C++.

### 4. Entrées et sorties

Les quatre opérations essentielles de Pydantic v2 sont :

```python
request = StudyRequest.model_validate(python_dict)
request = StudyRequest.model_validate_json(json_text)
python_dict = request.model_dump()
json_text = request.model_dump_json()
```

`model_json_schema()` produit aussi le JSON Schema réutilisé par FastAPI,
Outlines et les outils OpenAPI.

## Expérience

### Exemple débogable dans VS Code

Le fichier `exercices/01_pydantic_premier_modele.py` reprend le premier modèle
dans de petites fonctions adaptées au pas-à-pas. Il contient trois commentaires
`POINT D'ARRÊT` qui indiquent où observer les données.

Le fichier `exercices/02_pydantic_validation_conversion.py` poursuit avec trois
entrées : un entier, une chaîne convertible et une chaîne invalide. Il permet
d'inspecter un objet `ValidationError` dans le débogueur.

Le fichier `exercices/03_pydantic_contraintes_field.py` ajoute des bornes avec
`Field`, une valeur par défaut et l'export des contraintes en JSON Schema.

Exécution normale :

```powershell
python exercices/01_pydantic_premier_modele.py
```

Pour le débogage, ouvre le fichier dans VS Code, place un point d'arrêt sur
l'appel à `create_learning_goal`, lance `Python Debugger: Python File` avec
`F5`, puis utilise `F11` pour entrer dans la fonction et `F10` pour exécuter la
construction Pydantic sans parcourir immédiatement son code interne.

### Tests du contrat complet

Depuis le dossier `09-projets/02-assistant-apprentissage-ia/` :

```powershell
python -m pytest tests/test_schemas.py -v
```

Observe particulièrement :

- la conversion de `"45"` vers `45` ;
- le nettoyage des espaces autour de `Pydantic` ;
- le refus d'un champ inconnu ;
- le refus d'un total incohérent.

Pour afficher le schéma JSON :

```powershell
python -c "from study_assistant.schemas import StudyRequest; import json; print(json.dumps(StudyRequest.model_json_schema(), indent=2, ensure_ascii=False))"
```

Cette dernière commande suppose que le paquet a été installé en mode éditable.

## Exercice

Ajoute à `StudyRequest` un champ `language` limité à `"fr"` ou `"en"`, avec
`"fr"` par défaut. Ajoute ensuite deux tests : valeur par défaut et valeur
invalide.

Ne modifie pas encore FastAPI : le but est de constater qu'une modification du
contrat partagé se propage ensuite naturellement aux autres couches.

## Critère de réussite

Tu dois pouvoir expliquer pourquoi `dict` est acceptable à l'extérieur d'une
frontière, mais insuffisant comme contrat interne, et pourquoi une sortie LLM
doit encore passer par `model_validate*()`.

## Référence officielle

- [Pydantic — Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic — Validators](https://docs.pydantic.dev/latest/concepts/validators/)
