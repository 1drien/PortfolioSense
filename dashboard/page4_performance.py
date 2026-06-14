# dashboard/page4_performance.py
# Performance prouvée — backtest walk-forward
# Modules : optimization/backtest.py (Adrien) + data (Membre 2)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys
sys.path.insert(0, '.')


@st.cache_data(show_spinner=False)
def load_returns():
    return pd.read_csv("data/returns_clean.csv", index_col=0, parse_dates=True)


@st.cache_data(show_spinner=False)
def load_or_run_backtest():
    """Charge les résultats du backtest s'ils existent, sinon les calcule."""
    path = "data/backtest_results.csv"
    if os.path.exists(path):
        return pd.read_csv(path, index_col=0)

    from optimization.backtest import compare_backtests
    returns = load_returns()
    df = compare_backtests(returns)
    df.to_csv(path)
    return df


@st.cache_data(show_spinner=False)
def equity_curves():
    """Calcule les courbes d'équité walk-forward de chaque stratégie."""
    from optimization.backtest import walk_forward_backtest
    from optimization.optimizer import max_sharpe, min_variance, risk_parity

    returns = load_returns()
    curves = {}

    strategies = {
        "Max Sharpe (agressif)":     max_sharpe,
        "Min Variance (conservateur)": min_variance,
        "Risk Parity (équilibré)":   risk_parity,
    }
    for name, fn in strategies.items():
        port_ret = walk_forward_backtest(returns, fn)
        curves[name] = (1 + port_ret).cumprod()

    # Benchmark equal-weight
    def eq_fn(train):
        n = len(train.columns)
        return {"strategy": "eq", "weights": {t: 1/n for t in train.columns}}
    port_eq = walk_forward_backtest(returns, eq_fn)
    curves["Equal-Weight (benchmark)"] = (1 + port_eq).cumprod()

    return curves


def render():
    st.title("📈 Performance prouvée")
    st.caption(
        "Pas de promesses en l'air : nous testons nos stratégies comme un "
        "vrai investisseur les aurait vécues — sans jamais connaître l'avenir."
    )

    with st.expander("🔬 Comment ça marche ? (méthodologie walk-forward)"):
        st.markdown(
            """
            À chaque période de 6 mois, nous optimisons le portefeuille en
            utilisant **uniquement les 2 années précédentes** — exactement
            comme un investisseur réel qui ne connaît pas le futur.

            Cette méthode (*walk-forward backtesting*) élimine le biais de
            lucidité rétrospective qui rend la plupart des backtests trop
            optimistes.
            """
        )

    # ── Tableau comparatif ──
    st.divider()
    st.subheader("Les chiffres sur 7,5 ans de test (2017-2024)")

    with st.spinner("Chargement des résultats du backtest..."):
        results = load_or_run_backtest()

    capital = st.session_state.get("capital", 10_000)

    display = pd.DataFrame({
        "Rendement annuel":  (results["return_ann"] * 100).round(1).astype(str) + " %",
        "Sharpe":            results["sharpe"].round(2),
        "Pire chute":        (results["max_drawdown"] * 100).round(1).astype(str) + " %",
        f"{capital:,} € seraient devenus": (
            (1 + results["cum_return"]) * capital
        ).round(0).astype(int).astype(str) + " €",
    })
    display.index = display.index.str.replace("_", " ").str.title()
    st.dataframe(display, use_container_width=True)

    st.caption(
        "💬 **Honnêteté scientifique :** la stratégie naïve equal-weight est "
        "réputée difficile à battre en ratio de Sharpe (DeMiguel et al., 2009). "
        "Notre valeur ajoutée n'est pas de la battre systématiquement, mais "
        "d'adapter la stratégie à VOTRE profil et au régime de marché : "
        "Max Sharpe maximise le gain absolu, Min Variance minimise les chutes."
    )

    # ── Courbes d'équité ──
    st.divider()
    st.subheader(f"Évolution de {capital:,} € investis en 2017")

    with st.spinner("Calcul des courbes d'évolution (peut prendre 1 minute)..."):
        curves = equity_curves()

    fig = go.Figure()
    colors = {
        "Max Sharpe (agressif)":       "#D85A30",
        "Min Variance (conservateur)": "#185FA5",
        "Risk Parity (équilibré)":     "#1D9E75",
        "Equal-Weight (benchmark)":    "#888780",
    }
    for name, curve in curves.items():
        fig.add_trace(go.Scatter(
            x=curve.index,
            y=curve * capital,
            name=name,
            line=dict(
                color=colors.get(name, "#333"),
                width=2,
                dash="dot" if "benchmark" in name else "solid",
            ),
        ))
    fig.update_layout(
        height=480,
        yaxis_title="Valeur du portefeuille (€)",
        template="plotly_white",
        legend=dict(orientation="h", y=1.12),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "📌 Zones de chute visibles : COVID (mars 2020) et crise des "
        "taux (2022). Observez comment Min Variance amortit mieux les crises."
    )
