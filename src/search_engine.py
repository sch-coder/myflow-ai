import json
import sys

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import (
    DATA_PATH,
    LONGUEUR_MIN,
    MARGE_AMBIGUITE,
    MODEL_NAME,
    MOTS_MIN,
    SEUIL_PERTINENCE,
    TOP_K,
)


def charger_procedures(chemin=DATA_PATH):
    """Lit la base documentaire JSON et renvoie la liste des procédures."""
    with open(chemin, encoding="utf-8") as fichier:
        return json.load(fichier)


class MoteurRecherche:
    """Recherche sémantique locale : embeddings + similarité cosinus."""

    def __init__(self):
        self.procedures = charger_procedures()
        self.modele = SentenceTransformer(MODEL_NAME)

        # Chaque procédure est découpée en plusieurs courts passages.
        # Raison : ce modèle ne lit que ~128 mots-pièces ; un seul gros texte
        # serait tronqué et les exemples de demandes seraient ignorés.
        self.passages = []  # liste de (index_procedure, texte)
        for i, proc in enumerate(self.procedures):
            self.passages.append((i, f"{proc['titre']}. {proc['description']}"))
            self.passages.append((i, "Mots-clés : " + ", ".join(proc["mots_cles"])))
            for exemple in proc["exemples_demandes"]:
                self.passages.append((i, exemple))

        textes = [texte for _, texte in self.passages]
        self.embeddings = self.modele.encode(textes, normalize_embeddings=True)

    def rechercher(self, demande, top_k=TOP_K):
        """Analyse la demande et renvoie un dictionnaire :

        - statut : "ok", "ambigu", "hors_sujet" ou "trop_court"
        - message : explication destinée à l'utilisateur (vide si "ok")
        - resultats : liste des procédures proches (vide si hors sujet / trop court)
        - meilleur_score : meilleur score de recherche (None si trop court)

        Le score est un score de recherche (similarité cosinus), pas une
        probabilité de confiance de l'IA.
        """
        demande = demande.strip()
        if not demande:
            raise ValueError("La demande est vide.")

        if len(demande) < LONGUEUR_MIN or len(demande.split()) < MOTS_MIN:
            return {
                "statut": "trop_court",
                "message": "La demande est trop courte pour être analysée. Décrivez votre besoin en une phrase.",
                "resultats": [],
                "meilleur_score": None,
            }

        vecteur = self.modele.encode([demande], normalize_embeddings=True)
        similarites = cosine_similarity(vecteur, self.embeddings)[0]

        # Pour chaque procédure, on garde son meilleur passage
        meilleurs = {}
        for (index, texte), score in zip(self.passages, similarites):
            if index not in meilleurs or score > meilleurs[index][0]:
                meilleurs[index] = (float(score), texte)

        classement = sorted(meilleurs.items(), key=lambda x: x[1][0], reverse=True)

        resultats = []
        for index, (score, texte) in classement[:top_k]:
            resultats.append(
                {
                    "procedure": self.procedures[index],
                    "score": score,
                    "passage": texte,
                }
            )

        meilleur_score = resultats[0]["score"]

        # Garde-fou anti-hallucination : sous le seuil, on ne recommande rien.
        if meilleur_score < SEUIL_PERTINENCE:
            return {
                "statut": "hors_sujet",
                "message": "Aucune procédure pertinente trouvée dans la base documentaire. Reformulez ou contactez le support.",
                "resultats": [],
                "meilleur_score": meilleur_score,
            }

        # Ambiguïté : deux procédures presque à égalité.
        if len(resultats) > 1 and (resultats[0]["score"] - resultats[1]["score"]) < MARGE_AMBIGUITE:
            return {
                "statut": "ambigu",
                "message": "Plusieurs procédures sont proches : choisissez celle qui correspond à votre besoin.",
                "resultats": resultats,
                "meilleur_score": meilleur_score,
            }

        return {
            "statut": "ok",
            "message": "",
            "resultats": resultats,
            "meilleur_score": meilleur_score,
        }


def afficher(analyse):
    print(f"\nStatut : {analyse['statut']}")
    if analyse["message"]:
        print(f"Message : {analyse['message']}")
    for rang, r in enumerate(analyse["resultats"], start=1):
        proc = r["procedure"]
        print(f"\n{rang}. {proc['titre']}  [{proc['id']}]")
        print(f"   Score de recherche (similarité cosinus) : {r['score']:.3f}")
        print(f"   Catégorie : {proc['categorie']}")
        print(f"   Passage le plus proche : {r['passage']}")
        print(f"   Source : {proc['source']}")


def main():
    # Évite les problèmes d'accents dans le terminal Windows
    sys.stdout.reconfigure(encoding="utf-8")

    print("Chargement du modèle (le premier lancement télécharge le modèle)...")
    moteur = MoteurRecherche()
    print("Moteur prêt.")

    # Mode 1 : demande donnée en argument
    if len(sys.argv) > 1:
        afficher(moteur.rechercher(" ".join(sys.argv[1:])))
        return

    # Mode 2 : boucle interactive
    print("Tape ta demande (ligne vide pour quitter).")
    while True:
        demande = input("\nDemande > ").strip()
        if not demande:
            break
        afficher(moteur.rechercher(demande))


if __name__ == "__main__":
    main()