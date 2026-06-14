# main.py — PortfolioSense
# Point d'entrée Streamlit
# Lancer avec : streamlit run main.py

import streamlit as st

st.set_page_config(
    page_title="PortfolioSense",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── État de session (profil utilisateur persistant) ────────────
if "onboarded" not in st.session_state:
    st.session_state["onboarded"] = False
    st.session_state["capital"]   = 10_000
    st.session_state["horizon"]   = 5
    st.session_state["perte_max"] = 15
    st.session_state["profil"]    = "equilibre"

# ─── Sidebar ──────────────────────────────────────────────────────
st.sidebar.title("📊 PortfolioSense")
st.sidebar.caption("Votre copilote d'investissement quantitatif")
st.sidebar.divider()

# Afficher le profil actuel si onboardé
if st.session_state["onboarded"]:
    profil_display = {
        "conservateur": "🟢 Conservateur",
        "equilibre":    "🟡 Équilibré",
        "agressif":     "🔴 Agressif",
    }
    st.sidebar.success(
        f"**Profil :** {profil_display[st.session_state['profil']]}\n\n"
        f"**Capital :** {st.session_state['capital']:,} €"
    )
    st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Mon profil",
        "💼 Mon portefeuille",
        "🛡️ Mon risque",
        "🧠 Météo des marchés",
        "📈 Performance prouvée",
    ],
)

st.sidebar.divider()
st.sidebar.caption("PFE Finance Quantitative · 2026")
st.sidebar.caption("⚠️ Outil d'aide à la décision — n'exécute aucun ordre")

# ─── Routing ──────────────────────────────────────────────────────
if page == "🏠 Mon profil":
    from dashboard.page0_accueil import render
elif page == "💼 Mon portefeuille":
    from dashboard.page1_construction import render
elif page == "🛡️ Mon risque":
    from dashboard.page2_risk import render
elif page == "🧠 Météo des marchés":
    from dashboard.page3_regimes import render
elif page == "📈 Performance prouvée":
    from dashboard.page4_performance import render

render()
