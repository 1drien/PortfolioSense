import pandas as pd
from scipy.stats import skew, kurtosis, jarque_bera

def compute_skewness(returns: pd.Series) -> float:
    """
    Calcule l'asymétrie (Skewness). 
    Un skew négatif indique une probabilité plus forte de rendements très négatifs.
    """
    return float(skew(returns.dropna()))

def compute_kurtosis(returns: pd.Series) -> float:
    """
    Calcule l'aplatissement (Excess Kurtosis de Fisher). 
    > 0 indique des queues de distribution épaisses (Fat Tails / risque de krach élevé).
    """
    return float(kurtosis(returns.dropna()))

def test_normality_jarque_bera(returns: pd.Series) -> dict:
    """
    Test statistique de Jarque-Bera pour la normalité.
    Très utilisé pour valider les hypothèses des modèles paramétriques.
    """
    clean_returns = returns.dropna()
    jb_stat, p_value = jarque_bera(clean_returns)
    
    return {
        "Statistique JB": float(jb_stat),
        "P-Value": float(p_value),
        "Est Normal (> 5%)": bool(p_value > 0.05)
    }