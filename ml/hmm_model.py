import os
import numpy as np
import pandas as pd
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA     = os.path.join(BASE_DIR, "data")

LABELS = ["Bear", "Lateral", "Bull"]
COLORS = ["#E24B4A", "#EF9F27", "#1D9E75"]

_CACHE = {"model": None, "scaler": None, "state_map": None}


def _build_features(port_ret, corr_series):
    feats = pd.DataFrame({
        "return":      port_ret,
        "volatility":  port_ret.rolling(20).std(),
        "momentum":    port_ret.rolling(5).mean(),
        "correlation": corr_series,
    }).dropna()
    return feats


def train_hmm(returns=None):
    if returns is None:
        returns = pd.read_csv(os.path.join(DATA, "returns_clean.csv"),
                              index_col="Date", parse_dates=True)
    port_returns = returns.mean(axis=1)
    corr_data = pd.read_csv(os.path.join(DATA, "rolling_corr_mean.csv"),
                            index_col="Date", parse_dates=True)
    features = _build_features(port_returns, corr_data["corr_moyenne"])
    scaler = StandardScaler()
    X = scaler.fit_transform(features)
    best_score, best_model = -np.inf, None
    for seed in range(20):
        m = hmm.GaussianHMM(n_components=3, covariance_type="full",
                            n_iter=2000, random_state=seed, tol=1e-5)
        m.fit(X)
        score = m.score(X)
        if score > best_score:
            best_score, best_model = score, m
    states = best_model.predict(X)
    port_trim = port_returns[features.index]
    state_means = {s: port_trim[states == s].mean() for s in range(3)}
    order = sorted(state_means, key=state_means.get)
    state_map = {state_idx: (LABELS[rank], COLORS[rank])
                 for rank, state_idx in enumerate(order)}
    _CACHE["model"] = best_model
    _CACHE["scaler"] = scaler
    _CACHE["state_map"] = state_map
    regime_series = pd.Series([state_map[s][0] for s in states],
                              index=features.index, name="regime")
    return regime_series, port_trim


def detect_regime(returns_window):
    if _CACHE["model"] is None:
        train_hmm()
    model     = _CACHE["model"]
    scaler    = _CACHE["scaler"]
    state_map = _CACHE["state_map"]
    port_ret = returns_window.mean(axis=1)
    corr = pd.read_csv(os.path.join(DATA, "rolling_corr_mean.csv"),
                       index_col="Date", parse_dates=True)
    feats = _build_features(port_ret, corr["corr_moyenne"])
    if len(feats) < 30:
        return "Lateral"
    X_new = scaler.transform(feats)
    last_state = model.predict(X_new)[-1]
    return state_map[last_state][0]


if __name__ == "__main__":
    returns = pd.read_csv(os.path.join(DATA, "returns_clean.csv"),
                          index_col="Date", parse_dates=True)
    regimes, port_trim = train_hmm(returns)
    print(f"Donnees : {returns.shape[0]} jours | {returns.shape[1]} actifs")
    print(f"Regime actuel : {regimes.iloc[-1]} ({regimes.index[-1].date()})")
    for label in LABELS:
        mask = regimes == label
        r = port_trim[mask]
        if mask.sum() > 0:
            print(f"{label:8s} | Rend. ann. {r.mean()*252:+.1%} | {mask.sum()} jours ({mask.mean():.0%})")
