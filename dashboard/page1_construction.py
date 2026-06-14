# dashboard/page1_construction.py
# Mon portefeuille — allocation optimale selon le profil
# Module : optimization (Adrien)

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
sys.path.insert(0, '.')

from optimization.optimizer import get_strategy_from_profile, weights_to_euros
from optimization.plots import plot_efficient_frontier


@st.cache_data(show_spinner=False)
def load_returns():
    return pd.read_csv("data/returns_clean.csv", index_col=0, parse_dates=True)


@st.cache_data(show_spinner=False)
def optimize(profil: str):
    returns = load_returns()
    return get_strategy_from_profile(profil, returns)


def render():
    st.title("💼 Mon portefeuille")

    if not st.session_state.get("onboarded"):
        st.warning("👈 Commencez par définir votre profil dans **🏠 Mon profil**")
        return

    profil  = st.session_state["profil"]
    capital = st.session_state["capital"]

    strategie_nom = {
        "conservateur": "Minimum Variance — priorité à la stabilité",
        "equilibre":    "Risk Parity — risque équilibré entre tous les actifs",
        "agressif":     "Maximum Sharpe — rendement maximal par unité de risque",
    }

    st.info(f"**Stratégie appliquée :** {strategie_nom[profil]}")

    # ── Optimisation ──
    with st.spinner("Optimisation de votre portefeuille..."):
        returns = load_returns()
        result  = optimize(profil)
        weights = result["weights"]
        metrics = result["metrics"]

    # ── Métriques traduites ──
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Rendement espéré",
        f"{metrics['return']*100:.1f}% / an",
        help="Basé sur les performances historiques 2015-2024",
    )
    gain_espere = capital * metrics['return']
    col2.metric(
        "Soit environ",
        f"+{gain_espere:,.0f} € / an",
        help="Gain annuel espéré sur votre capital",
    )
    col3.metric(
        "Ratio de Sharpe",
        f"{metrics['sharpe']:.2f}",
        help="Rendement par unité de risque — au-dessus de 0.5 c'est bien",
    )

    # ── Allocation en euros ──
    st.divider()
    st.subheader(f"Votre allocation pour {capital:,} €")

    euros = weights_to_euros(weights, capital)
    alloc = pd.DataFrame({
        "Actif":       list(euros.keys()),
        "Montant (€)": list(euros.values()),
        "Poids (%)":   [round(weights[t] * 100, 1) for t in euros.keys()],
    }).sort_values("Montant (€)", ascending=False).reset_index(drop=True)

    col_table, col_pie = st.columns([1, 1], gap="large")

    with col_table:
        st.dataframe(
            alloc,
            use_container_width=True,
            hide_index=True,
            height=400,
        )

    with col_pie:
        fig_pie = px.pie(
            alloc.head(12),  # top 12 pour la lisibilité
            values="Montant (€)",
            names="Actif",
            hole=0.45,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, height=400,
                              margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Frontière efficiente ──
    st.divider()
    st.subheader("Où se situe votre portefeuille ?")
    st.caption(
        "Chaque point est un portefeuille possible. Votre stratégie "
        "(étoile) se situe sur la frontière des meilleurs choix possibles."
    )

    with st.spinner("Génération de la frontière efficiente..."):
        fig = plot_efficient_frontier(returns, n_portfolios=1500)
    st.plotly_chart(fig, use_container_width=True)

    # ── Disclaimer ──
    st.divider()
    st.caption(
        "💡 PortfolioSense recommande — vous décidez. Pour appliquer cette "
        "allocation, passez vos ordres sur votre courtier habituel "
        "(Trade Republic, Boursorama, eToro...)."
    )
