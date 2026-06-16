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
                          test_window=126,
                          capital=10000):
    from config import COMMISSION_PAR_ORDRE

    portfolio_returns = []
    prev_weights = None
    start = train_window
    cout_total_reel = 0  # cumul des vraies commissions

    while start + test_window <= len(returns):
        train = returns.iloc[start - train_window : start]
        test  = returns.iloc[start : start + test_window]

        try:
            result  = strategy_fn(train)
            weights = pd.Series(result["weights"])
        except Exception as e:
            print(f"Skip period at {returns.index[start].date()} : {e}")
            start += test_window
            continue

        # Calcul des vrais ordres necessaires
        if prev_weights is None:
            nb_ordres = sum(1 for v in weights if v > 0.001)
        else:
            nb_ordres = sum(
                1 for t in weights.index
                if abs(weights.get(t, 0) - prev_weights.get(t, 0)) > 0.01
            )

        cout = nb_ordres * COMMISSION_PAR_ORDRE
        cout_total_reel += cout

        if capital > 0 and cout < capital:
            cout_journalier = np.log(1 - cout / capital)
        else:
            cout_journalier = 0

        test_returns = test[weights.index] @ weights
        test_returns.iloc[0] += cout_journalier

        portfolio_returns.append(test_returns)
        prev_weights = weights
        start += test_window

    return pd.concat(portfolio_returns), cout_total_reel


def compute_metrics(portfolio_returns, capital=10000,
                    cout_total_reel=None, commission=None):
    from config import COMMISSION_PAR_ORDRE, TRADING_DAYS
    if commission is None:
        commission = COMMISSION_PAR_ORDRE

    n_days = len(portfolio_returns)

    ret_ann = portfolio_returns.mean() * TRADING_DAYS
    vol_ann = portfolio_returns.std() * np.sqrt(TRADING_DAYS)
    sharpe  = (ret_ann - RISK_FREE_RATE) / vol_ann
    cum_return = (1 + portfolio_returns).prod() - 1

    # Utilise les vraies commissions si disponibles
    if cout_total_reel is None:
        n_rebalancements = n_days // 126
        cout_total = n_rebalancements * 35 * commission
    else:
        cout_total = cout_total_reel

    cout_pct       = cout_total / capital
    cum_return_net = cum_return - cout_pct
    ret_ann_net    = ret_ann - (cout_pct / (n_days / TRADING_DAYS))

    cumulative  = (1 + portfolio_returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown    = (cumulative - rolling_max) / rolling_max
    max_dd      = drawdown.min()

    return {
        "return_ann":       round(ret_ann, 4),
        "return_ann_net":   round(ret_ann_net, 4),
        "vol_ann":          round(vol_ann, 4),
        "sharpe":           round(sharpe, 4),
        "sharpe_net":       round((ret_ann_net - RISK_FREE_RATE) / vol_ann, 4),
        "max_drawdown":     round(max_dd, 4),
        "cum_return":       round(cum_return, 4),
        "cum_return_net":   round(cum_return_net, 4),
        "cout_commissions": round(cout_total, 2),
        "n_days":           n_days,
    }


def compare_backtests(returns, capital=10000):
    """
    Lance le backtest walk-forward sur toutes les strategies
    et retourne un tableau comparatif.
    """
    results = {}

    strategies = {
        "max_sharpe":   max_sharpe,
        "min_variance": min_variance,
        "risk_parity":  risk_parity,
    }

    for name, fn in strategies.items():
        print(f"Backtest {name} ...")
        port_ret, cout_reel = walk_forward_backtest(returns, fn, capital=capital)
        results[name] = compute_metrics(port_ret, capital=capital,
                                        cout_total_reel=cout_reel)

    # Benchmark : equal-weight
    print("Backtest equal_weight (benchmark) ...")
    def equal_weight_fn(train):
        n = len(train.columns)
        return {
            "strategy": "equal_weight",
            "weights":  {t: 1/n for t in train.columns},
        }

    port_ret_eq, cout_reel_eq = walk_forward_backtest(
        returns, equal_weight_fn, capital=capital
    )
    results["equal_weight"] = compute_metrics(
        port_ret_eq, capital=capital, cout_total_reel=cout_reel_eq
    )

    return pd.DataFrame(results).T


if __name__ == "__main__":
    returns = pd.read_csv("data/returns_clean.csv", index_col=0, parse_dates=True)

    # Test avec differents capitaux
    for capital in [1000, 10000, 50000]:
        print(f"\n=== CAPITAL : {capital}EUR ===")
        df = compare_backtests(returns, capital=capital)
        print(df[["return_ann", "return_ann_net", "sharpe_net",
                   "cout_commissions"]].to_string())

    # Sauvegarde avec capital par defaut 10 000EUR
    df = compare_backtests(returns, capital=10000)
    df.to_csv("data/backtest_results.csv")
    print("\nSauvegarde -> data/backtest_results.csv")