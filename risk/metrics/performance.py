import numpy as np
import pandas as pd
from .volatility import compute_annualized_volatility, compute_downside_volatility
from .drawdowns import compute_max_drawdown

def compute_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """Ratio de Sharpe : Rendement excédentaire par unité de risque total."""
    ann_return = returns.mean() * periods_per_year
    ann_vol = compute_annualized_volatility(returns, periods_per_year)
    if ann_vol == 0:
        return 0.0
    return float((ann_return - risk_free_rate) / ann_vol)

def compute_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """Ratio de Sortino : Rendement excédentaire par unité de risque baissier."""
    ann_return = returns.mean() * periods_per_year
    downside_vol = compute_downside_volatility(returns, mar=risk_free_rate/periods_per_year, periods_per_year=periods_per_year)
    if downside_vol == 0:
        return 0.0
    return float((ann_return - risk_free_rate) / downside_vol)

def compute_calmar_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """Ratio de Calmar : Rendement excédentaire par rapport au Max Drawdown."""
    ann_return = returns.mean() * periods_per_year
    max_dd = abs(compute_max_drawdown(returns)) # On prend la valeur absolue du drawdown
    if max_dd == 0:
        return 0.0
    return float((ann_return - risk_free_rate) / max_dd)