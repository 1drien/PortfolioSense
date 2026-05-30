import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

def calculate_max_drawdown(portfolio_returns: pd.Series) -> float:
    """Calcule le Maximum Drawdown global."""
    simple_returns = np.exp(portfolio_returns) - 1
    wealth_index = (1 + simple_returns).cumprod()
    previous_peaks = wealth_index.cummax()
    drawdowns = (wealth_index - previous_peaks) / previous_peaks
    return drawdowns.min()

def get_risk_summary(returns_df: pd.DataFrame) -> pd.DataFrame:
    """Résumé des statistiques de distribution (Skewness, Kurtosis)."""
    metrics = {
        "Volatilité Annualisée": returns_df.std() * np.sqrt(252),
        "Skewness": returns_df.apply(skew),
        "Kurtosis": returns_df.apply(kurtosis)
    }
    return pd.DataFrame(metrics)