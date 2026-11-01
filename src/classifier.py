def construire_recommandation(analyse):
    """Transforme le résultat de la recherche en recommandation structurée.

    La classification n'utilise AUCUN second modèle : elle lit les métadonnées
    de la procédure la plus proche (catégorie, contexte, workflow, validation).
    Aucun texte n'est généré : tout provient de la base documentaire.

    Renvoie None si aucune recommandation ne peut être faite (hors sujet,
    trop court). Si la demande est ambiguë, la recommandation est marquée
    comme telle et les alternatives sont fournies.
    """
    if not analyse["resultats"]:
        return None

    meilleur = analyse["resultats"][0]
    proc = meilleur["procedure"]

    explication = (
        f"Cette procédure est proposée car la demande est proche (score de recherche "
        f"{meilleur['score']:.2f}) du passage suivant de la base documentaire : "
        f"« {meilleur['passage']} ». Ce score mesure la proximité des textes ; "
        f"ce n'est pas une probabilité que la recommandation soit correcte."
    )

    return {
        "ambigu": analyse["statut"] == "ambigu",
        "procedure_id": proc["id"],
        "titre": proc["titre"],
        "categorie": proc["categorie"],
        "contexte": proc["contexte"],
        "workflow": proc["workflow"],
        "validation_requise": proc["validation_requise"],
        "score_recherche": meilleur["score"],
        "explication": explication,
        "source": proc["source"],
        "alternatives": [
            {"id": r["procedure"]["id"], "titre": r["procedure"]["titre"], "score": r["score"]}
            for r in analyse["resultats"][1:]
        ],
    }