import os
import sys
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config import RISK_FREE_RATE, TRAIN_WINDOW, TEST_WINDOW, HMM_LOOKBACK
from optimization.optimizer import max_sharpe, min_variance, risk_parity
from ml.hmm_model import detect_regime

REGIME_STRATEGY = {"Bull": max_sharpe, "Lateral": risk_parity, "Bear": min_variance}


def get_current_regime(returns):
    return detect_regime(returns.tail(HMM_LOOKBACK))


def get_regime_allocation(returns):
    regime = get_current_regime(returns)
    result = REGIME_STRATEGY[regime](returns)
    result["regime"] = regime
    return result


def backtest_regime_allocation(returns):
    """
    Walk-forward backtest dynamique.
    IMPORTANT : le Sharpe est calcule sur la SERIE CONTINUE des rendements
    de test (et non en moyennant les Sharpe par periode, ce qui gonflait
    le resultat). Methode identique au backtest statique d'Adrien.
    """
    all_test_returns = []
    n = len(returns)
    start = TRAIN_WINDOW
    while start + TEST_WINDOW <= n:
        train = returns.iloc[start - TRAIN_WINDOW:start]
        test  = returns.iloc[start:start + TEST_WINDOW]
        try:
            result = get_regime_allocation(train)
            weights = pd.Series(result["weights"])
            test_ret = test[weights.index] @ weights
            all_test_returns.append(test_ret)
        except Exception as e:
            print(f"skip {returns.index[start].date()}: {e}")
        start += TEST_WINDOW

    full_series = pd.concat(all_test_returns)
    sharpe = (full_series.mean() * 252 - RISK_FREE_RATE) / (full_series.std() * np.sqrt(252))
    cum = (1 + full_series).cumprod()
    max_dd = (cum / cum.cummax() - 1).min()
    ret_ann = full_series.mean() * 252
    return {
        "sharpe": round(float(sharpe), 4),
        "return_ann": round(float(ret_ann), 4),
        "max_drawdown": round(float(max_dd), 4),
        "series": full_series,
    }


if __name__ == "__main__":
    returns = pd.read_csv(os.path.join(BASE_DIR, "data", "returns_clean.csv"),
                          index_col="Date", parse_dates=True)
    res = backtest_regime_allocation(returns)
    print(f"Sharpe GLOBAL (serie continue) : {res['sharpe']}")
    print(f"Rendement annualise            : {res['return_ann']:.1%}")
    print(f"Max drawdown                   : {res['max_drawdown']:.1%}")
