# ============================================================
#  PortfolioSense — Module data/ (Membre 2)
#  Corrélations glissantes — fenêtre de 60 jours
#  Livrable : data/rolling_corr_mean.csv
#             data/rolling_corr_max.csv
#             data/rolling_corr_snapshot.csv
# ============================================================

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import RETURNS_CLEAN, DATA_DIR


def compute_rolling_correlation(returns, window=60):
    """
    Calcule pour chaque jour :
    - la corrélation moyenne entre tous les actifs (sur les window derniers jours)
    - la corrélation maximale (hors diagonale)
    - la corrélation minimale (hors diagonale)

    Ces trois séries permettent de détecter les périodes de crise
    où les corrélations explosent — input direct pour le HMM.
    """
    dates = returns.index[window:]
    corr_mean = []
    corr_max  = []
    corr_min  = []

    print(f"Calcul des corrélations glissantes ({window} jours)...")
    total = len(dates)

    for i, date in enumerate(dates):
        if i % 200 == 0:
            print(f"  {i}/{total} jours traités...")

        window_data = returns.loc[:date].tail(window)
        corr = window_data.corr()

        # Extraire les valeurs hors diagonale
        vals = corr.where(lambda x: x < 1).stack()

        corr_mean.append(vals.mean())
        corr_max.append(vals.max())
        corr_min.append(vals.min())

    result = pd.DataFrame({
        "corr_moyenne": corr_mean,
        "corr_max":     corr_max,
        "corr_min":     corr_min,
    }, index=dates)

    return result


def compute_pairwise_rolling(returns, window=60, top_pairs=10):
    """
    Calcule la corrélation glissante pour les paires d'actifs
    les plus corrélées en moyenne — utile pour le dashboard.
    """
    # Trouver les paires les plus corrélées
    corr_global = returns.corr()
    pairs = []
    tickers = returns.columns.tolist()

    for i in range(len(tickers)):
        for j in range(i+1, len(tickers)):
            t1, t2 = tickers[i], tickers[j]
            pairs.append((t1, t2, corr_global.loc[t1, t2]))

    pairs.sort(key=lambda x: -abs(x[2]))
    top = pairs[:top_pairs]

    print(f"\nTop {top_pairs} paires les plus corrélées :")
    result = {}
    for t1, t2, corr_val in top:
        print(f"  {t1}/{t2} : {corr_val:.3f}")
        rc = returns[t1].rolling(window).corr(returns[t2]).dropna()
        result[f"{t1}_{t2}"] = rc

    return pd.DataFrame(result)


def regime_from_correlation(rolling_corr, threshold_bear=0.65, threshold_bull=0.40):
    """
    Détection naïve de régime basée sur la corrélation moyenne :
    - corr > threshold_bear  → Bear (corrélations élevées = crise)
    - corr < threshold_bull  → Bull (corrélations faibles = marché calme)
    - entre les deux         → Lateral

    Sert de BASELINE pour comparer avec le HMM de Membre 4.
    """
    regimes = []
    for val in rolling_corr["corr_moyenne"]:
        if val > threshold_bear:
            regimes.append("bear")
        elif val < threshold_bull:
            regimes.append("bull")
        else:
            regimes.append("lateral")

    rolling_corr = rolling_corr.copy()
    rolling_corr["regime_naif"] = regimes
    return rolling_corr


def run_rolling_correlation_pipeline():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Charge les données
    print("Chargement de returns_clean.csv...")
    returns = pd.read_csv(RETURNS_CLEAN, index_col=0, parse_dates=True)
    print(f"  {returns.shape[0]} jours x {returns.shape[1]} actifs")

    # ── 1. Corrélations glissantes globales ────────────────
    rolling = compute_rolling_correlation(returns, window=60)

    # Ajoute la détection naïve de régime
    rolling = regime_from_correlation(rolling)

    rolling.to_csv(os.path.join(DATA_DIR, "rolling_corr_mean.csv"))
    print(f"\n  Sauvegarde -> {DATA_DIR}rolling_corr_mean.csv")

    # ── 2. Stats par période ───────────────────────────────
    print("\n── Corrélation moyenne par période ──")
    periodes = {
        "Pre-COVID (2015-2019)":  ("2015-01-01", "2019-12-31"),
        "COVID (mars 2020)":      ("2020-02-01", "2020-04-30"),
        "Post-COVID (2021)":      ("2021-01-01", "2021-12-31"),
        "Taux 2022":              ("2022-01-01", "2022-12-31"),
        "Remontee (2023-2024)":   ("2023-01-01", "2024-12-31"),
    }

    for label, (start, end) in periodes.items():
        subset = rolling["corr_moyenne"][start:end]
        if len(subset) > 0:
            print(f"  {label:30s} : {subset.mean():.3f} (max: {subset.max():.3f})")

    # ── 3. Distribution des régimes ────────────────────────
    print("\n── Distribution des régimes naifs ──")
    dist = rolling["regime_naif"].value_counts(normalize=True) * 100
    for regime, pct in dist.items():
        print(f"  {regime:10s} : {pct:.1f}%")

    # ── 4. Paires les plus corrélées ──────────────────────
    pairwise = compute_pairwise_rolling(returns, window=60, top_pairs=10)
    pairwise.to_csv(os.path.join(DATA_DIR, "rolling_corr_pairs.csv"))
    print(f"\n  Sauvegarde -> {DATA_DIR}rolling_corr_pairs.csv")

    print(f"\nCorrelations glissantes terminees")
    print(f"  rolling_corr_mean.csv  : correlation moyenne + regime naif")
    print(f"  rolling_corr_pairs.csv : top 10 paires les plus correlees")

    return rolling, pairwise


if __name__ == "__main__":
    rolling, pairs = run_rolling_correlation_pipeline()