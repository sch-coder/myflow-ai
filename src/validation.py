import json
import uuid
from datetime import datetime, timezone

from src.config import JOURNAL_PATH
from src.form_assistant import A_RENSEIGNER

ETAT_SUGGERE = "suggere"
ETAT_VALIDE = "valide_par_utilisateur"
ETAT_REFUSE = "refuse_par_utilisateur"

# Libellés lisibles pour l'interface
LIBELLES_ETAT = {
    ETAT_SUGGERE: "Suggéré (en attente de votre validation)",
    ETAT_VALIDE: "Validé par l'utilisateur",
    ETAT_REFUSE: "Refusé par l'utilisateur",
}


def _maintenant():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def journaliser(dossier, evenement, chemin=JOURNAL_PATH):
    """Ajoute une ligne au journal.

    Minimisation des données : on n'enregistre NI le texte de la demande,
    NI les valeurs des champs, seulement leur statut.
    """
    entree = {
        "horodatage": _maintenant(),
        "id_dossier": dossier["id_dossier"],
        "evenement": evenement,
        "etat": dossier["etat"],
        "procedure_id": dossier["procedure_id"],
        "score_recherche": round(dossier["score_recherche"], 3),
        "champs": {c["cle"]: c["statut"] for c in dossier["champs"]},
    }
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "a", encoding="utf-8") as fichier:
        fichier.write(json.dumps(entree, ensure_ascii=False) + "\n")


def creer_dossier(recommandation, champs, chemin_journal=JOURNAL_PATH):
    """Crée un dossier à l'état « suggéré ». Aucune action n'est exécutée."""
    dossier = {
        "id_dossier": uuid.uuid4().hex[:8],
        "etat": ETAT_SUGGERE,
        "procedure_id": recommandation["procedure_id"],
        "workflow": recommandation["workflow"],
        "validation_requise": recommandation["validation_requise"],
        "score_recherche": recommandation["score_recherche"],
        "champs": [dict(c) for c in champs],
        "cree_le": _maintenant(),
    }
    journaliser(dossier, "dossier_cree", chemin_journal)
    return dossier


def valider(dossier, valeurs, chemin_journal=JOURNAL_PATH):
    """Valide le dossier, uniquement si l'utilisateur a renseigné TOUS les champs.

    `valeurs` : dictionnaire {cle_du_champ: valeur saisie par l'utilisateur}.
    Les champs préremplis doivent aussi être confirmés (fournis dans `valeurs`).
    """
    if dossier["etat"] != ETAT_SUGGERE:
        raise ValueError("Ce dossier a déjà été traité.")

    manquants = []
    for champ in dossier["champs"]:
        valeur = str(valeurs.get(champ["cle"], "")).strip()
        if not valeur or valeur == A_RENSEIGNER:
            manquants.append(champ["libelle"])

    if manquants:
        journaliser(dossier, "validation_incomplete", chemin_journal)
        raise ValueError("Champs à renseigner : " + ", ".join(manquants))

    for champ in dossier["champs"]:
        champ["valeur"] = str(valeurs[champ["cle"]]).strip()
        champ["statut"] = "valide_utilisateur"

    dossier["etat"] = ETAT_VALIDE
    dossier["valide_le"] = _maintenant()
    journaliser(dossier, "validation", chemin_journal)
    return dossier


def refuser(dossier, chemin_journal=JOURNAL_PATH):
    """Marque le dossier comme refusé par l'utilisateur."""
    if dossier["etat"] != ETAT_SUGGERE:
        raise ValueError("Ce dossier a déjà été traité.")
    dossier["etat"] = ETAT_REFUSE
    journaliser(dossier, "refus", chemin_journal)
    return dossier