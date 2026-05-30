import pandas as pd
import numpy as np

def run_stress_tests(portfolio_returns: pd.Series) -> pd.DataFrame:
    """
    Rejoue des scénarios de crise historiques et calcule le rendement cumulé 
    et le pire Drawdown sur ces périodes.
    """
    scenarios = {
        "Global Financial Crisis (2008)": ("2008-09-01", "2009-03-31"),
        "COVID-19 Crash (2020)": ("2020-02-15", "2020-03-31"),
        "Crise des Taux (2022)": ("2022-01-01", "2022-12-31")
    }
    
    results = {}
    
    for name, (start, end) in scenarios.items():
        try:
            # Extraction de la période
            period_returns = portfolio_returns.loc[start:end]
            if len(period_returns) == 0:
                continue
                
            # Calcul du rendement cumulé
            cum_return = np.exp(period_returns.sum()) - 1
            
            # Calcul du Max Drawdown sur la période
            wealth = (1 + (np.exp(period_returns) - 1)).cumprod()
            peaks = wealth.cummax()
            drawdown = (wealth - peaks) / peaks
            max_dd = drawdown.min()
            
            results[name] = {
                "Rendement Cumulé": f"{cum_return:.2%}",
                "Max Drawdown": f"{max_dd:.2%}"
            }
        except KeyError:
            pass # Si les dates ne sont pas dans l'index
            
    return pd.DataFrame(results).T