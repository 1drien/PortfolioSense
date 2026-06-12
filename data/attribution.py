# ============================================================
#  PortfolioSense — Module data/ (Membre 2)
#  Performance Attribution : contribution de chaque actif
#  Période complète : 2015-2024
# ============================================================

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import RETURNS_CLEAN, DATA_DIR, TICKERS


# ── Fonctions principales ──────────────────────────────────

def equal_weight_portfolio(n_assets):
    """Portefeuille équipondéré — même poids pour chaque actif."""
    return np.ones(n_assets) / n_assets


def compute_portfolio_returns(returns, weights):
    """
    Calcule les rendements journaliers du portefeuille.
    r_portfolio(t) = sum(w_i * r_i(t))
    """
    return returns.dot(weights)


def compute_contribution(returns, weights):
    """
    Contribution de chaque actif au rendement du portefeuille.
    Contribution_i = w_i * rendement_cumulé_i
    """
    ann_factor = 252
    cumulative_returns = (np.exp(returns.sum()) - 1) * 100
    ann_returns        = returns.mean() * ann_factor * 100
    ann_vol            = returns.std() * np.sqrt(ann_factor) * 100

    contribution_cumul = weights * cumulative_returns
    contribution_ann   = weights * ann_returns

    df = pd.DataFrame({
        "Poids (%)"                    : (weights * 100).round(2),
        "Rendement cumulé actif (%)"   : cumulative_returns.round(2),
        "Rendement annualisé actif (%)": ann_returns.round(2),
        "Volatilité annualisée (%)"    : ann_vol.round(2),
        "Contribution cumulée (%)"     : contribution_cumul.round(3),
        "Contribution annualisée (%)"  : contribution_ann.round(3),
    }, index=returns.columns)

    return df.sort_values("Contribution cumulée (%)", ascending=False)


def sector_attribution(contribution_df):
    """
    Regroupe les contributions par secteur.
    """
    secteurs = {
        "Technologie"              : ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMD", "INTC", "CRM"],
        "Finance"                  : ["JPM", "BAC", "GS", "BLK", "MS", "AXP"],
        "Santé"                    : ["JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY"],
        "Conso. discrétionnaire"   : ["AMZN", "TSLA", "HD", "NKE"],
        "Conso. de base"           : ["PG", "KO", "WMT"],
        "Énergie"                  : ["XOM", "CVX"],
        "Industrie"                : ["CAT", "BA", "HON", "UPS"],
        "Immobilier"               : ["PLD"],
        "Collectivités"            : ["NEE"],
    }

    sector_results = []
    for secteur, tickers in secteurs.items():
        tickers_present = [t for t in tickers if t in contribution_df.index]
        if tickers_present:
            subset = contribution_df.loc[tickers_present]
            sector_results.append({
                "Secteur"                      : secteur,
                "Nb actifs"                    : len(tickers_present),
                "Poids total (%)"              : subset["Poids (%)"].sum().round(2),
                "Contribution cumulée (%)"     : subset["Contribution cumulée (%)"].sum().round(3),
                "Contribution annualisée (%)"  : subset["Contribution annualisée (%)"].sum().round(3),
                "Rdt moyen actifs (%)"         : subset["Rendement annualisé actif (%)"].mean().round(2),
            })

    return pd.DataFrame(sector_results).set_index("Secteur").sort_values(
        "Contribution cumulée (%)", ascending=False
    )


def best_worst_contributors(contribution_df, n=5):
    """Top 5 et bottom 5 contributeurs."""
    top    = contribution_df.head(n)
    bottom = contribution_df.tail(n)
    return top, bottom


def portfolio_summary(port_returns, contribution_df):
    """Résumé global du portefeuille équipondéré."""
    ann_factor = 252
    cumul  = (np.exp(port_returns.sum()) - 1) * 100
    ann    = port_returns.mean() * ann_factor * 100
    vol    = port_returns.std() * np.sqrt(ann_factor) * 100
    sharpe = ann / vol

    print(f"\n  Rendement cumulé   : {cumul:.2f}%")
    print(f"  Rendement annualisé : {ann:.2f}%")
    print(f"  Volatilité          : {vol:.2f}%")
    print(f"  Sharpe              : {sharpe:.2f}")
    print(f"  Nb actifs positifs  : {(contribution_df['Rendement annualisé actif (%)'] > 0).sum()} / {len(contribution_df)}")


# ── Pipeline principal ─────────────────────────────────────

def run_attribution_pipeline():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Charge le returns_clean.csv
    print("Chargement de returns_clean.csv...")
    returns = pd.read_csv(RETURNS_CLEAN, index_col=0, parse_dates=True)
    print(f"  → {returns.shape[0]} jours × {returns.shape[1]} actifs")

    # Poids équipondérés
    n = returns.shape[1]
    weights = equal_weight_portfolio(n)

    # ── 1. Rendements du portefeuille ──────────────────────
    print("\n" + "="*60)
    print("  PORTEFEUILLE ÉQUIPONDÉRÉ — Résumé global")
    print("="*60)

    port_returns = compute_portfolio_returns(returns, weights)
    contribution_df = compute_contribution(returns, weights)
    portfolio_summary(port_returns, contribution_df)

    # ── 2. Contribution par actif ──────────────────────────
    print("\n" + "="*60)
    print("  CONTRIBUTION PAR ACTIF (classé par contribution)")
    print("="*60)
    print(contribution_df.to_string())

    contribution_df.to_csv(DATA_DIR + "attribution_actifs.csv")
    print(f"\n  Sauvegardé → {DATA_DIR}attribution_actifs.csv")

    # ── 3. Top 5 / Bottom 5 ────────────────────────────────
    print("\n" + "="*60)
    print("  TOP 5 CONTRIBUTEURS")
    print("="*60)
    top, bottom = best_worst_contributors(contribution_df)
    print(top[["Poids (%)", "Rendement annualisé actif (%)", "Contribution annualisée (%)"]].to_string())

    print("\n" + "="*60)
    print("  BOTTOM 5 CONTRIBUTEURS")
    print("="*60)
    print(bottom[["Poids (%)", "Rendement annualisé actif (%)", "Contribution annualisée (%)"]].to_string())

    # ── 4. Attribution par secteur ─────────────────────────
    print("\n" + "="*60)
    print("  ATTRIBUTION PAR SECTEUR")
    print("="*60)

    sector_df = sector_attribution(contribution_df)
    print(sector_df.to_string())

    sector_df.to_csv(DATA_DIR + "attribution_secteurs.csv")
    print(f"\n  Sauvegardé → {DATA_DIR}attribution_secteurs.csv")

    # ── 5. Analyse temporelle ──────────────────────────────
    print("\n" + "="*60)
    print("  CONTRIBUTION PAR PÉRIODE")
    print("="*60)

    periodes = {
        "Pre-COVID (2015-2019)" : ("2015-01-01", "2019-12-31"),
        "COVID (2020)"          : ("2020-01-01", "2020-12-31"),
        "Post-COVID (2021-2022)": ("2021-01-01", "2022-12-31"),
        "Remontee (2023-2024)"  : ("2023-01-01", "2024-12-31"),
    }

    period_results = {}
    for label, (start, end) in periodes.items():
        ret_period = returns[start:end]
        w = equal_weight_portfolio(ret_period.shape[1])
        port_ret_period = compute_portfolio_returns(ret_period, w)
        cumul = (np.exp(port_ret_period.sum()) - 1) * 100
        ann   = port_ret_period.mean() * 252 * 100
        vol   = port_ret_period.std() * np.sqrt(252) * 100
        period_results[label] = {
            "Rendement cumulé (%)": round(cumul, 2),
            "Rendement annualisé (%)": round(ann, 2),
            "Volatilité (%)": round(vol, 2),
            "Sharpe": round(ann / vol, 2),
        }

    period_df = pd.DataFrame(period_results).T
    print(period_df.to_string())

    period_df.to_csv(DATA_DIR + "attribution_periodes.csv")
    print(f"\n  Sauvegardé → {DATA_DIR}attribution_periodes.csv")

    print(f"\n Performance attribution terminée — fichiers dans {DATA_DIR}")
    print("   attribution_actifs.csv | attribution_secteurs.csv | attribution_periodes.csv")

    return contribution_df, sector_df, period_df


if __name__ == "__main__":
    contribution, secteurs, periodes = run_attribution_pipeline()