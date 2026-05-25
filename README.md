# PortfolioSense

Dashboard d'aide à la décision en gestion de portefeuille d'actifs.

## Architecture

PortfolioSense/
├── data/                   Pipeline de données (yfinance, nettoyage, rendements)
├── optimization/           Markowitz, Black-Litterman, Risk Parity
├── risk/                   VaR, CVaR, stress tests, backtesting
├── ml/                     HMM régimes de marché, SHAP explicabilité
├── dashboard/              Pages Streamlit (5 pages)
├── utils/                  Fonctions partagées
├── config.py               Paramètres centralisés — ne pas modifier sans accord
├── main.py                 Point d'entrée Streamlit
└── requirements.txt        Dépendances

## Format de données standard (obligatoire pour tous les modules)

returns : pd.DataFrame
  index   -> DatetimeIndex (YYYY-MM-DD)
  colonnes -> tickers (ex: AAPL, MSFT ...)
  valeurs  -> float, log-rendements journaliers

## Règles Git

- main est protégée : merge uniquement via Pull Request
- Une branche par membre (voir ci-dessous)
- Préfixes commits : feat: fix: data: doc: test:
- Ne jamais push directement sur main

## Branches

feat/data          -> Membre 2 (Data Engineering)
feat/optimization  -> Adrien  (Optimisation)
feat/risk          -> Membre 3 (Risk Analysis)
feat/ml            -> Membre 4 (IA / ML)
feat/dashboard     -> Membre 5 (Dashboard)

## Installation

git clone https://github.com/1drien/PortfolioSense.git
cd PortfolioSense
pip install -r requirements.txt
streamlit run main.py
