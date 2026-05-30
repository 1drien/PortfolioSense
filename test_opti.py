import sys
sys.path.insert(0, '.')

from data.mock_data import get_mock_returns
from optimization.optimizer import get_mu_sigma

returns = get_mock_returns()
mu, sigma = get_mu_sigma(returns)

print("Rendements espérés annualisés :")
print(mu)
print("\nShape de sigma :", sigma.shape)

from optimization.optimizer import get_mu_sigma, portfolio_metrics

mu, sigma = get_mu_sigma(returns)

# Test avec poids egaux pour commencer
n = len(returns.columns)
weights = {t: 1/n for t in returns.columns}

metrics = portfolio_metrics(weights, returns)
print("Métriques du portefeuille :", metrics)