import numpy as np
import pandas as pd
import scipy.stats as stats

def kupiec_pof_test(returns: pd.Series, var_forecast: float, confidence: float = 0.95) -> dict:
    """
    Test de Kupiec (Proportion of Failures) pour valider le modèle de VaR.
    Version robuste : utilise les propriétés logarithmiques pour éviter l'underflow numérique.
    """
    n_obs = len(returns.dropna())
    exceptions = np.sum(returns < var_forecast)
    p_expected = 1 - confidence
    p_observed = exceptions / n_obs
    
    # Gestion des cas extrêmes
    if exceptions == 0:
        lr_stat = -2 * (n_obs * np.log(1 - p_expected))
    elif exceptions == n_obs:
        lr_stat = -2 * (n_obs * np.log(p_expected))
    else:
        # Transformation mathématique : ln(x^y) = y * ln(x)
        # Cela empêche les résultats de devenir "0.0" lors de grandes puissances
        log_num = (n_obs - exceptions) * np.log(1 - p_expected) + exceptions * np.log(p_expected)
        log_den = (n_obs - exceptions) * np.log(1 - p_observed) + exceptions * np.log(p_observed)
        
        lr_stat = -2 * (log_num - log_den)
        
    # Calcul de la p-value avec la loi du Chi-2
    p_value = 1 - stats.chi2.cdf(lr_stat, df=1)
    
    return {
        "Observations": n_obs,
        "Violations Attendues": round(n_obs * p_expected, 2),
        "Violations Observées": exceptions,
        "P-Value": round(p_value, 4),
        "Modèle Valide (> 5%)": p_value > 0.05
    }