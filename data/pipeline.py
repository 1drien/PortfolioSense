# ============================================================
#  PortfolioSense — Module data/ (Membre 2)
#  Pipeline : téléchargement → nettoyage → log-rendements
#  Livrable : data/returns_clean.csv
# ============================================================

import yfinance as yf
import pandas as pd
import numpy as np
import sys
import os

# On importe la config depuis le dossier parent
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import TICKERS, START_DATE, END_DATE, PRICES_RAW, RETURNS_CLEAN


# ── Étape 1 : Téléchargement des prix ──────────────────────

def download_prices(tickers, start, end):
    """
    Télécharge les prix de clôture ajustés via yfinance.
    Retourne un DataFrame (DatetimeIndex x tickers).
    """
    print(f"Téléchargement de {len(tickers)} actifs ({start} → {end})...")

    raw = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,   # prix ajustés splits/dividendes
        progress=False,
    )

    # yfinance retourne un MultiIndex si plusieurs tickers
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]]
        prices.columns = tickers

    print(f"  → {prices.shape[0]} jours, {prices.shape[1]} actifs téléchargés")
    return prices


# ── Étape 2 : Nettoyage ────────────────────────────────────

def clean_prices(prices):
    """
    Nettoyage :
      - Supprime les colonnes (actifs) avec trop de NaN (>5%)
      - Aligne les dates : garde seulement les jours où TOUS les actifs cotent
      - Remplit les NaN résiduels par propagation forward (max 1 jour)
    Retourne un DataFrame propre.
    """
    print("\nNettoyage des données...")

    # 1. Supprime les actifs avec plus de 5% de valeurs manquantes
    threshold = 0.05
    missing_ratio = prices.isna().mean()
    bad_tickers = missing_ratio[missing_ratio > threshold].index.tolist()
    if bad_tickers:
        print(f"  ⚠ Actifs supprimés (trop de NaN) : {bad_tickers}")
        prices = prices.drop(columns=bad_tickers)
    else:
        print("  ✓ Aucun actif avec trop de NaN")

    # 2. Propagation forward sur max 1 jour (jours fériés locaux)
    prices = prices.ffill(limit=1)

    # 3. Supprime les lignes (jours) où il reste des NaN
    before = len(prices)
    prices = prices.dropna()
    after = len(prices)
    if before != after:
        print(f"  → {before - after} jours supprimés (NaN résiduels)")

    # 4. Vérification des outliers : returns journaliers > 50% = suspect
    daily_ret = prices.pct_change()
    outliers = (daily_ret.abs() > 0.50).sum()
    if outliers.any():
        print(f"  ⚠ Variations >50% détectées :\n{outliers[outliers > 0]}")
        print("    → Ces valeurs sont conservées (splits probablement corrigés par auto_adjust)")

    print(f"  ✓ Données propres : {prices.shape[0]} jours × {prices.shape[1]} actifs")
    return prices


# ── Étape 3 : Calcul des log-rendements ───────────────────

def compute_log_returns(prices):
    """
    Calcule les log-rendements journaliers : log(P_t / P_{t-1}).
    Supprime la première ligne (NaN après le premier diff).
    Retourne un DataFrame au format standard du projet.
    """
    print("\nCalcul des log-rendements...")

    log_returns = np.log(prices / prices.shift(1)).dropna()

    print(f"  ✓ Log-rendements : {log_returns.shape[0]} jours × {log_returns.shape[1]} actifs")
    return log_returns


# ── Étape 4 : Analyse exploratoire rapide ─────────────────

def quick_analysis(returns):
    """
    Affiche quelques statistiques descriptives pour vérification.
    """
    print("\n── Statistiques descriptives (rendements annualisés) ──")
    ann_mean = returns.mean() * 252
    ann_vol  = returns.std() * np.sqrt(252)
    stats = pd.DataFrame({
        "Rendement annualisé (%)": (ann_mean * 100).round(2),
        "Volatilité annualisée (%)": (ann_vol * 100).round(2),
        "Sharpe approx.": (ann_mean / ann_vol).round(2),
        "Skewness": returns.skew().round(3),
        "Kurtosis": returns.kurtosis().round(3),
    })
    print(stats.to_string())

    print(f"\nPériode : {returns.index[0].date()} → {returns.index[-1].date()}")
    print(f"Corrélation max (hors diag.) : {returns.corr().where(lambda x: x < 1).max().max():.3f}")
    print(f"Corrélation min (hors diag.) : {returns.corr().where(lambda x: x < 1).min().min():.3f}")


# ── Pipeline principal ─────────────────────────────────────

def run_pipeline():
    os.makedirs("data", exist_ok=True)

    # Étape 1 : Téléchargement
    prices = download_prices(TICKERS, START_DATE, END_DATE)
    prices.to_csv(PRICES_RAW)
    print(f"  💾 Prix bruts sauvegardés → {PRICES_RAW}")

    # Étape 2 : Nettoyage
    prices_clean = clean_prices(prices)

    # Étape 3 : Log-rendements
    log_returns = compute_log_returns(prices_clean)

    # Étape 4 : Sauvegarde du livrable
    log_returns.to_csv(RETURNS_CLEAN)
    print(f"\n  ✅ Livrable sauvegardé → {RETURNS_CLEAN}")

    # Étape 5 : Analyse rapide
    quick_analysis(log_returns)

    return log_returns


if __name__ == "__main__":
    returns = run_pipeline()