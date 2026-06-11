# ============================================================
#  PortfolioSense — Module data/ (Membre 2)
#  Stress Tests : GFC 2008, COVID 2020, Crise des taux 2022
# ============================================================

import yfinance as yf
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import RETURNS_CLEAN, DATA_DIR

# ── Paramètres des périodes de crise ───────────────────────

CRISES = {
    "GFC_2008": {
        "label"      : "Grande Crise Financière (GFC 2008)",
        "start"      : "2008-01-01",
        "end"        : "2009-06-30",
        "description": "Crise des subprimes — effondrement de Lehman Brothers (sept. 2008)",
    },
    "COVID_2020": {
        "label"      : "Crise COVID-19 (2020)",
        "start"      : "2020-02-01",
        "end"        : "2020-04-30",
        "description": "Krach eclair — S&P 500 -34% en 33 jours (pic : 19 fev. 2020)",
    },
    "RATES_2022": {
        "label"      : "Crise des taux (2022)",
        "start"      : "2022-01-01",
        "end"        : "2022-12-31",
        "description": "Hausse brutale des taux Fed — S&P 500 -19%, NASDAQ -33%",
    },
}

# Actifs existants en 2008 (cotes avant 2008)
TICKERS_GFC = [
    "AAPL", "MSFT", "GOOGL", "INTC",          # Tech
    "JPM",  "BAC",  "GS",    "MS",   "AXP",   # Finance
    "JNJ",  "PFE",  "MRK",                    # Santé (ABBV spinoff 2013 -> exclu)
    "HD",   "NKE",                             # Conso. discrétionnaire
    "PG",   "KO",   "WMT",                    # Conso. de base
    "XOM",  "CVX",                            # Énergie
    "CAT",  "HON",  "UPS",   "BA",            # Industrie
    "NEE",                                    # Collectivités
]
# Note : ABBV (spinoff d'Abbott en 2013), META (IPO 2012), TSLA (IPO 2010),
#        AMZN (ok mais données partielles), NVDA (ok), AMD (ok),
#        CRM (IPO 2004 ok), BLK (IPO 1999 ok), LLY (ok), PLD (ok)
# On garde uniquement les actifs avec données complètes sur 2008-2009


# ── Fonctions utilitaires ──────────────────────────────────

def compute_log_returns(prices):
    return np.log(prices / prices.shift(1)).dropna()


def stress_stats(returns, label):
    """
    Calcule les statistiques clés sur une période de crise.
    """
    ann_factor = 252
    stats = pd.DataFrame({
        "Rendement cumulé (%)": ((np.exp(returns.sum()) - 1) * 100).round(2),
        "Rendement annualisé (%)": (returns.mean() * ann_factor * 100).round(2),
        "Volatilité annualisée (%)": (returns.std() * np.sqrt(ann_factor) * 100).round(2),
        "Sharpe": (returns.mean() / returns.std() * np.sqrt(ann_factor)).round(2),
        "Pire jour (%)": (returns.min() * 100).round(2),
        "Meilleur jour (%)": (returns.max() * 100).round(2),
        "Skewness": returns.skew().round(3),
        "Kurtosis": returns.kurtosis().round(3),
    })
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(stats.to_string())
    return stats


def max_drawdown(prices):
    """
    Calcule le drawdown maximum pour chaque actif.
    Drawdown = perte maximale depuis un pic historique.
    """
    rolling_max = prices.cummax()
    drawdown = (prices - rolling_max) / rolling_max
    return drawdown.min()


def correlation_analysis(returns, label):
    """
    Analyse de la structure de corrélation en période de crise.
    """
    corr = returns.corr()
    avg_corr = corr.where(lambda x: x < 1).stack().mean()
    max_corr  = corr.where(lambda x: x < 1).stack().max()
    min_corr  = corr.where(lambda x: x < 1).stack().min()
    print(f"\n  Corrélations ({label}) :")
    print(f"    Moyenne : {avg_corr:.3f}")
    print(f"    Max     : {max_corr:.3f}")
    print(f"    Min     : {min_corr:.3f}")
    print(f"  → {'⚠ Corrélations élevées : diversification réduite en crise' if avg_corr > 0.5 else '✓ Diversification maintenue'}")


# ── Étape 1 : GFC 2008 (téléchargement séparé) ─────────────

def run_gfc_stress():
    print("\n" + "="*60)
    print("  STRESS TEST — GFC 2008")
    print("  Sous-portefeuille : actifs cotés avant 2008")
    print("="*60)

    crisis = CRISES["GFC_2008"]
    print(f"\nTéléchargement de {len(TICKERS_GFC)} actifs ({crisis['start']} → {crisis['end']})...")

    raw = yf.download(
        TICKERS_GFC,
        start="2007-01-01",  # On prend un peu avant pour voir le pic
        end=crisis["end"],
        auto_adjust=True,
        progress=False,
    )
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]]

    # Nettoyage
    prices = prices.ffill(limit=1).dropna()
    print(f"  → {prices.shape[0]} jours, {prices.shape[1]} actifs")

    # Log-rendements sur la fenêtre de crise uniquement
    log_ret_full = compute_log_returns(prices)
    log_ret_crisis = log_ret_full[crisis["start"]:crisis["end"]]

    # Stats
    stats = stress_stats(log_ret_crisis, crisis["label"])

    # Drawdown
    prices_crisis = prices[crisis["start"]:crisis["end"]]
    dd = max_drawdown(prices_crisis)
    print(f"\n  Drawdowns maximaux (pires actifs) :")
    print(dd.sort_values().head(10).apply(lambda x: f"{x*100:.2f}%").to_string())

    # Corrélations
    correlation_analysis(log_ret_crisis, crisis["label"])

    # Sauvegarde
    os.makedirs(DATA_DIR, exist_ok=True)
    stats.to_csv(DATA_DIR + "stress_gfc2008.csv")
    dd.to_frame("max_drawdown").to_csv(DATA_DIR + "drawdown_gfc2008.csv")
    print(f"\n  Sauvegardé → {DATA_DIR}stress_gfc2008.csv")

    return stats, dd


# ── Étape 2 : COVID 2020 ───────────────────────────────────

def run_covid_stress(returns_full, prices_full):
    crisis = CRISES["COVID_2020"]
    print(f"\n\n{'='*60}")
    print(f"  STRESS TEST — COVID 2020")
    print(f"{'='*60}")

    log_ret_crisis = returns_full[crisis["start"]:crisis["end"]]
    prices_crisis  = prices_full[crisis["start"]:crisis["end"]]

    print(f"  Période : {log_ret_crisis.index[0].date()} → {log_ret_crisis.index[-1].date()}")
    print(f"  Nombre de jours : {len(log_ret_crisis)}")

    stats = stress_stats(log_ret_crisis, crisis["label"])
    dd    = max_drawdown(prices_crisis)

    print(f"\n  Drawdowns maximaux (pires actifs) :")
    print(dd.sort_values().head(10).apply(lambda x: f"{x*100:.2f}%").to_string())

    correlation_analysis(log_ret_crisis, crisis["label"])

    stats.to_csv(DATA_DIR + "stress_covid2020.csv")
    dd.to_frame("max_drawdown").to_csv(DATA_DIR + "drawdown_covid2020.csv")
    print(f"\n  Sauvegardé → {DATA_DIR}stress_covid2020.csv")

    return stats, dd


# ── Étape 3 : Crise des taux 2022 ─────────────────────────

def run_rates_stress(returns_full, prices_full):
    crisis = CRISES["RATES_2022"]
    print(f"\n\n{'='*60}")
    print(f"  STRESS TEST — CRISE DES TAUX 2022")
    print(f"{'='*60}")

    log_ret_crisis = returns_full[crisis["start"]:crisis["end"]]
    prices_crisis  = prices_full[crisis["start"]:crisis["end"]]

    print(f"  Période : {log_ret_crisis.index[0].date()} → {log_ret_crisis.index[-1].date()}")
    print(f"  Nombre de jours : {len(log_ret_crisis)}")

    stats = stress_stats(log_ret_crisis, crisis["label"])
    dd    = max_drawdown(prices_crisis)

    print(f"\n  Drawdowns maximaux (pires actifs) :")
    print(dd.sort_values().head(10).apply(lambda x: f"{x*100:.2f}%").to_string())

    correlation_analysis(log_ret_crisis, crisis["label"])

    stats.to_csv(DATA_DIR + "stress_rates2022.csv")
    dd.to_frame("max_drawdown").to_csv(DATA_DIR + "drawdown_rates2022.csv")
    print(f"\n  Sauvegardé → {DATA_DIR}stress_rates2022.csv")

    return stats, dd


# ── Étape 4 : Comparaison des crises ──────────────────────

def compare_crises(stats_covid, stats_rates):
    """
    Compare les deux crises sur les actifs communs.
    """
    print(f"\n\n{'='*60}")
    print(f"  COMPARAISON : COVID vs CRISE DES TAUX")
    print(f"{'='*60}")

    compare = pd.DataFrame({
        "Rdt cumulé COVID (%)": stats_covid["Rendement cumulé (%)"],
        "Rdt cumulé 2022 (%)": stats_rates["Rendement cumulé (%)"],
        "Vol COVID (%)": stats_covid["Volatilité annualisée (%)"],
        "Vol 2022 (%)": stats_rates["Volatilité annualisée (%)"],
    })
    print(compare.to_string())

    compare.to_csv(DATA_DIR + "stress_comparaison.csv")
    print(f"\n  Sauvegardé → {DATA_DIR}stress_comparaison.csv")


# ── Pipeline principal ─────────────────────────────────────

def run_stress_pipeline():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Charge le returns_clean.csv déjà généré
    print("Chargement de returns_clean.csv...")
    returns_full = pd.read_csv(RETURNS_CLEAN, index_col=0, parse_dates=True)
    print(f"  → {returns_full.shape[0]} jours × {returns_full.shape[1]} actifs chargés")

    # Reconstitue les prix à partir des log-rendements
    # (prix relatifs, base 100 au premier jour)
    prices_full = np.exp(returns_full.cumsum()) * 100

    # Stress tests
    stats_gfc,   dd_gfc   = run_gfc_stress()
    stats_covid, dd_covid = run_covid_stress(returns_full, prices_full)
    stats_rates, dd_rates = run_rates_stress(returns_full, prices_full)

    # Comparaison
    compare_crises(stats_covid, stats_rates)

    print(f"\n\n Stress tests terminés — fichiers sauvegardés dans {DATA_DIR}")
    print("   stress_gfc2008.csv | stress_covid2020.csv | stress_rates2022.csv")
    print("   drawdown_gfc2008.csv | drawdown_covid2020.csv | drawdown_rates2022.csv")
    print("   stress_comparaison.csv")


if __name__ == "__main__":
    run_stress_pipeline()