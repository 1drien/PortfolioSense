# optimization/optimizer.py
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt.black_litterman import BlackLittermanModel
from pypfopt.risk_models import CovarianceShrinkage
import sys
sys.path.insert(0, '.')
from config import RISK_FREE_RATE, TRADING_DAYS, WEIGHT_MIN, WEIGHT_MAX


def get_mu_sigma(returns):
    prices = np.exp(returns.cumsum())
    mu     = expected_returns.mean_historical_return(prices, frequency=252)
    sigma  = CovarianceShrinkage(prices, frequency=252).ledoit_wolf()
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


def max_sharpe(returns):
    mu, sigma = get_mu_sigma(returns)
    ef = EfficientFrontier(mu, sigma, weight_bounds=(WEIGHT_MIN, WEIGHT_MAX))
    ef.max_sharpe(risk_free_rate=RISK_FREE_RATE)
    weights = ef.clean_weights()
    metrics = portfolio_metrics(weights, returns)
    return {"strategy": "max_sharpe", "weights": weights, "metrics": metrics}


def min_variance(returns):
    mu, sigma = get_mu_sigma(returns)
    ef = EfficientFrontier(mu, sigma, weight_bounds=(WEIGHT_MIN, WEIGHT_MAX))
    ef.min_volatility()
    weights = ef.clean_weights()
    metrics = portfolio_metrics(weights, returns)
    return {"strategy": "min_variance", "weights": weights, "metrics": metrics}


def risk_parity(returns):
    _, sigma = get_mu_sigma(returns)
    Sigma    = sigma.values
    n        = len(Sigma)

    def objective(w):
        port_vol = np.sqrt(w @ Sigma @ w)
        marginal = Sigma @ w / port_vol
        contrib  = w * marginal
        target   = port_vol / n
        return np.sum((contrib - target) ** 2)

    w0     = np.ones(n) / n
    bounds = [(WEIGHT_MIN, WEIGHT_MAX)] * n
    cons   = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    result = minimize(objective, w0, method="SLSQP",
                      bounds=bounds, constraints=cons,
                      options={"ftol": 1e-12, "maxiter": 1000})
    weights = dict(zip(returns.columns, result.x.round(4)))
    metrics = portfolio_metrics(weights, returns)
    return {"strategy": "risk_parity", "weights": weights, "metrics": metrics}


def black_litterman(returns, views=None, confidences=None):
    mu, sigma = get_mu_sigma(returns)
    bl = BlackLittermanModel(sigma, pi="equal",
                             absolute_views=views or {},
                             omega="idzorek",
                             view_confidences=confidences or [])
    ret_bl = bl.bl_returns()
    cov_bl = bl.bl_cov()
    ef = EfficientFrontier(ret_bl, cov_bl,
                           weight_bounds=(WEIGHT_MIN, WEIGHT_MAX))
    ef.max_sharpe(risk_free_rate=RISK_FREE_RATE)
    weights = ef.clean_weights()
    metrics = portfolio_metrics(weights, returns)
    return {"strategy": "black_litterman", "weights": weights, "metrics": metrics}


def efficient_frontier_curve(returns, n_portfolios=3000):
    mu, sigma = get_mu_sigma(returns)
    n         = len(returns.columns)
    records   = []
    for _ in range(n_portfolios):
        w   = np.random.dirichlet(np.ones(n))
        ret = float(mu.values @ w)
        vol = float(np.sqrt(w @ sigma.values @ w))
        records.append({
            "return":     round(ret, 4),
            "volatility": round(vol, 4),
            "sharpe":     round((ret - RISK_FREE_RATE) / vol, 4),
        })
    return pd.DataFrame(records)


def compare_strategies(returns):
    results = []
    for fn in [max_sharpe, min_variance, risk_parity]:
        r   = fn(returns)
        row = {"strategy": r["strategy"]}
        row.update(r["metrics"])
        results.append(row)
    return pd.DataFrame(results).set_index("strategy")