import streamlit as st

CSS = """
:root {
    --navy: #101D32;
    --teal: #087F70;
    --light: #EAF2F8;
    --grey: #5B6675;
    --border: #D5DEE8;
}

.stApp { background: #FFFFFF; color: var(--navy); font-family: "Segoe UI", system-ui, -apple-system, sans-serif; }
.block-container { padding-top: 2.5rem; max-width: 1100px; }
h1, h2, h3 { color: var(--navy); font-family: Georgia, "Times New Roman", serif; font-weight: 600; letter-spacing: -0.01em; }

/* Barre latérale */
[data-testid="stSidebar"] { background: var(--navy); }
[data-testid="stSidebar"] * { color: #FFFFFF !important; }

/* Éléments Streamlit masqués (menu, barre d'outils) */
[data-testid="stToolbar"], #MainMenu { visibility: hidden; }

/* Boutons */
.stButton > button[kind="primary"] {
    background: var(--teal); border: 1px solid var(--teal); color: #FFFFFF;
    border-radius: 6px; font-weight: 600; padding: 0.6rem 1.4rem;
}
.stButton > button[kind="primary"]:hover { background: #066357; border-color: #066357; }
.stButton > button[kind="secondary"] {
    background: #FFFFFF; color: var(--navy); border: 1px solid var(--border); border-radius: 6px;
}
.stButton > button[kind="secondary"]:hover { border-color: var(--teal); color: var(--teal); }

/* Logo */
.mf-logo { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0 1.5rem 0; }
.mf-logo-mark { width: 14px; height: 38px; background: var(--teal); border-radius: 3px; display: inline-block; }
.mf-logo-title { font-family: Georgia, serif; font-size: 1.35rem; font-weight: 600; line-height: 1.1; }
.mf-logo-sub { font-size: 0.72rem; opacity: 0.75; letter-spacing: 0.04em; }

/* Cartes */
.mf-card {
    background: #FFFFFF; border: 1px solid var(--border); border-radius: 10px;
    padding: 1.1rem 1.3rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(16, 29, 50, 0.06);
}
.mf-card-title {
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--grey); font-weight: 600; margin-bottom: 0.5rem;
}
.mf-card-value { font-family: Georgia, serif; font-size: 1.25rem; color: var(--navy); line-height: 1.3; }
.mf-score { font-family: Georgia, serif; font-size: 2rem; color: var(--teal); line-height: 1.1; }
.mf-muted { color: var(--grey); font-size: 0.85rem; }
.mf-source { background: var(--light); border-left: 4px solid var(--teal); border-radius: 6px; padding: 0.8rem 1rem; }
.mf-citation { font-style: italic; color: var(--navy); }

/* Badges */
.mf-badge { display: inline-block; padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
.mf-badge-sugg { background: var(--light); color: var(--navy); border: 1px solid var(--border); }
.mf-badge-todo { background: #FFFFFF; color: var(--grey); border: 1px dashed var(--grey); }

/* Tableau des champs */
.mf-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
.mf-table th { text-align: left; color: var(--grey); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; padding: 0.4rem 0.5rem; border-bottom: 2px solid var(--border); }
.mf-table td { padding: 0.55rem 0.5rem; border-bottom: 1px solid var(--border); vertical-align: top; }
.mf-empty { color: var(--grey); font-style: italic; }

/* Pied de page */
.mf-footer {
    margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border);
    color: var(--grey); font-size: 0.8rem; text-align: center;
}
"""


def appliquer_styles():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)