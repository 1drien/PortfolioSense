import sys
sys.path.insert(0, '.')

from data.mock_data import get_mock_returns
from optimization.optimizer import compare_strategies

returns = get_mock_returns()
print(compare_strategies(returns))

from optimization.optimizer import efficient_frontier_curve

curve = efficient_frontier_curve(returns, n_portfolios=1000)
print(curve.head(10))
print("\nSharpe max dans le nuage :", curve["sharpe"].max())
print("Sharpe min dans le nuage :", curve["sharpe"].min())