import pandas as pd
import numpy as np
from risk.metrics.drawdowns import compute_max_drawdown

def run_stress_tests(returns: pd.Series) -> pd.DataFrame:
    """
    Rejoue les scénarios de crise historiques sur le portefeuille.
    """
    scenarios = {
        "Global Financial Crisis (2008)": ("2008-09-01", "2009-03-31"),
        "COVID-19 Crash (2020)": ("2020-02-15", "2020-03-31"),
        "Crise des Taux (2022)": ("2022-01-01", "2022-12-31")
    }
    
    results = {}
    
    for name, (start, end) in scenarios.items():
        try:
            period_returns = returns.loc[start:end]
            if not period_returns.empty:
                cum_return = np.exp(period_returns.sum()) - 1
                max_dd = compute_max_drawdown(period_returns)
                
                results[name] = {
                    "Rendement Cumulé": f"{cum_return:.2%}",
                    "Max Drawdown": f"{max_dd:.2%}"
                }
        except KeyError:
            continue
            
    return pd.DataFrame(results).T