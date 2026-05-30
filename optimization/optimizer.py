import numpy as np
import pandas as pd
from pypfopt import expected_returns, risk_models
from config import RISK_FREE_RATE, TRADING_DAYS

def get_mu_sigma(returns):
    prices = np.exp(returns.cumsum())
    mu     = expected_returns.mean_historical_return(prices, frequency=252)
    sigma  = risk_models.CovarianceShrinkage(prices, frequency=252).ledoit_wolf()
    return mu, sigma

def portfolio_metrics(weights, returns):
    w      = pd.Series(weights)
    ret    = float(returns.mean() @ w * 252)
    vol    = float(np.sqrt(w @ (returns.cov() * 252) @ w))
    sharpe = (ret - RISK_FREE_RATE) / vol
    return {
        "return":     round(ret, 4),
        "volatility": round(vol, 4),
        "sharpe":     round(sharpe, 4),
    }