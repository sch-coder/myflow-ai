from pathlib import Path

# Dossier racine du projet (myflow-ai)
BASE_DIR = Path(__file__).resolve().parent.parent

# Base documentaire fictive
DATA_PATH = BASE_DIR / "data" / "procedures.json"

# Journal de traçabilité (une ligne JSON par événement, sans données personnelles)
JOURNAL_PATH = BASE_DIR / "logs" / "journal.jsonl"

# Modèle multilingue (compatible français), exécuté en local
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Nombre de procédures renvoyées par la recherche
TOP_K = 3

# Sous ce score, la demande est considérée hors sujet (aucune recommandation).
# Valeur provisoire, fixée sur un petit jeu de tests : à réviser avec plus de données.
SEUIL_PERTINENCE = 0.30

# Si l'écart entre le 1er et le 2e résultat est inférieur à cette marge,
# la demande est signalée comme ambiguë (plusieurs procédures proches).
MARGE_AMBIGUITE = 0.05

# Nombre minimal de caractères et de mots pour qu'une demande soit analysée
LONGUEUR_MIN = 3
MOTS_MIN = 2