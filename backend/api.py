# backend/api.py
# API REST PortfolioSense — expose les modules Python au frontend React
# Lancer DEPUIS LA RACINE du repo : uvicorn backend.api:app --reload --port 8000

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from functools import lru_cache
from backend.shap_explain import explain_portfolio
from backend.database import (
    init_db, create_user, verify_user, create_session,
    get_user_from_token, get_profile, update_profile,
)

from optimization.optimizer import (
    get_strategy_from_profile, weights_to_euros,
    max_sharpe, min_variance, risk_parity, efficient_frontier_curve,
)
from risk.metrics import (
    compute_historical_var, compute_cvar, compute_max_drawdown,
    compute_annualized_volatility, compute_cornish_fisher_var,
    compute_ulcer_index, compute_sharpe_ratio, compute_sortino_ratio, 
    compute_calmar_ratio, compute_drawdown_series,
    compute_skewness, compute_kurtosis, test_normality_jarque_bera
)
from risk.models import (
    run_stress_tests, kupiec_pof_test
)
from fastapi.responses import Response
from backend.pdf_report import build_pdf
app = FastAPI(title="PortfolioSense API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "returns_clean.csv")


@lru_cache(maxsize=1)
def load_returns():
    return pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)


def auth(authorization: str = "") -> str:
    """Vérifie le token Bearer et retourne le user_id."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Non authentifié")
    user_id = get_user_from_token(authorization[7:])
    if not user_id:
        raise HTTPException(401, "Session invalide")
    return user_id


# ─── AUTH ─────────────────────────────────────────────────────────

class Credentials(BaseModel):
    email: str
    password: str


@app.post("/api/register")
def register(creds: Credentials):
    if len(creds.password) < 6:
        raise HTTPException(400, "Mot de passe trop court (6 caractères min)")
    user_id = create_user(creds.email, creds.password)
    if not user_id:
        raise HTTPException(409, "Cet email est déjà utilisé")
    token = create_session(user_id)
    return {"token": token}


@app.post("/api/login")
def login(creds: Credentials):
    user_id = verify_user(creds.email, creds.password)
    if not user_id:
        raise HTTPException(401, "Email ou mot de passe incorrect")
    token = create_session(user_id)
    return {"token": token}


# ─── PROFIL ───────────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    capital: float
    horizon: int
    perte_max: int


def deduce_profil(perte_max: int) -> str:
    if perte_max <= 10:
        return "conservateur"
    if perte_max <= 25:
        return "equilibre"
    return "agressif"


@app.get("/api/profile")
def read_profile(authorization: str = Header("")):
    user_id = auth(authorization)
    return get_profile(user_id)


@app.post("/api/profile")
def save_profile(body: ProfileUpdate, authorization: str = Header("")):
    user_id = auth(authorization)
    profil = deduce_profil(body.perte_max)
    update_profile(user_id, body.capital, body.horizon, body.perte_max, profil)
    return {"profil": profil}


# ─── PORTEFEUILLE ─────────────────────────────────────────────────

@app.get("/api/portfolio")
def portfolio(authorization: str = Header("")):
    user_id = auth(authorization)
    prof = get_profile(user_id)
    returns = load_returns()

    result = get_strategy_from_profile(prof["profil"], returns)
    weights = result["weights"]
    euros = weights_to_euros(weights, prof["capital"])

    allocation = [
        {"ticker": t, "euros": e, "pct": round(weights[t] * 100, 1)}
        for t, e in sorted(euros.items(), key=lambda x: -x[1])
    ]
    return {
        "profil": prof["profil"],
        "capital": prof["capital"],
        "metrics": result["metrics"],
        "gain_espere": round(prof["capital"] * result["metrics"]["return"]),
        "allocation": allocation,
    }


@app.get("/api/frontier")
def frontier(authorization: str = Header("")):
    auth(authorization)
    returns = load_returns()
    curve = efficient_frontier_curve(returns, n_portfolios=800)

    points = curve.round(4).to_dict(orient="records")
    strategies = {}
    for name, fn in [("max_sharpe", max_sharpe),
                     ("min_variance", min_variance),
                     ("risk_parity", risk_parity)]:
        m = fn(returns)["metrics"]
        strategies[name] = m
    return {"cloud": points, "strategies": strategies}


# ─── RISQUE ───────────────────────────────────────────────────────

@app.get("/api/risk")
def risk_metrics(authorization: str = Header("")):
    user_id = auth(authorization)
    prof = get_profile(user_id)
    returns = load_returns()
 
    result = get_strategy_from_profile(prof["profil"], returns)
    weights = pd.Series(result["weights"])
    pf = returns[weights.index] @ weights
 
    cap = prof["capital"]
 
    # ── Métriques existantes ──────────────────────────────────────
    var_h  = float(compute_historical_var(pf))
    cvar   = float(compute_cvar(pf))
    max_dd = float(compute_max_drawdown(pf))
 
    stress = run_stress_tests(pf)
    stress_list = [
        {
            "crise": idx,
            "rendement": row["Rendement Cumulé"],
            "drawdown": row["Max Drawdown"],
            "impact_eur": round(float(row["Rendement Cumulé"].strip("%")) / 100 * cap),
        }
        for idx, row in stress.iterrows()
    ]
 
    kupiec = kupiec_pof_test(pf, var_h)
 
    # ── Nouvelles métriques ───────────────────────────────────────
 
    # VaR Cornish-Fisher (95 % et 99 %)
    var_cf_95 = float(compute_cornish_fisher_var(pf, confidence=0.95))
    var_cf_99 = float(compute_cornish_fisher_var(pf, confidence=0.99))
 
    # Ulcer Index
    ulcer = float(compute_ulcer_index(pf))
 
    # Ratios
    sortino = float(compute_sortino_ratio(pf))
    calmar  = float(compute_calmar_ratio(pf))
    sharpe  = float(compute_sharpe_ratio(pf))
 
    # Distribution
    skew_val = float(compute_skewness(pf))
    kurt_val = float(compute_kurtosis(pf))
    jb       = test_normality_jarque_bera(pf)
 
    # Série temporelle des drawdowns — 1 point tous les 3 jours
    dd_series = compute_drawdown_series(pf)
    step = 3
    drawdown_series = [
        {
            "date": str(d.date()),
            "drawdown": round(float(v), 6),
        }
        for d, v in dd_series.iloc[::step].items()
    ]
 
    return {
        # ── Existant ──────────────────────────────────────────────
        "var_pct":        round(var_h * 100, 2),
        "var_eur":        round(abs(var_h) * cap),
        "cvar_pct":       round(cvar * 100, 2),
        "cvar_eur":       round(abs(cvar) * cap),
        "max_dd_pct":     round(max_dd * 100, 2),
        "max_dd_eur":     round(abs(max_dd) * cap),
        "volatilite_pct": round(float(compute_annualized_volatility(pf)) * 100, 1),
        "stress_tests":   stress_list,
        "kupiec_valide":  bool(kupiec.get("Modèle Valide (> 5%)", False)),
        "kupiec_pvalue":  kupiec.get("P-Value Kupiec"),
 
        # ── Nouveau — Tail Risk ───────────────────────────────────
        "var_cornish_fisher_95_pct": round(var_cf_95 * 100, 2),
        "var_cornish_fisher_95_eur": round(abs(var_cf_95) * cap),
        "var_cornish_fisher_99_pct": round(var_cf_99 * 100, 2),
        "var_cornish_fisher_99_eur": round(abs(var_cf_99) * cap),
 
        # ── Nouveau — Drawdowns ───────────────────────────────────
        "ulcer_index":     round(ulcer, 4),
        "drawdown_series": drawdown_series,
 
        # ── Nouveau — Ratios de performance ──────────────────────
        "sharpe_ratio":  round(sharpe, 4),
        "sortino_ratio": round(sortino, 4),
        "calmar_ratio":  round(calmar, 4),
 
        # ── Nouveau — Distribution ────────────────────────────────
        "skewness": round(skew_val, 4),
        "kurtosis": round(kurt_val, 4),
        "jarque_bera": {
            "stat":      round(jb["Statistique JB"], 4),
            "p_value":   round(jb["P-Value"], 6),
            "is_normal": jb["Est Normal (> 5%)"],
        },
    }


# ─── RÉGIMES DE MARCHÉ (HMM) ──────────────────────────────────────

@lru_cache(maxsize=1)
def train_hmm():
    from hmmlearn.hmm import GaussianHMM
    from sklearn.preprocessing import StandardScaler

    returns = load_returns()
    market = returns.mean(axis=1)

    # Chargement corrélation glissante (Membre 2)
    corr_path = os.path.join(os.path.dirname(__file__), "..", "data", "rolling_corr_mean.csv")
    corr_data = pd.read_csv(corr_path, index_col="Date", parse_dates=True)

    # 4 features au lieu de 3
    feats = pd.DataFrame(index=market.index)
    feats["ret"]      = market
    feats["vol_20d"]  = market.rolling(20).std()
    feats["ret_5d"]   = market.rolling(5).sum()
    feats["corr_60d"] = corr_data["corr_moyenne"]
    feats = feats.dropna()

    scaler = StandardScaler()
    X = scaler.fit_transform(feats.values)

    # 20 initialisations pour trouver le meilleur modèle
    best_model, best_score = None, -np.inf
    for seed in range(20):
        m = GaussianHMM(n_components=3, covariance_type="full",
                        n_iter=2000, random_state=seed, tol=1e-5)
        m.fit(X)
        if m.score(X) > best_score:
            best_score, best_model = m.score(X), m

    states = best_model.predict(X)
    state_ret = {s: float(market.loc[feats.index][states == s].mean())
                 for s in range(3)}
    ordered = sorted(state_ret, key=state_ret.get)
    labels = {ordered[0]: "bear", ordered[1]: "lateral", ordered[2]: "bull"}

    regimes = pd.Series([labels[s] for s in states], index=feats.index)
    cumulative = (1 + market.loc[feats.index]).cumprod()
    return regimes, cumulative

REGIME_META = {
    "bull":    {"label": "Marché haussier", "emoji": "🟢",
                "strategie": "Maximum Sharpe", "profil": "agressif",
                "explication": "Les marchés sont confiants : rendements positifs, volatilité faible. C'est le moment de viser la performance."},
    "bear":    {"label": "Marché en crise", "emoji": "🔴",
                "strategie": "Minimum Variance", "profil": "conservateur",
                "explication": "Turbulences détectées : les actifs chutent et se corrèlent. Il faut se replier sur les valeurs défensives."},
    "lateral": {"label": "Marché indécis", "emoji": "🟡",
                "strategie": "Risk Parity", "profil": "equilibre",
                "explication": "Le marché hésite, sans tendance claire. La meilleure défense est un risque parfaitement équilibré."},
}


@app.get("/api/regimes")
def regimes(authorization: str = Header("")):
    user_id = auth(authorization)
    prof = get_profile(user_id)
    reg, cumulative = train_hmm()

    current = reg.iloc[-1]
    meta = REGIME_META[current]

    # Sous-échantillonner l'historique pour le frontend (1 point / 3 jours)
    step = 3
    history = [
        {"date": str(d.date()), "value": round(float(v), 4),
         "regime": str(reg.loc[d])}
        for d, v in cumulative.iloc[::step].items()
    ]

    counts = reg.value_counts(normalize=True)
    repartition = {k: round(float(v) * 100) for k, v in counts.items()}

    return {
        "regime_actuel": current,
        "meta": meta,
        "aligne": prof["profil"] == meta["profil"],
        "profil_user": prof["profil"],
        "history": history,
        "repartition": repartition,
    }


# ─── PERFORMANCE (BACKTEST) ───────────────────────────────────────

@app.get("/api/backtest")
def backtest(authorization: str = Header("")):
    user_id = auth(authorization)
    prof = get_profile(user_id)
    path = os.path.join(os.path.dirname(__file__), "..", "data", "backtest_results.csv")

    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0)
    else:
        from optimization.backtest import compare_backtests
        df = compare_backtests(load_returns())
        df.to_csv(path)

    cap = prof["capital"]
    rows = []
    for name, r in df.iterrows():
        rows.append({
            "strategie": name.replace("_", " ").title(),
            "rendement_ann": round(r["return_ann"] * 100, 1),
            "sharpe": round(r["sharpe"], 2),
            "max_dd": round(r["max_drawdown"] * 100, 1),
            "valeur_finale": round((1 + r["cum_return"]) * cap),
        })
    return {"capital": cap, "results": rows}

@app.get("/api/explain")
def explain(authorization: str = Header("")):
    user_id = auth(authorization)
    prof    = get_profile(user_id)
    returns = load_returns()
    return {"explanations": explain_portfolio(returns, prof["profil"])}

@app.get("/api/report")
def report(authorization: str = Header("")):
    user_id = auth(authorization)
    prof = get_profile(user_id)
    returns = load_returns()

    # Réutiliser la logique des endpoints existants
    p = portfolio(authorization)
    r = risk_metrics(authorization)
    e = explain(authorization)["explanations"]

    pdf_bytes = build_pdf(prof, p, r, e)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=PortfolioSense_Rapport.pdf"},
    )

class CurrentPositions(BaseModel):
    positions: dict   # {"AAPL": 3000, "TSLA": 500} — montants en euros


@app.post("/api/compare")
def compare(body: CurrentPositions, authorization: str = Header("")):
    user_id = auth(authorization)
    prof = get_profile(user_id)
    returns = load_returns()

    result = get_strategy_from_profile(prof["profil"], returns)
    optimal_weights = result["weights"]

    total = sum(body.positions.values())
    if total <= 0:
        raise HTTPException(400, "Portefeuille vide")

    # Normaliser les tickers (évite les doublons aapl/AAPL)
    positions = {t.upper().strip(): v for t, v in body.positions.items()}

    rows = []
    all_tickers = set(positions) | {
        t for t, w in optimal_weights.items() if w > 0.005
    }
    for t in sorted(all_tickers):
        current_eur = positions.get(t, 0)
        current_pct = current_eur / total * 100
        optimal_pct = optimal_weights.get(t, 0) * 100
        optimal_eur = optimal_weights.get(t, 0) * total
        ecart_eur = round(optimal_eur - current_eur)

        if abs(ecart_eur) < total * 0.02:        # < 2% d'écart = OK
            statut, action = "ok", "Conserver"
        elif ecart_eur > 0:
            statut, action = "sous", f"Acheter {ecart_eur:,} €".replace(",", " ")
        else:
            statut, action = "sur", f"Vendre {abs(ecart_eur):,} €".replace(",", " ")

        rows.append({
            "ticker": t,
            "current_pct": round(current_pct, 1),
            "optimal_pct": round(optimal_pct, 1),
            "ecart_eur": ecart_eur,
            "statut": statut,
            "action": action,
        })

    rows.sort(key=lambda x: -abs(x["ecart_eur"]))
    return {"total": total, "profil": prof["profil"], "comparison": rows}

@app.post("/api/refresh")
def refresh_data(authorization: str = Header("")):
    auth(authorization)
    try:
        import yfinance as yf

        returns = load_returns()
        tickers = list(returns.columns)
        last_date = returns.index[-1].date()

        # Télécharger depuis la dernière date connue jusqu'à aujourd'hui
        raw = yf.download(
            tickers,
            start=str(last_date),
            auto_adjust=True,
            progress=False,
        )["Close"]

        if raw.empty or len(raw) < 2:
            return {
                "status": "already_up_to_date",
                "last_date": str(last_date),
                "message": "Les données sont déjà à jour.",
            }

        # Calculer les nouveaux log-rendements
        new_returns = np.log(raw / raw.shift(1)).dropna()
        new_returns = new_returns[returns.columns]  # même ordre de colonnes

        # Fusionner sans doublons et sauvegarder
        combined = pd.concat([returns, new_returns])
        combined = combined[~combined.index.duplicated(keep="last")]
        combined.to_csv(DATA_PATH)

        # Invalider les caches pour forcer le recalcul
        load_returns.cache_clear()
        train_hmm.cache_clear()

        n_new = len(combined) - len(returns)
        return {
            "status": "updated",
            "last_date": str(combined.index[-1].date()),
            "new_days": n_new,
            "message": f"{n_new} nouveaux jours de marché intégrés. "
                       f"Régimes et allocations recalculés.",
        }

    except Exception as e:
        # Fallback : on continue avec les données locales
        return {
            "status": "offline",
            "last_date": str(load_returns().index[-1].date()),
            "message": "Connexion aux marchés indisponible — "
                       "les données locales restent utilisées.",
        }

class BLViews(BaseModel):
    views: dict          # {"NVDA": 0.30, "PFE": -0.05}
    confidences: dict    # {"NVDA": 0.8, "PFE": 0.6}


@app.post("/api/black-litterman")
def black_litterman_endpoint(body: BLViews, authorization: str = Header("")):
    user_id = auth(authorization)
    prof = get_profile(user_id)
    returns = load_returns()

    if not body.views:
        raise HTTPException(400, "Ajoutez au moins une vue")

    # Aligner l'ordre views/confidences
    tickers = list(body.views.keys())
    views = {t: body.views[t] for t in tickers}
    confidences = [body.confidences.get(t, 0.5) for t in tickers]

    from optimization.optimizer import black_litterman
    result = black_litterman(returns, views=views, confidences=confidences)

    cap = prof["capital"]
    allocation = [
        {"ticker": t, "euros": round(w * cap, 2), "pct": round(w * 100, 1)}
        for t, w in sorted(result["weights"].items(), key=lambda x: -x[1])
        if w > 0.001
    ]
    return {"metrics": result["metrics"], "allocation": allocation}

@app.get("/api/regimes/details")
def regimes_details(authorization: str = Header("")):
    auth(authorization)
    reg, cumulative = train_hmm()
    returns = load_returns()
    market = returns.mean(axis=1)

    # Stats par régime
    stats = {}
    for regime in ["bull", "bear", "lateral"]:
        mask = reg == regime
        r = market.loc[reg.index][mask.values]
        stats[regime] = {
            "return_ann":  round(float(r.mean() * 252) * 100, 1),
            "vol_ann":     round(float(r.std() * np.sqrt(252)) * 100, 1),
            "n_days":      int(mask.sum()),
            "pct":         round(float(mask.mean()) * 100, 1),
        }

    # Matrice de transition
    from hmmlearn.hmm import GaussianHMM
    from sklearn.preprocessing import StandardScaler
    corr_path = os.path.join(os.path.dirname(__file__), "..", "data", "rolling_corr_mean.csv")
    corr_data = pd.read_csv(corr_path, index_col="Date", parse_dates=True)
    feats = pd.DataFrame(index=market.index)
    feats["ret"]      = market
    feats["vol_20d"]  = market.rolling(20).std()
    feats["ret_5d"]   = market.rolling(5).sum()
    feats["corr_60d"] = corr_data["corr_moyenne"]
    feats = feats.dropna()
    scaler = StandardScaler()
    X = scaler.fit_transform(feats.values)
    best_model, best_score = None, -np.inf
    for seed in range(20):
        m = GaussianHMM(n_components=3, covariance_type="full",
                        n_iter=2000, random_state=seed, tol=1e-5)
        m.fit(X)
        if m.score(X) > best_score:
            best_score, best_model = m.score(X), m
    states = best_model.predict(X)
    state_ret = {s: float(market.loc[feats.index][states == s].mean())
                 for s in range(3)}
    ordered = sorted(state_ret, key=state_ret.get)
    label_map = {ordered[0]: "bear", ordered[1]: "lateral", ordered[2]: "bull"}
    trans = best_model.transmat_
    transition_matrix = {}
    for i in range(3):
        from_label = label_map[i]
        transition_matrix[from_label] = {}
        for j in range(3):
            to_label = label_map[j]
            transition_matrix[from_label][to_label] = round(float(trans[i][j]), 3)

    # Comparaison HMM vs naïf
    naive = corr_data["regime_naif"].str.lower()
    common = naive.index.intersection(reg.index)
    accord = float((naive.loc[common] == reg.loc[common]).mean())

    return {
        "stats":             stats,
        "transition_matrix": transition_matrix,
        "hmm_vs_naive":      round(accord * 100, 1),
    }

@app.get("/api/health")
def health():
    return {"status": "ok"}
