import sys
sys.path.insert(0, '.')

from data.mock_data import get_mock_returns
from optimization.optimizer import get_mu_sigma

returns = get_mock_returns()
mu, sigma = get_mu_sigma(returns)

print("Rendements espérés annualisés :")
print(mu)
print("\nShape de sigma :", sigma.shape)