# dashboard/page2_risk.py
# Mon risque — VaR et stress tests traduits en langage naturel
# Module : risk (Membre 3)

import streamlit as st
import pandas as pd
import sys
sys.path.insert(0, '.')

from optimization.optimizer import get_strategy_from_profile
from risk import (
    compute_historical_var, compute_cornish_fisher_var, compute_cvar,
    compute_max_drawdown, compute_annualized_volatility,
    compute_sharpe_ratio, compute_sortino_ratio,
    run_stress_tests, kupiec_pof_test,
)


@st.cache_data(show_spinner=False)
def load_returns():
    return pd.read_csv("data/returns_clean.csv", index_col=0, parse_dates=True)


def render():
    st.title("🛡️ Mon risque")

    if not st.session_state.get("onboarded"):
        st.warning("👈 Commencez par définir votre profil dans **🏠 Mon profil**")
        return

    profil  = st.session_state["profil"]
    capital = st.session_state["capital"]

    # ── Portefeuille optimisé selon le profil ──
    with st.spinner("Analyse du risque de votre portefeuille..."):
        returns = load_returns()
        result  = get_strategy_from_profile(profil, returns)
        weights = pd.Series(result["weights"])
        portfolio = returns[weights.index] @ weights

        var_h  = compute_historical_var(portfolio)
        cvar   = compute_cvar(portfolio)
        max_dd = compute_max_drawdown(portfolio)
        vol    = compute_annualized_volatility(portfolio)

    # ── La question que tout investisseur se pose ──
    st.subheader("Combien puis-je perdre ?")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Mauvaise journée (cas typique)",
        f"{abs(var_h)*capital:,.0f} €",
        delta=f"{var_h*100:.1f}%",
        delta_color="inverse",
        help="VaR 95% : dans 95% des cas, votre perte quotidienne ne dépassera pas ce montant",
    )
    col2.metric(
        "Très mauvaise journée (pire 5%)",
        f"{abs(cvar)*capital:,.0f} €",
        delta=f"{cvar*100:.1f}%",
        delta_color="inverse",
        help="CVaR : perte moyenne dans les 5% des pires journées",
    )
    col3.metric(
        "Pire crise traversée (2015-2024)",
        f"{abs(max_dd)*capital:,.0f} €",
        delta=f"{max_dd*100:.1f}%",
        delta_color="inverse",
        help="Maximum Drawdown : la pire chute historique depuis un sommet",
    )

    st.caption(
        f"💬 **En clair :** sur une journée normale, votre portefeuille de "
        f"{capital:,} € ne devrait pas perdre plus de "
        f"{abs(var_h)*capital:,.0f} €. Lors de la pire crise de la décennie "
        f"(COVID, mars 2020), il aurait temporairement perdu "
        f"{abs(max_dd)*capital:,.0f} € avant de se redresser."
    )

    # ── Stress tests ──
    st.divider()
    st.subheader("Et si une crise éclatait demain ?")
    st.caption("Nous rejouons les grandes crises historiques sur VOTRE portefeuille.")

    stress = run_stress_tests(portfolio)
    if not stress.empty:
        # Traduire en euros
        stress_display = stress.copy()
        stress_display["Impact sur votre capital"] = [
            f"{float(r.strip('%'))/100 * capital:,.0f} €"
            for r in stress["Rendement Cumulé"]
        ]
        st.dataframe(stress_display, use_container_width=True)

    # ── Validation scientifique ──
    st.divider()
    with st.expander("🔬 Validation scientifique de nos modèles (test de Kupiec)"):
        st.markdown(
            """
            Nous ne nous contentons pas de calculer le risque — nous **vérifions
            que nos modèles sont fiables**. Le test de Kupiec compare le nombre
            de fois où la perte réelle a dépassé notre prédiction avec le
            niveau théorique attendu.
            """
        )
        kupiec = kupiec_pof_test(portfolio, var_h)
        kupiec_df = pd.DataFrame([kupiec]).T.rename(columns={0: "Valeur"})
        st.dataframe(kupiec_df, use_container_width=True)
        if kupiec.get("Modèle Valide (> 5%)"):
            st.success("✅ Notre modèle de risque est statistiquement validé")
        else:
            st.warning("⚠️ Le modèle nécessite une recalibration")
