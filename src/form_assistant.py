import re

A_RENSEIGNER = "À renseigner par l'utilisateur"

MOIS = (
    "janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|"
    "septembre|octobre|novembre|décembre|decembre"
)

# Champs de type date : préremplis seulement si une date est écrite dans la demande
CHAMPS_DATE = {"date_arrivee", "date_depart", "date_effet"}

# Champs de description : repris tels quels de la demande de l'utilisateur
CHAMPS_DESCRIPTION = {"description_incident", "description_evenement"}

MOTIF_DATE = re.compile(
    rf"\b(\d{{1,2}}/\d{{1,2}}(?:/\d{{2,4}})?|\d{{1,2}}(?:er)?\s+(?:{MOIS})(?:\s+\d{{4}})?)\b",
    re.IGNORECASE,
)


def extraire_date(texte):
    """Renvoie la première date écrite explicitement dans le texte, sinon None.

    Rien n'est déduit : « lundi prochain » ou « demain » ne sont pas convertis.
    """
    correspondance = MOTIF_DATE.search(texte)
    return correspondance.group(1) if correspondance else None


def suggerer_champs(procedure, demande):
    """Renvoie la liste des champs du formulaire avec leur statut.

    Les champs viennent uniquement de procedure["champs_requis"].
    statut : "suggere" (valeur issue de la demande, à vérifier)
          ou "a_renseigner" (aucune valeur trouvée : rien n'est inventé).
    """
    champs = []
    for champ in procedure["champs_requis"]:
        valeur = A_RENSEIGNER
        statut = "a_renseigner"
        origine = "Aucune information dans la demande"

        if champ["cle"] in CHAMPS_DATE:
            date = extraire_date(demande)
            if date:
                valeur, statut = date, "suggere"
                origine = "Date écrite dans votre demande"
        elif champ["cle"] in CHAMPS_DESCRIPTION:
            valeur, statut = demande.strip(), "suggere"
            origine = "Texte repris de votre demande"

        champs.append(
            {
                "cle": champ["cle"],
                "libelle": champ["libelle"],
                "valeur": valeur,
                "statut": statut,
                "origine": origine,
            }
        )
    return champs