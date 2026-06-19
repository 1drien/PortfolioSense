# PortfolioSense

**Démocratiser la gestion quantitative de portefeuille**

PortfolioSense est un outil d'aide à la décision en gestion de portefeuille destiné à l'investisseur particulier averti. Il combine l'optimisation quantitative (Markowitz, Ledoit-Wolf, Risk Parity, Black-Litterman), une analyse de risque de niveau professionnel (VaR, CVaR, stress tests) et une couche d'intelligence artificielle (détection de régimes de marché par HMM, explicabilité SHAP), le tout exposé via une interface web pédagogique.

Projet de Fin d'Études — ING3 Fintech, CY Tech (2025–2026).

---

## Architecture

Le projet est organisé en cinq modules :

| Module                   | Rôle                                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| `data/`                  | Collecte, nettoyage et validation des données de marché (source unique : `returns_clean.csv`)   |
| `optimization/`          | Calcul des allocations : Max Sharpe, Min Variance, Risk Parity, Black-Litterman                 |
| `risk/`                  | Mesures de risque : VaR, CVaR, drawdown, ratios, stress tests, validation (Kupiec, Jarque-Bera) |
| `ml/`                    | Détection de régimes de marché (HMM) et explicabilité des décisions (SHAP)                      |
| `backend/` + `frontend/` | Interface applicative : API FastAPI + dashboard React                                           |

L'architecture est en cascade : `data/` produit un jeu de données unique, consommé par `optimization/`, `risk/` et `ml/`, dont les résultats sont exposés à l'utilisateur via l'interface.

---

## Stack technique

- **Backend** : Python, FastAPI, SQLite (port 8000)
- **Frontend** : React, Vite, Recharts (port 5173)
- **Quantitatif** : NumPy, pandas, SciPy, PyPortfolioOpt, scikit-learn, hmmlearn, SHAP
- **Données** : yfinance (Yahoo Finance)

---

## Installation

### Prérequis

- Python 3.10+
- Node.js 18+

### 1. Cloner le dépôt

```bash
git clone https://github.com/1drien/PortfolioSense.git
cd PortfolioSense
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Installer les dépendances du frontend

```bash
cd frontend
npm install
cd ..
```

---

## Lancement

Le projet nécessite **deux terminaux** : un pour le backend, un pour le frontend.

### Terminal 1 — Backend (depuis la racine du repo)

```bash
uvicorn backend.api:app --reload --port 8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Puis ouvrir **http://localhost:5173** dans le navigateur.

> **Note** : au premier lancement, le module `data/` télécharge les données de marché via yfinance. Une connexion internet est requise.

---

## Utilisation

1. **Créer un compte** sur la page d'inscription.
2. **Répondre aux 3 questions d'onboarding** (capital, horizon, perte maximale tolérée) — le profil de risque est déduit automatiquement.
3. **Consulter l'allocation optimale**, les métriques de risque, le régime de marché détecté et les résultats de backtest.
4. **Saisir un portefeuille réel** sur la page Rééquilibrage pour obtenir les ajustements recommandés.

---

## Tests

La suite de tests unitaires (module `data/`) s'exécute via :

```bash
pytest
```

---

## Structure du dépôt

```
PortfolioSense/
├── config.py              # Paramètres partagés (tickers, fenêtres, taux sans risque)
├── data/                  # Pipeline de données + stress tests + attribution
├── optimization/          # Optimiseur + backtest + frontière efficiente
├── risk/                  # Métriques de risque + validation statistique
├── ml/                    # HMM + allocation conditionnelle + SHAP
├── backend/               # API FastAPI + base SQLite
├── frontend/              # Dashboard React
├── tests/                 # Tests unitaires
└── requirements.txt
```

---

## Équipe

- **Ayman El Kili** — module `risk/`
- **Anasthasia Daunes** — module `data/`
- **Adrien Morlet** — module `optimization/` + dashboard
- **Kiane Lachkar** — module `ml/`

Encadrants : Bruno Iksil, Julien Savry, Houcine Senoussi.

---

## Avertissement

PortfolioSense est un outil d'aide à la décision à vocation pédagogique. Il n'exécute aucun ordre et ne constitue pas un conseil en investissement. Les performances passées ne préjugent pas des performances futures.
