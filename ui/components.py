import html

import streamlit as st

from src.validation import ETAT_REFUSE, ETAT_SUGGERE, ETAT_VALIDE, LIBELLES_ETAT, refuser, valider


def e(texte):
    """Échappe un texte avant de l'insérer dans du HTML (protection contre l'injection)."""
    return html.escape(str(texte))


def logo_sidebar():
    st.sidebar.markdown(
        '<div class="mf-logo"><span class="mf-logo-mark"></span>'
        '<div><div class="mf-logo-title">MyFlow AI</div>'
        '<div class="mf-logo-sub">Intelligent Workflow Assistant</div></div></div>',
        unsafe_allow_html=True,
    )


def note_sidebar():
    st.sidebar.markdown(
        '<div style="font-size:0.75rem; opacity:0.75; margin-top:2rem;">'
        "POC indépendant<br>Données fictives<br>Traitement 100 % local</div>",
        unsafe_allow_html=True,
    )


def carte(titre, corps_html):
    """Affiche une carte. `corps_html` doit déjà être échappé par l'appelant."""
    st.markdown(
        f'<div class="mf-card"><div class="mf-card-title">{e(titre)}</div>{corps_html}</div>',
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        '<div class="mf-footer">MyFlow AI Assistant : POC indépendant à visée de démonstration. '
        "Projet personnel, non affilié à un établissement bancaire, sans connexion à un système réel. "
        "Données fictives uniquement.</div>",
        unsafe_allow_html=True,
    )


def page_a_venir(nom):
    st.title(nom)
    st.info("Cette page sera ajoutée dans une prochaine étape du projet.")


def _table_champs(champs):
    lignes = []
    for c in champs:
        if c["statut"] == "suggere":
            valeur = e(c["valeur"])
            badge = '<span class="mf-badge mf-badge-sugg">Suggéré</span>'
        else:
            valeur = f'<span class="mf-empty">{e(c["valeur"])}</span>'
            badge = '<span class="mf-badge mf-badge-todo">À renseigner</span>'
        lignes.append(
            f"<tr><td>{e(c['libelle'])}</td><td>{valeur}</td><td>{badge}</td>"
            f'<td class="mf-muted">{e(c["origine"])}</td></tr>'
        )
    return (
        '<table class="mf-table"><thead><tr><th>Champ</th><th>Valeur</th><th>Statut</th><th>Origine</th></tr></thead>'
        f"<tbody>{''.join(lignes)}</tbody></table>"
    )


def _table_champs_valides(champs):
    lignes = "".join(
        f"<tr><td>{e(c['libelle'])}</td><td>{e(c['valeur'])}</td></tr>" for c in champs
    )
    return (
        '<table class="mf-table"><thead><tr><th>Champ</th><th>Valeur confirmée</th></tr></thead>'
        f"<tbody>{lignes}</tbody></table>"
    )


def section_validation(res, index):
    """Formulaire de validation humaine. Utilise le dossier stocké dans res["dossier"]."""
    dossier = res["dossier"]
    etat = dossier["etat"]

    st.markdown("#### Validation humaine")
    st.caption(
        f"État du dossier {dossier['id_dossier']} : **{LIBELLES_ETAT[etat]}**. "
        "L'application n'exécute aucune action : valider enregistre uniquement votre décision."
    )

    if etat == ETAT_VALIDE:
        st.success("Dossier validé par l'utilisateur. Il doit maintenant suivre l'approbation prévue : "
                   f"{dossier['validation_requise']}. Cette étape n'est pas simulée dans ce POC.")
        carte("Valeurs confirmées par l'utilisateur", _table_champs_valides(dossier["champs"]))
        return

    if etat == ETAT_REFUSE:
        st.info("Dossier refusé par l'utilisateur. Aucune action n'a été enregistrée.")
        return

    st.markdown(
        "Vérifiez ou complétez **chaque** champ. Les valeurs suggérées ne sont pas validées "
        "tant que vous ne les avez pas confirmées."
    )

    valeurs = {}
    for champ in dossier["champs"]:
        defaut = champ["valeur"] if champ["statut"] == "suggere" else ""
        valeurs[champ["cle"]] = st.text_input(
            champ["libelle"],
            value=defaut,
            key=f"champ_{dossier['id_dossier']}_{champ['cle']}",
            max_chars=300,
        )

    col1, col2, _ = st.columns([1.3, 1, 3])
    with col1:
        clic_valider = st.button("Valider la demande", type="primary", key=f"val_{dossier['id_dossier']}")
    with col2:
        clic_refuser = st.button("Refuser", key=f"ref_{dossier['id_dossier']}")

    if clic_valider:
        try:
            valider(dossier, valeurs)
            st.rerun()
        except ValueError as erreur:
            st.error(str(erreur))
    if clic_refuser:
        refuser(dossier)
        st.rerun()


def afficher_resultats(res):
    """Affiche le résultat d'une analyse (dictionnaire construit par app.py)."""
    analyse = res["analyse"]
    reco = res["reco"]
    champs = res["champs"]
    statut = analyse["statut"]

    if statut in ("trop_court", "hors_sujet"):
        st.warning(analyse["message"])
        if analyse["meilleur_score"] is not None:
            st.caption(
                f"Meilleur score de recherche : {analyse['meilleur_score']:.2f} "
                "(sous le seuil de pertinence, aucune procédure n'est recommandée)."
            )
        return

    if statut == "ambigu":
        st.warning(analyse["message"] + " La procédure en tête est affichée ci-dessous, avec les alternatives.")
    else:
        st.success("Analyse terminée. Cette recommandation est une suggestion : elle n'est pas validée.")

    col1, col2, col3 = st.columns([1.2, 1.6, 1.2])
    with col1:
        carte(
            "Catégorie",
            f'<div class="mf-card-value">{e(reco["categorie"])}</div>'
            f'<div class="mf-muted">Contexte : {e(reco["contexte"])}</div>',
        )
    with col2:
        carte(
            "Workflow recommandé",
            f'<div class="mf-card-value">{e(reco["workflow"])}</div>'
            f'<div class="mf-muted">Validation requise : {e(reco["validation_requise"])}</div>',
        )
    with col3:
        carte(
            "Score de recherche",
            f'<div class="mf-score">{reco["score_recherche"]:.2f}</div>'
            '<div class="mf-muted">Similarité cosinus. Ce n\'est pas une probabilité de confiance de l\'IA.</div>',
        )

    carte(
        "Pourquoi cette recommandation ?",
        f'<div class="mf-muted">{e(reco["explication"])}</div>',
    )

    carte(
        "Document source",
        f'<div class="mf-source">{e(reco["source"])}<br>'
        f'<span class="mf-muted">Procédure : {e(reco["titre"])} ({e(reco["procedure_id"])})</span></div>',
    )

    if res["dossier"]["etat"] == ETAT_SUGGERE:
        carte("Champs de formulaire suggérés", _table_champs(champs))

    if reco["alternatives"]:
        items = "".join(
            f"<li>{e(a['titre'])} ({e(a['id'])}) : score {a['score']:.2f}</li>"
            for a in reco["alternatives"]
        )
        carte("Autres procédures proches", f'<ul class="mf-muted" style="margin:0; padding-left:1.1rem;">{items}</ul>')

    section_validation(res, 0)