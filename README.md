# MyFlow AI Assistant

*Intelligent Workflow Assistant*

> **POC personnel indépendant.** Ce projet n'est pas une application officielle d'un établissement bancaire, n'est connecté à aucune infrastructure réelle et n'utilise que des **données fictives**.

## Objectif

Un employé décrit un besoin en français. L'application :

1. cherche la procédure la plus proche dans une base documentaire JSON (recherche sémantique locale) ;
2. recommande un workflow, avec sa catégorie, son contexte et le validateur requis ;
3. explique la recommandation en citant le passage de la base qui l'a motivée ;
4. suggère les champs de formulaire (un champ inconnu reste « À renseigner par l'utilisateur ») ;
5. affiche le document source et le score de recherche ;
6. exige une validation humaine explicite avant d'enregistrer quoi que ce soit.

Le score affiché est une **similarité cosinus** (score de recherche). Ce n'est **pas** une probabilité de confiance de l'IA.

## Technologies

Python 3.11, Streamlit, Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`, exécuté en local), scikit-learn, JSON.

## Installation (Windows PowerShell)

```powershell
git clone <url-du-depot>
cd myflow-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Le premier lancement télécharge le modèle (environ 470 Mo). Ensuite, tout fonctionne hors ligne.

## Tests

```powershell
python -m tests.test_validation
python -m tests.test_scenarios
```

## Structure

```
myflow-ai/
  app.py                 point d'entrée Streamlit
  data/procedures.json   base documentaire fictive (12 procédures)
  src/                   moteur de recherche, classification, formulaire, validation
  ui/                    styles et composants de l'interface
  tests/                 tests de scénarios et de validation
```

## Sécurité et confidentialité

- Traitement 100 % local : aucune donnée envoyée à un service externe.
- Minimisation des données : le journal de traçabilité (`logs/`, non versionné) enregistre des statuts, jamais le texte des demandes ni les valeurs saisies.
- Supervision humaine : aucune action n'est exécutée ; l'état « suggéré » est distinct de « validé par l'utilisateur ».
- Prévention des hallucinations : classification par métadonnées du document le plus proche, explication issue d'une citation, seuil de pertinence, détection d'ambiguïté.
- Texte utilisateur échappé avant affichage HTML, saisie limitée à 1000 caractères.
- Aucun secret dans le dépôt : `.env` est ignoré, `.env.example` documente la règle.

## Résultats des tests et limites

Premiers tests sur de très petits jeux de phrases écrites à la main (11, 6 et 6 cas) : **ce ne sont pas des mesures statistiques de précision.**

| Jeu | Top 1 | Top 3 |
|---|---|---|
| Développement (11) | 8/11 | 11/11 |
| Validation 1 (6) | 6/6 | 6/6 |
| Validation 2 (6, partiellement contaminé) | 3/6 | 5/6 |

Limites connues :

- Le score ne mesure pas la justesse : des erreurs peuvent avoir un score élevé. La validation humaine est donc obligatoire.
- Les fautes de frappe (« mot de pase ») et les noms de marque (« ChatGPT ») sont mal gérés.
- Les seuils (pertinence 0,30, ambiguïté 0,05) sont provisoires et réglés sur peu de données.
- Les exemples de demandes de la base peuvent donner des scores artificiellement hauts sur des phrases proches.

## Pistes d'évolution

Jeu de test plus large, gestion des fautes de frappe, extension optionnelle FastAPI ou LLM avec repli local.