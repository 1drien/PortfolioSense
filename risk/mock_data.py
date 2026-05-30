import pandas as pd
import numpy as np

def generate_mock_returns(n_assets: int = 5, seed: int = 42) -> pd.DataFrame:
    """
    Génère un DataFrame de log-rendements factices (2005 - 2024) pour tester 
    les mesures de risque et les stress tests historiques.
    """
    np.random.seed(seed)
    
    # Période couvrant la crise de 2008 (GFC), le COVID (2020) et la crise des taux (2022)
    dates = pd.date_range(start="2005-01-01", end="2024-01-01", freq='B')
    n_days = len(dates)
    
    tickers = [f"TICKER_{i}" for i in range(1, n_assets + 1)]
    
    # Rendements de base (Distribution normale)
    mu, sigma = 0.0002, 0.012
    data = np.random.normal(loc=mu, scale=sigma, size=(n_days, n_assets))
    
    returns_df = pd.DataFrame(data, index=dates, columns=tickers)
    
    # Injection de chocs artificiels pour que les stress tests détectent quelque chose
    # 1. GFC (Sep 2008 - Mar 2009)
    returns_df.loc['2008-09-01':'2009-03-31'] += np.random.normal(-0.005, 0.03, size=(returns_df.loc['2008-09-01':'2009-03-31'].shape))
    # 2. COVID (Fev 2020 - Mar 2020)
    returns_df.loc['2020-02-15':'2020-03-31'] += np.random.normal(-0.01, 0.05, size=(returns_df.loc['2020-02-15':'2020-03-31'].shape))
    # 3. Crise Taux (2022)
    returns_df.loc['2022-01-01':'2022-12-31'] += np.random.normal(-0.001, 0.02, size=(returns_df.loc['2022-01-01':'2022-12-31'].shape))
    
    return returns_df