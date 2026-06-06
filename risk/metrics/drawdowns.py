import numpy as np
import pandas as pd

def compute_drawdown_series(returns: pd.Series) -> pd.Series:
    """Calcule l'évolution temporelle des pertes depuis les plus-hauts."""
    simple_returns = np.exp(returns) - 1
    wealth = (1 + simple_returns).cumprod()
    peaks = wealth.cummax()
    return (wealth - peaks) / peaks

def compute_max_drawdown(returns: pd.Series) -> float:
    """Extrait le pire drawdown absolu."""
    return float(compute_drawdown_series(returns).min())

def compute_ulcer_index(returns: pd.Series) -> float:
    """
    Ulcer Index (Martin & McCann, 1989).
    Mesure la profondeur et la durée combinées des drawdowns.
    """
    drawdowns = compute_drawdown_series(returns)
    # Racine carrée de la moyenne des drawdowns au carré
    squared_dd = (drawdowns * 100) ** 2 # En pourcentage pour le standard de l'indice
    ulcer = np.sqrt(squared_dd.mean())
    return float(ulcer)