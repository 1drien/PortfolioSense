# optimization/backtest.py
# Walk-forward backtesting des stratégies d'optimisation
# Prouve empiriquement que nos stratégies battent un benchmark

import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from optimization.optimizer import max_sharpe, min_variance, risk_parity
from config import RISK_FREE_RATE, TRADING_DAYS


def walk_forward_backtest(returns, strategy_fn,
                          train_window=504,
                          test_window=126):
    """
    Backtest walk-forward d'une stratégie.
    
    À chaque pas :
    1. Optimise les poids sur train_window jours
    2. Applique ces poids sur test_window jours suivants
    3. Mesure la performance réalisée
    
    Retourne la série temporelle des rendements du portefeuille.
    """
    # On va remplir ça pendant la boucle
    portfolio_returns = []   # on collecte les rendements jour par jour
    
    start = train_window     # on commence après le premier train possible
    
    while start + test_window <= len(returns):
        # 1. Fenêtre d'entraînement
        train = returns.iloc[start - train_window : start]
        
        # 2. Fenêtre de test
        test  = returns.iloc[start : start + test_window]
        
        # 3. Optimisation sur le train
        try:
            result  = strategy_fn(train)
            weights = pd.Series(result["weights"])
        except Exception as e:
            print(f"Skip period at {returns.index[start].date()} : {e}")
            start += test_window
            continue
        
        # 4. Application des poids sur le test
        test_returns = test[weights.index] @ weights
        portfolio_returns.append(test_returns)
        
        # 5. Avancer
        start += test_window
    
    # Concaténer tous les segments en une seule série
    return pd.concat(portfolio_returns)

def compute_metrics(portfolio_returns):
    """
    Calcule les métriques clés d'une série de rendements de portefeuille.
    
    Retourne un dict avec :
    - return_ann   : rendement annualisé
    - vol_ann      : volatilité annualisée  
    - sharpe       : ratio de Sharpe annualisé
    - max_drawdown : pire perte depuis un pic
    - cum_return   : rendement cumulé total
    """
    n_days = len(portfolio_returns)
    
    # Rendement et volatilité annualisés
    ret_ann = portfolio_returns.mean() * TRADING_DAYS
    vol_ann = portfolio_returns.std() * np.sqrt(TRADING_DAYS)
    sharpe  = (ret_ann - RISK_FREE_RATE) / vol_ann
    
    # Rendement cumulé (composé)
    cum_return = (1 + portfolio_returns).prod() - 1
    
    # Max Drawdown : pire perte depuis un pic
    cumulative = (1 + portfolio_returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()
    
    return {
        "return_ann":   round(ret_ann, 4),
        "vol_ann":      round(vol_ann, 4),
        "sharpe":       round(sharpe, 4),
        "max_drawdown": round(max_dd, 4),
        "cum_return":   round(cum_return, 4),
        "n_days":       n_days,
    }

def compare_backtests(returns):
    """
    Lance le backtest walk-forward sur toutes les stratégies
    et retourne un tableau comparatif.
    """
    results = {}
    
    # 3 stratégies à tester
    strategies = {
        "max_sharpe":   max_sharpe,
        "min_variance": min_variance,
        "risk_parity":  risk_parity,
    }
    
    for name, fn in strategies.items():
        print(f"Backtest {name} ...")
        port_ret = walk_forward_backtest(returns, fn)
        results[name] = compute_metrics(port_ret)
    
    # Benchmark : equal-weight (le plus dur à battre)
    print("Backtest equal_weight (benchmark) ...")
    def equal_weight_fn(train):
        n = len(train.columns)
        return {
            "strategy": "equal_weight",
            "weights":  {t: 1/n for t in train.columns},
        }
    
    port_ret_eq = walk_forward_backtest(returns, equal_weight_fn)
    results["equal_weight"] = compute_metrics(port_ret_eq)
    
    return pd.DataFrame(results).T


if __name__ == "__main__":
    returns = pd.read_csv("data/returns_clean.csv", index_col=0, parse_dates=True)
    df = compare_backtests(returns)
    print("\n=== RESULTATS WALK-FORWARD ===")
    print(df.to_string())
    df.to_csv("data/backtest_results.csv")
    print("\nSauvegardé → data/backtest_results.csv")