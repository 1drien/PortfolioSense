import sys
sys.path.insert(0, '.')

import pandas as pd
from optimization.optimizer import compare_strategies, efficient_frontier_curve

# Vraies données
returns = pd.read_csv("data/returns_clean.csv", index_col=0, parse_dates=True)
print(f"Données chargées : {returns.shape}")
print(f"Période : {returns.index[0].date()} -> {returns.index[-1].date()}")

# Tableau comparatif
print("\n=== TABLEAU COMPARATIF ===")
print(compare_strategies(returns))

# Frontière efficiente
print("\n=== FRONTIÈRE EFFICIENTE ===")
curve = efficient_frontier_curve(returns, n_portfolios=500)
print(f"Sharpe max du nuage : {curve['sharpe'].max():.3f}")
