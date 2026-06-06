import pandas as pd
import warnings

# Suppression des warnings pandas pour un affichage propre
warnings.filterwarnings("ignore")

# Importation depuis notre architecture modulaire
from mock_data import generate_mock_returns
from metrics import (
    compute_historical_var, compute_cornish_fisher_var, compute_cvar,
    compute_annualized_volatility, compute_downside_volatility,
    compute_max_drawdown, compute_ulcer_index,
    compute_sharpe_ratio, compute_sortino_ratio, compute_calmar_ratio,
    compute_skewness, compute_kurtosis, test_normality_jarque_bera
)
from models import run_stress_tests, kupiec_pof_test

print("="*50)
print("  AUDIT DE RISQUE INSTITUTIONNEL - PORTFOLIOSENSE")
print("="*50)

# 1. Génération des données
df_returns = generate_mock_returns()
portfolio = df_returns.mean(axis=1) # Portefeuille équipondéré

print("\n[1] METRIQUES DE DISTRIBUTION")
print("-" * 30)
print(f"Skewness         : {compute_skewness(portfolio):.2f}")
print(f"Kurtosis         : {compute_kurtosis(portfolio):.2f}")
jb_test = test_normality_jarque_bera(portfolio)
print(f"Test Jarque-Bera : P-Value = {jb_test['P-Value']:.4f} | Normal = {jb_test['Est Normal (> 5%)']}")

print("\n[2] RISQUES EXTREMES (TAIL RISK) - Confiance 95%")
print("-" * 30)
print(f"VaR Historique     : {compute_historical_var(portfolio):.2%}")
print(f"VaR Cornish-Fisher : {compute_cornish_fisher_var(portfolio):.2%}")
print(f"Expected Shortfall : {compute_cvar(portfolio, method='historical'):.2%}")

print("\n[3] VOLATILITE & CHUTES")
print("-" * 30)
print(f"Volatilité Annuelle  : {compute_annualized_volatility(portfolio):.2%}")
print(f"Semi-Volatilité      : {compute_downside_volatility(portfolio):.2%}")
print(f"Max Drawdown Global  : {compute_max_drawdown(portfolio):.2%}")
print(f"Ulcer Index          : {compute_ulcer_index(portfolio):.2f}")

print("\n[4] RATIOS DE PERFORMANCE AJUSTES AU RISQUE")
print("-" * 30)
print(f"Ratio de Sharpe  : {compute_sharpe_ratio(portfolio):.2f}")
print(f"Ratio de Sortino : {compute_sortino_ratio(portfolio):.2f}")
print(f"Ratio de Calmar  : {compute_calmar_ratio(portfolio):.2f}")

print("\n[5] STRESS TESTS HISTORIQUES")
print("-" * 30)
print(run_stress_tests(portfolio))

print("\n[6] BACKTEST STATISTIQUE (Kupiec POF)")
print("-" * 30)
var_hist = compute_historical_var(portfolio)
print(pd.DataFrame([kupiec_pof_test(portfolio, var_hist)]).T)

print("\n" + "="*50)
print("           AUDIT TERMINE AVEC SUCCES")
print("="*50)