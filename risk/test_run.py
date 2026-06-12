import pandas as pd
import warnings
import os

# Suppression des warnings pandas pour un affichage propre
warnings.filterwarnings("ignore")

# Importation depuis votre architecture modulaire
from metrics import (
    compute_historical_var, compute_cornish_fisher_var, compute_cvar,
    compute_annualized_volatility, compute_downside_volatility,
    compute_max_drawdown, compute_ulcer_index,
    compute_sharpe_ratio, compute_sortino_ratio, compute_calmar_ratio,
    compute_skewness, compute_kurtosis, test_normality_jarque_bera
)
from models import run_stress_tests, kupiec_pof_test

print("="*60)
print("  AUDIT DE RISQUE INSTITUTIONNEL - PORTFOLIOSENSE")
print("="*60)

# ─── CHARGEMENT STRICT DES VRAIES DONNÉES ───────────────────────
# On pointe directement vers le CSV généré par le Membre 2 (Dossier data/)
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "returns_clean.csv")

try:
    # parse_dates=True convertit automatiquement la colonne de dates en DatetimeIndex
    df_returns = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    print(f"[INFO] Vraies données chargées avec succès !")
    print(f"[INFO] {df_returns.shape[1]} actifs analysés du {df_returns.index[0].date()} au {df_returns.index[-1].date()}\n")
except FileNotFoundError:
    print(f"[ERREUR CRITIQUE] Le fichier {DATA_PATH} est introuvable.")
    print("Veuillez vous assurer d'avoir fait un 'git pull' pour récupérer les données du Membre 2.")
    exit()

# ─── CRÉATION DU PORTEFEUILLE DE TEST ───────────────────────────
# Pour tester, on simule un portefeuille équipondéré (Equal-Weight)
portfolio = df_returns.mean(axis=1)

# ─── APPLICATION DES MÉTRIQUES ──────────────────────────────────
print("\n[1] METRIQUES DE DISTRIBUTION")
print("-" * 40)
print(f"Skewness         : {compute_skewness(portfolio):.2f}")
print(f"Kurtosis         : {compute_kurtosis(portfolio):.2f}")
jb_test = test_normality_jarque_bera(portfolio)
print(f"Test Jarque-Bera : P-Value = {jb_test['P-Value']:.4f} | Normal = {jb_test['Est Normal (> 5%)']}")

print("\n[2] RISQUES EXTREMES (TAIL RISK) - Confiance 95%")
print("-" * 40)
print(f"VaR Historique     : {compute_historical_var(portfolio):.2%}")
print(f"VaR Cornish-Fisher : {compute_cornish_fisher_var(portfolio):.2%}")
print(f"Expected Shortfall : {compute_cvar(portfolio, method='historical'):.2%}")

print("\n[3] VOLATILITE & CHUTES")
print("-" * 40)
print(f"Volatilité Annuelle  : {compute_annualized_volatility(portfolio):.2%}")
print(f"Semi-Volatilité      : {compute_downside_volatility(portfolio):.2%}")
print(f"Max Drawdown Global  : {compute_max_drawdown(portfolio):.2%}")
print(f"Ulcer Index          : {compute_ulcer_index(portfolio):.2f}")

print("\n[4] RATIOS DE PERFORMANCE AJUSTES AU RISQUE")
print("-" * 40)
print(f"Ratio de Sharpe  : {compute_sharpe_ratio(portfolio):.2f}")
print(f"Ratio de Sortino : {compute_sortino_ratio(portfolio):.2f}")
print(f"Ratio de Calmar  : {compute_calmar_ratio(portfolio):.2f}")

print("\n[5] STRESS TESTS HISTORIQUES")
print("-" * 40)
print(run_stress_tests(portfolio))

print("\n[6] BACKTEST STATISTIQUE (Kupiec POF)")
print("-" * 40)
var_hist = compute_historical_var(portfolio)
print(pd.DataFrame([kupiec_pof_test(portfolio, var_hist)]).T)

print("\n" + "="*60)
print("           AUDIT TERMINE AVEC SUCCES")
print("="*60)