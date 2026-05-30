import numpy as np
import pandas as pd
from scipy.stats import norm

def compute_historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """VaR Historique : quantile empirique[cite: 49]."""
    return np.percentile(returns.dropna(), (1 - confidence) * 100)

def compute_parametric_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """VaR Paramétrique : hypothèse de normalité, utilise le Z-score[cite: 50]."""
    mu = np.mean(returns)
    sigma = np.std(returns)
    z_score = norm.ppf(1 - confidence)
    return mu + z_score * sigma

def compute_monte_carlo_var(returns: pd.Series, confidence: float = 0.95, n_sims: int = 10000) -> float:
    """VaR Monte Carlo : 10 000 simulations de la distribution[cite: 51]."""
    np.random.seed(42)
    mu, sigma = np.mean(returns), np.std(returns)
    simulated_returns = np.random.normal(loc=mu, scale=sigma, size=n_sims)
    return np.percentile(simulated_returns, (1 - confidence) * 100)

def compute_cvar(returns: pd.Series, confidence: float = 0.95, method: str = 'historical') -> float:
    """CVaR / Expected Shortfall : moyenne des pertes au-delà de la VaR[cite: 52, 111]."""
    if method == 'historical':
        var_value = compute_historical_var(returns, confidence)
    elif method == 'parametric':
        var_value = compute_parametric_var(returns, confidence)
    else:
        var_value = compute_monte_carlo_var(returns, confidence)
        
    tail_losses = returns[returns <= var_value]
    return np.mean(tail_losses) if len(tail_losses) > 0 else var_value