import sys
sys.path.insert(0, '.')

from data.mock_data import get_mock_returns
from optimization.optimizer import compare_strategies

returns = get_mock_returns()
print(compare_strategies(returns))