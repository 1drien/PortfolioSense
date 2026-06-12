# PortfolioSense — Version SaaS (React + FastAPI)

## Architecture
```
frontend/   → React + Vite + Recharts (port 5173)
backend/    → FastAPI + SQLite (port 8000)
            → réutilise optimization/, risk/, data/ existants
```

## Installation (une seule fois)

### Backend
```bash
pip install fastapi uvicorn hmmlearn scikit-learn
```

### Frontend
```bash
cd frontend
npm install
```

## Lancement (2 terminaux)

### Terminal 1 — Backend (DEPUIS LA RACINE du repo)
```bash
uvicorn backend.api:app --reload --port 8000
```

### Terminal 2 — Frontend
```bash
cd frontend
npm run dev
```

Ouvrir http://localhost:5173

## Fonctionnalités SaaS
- Inscription / connexion (sessions persistées en SQLite)
- Profil utilisateur sauvegardé entre les sessions
- Onboarding 3 questions → déduction du profil de risque
- Portefeuille optimisé en euros + frontière efficiente interactive
- Risque traduit en langage naturel + stress tests + validation Kupiec
- Détection de régime HMM en temps réel + alertes d'alignement
- Backtest walk-forward avec honnêteté scientifique (DeMiguel 2009)

## Fallback
Si problème React le jour J : `streamlit run main.py` (version Streamlit conservée)
