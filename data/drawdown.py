# ============================================================
#  PortfolioSense — Module data/ (Membre 2)
#  Drawdown Historique : perte maximale depuis un pic
#  Période complète : 2015-2024
# ============================================================

import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config import RETURNS_CLEAN, DATA_DIR


# ── Fonctions principales ──────────────────────────────────

def compute_drawdown_series(prices):
    """
    Calcule la série de drawdown pour chaque actif.
    Drawdown(t) = (Prix(t) - Max(Prix jusqu'à t)) / Max(Prix jusqu'à t)
    Valeurs entre -1 (perte totale) et 0 (au pic).
    """
    rolling_max = prices.cummax()
    drawdown = (prices - rolling_max) / rolling_max
    return drawdown


def compute_max_drawdown_details(prices):
    """
    Pour chaque actif, calcule :
    - Max drawdown (%)
    - Date du pic (avant la chute)
    - Date du creux (point le plus bas)
    - Durée de la chute (jours)
    - Date de récupération (retour au niveau du pic)
    - Durée totale de récupération (jours)
    """
    results = []

    for ticker in prices.columns:
        serie = prices[ticker].dropna()
        rolling_max = serie.cummax()
        drawdown = (serie - rolling_max) / rolling_max

        # Max drawdown et date du creux
        max_dd = drawdown.min()
        date_creux = drawdown.idxmin()

        # Date du pic (dernier max avant le creux)
        date_pic = serie[:date_creux].idxmax()

        # Durée de la chute (pic → creux)
        duree_chute = (date_creux - date_pic).days

        # Date de récupération (premier jour où on repasse le niveau du pic)
        niveau_pic = serie[date_pic]
        apres_creux = serie[date_creux:]
        recuperation = apres_creux[apres_creux >= niveau_pic]

        if len(recuperation) > 0:
            date_recup = recuperation.index[0]
            duree_recup = (date_recup - date_creux).days
            statut = "Recupere"
        else:
            date_recup = None
            duree_recup = None
            statut = "Pas encore recupere"

        results.append({
            "Ticker"              : ticker,
            "Max Drawdown (%)"    : round(max_dd * 100, 2),
            "Date Pic"            : date_pic.date(),
            "Date Creux"          : date_creux.date(),
            "Duree Chute (jours)" : duree_chute,
            "Date Recuperation"   : date_recup.date() if date_recup else "N/A",
            "Duree Recup (jours)" : duree_recup if duree_recup else "N/A",
            "Statut"              : statut,
        })

    df = pd.DataFrame(results).set_index("Ticker")
    return df.sort_values("Max Drawdown (%)")


def compute_underwater_duration(prices):
    """
    Calcule le nombre total de jours passés "sous l'eau"
    (en dessous du dernier pic) pour chaque actif.
    """
    rolling_max = prices.cummax()
    drawdown = (prices - rolling_max) / rolling_max
    underwater = (drawdown < 0).sum()
    return underwater.sort_values(ascending=False)


def rolling_max_drawdown(prices, window=252):
    """
    Calcule le drawdown maximum sur une fenêtre glissante d'un an (252 jours).
    Utile pour voir comment le risque évolue dans le temps.
    """
    rolling_dd = pd.DataFrame(index=prices.index, columns=prices.columns)

    for ticker in prices.columns:
        serie = prices[ticker]
        for i in range(window, len(serie)):
            window_prices = serie.iloc[i-window:i]
            peak = window_prices.cummax()
            dd = (window_prices - peak) / peak
            rolling_dd.loc[serie.index[i], ticker] = dd.min()

    return rolling_dd.astype(float)


# ── Pipeline principal ─────────────────────────────────────

def run_drawdown_pipeline():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Charge le returns_clean.csv
    print("Chargement de returns_clean.csv...")
    returns = pd.read_csv(RETURNS_CLEAN, index_col=0, parse_dates=True)
    print(f"  → {returns.shape[0]} jours × {returns.shape[1]} actifs")

    # Reconstitue les prix (base 100 au premier jour)
    prices = np.exp(returns.cumsum()) * 100

    # ── 1. Drawdown détaillé par actif ─────────────────────
    print("\n" + "="*60)
    print("  DRAWDOWN HISTORIQUE — 2015 à 2024")
    print("="*60)

    dd_details = compute_max_drawdown_details(prices)

    print("\n── Classement par drawdown maximum ──")
    print(dd_details.to_string())

    dd_details.to_csv(DATA_DIR + "drawdown_historique.csv")
    print(f"\n  💾 Sauvegardé → {DATA_DIR}drawdown_historique.csv")

    # ── 2. Jours sous l'eau ────────────────────────────────
    print("\n" + "="*60)
    print("  JOURS PASSES SOUS L'EAU (en dessous du dernier pic)")
    print("="*60)

    underwater = compute_underwater_duration(prices)
    underwater_pct = (underwater / len(prices) * 100).round(1)

    underwater_df = pd.DataFrame({
        "Jours sous l'eau"    : underwater,
        "% du temps sous l'eau" : underwater_pct,
    })
    print(underwater_df.to_string())

    underwater_df.to_csv(DATA_DIR + "drawdown_underwater.csv")
    print(f"\n  💾 Sauvegardé → {DATA_DIR}drawdown_underwater.csv")

    # ── 3. Résumé synthétique ──────────────────────────────
    print("\n" + "="*60)
    print("  RESUME SYNTHETIQUE")
    print("="*60)

    print(f"\n  Pire drawdown       : {dd_details['Max Drawdown (%)'].min():.2f}%  ({dd_details['Max Drawdown (%)'].idxmin()})")
    print(f"  Meilleur drawdown   : {dd_details['Max Drawdown (%)'].max():.2f}%  ({dd_details['Max Drawdown (%)'].idxmax()})")
    print(f"  Drawdown moyen      : {dd_details['Max Drawdown (%)'].mean():.2f}%")

    non_recuperes = dd_details[dd_details["Statut"] == "Pas encore recupere"]
    if len(non_recuperes) > 0:
        print(f"\n  ⚠ Actifs pas encore recuperes ({len(non_recuperes)}) :")
        for ticker in non_recuperes.index:
            print(f"    - {ticker} : {non_recuperes.loc[ticker, 'Max Drawdown (%)']:.2f}% (creux le {non_recuperes.loc[ticker, 'Date Creux']})")
    else:
        print("\n  ✓ Tous les actifs se sont recuperes de leur max drawdown")

    print(f"\n Drawdown terminé — fichiers sauvegardés dans {DATA_DIR}")
    print("   drawdown_historique.csv | drawdown_underwater.csv")

    return dd_details, underwater_df


if __name__ == "__main__":
    dd, underwater = run_drawdown_pipeline()