# data/mock_data.py
# Donnees fictives pour permettre a tous les membres de developper
# sans attendre le pipeline yfinance du Membre 2.
# A remplacer par load_returns() une fois returns_clean.csv disponible.

import numpy as np
import pandas as pd

TICKERS_MOCK = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META",
    "JPM", "BAC", "GS", "JNJ", "UNH",
    "XOM", "CVX", "AMZN", "TSLA", "HD",
    "MCD", "CAT", "LMT", "PG", "BLK",
]

def get_mock_returns(n_days: int = 2000,
                     seed: int = 42) -> pd.DataFrame:
    """
    Genere des log-rendements journaliers fictifs mais realistes.
    Meme format que load_returns() — remplacement transparent.

    Usage dans chaque module :
        # Semaine 1 (avant donnees reelles)
        from data.mock_data import get_mock_returns
        returns = get_mock_returns()

        # Semaine 2+ (donnees reelles disponibles)
        from data.loader import load_returns
        returns = load_returns()
    """
    np.random.seed(seed)
    n = len(TICKERS_MOCK)

    # Parametres realistes par secteur
    mus  = np.array([0.0004] * 5 +   # Tech : rendement eleve
                    [0.0002] * 5 +   # Finance : rendement moyen
                    [0.0001] * 5 +   # Energie/Sante : rendement faible
                    [0.0003] * 5)    # Consommation/Industrie

    vols = np.array([0.022] * 5 +    # Tech : vol elevee
                    [0.016] * 5 +    # Finance : vol moyenne
                    [0.015] * 5 +    # Energie/Sante : vol faible
                    [0.014] * 5)     # Consommation : vol faible

    # Matrice de correlation avec structure sectorielle
    corr = np.eye(n)
    for i in range(n):
        for j in range(n):
            if i == j:
                corr[i, j] = 1.0
            elif i // 5 == j // 5:
                corr[i, j] = 0.6   # Forte correlation intra-secteur
            else:
                corr[i, j] = 0.25  # Correlation moderee inter-secteur

    # Matrice de covariance
    sigma = np.outer(vols, vols) * corr

    # Simulation des rendements
    raw = np.random.multivariate_normal(mus, sigma, size=n_days)

    dates = pd.bdate_range(end="2024-12-31", periods=n_days)
    returns = pd.DataFrame(raw, index=dates, columns=TICKERS_MOCK)

    return returns


if __name__ == "__main__":
    r = get_mock_returns()
    print(f"Shape : {r.shape}")
    print(f"Periode : {r.index[0].date()} -> {r.index[-1].date()}")
    print(r.describe().round(4))