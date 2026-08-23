# 04 — LangChain : composer des composants LLM

## Objectif

À la fin de ce chapitre, tu dois pouvoir composer un prompt, un modèle et un
parseur, injecter un faux modèle pour les tests et expliquer le coût d'une
abstraction supplémentaire.

Le fichier étudié est `src/study_assistant/chain.py`.

## Pourquoi LangChain existe

Chaque fournisseur possède ses formats de messages, ses options, ses réponses
et ses méthodes de streaming. Sans abstraction, changer Ollama pour un autre
fournisseur propage ces détails dans tout le programme.

LangChain définit des interfaces et des composants composables. Dans cet
exemple, la chaîne est :

```text
dictionnaire d'entrée
        |
        v
ChatPromptTemplate
        |
        v
ChatModel
        |
        v
StrOutputParser
        |
        v
str
```

L'opérateur `|` construit cette composition. Il ne déclenche pas l'exécution ;
`invoke()` fournit ensuite une entrée à la chaîne construite.

## Une analogie C++

Chaque composant se comporte comme un objet qui respecte une interface de type
« entrée vers sortie ». L'opérateur `|` ressemble à la composition de
foncteurs : la sortie compatible du composant A devient l'entrée de B.

L'intérêt n'est pas la syntaxe elle-même. Il vient de l'interface commune :
invocation synchrone ou asynchrone, batch, streaming, configuration, traces et
substitution d'un composant.

## Lecture guidée du code

`build_teacher_prompt()` ne connaît aucun fournisseur. Les deux constructeurs
suivants réutilisent exactement ce prompt :

- `build_offline_chain()` branche un `RunnableLambda` déterministe ;
- `build_ollama_chain()` branche `ChatOllama`.

Le faux modèle retourne un `AIMessage`, pas une simple chaîne. Il respecte ainsi
le même type de sortie conceptuel qu'un chat model avant le
`StrOutputParser`.

Cette substitution est un exemple d'inversion de dépendance :
`explain_topic()` reçoit un `Runnable` et n'a pas besoin de savoir s'il appelle
une lambda locale, Ollama ou un fournisseur cloud.

## API actuelle et vieux tutoriels

Le projet cible LangChain 1.3. Beaucoup d'exemples en ligne concernent les
versions 0.x et utilisent des abstractions déplacées vers
`langchain-classic`. Ne copie pas une classe comme `LLMChain` uniquement parce
qu'un tutoriel ancien l'utilise. Pars des interfaces actuelles : modèles,
messages, outils, agents et `Runnable`.

## Expérience hors ligne

```powershell
python -m pytest tests/test_chain.py -v
```

Le test prouve que :

- les variables remplissent le template ;
- le faux modèle reçoit un prompt formaté ;
- le parseur convertit `AIMessage` vers `str` ;
- aucun serveur n'est nécessaire.

Tu peux aussi invoquer la chaîne dans Python :

```python
from study_assistant.chain import explain_topic
from study_assistant.schemas import StudyRequest

request = StudyRequest(topic="LCEL", available_minutes=30)
print(explain_topic(request))
```

## Remplacer la simulation par Ollama

```python
from study_assistant.chain import build_ollama_chain, explain_topic
from study_assistant.schemas import StudyRequest

request = StudyRequest(topic="LangChain", available_minutes=45)
chain = build_ollama_chain()
print(explain_topic(request, chain=chain))
```

Le changement concerne la construction du modèle, pas le prompt ni la fonction
appelante. C'est le bénéfice architectural recherché.

## Quand ne pas utiliser LangChain

Pour un seul appel HTTP stable, une petite fonction utilisant le SDK officiel
peut être plus lisible. Une abstraction se justifie si elle apporte une valeur
réelle : composition, outils, fournisseurs interchangeables, streaming,
observabilité ou conventions partagées.

## Exercice

Ajoute un second `RunnableLambda` après le parseur pour retourner un dictionnaire
contenant `answer` et `character_count`. Mets à jour le test avant de modifier
le code.

## Critère de réussite

Tu dois pouvoir identifier le type conceptuel à chaque étape de la chaîne et
remplacer le modèle sans modifier le template.

## Référence officielle

- [LangChain — Overview](https://docs.langchain.com/oss/python/langchain/overview)
- [LangChain — ChatOllama](https://docs.langchain.com/oss/python/integrations/chat/ollama)
- [LangChain v1](https://docs.langchain.com/oss/python/releases/langchain-v1)
