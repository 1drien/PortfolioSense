import numpy as np
import pandas as pd

def compute_annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Volatilité historique annualisée standard."""
    return float(returns.std() * np.sqrt(periods_per_year))

def compute_downside_volatility(returns: pd.Series, mar: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Downside Deviation (Semi-volatilité).
    Ne prend en compte que les rendements inférieurs au MAR (Minimum Acceptable Return).
    """
    downside_returns = returns[returns < mar]
    if downside_returns.empty:
        return 0.0
    # On somme les carrés des écarts sous le MAR
    sq_deviations = (downside_returns - mar) ** 2
    downside_variance = sq_deviations.mean()
    return float(np.sqrt(downside_variance) * np.sqrt(periods_per_year))

def compute_ewma_volatility(returns: pd.Series, lambda_: float = 0.94, periods_per_year: int = 252) -> pd.Series:
    """Volatilité EWMA (RiskMetrics). La série temporelle des volatilités locales."""
    variance = returns.ewm(alpha=(1 - lambda_), adjust=False).var()
    return np.sqrt(variance) * np.sqrt(periods_per_year)