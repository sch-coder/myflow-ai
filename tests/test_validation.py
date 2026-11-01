import json
import sys
import tempfile
from pathlib import Path

from src.form_assistant import suggerer_champs
from src.validation import (
    ETAT_REFUSE,
    ETAT_SUGGERE,
    ETAT_VALIDE,
    creer_dossier,
    refuser,
    valider,
)

PROCEDURE = {
    "id": "PROC-TEST",
    "champs_requis": [
        {"cle": "nom_collaborateur", "libelle": "Nom du collaborateur"},
        {"cle": "date_arrivee", "libelle": "Date d'arrivée"},
    ],
}
RECOMMANDATION = {
    "procedure_id": "PROC-TEST",
    "workflow": "Workflow de test",
    "validation_requise": "Manager",
    "score_recherche": 0.6123,
}

nb_ok = 0
nb_total = 0


def verifier(nom, condition):
    global nb_ok, nb_total
    nb_total += 1
    nb_ok += bool(condition)
    print(f"[{'OK' if condition else 'KO'}] {nom}")


def leve_erreur(fonction, *args):
    try:
        fonction(*args)
    except ValueError:
        return True
    return False


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        journal = Path(tmp) / "logs" / "journal.jsonl"

        champs = suggerer_champs(PROCEDURE, "Un alternant arrive le 3 décembre")
        dossier = creer_dossier(RECOMMANDATION, champs, journal)
        verifier("état initial = suggéré", dossier["etat"] == ETAT_SUGGERE)

        verifier(
            "validation refusée si aucun champ n'est confirmé",
            leve_erreur(valider, dossier, {}, journal),
        )
        verifier("état toujours suggéré après l'échec", dossier["etat"] == ETAT_SUGGERE)

        valeurs = {"nom_collaborateur": "Jean Dupont", "date_arrivee": "3 décembre"}
        valider(dossier, valeurs, journal)
        verifier("état = validé après confirmation de tous les champs", dossier["etat"] == ETAT_VALIDE)
        verifier(
            "les valeurs saisies sont enregistrées dans le dossier",
            dossier["champs"][0]["valeur"] == "Jean Dupont",
        )
        verifier(
            "double validation refusée",
            leve_erreur(valider, dossier, valeurs, journal),
        )

        dossier2 = creer_dossier(RECOMMANDATION, champs, journal)
        refuser(dossier2, journal)
        verifier("état = refusé après refus", dossier2["etat"] == ETAT_REFUSE)
        verifier(
            "validation impossible après un refus",
            leve_erreur(valider, dossier2, valeurs, journal),
        )

        contenu = journal.read_text(encoding="utf-8")
        lignes = contenu.splitlines()
        verifier(f"journal : 5 lignes attendues (obtenu : {len(lignes)})", len(lignes) == 5)

        try:
            [json.loads(ligne) for ligne in lignes]
            json_valide = True
        except json.JSONDecodeError:
            json_valide = False
        verifier("chaque ligne du journal est un JSON valide", json_valide)

        verifier(
            "aucune donnée personnelle dans le journal",
            "Jean Dupont" not in contenu and "décembre" not in contenu,
        )

    print(f"\nRésultat : {nb_ok}/{nb_total}")


if __name__ == "__main__":
    main()