import numpy as np
import pandas as pd
import scipy.stats as stats

def kupiec_pof_test(returns: pd.Series, var_forecast: float, confidence: float = 0.95) -> dict:
    """
    Test de Proportion of Failures (POF) de Kupiec.
    Version robuste aux underflows numériques.
    """
    clean_returns = returns.dropna()
    n_obs = len(clean_returns)
    exceptions = int(np.sum(clean_returns < var_forecast))
    
    p_expected = 1 - confidence
    p_observed = exceptions / n_obs if n_obs > 0 else 0.0
    
    if n_obs == 0:
        return {"Erreur": "Données insuffisantes"}

    # Calcul robuste du Likelihood Ratio
    if exceptions == 0:
        lr_stat = -2 * (n_obs * np.log(1 - p_expected))
    elif exceptions == n_obs:
        lr_stat = -2 * (n_obs * np.log(p_expected))
    else:
        log_num = (n_obs - exceptions) * np.log(1 - p_expected) + exceptions * np.log(p_expected)
        log_den = (n_obs - exceptions) * np.log(1 - p_observed) + exceptions * np.log(p_observed)
        lr_stat = -2 * (log_num - log_den)
        
    p_value = float(1 - stats.chi2.cdf(lr_stat, df=1))
    
    return {
        "Observations": n_obs,
        "Exceptions Attendues": round(n_obs * p_expected, 2),
        "Exceptions Observées": exceptions,
        "P-Value Kupiec": round(p_value, 4),
        "Modèle Valide (> 5%)": bool(p_value > 0.05)
    }