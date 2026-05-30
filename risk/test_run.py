import pandas as pd
from mock_data import generate_mock_returns
from var import compute_historical_var, compute_cvar
from stress import run_stress_tests
from backtest import kupiec_pof_test
from metrics import calculate_max_drawdown

# 1. Générer les données
print("Génération des données factices (2005-2024)...")
df_returns = generate_mock_returns()
portfolio = df_returns.mean(axis=1) # Portefeuille équipondéré

# 2. VaR & CVaR
var_95 = compute_historical_var(portfolio, 0.95)
cvar_95 = compute_cvar(portfolio, 0.95, 'historical')
print(f"\n--- MESURES DE RISQUE ---")
print(f"VaR Historique (95%): {var_95:.2%}")
print(f"CVaR Historique (95%): {cvar_95:.2%}")
print(f"Max Drawdown Global: {calculate_max_drawdown(portfolio):.2%}")

# 3. Stress Tests
print("\n--- STRESS TESTS HISTORIQUES ---")
print(run_stress_tests(portfolio))

# 4. Backtest
print("\n--- BACKTEST KUPIEC ---")
print(pd.DataFrame([kupiec_pof_test(portfolio, var_95, 0.95)]).T)