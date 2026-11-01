import streamlit as st

from src.classifier import construire_recommandation
from src.form_assistant import suggerer_champs
from src.search_engine import MoteurRecherche
from src.validation import creer_dossier
from ui import components as ui
from ui.styles import appliquer_styles

st.set_page_config(page_title="MyFlow AI Assistant", layout="wide")

PAGES = [
    "Dashboard",
    "Recherche intelligente",
    "Recommandations de workflow",
    "Documentation",
    "À propos",
]

# Exemples : libellé du bouton -> demande
EXEMPLES = {
    "Accès pour un nouvel arrivant": "J'ai un nouveau collaborateur dans mon service et je dois lui donner accès à l'application de gestion de comptes",
    "Installer un logiciel": "Peux-tu installer Teams sur mon ordinateur ?",
    "Retirer des droits": "Un prestataire quitte la mission, je souhaite supprimer ses droits sur l'outil de suivi",
    "Lien suspect reçu": "J'ai cliqué sur un lien douteux dans un mail",
}

MAX_CARACTERES = 1000

LIBELLES_STATUT = {
    "ok": "",
    "ambigu": " (ambigu)",
    "hors_sujet": " (hors sujet, aucune recommandation)",
    "trop_court": " (demande trop courte)",
}


@st.cache_resource(show_spinner="Chargement du modèle de recherche local...")
def charger_moteur():
    return MoteurRecherche()


def definir_exemple(texte):
    st.session_state["demande"] = texte


def lancer_analyse(moteur, demande):
    analyse = moteur.rechercher(demande)
    reco = construire_recommandation(analyse)
    champs = []
    dossier = None
    if reco:
        champs = suggerer_champs(analyse["resultats"][0]["procedure"], demande)
        dossier = creer_dossier(reco, champs)
    return {"demande": demande, "analyse": analyse, "reco": reco, "champs": champs, "dossier": dossier}


def page_dashboard():
    st.title("Bienvenue sur MyFlow AI")
    st.markdown(
        "Décrivez votre besoin en français. L'assistant recherche la procédure la plus proche "
        "dans la base documentaire, explique sa recommandation et suggère les champs du formulaire. "
        "**Rien n'est exécuté sans votre validation.**"
    )

    try:
        moteur = charger_moteur()
    except Exception as erreur:
        st.error(f"Impossible de charger le moteur de recherche : {erreur}")
        st.stop()

    st.text_area(
        "Votre demande",
        key="demande",
        height=140,
        max_chars=MAX_CARACTERES,
        placeholder="Exemple : un nouveau collaborateur arrive dans mon service et a besoin d'un accès à une application...",
    )

    if st.button("Analyser la demande", type="primary"):
        demande = st.session_state["demande"]
        if not demande.strip():
            st.error("Saisissez une demande avant de lancer l'analyse.")
        else:
            try:
                with st.spinner("Analyse en cours..."):
                    resultat = lancer_analyse(moteur, demande)
            except Exception as erreur:
                st.session_state["derniere"] = None
                st.error(f"L'analyse a échoué : {erreur}. Réessayez ou contactez le support.")
            else:
                st.session_state["derniere"] = resultat
                titre = resultat["reco"]["titre"] if resultat["reco"] else "Aucune procédure"
                st.session_state["recentes"].insert(
                    0, {"demande": demande, "titre": titre, "statut": resultat["analyse"]["statut"]}
                )
                st.session_state["recentes"] = st.session_state["recentes"][:5]

    st.markdown("##### Exemples de demandes")
    colonnes = st.columns(2)
    for i, (libelle, texte) in enumerate(EXEMPLES.items()):
        with colonnes[i % 2]:
            st.button(libelle, key=f"ex_{i}", on_click=definir_exemple, args=(texte,), use_container_width=True)

    if st.session_state["derniere"]:
        st.divider()
        st.subheader("Résultat de l'analyse")
        ui.afficher_resultats(st.session_state["derniere"])

    st.divider()
    st.markdown("##### Analyses récentes")
    if not st.session_state["recentes"]:
        st.caption("Aucune analyse pour le moment. Les analyses récentes restent en mémoire pendant la session uniquement.")
    else:
        for r in st.session_state["recentes"]:
            suffixe = LIBELLES_STATUT.get(r["statut"], "")
            extrait = r["demande"] if len(r["demande"]) <= 70 else r["demande"][:70] + "..."
            st.markdown(f"- **{r['titre']}**{suffixe} : {extrait}")


def main():
    st.session_state.setdefault("demande", "")
    st.session_state.setdefault("derniere", None)
    st.session_state.setdefault("recentes", [])

    appliquer_styles()
    ui.logo_sidebar()
    page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")
    ui.note_sidebar()

    if page == "Dashboard":
        page_dashboard()
    else:
        ui.page_a_venir(page)

    ui.footer()


main()