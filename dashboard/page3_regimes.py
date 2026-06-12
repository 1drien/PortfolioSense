# dashboard/page3_regimes.py
# Météo des marchés — détection de régime HMM
# Module : ml (Membre 4)
# NOTE : version de base portable — Membre 4 peut la remplacer par son code
#        une fois ses chemins hardcodés corrigés.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
sys.path.insert(0, '.')

from optimization.optimizer import get_strategy_from_profile


@st.cache_data(show_spinner=False)
def load_returns():
    return pd.read_csv("data/returns_clean.csv", index_col=0, parse_dates=True)


@st.cache_resource(show_spinner=False)
def train_hmm_cached():
    """HMM 3 états sur le marché (moyenne des actifs comme proxy)."""
    from hmmlearn.hmm import GaussianHMM
    from sklearn.preprocessing import StandardScaler

    returns = load_returns()
    market  = returns.mean(axis=1)

    feats = pd.DataFrame(index=market.index)
    feats["ret"]     = market
    feats["vol_20d"] = market.rolling(20).std()
    feats["ret_5d"]  = market.rolling(5).sum()
    feats = feats.dropna()

    X = StandardScaler().fit_transform(feats.values)

    best_model, best_score = None, -np.inf
    for seed in range(5):
        m = GaussianHMM(n_components=3, covariance_type="full",
                        n_iter=200, random_state=seed)
        m.fit(X)
        if m.score(X) > best_score:
            best_score, best_model = m.score(X), m

    states = best_model.predict(X)

    # Nommer les régimes selon le rendement moyen par état
    state_ret = {s: market.loc[feats.index][states == s].mean() for s in range(3)}
    ordered   = sorted(state_ret, key=state_ret.get)
    labels    = {ordered[0]: "Bear 🔴", ordered[1]: "Latéral 🟡", ordered[2]: "Bull 🟢"}

    regimes = pd.Series([labels[s] for s in states], index=feats.index)
    return regimes, market.loc[feats.index]


REGIME_INFO = {
    "Bull 🟢": {
        "titre": "Marché haussier",
        "explication": (
            "Les marchés sont confiants : rendements positifs et volatilité "
            "faible. C'est le moment de viser la performance."
        ),
        "strategie": "Maximum Sharpe",
        "profil_strategie": "agressif",
    },
    "Bear 🔴": {
        "titre": "Marché en crise",
        "explication": (
            "Turbulences détectées : les actifs chutent et se corrèlent "
            "entre eux. La diversification classique ne protège plus — "
            "il faut se replier sur les actifs défensifs."
        ),
        "strategie": "Minimum Variance",
        "profil_strategie": "conservateur",
    },
    "Latéral 🟡": {
        "titre": "Marché indécis",
        "explication": (
            "Le marché hésite, sans tendance claire. La meilleure défense "
            "est un risque parfaitement équilibré entre tous les actifs."
        ),
        "strategie": "Risk Parity",
        "profil_strategie": "equilibre",
    },
}


def render():
    st.title("🧠 Météo des marchés")
    st.caption(
        "Notre intelligence artificielle (Hidden Markov Model) analyse les "
        "marchés en continu et détecte automatiquement leur régime."
    )

    with st.spinner("Analyse des régimes de marché..."):
        regimes, market = train_hmm_cached()

    regime_actuel = regimes.iloc[-1]
    info = REGIME_INFO[regime_actuel]

    # ── Le régime actuel ──
    st.divider()
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"# {regime_actuel.split()[-1]}")
        st.markdown(f"### {info['titre']}")

    with col2:
        st.markdown(f"**Situation :** {info['explication']}")
        st.markdown(f"**Stratégie recommandée :** {info['strategie']}")

        if st.session_state.get("onboarded"):
            profil_user = st.session_state["profil"]
            if profil_user != info["profil_strategie"]:
                st.warning(
                    f"⚠️ **Alerte :** votre profil ({profil_user}) suggère une "
                    f"autre stratégie que celle adaptée au marché actuel. "
                    f"En période {info['titre'].lower()}, nous recommandons "
                    f"de basculer temporairement vers **{info['strategie']}**."
                )
            else:
                st.success(
                    "✅ Votre stratégie actuelle est alignée avec le régime "
                    "de marché détecté."
                )

    # ── Historique des régimes ──
    st.divider()
    st.subheader("L'historique vu par notre IA")
    st.caption(
        "Validation : notre modèle a-t-il bien détecté les crises connues ? "
        "COVID (mars 2020) et la crise des taux (2022) doivent apparaître en rouge."
    )

    cumulative = (1 + market).cumprod()
    color_map = {"Bull 🟢": "#1D9E75", "Bear 🔴": "#D85A30", "Latéral 🟡": "#BA7517"}

    fig = go.Figure()
    for regime, color in color_map.items():
        mask = regimes == regime
        fig.add_trace(go.Scatter(
            x=cumulative.index[mask],
            y=cumulative[mask],
            mode="markers",
            marker=dict(size=3, color=color),
            name=regime,
        ))
    fig.update_layout(
        height=420,
        yaxis_title="Valeur du marché (base 1)",
        template="plotly_white",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Répartition du temps par régime ──
    st.divider()
    counts = regimes.value_counts()
    cols = st.columns(3)
    for i, (regime, n) in enumerate(counts.items()):
        cols[i].metric(regime, f"{n/len(regimes)*100:.0f}% du temps",
                       f"{n} jours")
