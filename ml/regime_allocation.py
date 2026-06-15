# ml/regime_allocation.py
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, 'c:/Users/lachk/OneDrive/Bureau/CY/ing3/PFE')

from config import N_REGIMES, HMM_LOOKBACK, RISK_FREE_RATE
from optimization.optimizer import max_sharpe, min_variance, risk_parity
from ml.hmm_model import detect_regime   # on va ajouter cette fonction

# ── Règle d'allocation par régime ────────────────────────────────────────────
REGIME_STRATEGY = {
    "Bull":    max_sharpe,
    "Lateral": risk_parity,
    "Bear":    min_variance,
}

def get_current_regime(returns):
    """
    Détecte le régime actuel à partir des HMM_LOOKBACK derniers jours.
    Retourne : "Bull", "Lateral" ou "Bear"
    """
    recent = returns.tail(HMM_LOOKBACK)
    regime = detect_regime(recent)
    return regime

def get_regime_allocation(returns):
    """
    Fonction principale du module ML.
    - Détecte le régime courant
    - Applique la stratégie correspondante
    - Retourne les poids + métriques + explication

    Usage :
        from ml.regime_allocation import get_regime_allocation
        result = get_regime_allocation(returns)
    """
    # 1. Détection du régime
    regime = get_current_regime(returns)

    # 2. Sélection de la stratégie
    strategy_fn = REGIME_STRATEGY[regime]

    # 3. Optimisation
    result = strategy_fn(returns)

    # 4. Ajout du régime dans le résultat
    result["regime"] = regime
    result["regime_rule"] = f"Régime {regime} → stratégie {result['strategy']}"

    return result

def backtest_regime_allocation(returns):
    """
    Walk-forward backtest :
    - Fenêtre d'entraînement : TRAIN_WINDOW jours (2 ans)
    - Fenêtre de test : TEST_WINDOW jours (6 mois)
    - À chaque étape : détecte le régime → applique la stratégie → mesure la perf
    Retourne un DataFrame avec les performances par période.
    """
    from config import TRAIN_WINDOW, TEST_WINDOW

    records = []
    n = len(returns)
    start = TRAIN_WINDOW

    while start + TEST_WINDOW <= n:
        # Fenêtre d'entraînement
        train = returns.iloc[start - TRAIN_WINDOW:start]
        # Fenêtre de test
        test  = returns.iloc[start:start + TEST_WINDOW]

        # Allocation basée sur le régime détecté sur la fenêtre train
        try:
            result  = get_regime_allocation(train)
            weights = pd.Series(result["weights"])
            regime  = result["regime"]
            strategy = result["strategy"]

            # Performance sur la fenêtre de test
            test_ret = test[weights.index] @ weights
            cumret   = (1 + test_ret).prod() - 1
            vol      = test_ret.std() * np.sqrt(252)
            sharpe   = (test_ret.mean() * 252 - RISK_FREE_RATE) / (vol + 1e-9)

            records.append({
                "date_start":  test.index[0].date(),
                "date_end":    test.index[-1].date(),
                "regime":      regime,
                "strategy":    strategy,
                "return":      round(cumret, 4),
                "volatility":  round(vol, 4),
                "sharpe":      round(sharpe, 4),
            })
        except Exception as e:
            print(f"Erreur sur la période {returns.index[start].date()} : {e}")

        start += TEST_WINDOW

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    # Test rapide
    returns = pd.read_csv(
        "c:/Users/lachk/OneDrive/Bureau/CY/ing3/PFE/data/returns_clean.csv",
        index_col="Date", parse_dates=True
    )

    print("── Test get_regime_allocation ───────────────────────────────")
    result = get_regime_allocation(returns)
    print(f"Régime détecté    : {result['regime']}")
    print(f"Stratégie appelée : {result['strategy']}")
    print(f"Métriques         : {result['metrics']}")
    print(f"\nTop 5 allocations :")
    weights = pd.Series(result["weights"]).sort_values(ascending=False)
    print(weights.head(5).to_string())

    print("\n── Backtest walk-forward ─────────────────────────────────────")
    df_bt = backtest_regime_allocation(returns)
    print(df_bt.to_string(index=False))
    print(f"\nSharpe moyen : {df_bt['sharpe'].mean():.3f}")
    print(f"Rendement moyen par période : {df_bt['return'].mean():.1%}")

    # Sauvegarde
    df_bt.to_csv(
        "c:/Users/lachk/OneDrive/Bureau/CY/ing3/PFE/data/backtest_regimes.csv",
        index=False
    )
    print("\nBacktest sauvegardé → data/backtest_regimes.csv")