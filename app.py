import streamlit as st

from src.classifier import construire_recommandation
from src.form_assistant import suggerer_champs
from src.search_engine import MoteurRecherche, charger_procedures
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


@st.cache_data
def charger_catalogue():
    return charger_procedures()


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


def obtenir_moteur():
    try:
        return charger_moteur()
    except Exception as erreur:
        st.error(f"Impossible de charger le moteur de recherche : {erreur}")
        st.stop()


def page_dashboard():
    st.title("Bienvenue sur MyFlow AI")
    st.markdown(
        "Décrivez votre besoin en français. L'assistant recherche la procédure la plus proche "
        "dans la base documentaire, explique sa recommandation et suggère les champs du formulaire. "
        "**Rien n'est exécuté sans votre validation.**"
    )

    moteur = obtenir_moteur()

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


def page_recherche():
    st.title("Recherche intelligente")
    st.markdown(
        "Recherche sémantique seule : les trois procédures les plus proches de votre texte, "
        "avec leur score. **Aucun dossier n'est créé et rien n'est enregistré.**"
    )

    moteur = obtenir_moteur()

    requete = st.text_input(
        "Votre recherche",
        key="requete",
        max_chars=MAX_CARACTERES,
        placeholder="Exemple : réinitialiser un mot de passe",
    )

    if st.button("Rechercher", type="primary"):
        if not requete.strip():
            st.error("Saisissez un texte avant de lancer la recherche.")
        else:
            try:
                with st.spinner("Recherche en cours..."):
                    st.session_state["recherche_res"] = moteur.rechercher(requete)
            except Exception as erreur:
                st.session_state["recherche_res"] = None
                st.error(f"La recherche a échoué : {erreur}")

    analyse = st.session_state["recherche_res"]
    if analyse is None:
        st.caption("Aucune recherche pour le moment.")
        return

    if analyse["statut"] in ("trop_court", "hors_sujet"):
        st.warning(analyse["message"])
        return
    if analyse["statut"] == "ambigu":
        st.warning(analyse["message"])

    st.caption("Les scores sont des similarités cosinus (scores de recherche), pas des probabilités de confiance.")
    for rang, r in enumerate(analyse["resultats"], start=1):
        proc = r["procedure"]
        with st.expander(f"{rang}. {proc['titre']} : score {r['score']:.2f}", expanded=(rang == 1)):
            st.markdown(f"**Catégorie :** {proc['categorie']}  \n**Workflow :** {proc['workflow']}")
            st.markdown(f"**Passage le plus proche :** {r['passage']}")
            st.markdown(f"**Source :** {proc['source']}")


def page_recommandations():
    st.title("Recommandations de workflow")
    st.markdown("Catalogue des procédures de la base documentaire (fictive).")

    procedures = charger_catalogue()
    categories = sorted({p["categorie"] for p in procedures})
    choix = st.selectbox("Catégorie", ["Toutes les catégories"] + categories)

    affichees = [p for p in procedures if choix == "Toutes les catégories" or p["categorie"] == choix]
    st.caption(f"{len(affichees)} procédure(s) affichée(s).")

    for proc in affichees:
        with st.expander(f"{proc['titre']} ({proc['id']})"):
            st.markdown(
                f"**Catégorie :** {proc['categorie']}  \n"
                f"**Contexte :** {proc['contexte']}  \n"
                f"**Workflow :** {proc['workflow']}  \n"
                f"**Validation requise :** {proc['validation_requise']}"
            )
            st.markdown(proc["description"])
            st.markdown("**Informations à fournir :**")
            for champ in proc["champs_requis"]:
                st.markdown(f"- {champ['libelle']}")
            st.caption(f"Source : {proc['source']}")


def page_documentation():
    st.title("Documentation")
    st.markdown(
        """
### Comment ça marche

1. Vous décrivez votre besoin en français.
2. Le texte est transformé en vecteur par un modèle multilingue exécuté **en local**.
3. Ce vecteur est comparé aux passages de la base documentaire (similarité cosinus).
4. La procédure la plus proche fournit la catégorie, le contexte, le workflow et le validateur.
5. L'explication cite le passage de la base qui a motivé la recommandation : aucun texte n'est généré.
6. Les champs du formulaire viennent de la procédure. Un champ inconnu reste « À renseigner par l'utilisateur ».
7. Vous vérifiez, complétez et validez. **Rien n'est exécuté par l'application.**

### Statuts d'une analyse

| Statut | Signification |
|---|---|
| Normal | Une procédure se détache nettement. |
| Ambigu | Deux procédures sont presque à égalité : à vous de choisir. |
| Hors sujet | Score sous le seuil de pertinence : aucune recommandation. |
| Trop court | Moins de deux mots : la demande n'est pas analysée. |

### États d'un dossier

- **Suggéré** : proposé par l'outil, non vérifié.
- **Validé par l'utilisateur** : tous les champs ont été confirmés par vous.
- **Refusé par l'utilisateur** : aucune suite donnée.

### À savoir

- Le score est une **mesure de proximité de textes**, pas une probabilité que la recommandation soit correcte.
- Les fautes de frappe et les noms de marque peuvent mal fonctionner.
- Le journal de traçabilité enregistre des statuts, jamais le texte de votre demande ni vos saisies.
"""
    )


def page_a_propos():
    st.title("À propos")
    st.markdown(
        """
**MyFlow AI Assistant** (*Intelligent Workflow Assistant*) est un **POC personnel indépendant**.
Ce n'est pas une application officielle d'un établissement bancaire, elle n'est connectée à aucune
infrastructure réelle et n'utilise que des **données fictives**.

### Technologies

Python 3.11, Streamlit, Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`, local),
scikit-learn (similarité cosinus), JSON.

### Principes de conception

- Traitement 100 % local, aucune donnée envoyée à l'extérieur.
- Supervision humaine obligatoire avant toute décision.
- Traçabilité minimale : statuts uniquement.
- Prévention des hallucinations : classification par métadonnées, explication par citation, seuil de pertinence, détection d'ambiguïté.

### Résultats des tests (très petits jeux, non statistiques)

| Jeu | Top 1 | Top 3 |
|---|---|---|
| Développement (11 cas) | 8/11 | 11/11 |
| Validation 1 (6 cas) | 6/6 | 6/6 |
| Validation 2 (6 cas, partiellement contaminé) | 3/6 | 5/6 |

Ces chiffres sont indicatifs : ils ne mesurent pas une précision réelle.
"""
    )


def main():
    st.session_state.setdefault("demande", "")
    st.session_state.setdefault("derniere", None)
    st.session_state.setdefault("recentes", [])
    st.session_state.setdefault("recherche_res", None)

    appliquer_styles()
    ui.logo_sidebar()
    page = st.sidebar.radio("Navigation", PAGES, label_visibility="collapsed")
    ui.note_sidebar()

    if page == "Dashboard":
        page_dashboard()
    elif page == "Recherche intelligente":
        page_recherche()
    elif page == "Recommandations de workflow":
        page_recommandations()
    elif page == "Documentation":
        page_documentation()
    else:
        page_a_propos()

    ui.footer()


main()