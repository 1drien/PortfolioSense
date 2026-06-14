import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis
from typing import Union

def compute_historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """VaR Historique (Quantile empirique)."""
    return np.percentile(returns.dropna(), (1 - confidence) * 100)

def compute_cornish_fisher_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """
    VaR Modifiée (Cornish-Fisher). 
    Ajuste le Z-score pour tenir compte du Skewness et du Kurtosis.
    Très utilisé dans les hedge funds pour les actifs non-normaux.
    """
    clean_returns = returns.dropna()
    mu = clean_returns.mean()
    sigma = clean_returns.std()
    
    # Moments statistiques
    s = skew(clean_returns)
    k = kurtosis(clean_returns) # Excess kurtosis
    
    # Z-score standard
    z = norm.ppf(1 - confidence)
    
    # Expansion de Cornish-Fisher
    z_cf = z + ( (z**2 - 1)*s )/6 + ( (z**3 - 3*z)*k )/24 - ( (2*z**3 - 5*z)*(s**2) )/36
    
    return float(mu + z_cf * sigma)

def compute_cvar(returns: pd.Series, confidence: float = 0.95, method: str = 'historical') -> float:
    """Expected Shortfall (CVaR). Moyenne des pires scénarios."""
    if method == 'historical':
        var_val = compute_historical_var(returns, confidence)
    elif method == 'cornish-fisher':
        var_val = compute_cornish_fisher_var(returns, confidence)
    else:
        raise ValueError("Méthode non supportée. Utilisez 'historical' ou 'cornish-fisher'.")
        
    tail_losses = returns[returns <= var_val]
    return float(tail_losses.mean()) if not tail_losses.empty else var_val