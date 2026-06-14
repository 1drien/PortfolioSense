# backend/shap_explain.py
# Explicabilité SHAP des allocations — version backend portable
# Inspiré du shap_explainer.py de Membre 4, adapté pour l'API

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import shap
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from optimization.optimizer import max_sharpe, min_variance, risk_parity


STRATEGY_MAP = {
    "agressif":     max_sharpe,
    "conservateur": min_variance,
    "equilibre":    risk_parity,
}

FEATURE_LABELS = {
    "return":      "son rendement historique",
    "volatility":  "sa volatilité",
    "correlation": "sa corrélation avec le reste du portefeuille",
    "momentum":    "sa tendance récente (60 derniers jours)",
}


def build_asset_features(returns: pd.DataFrame) -> pd.DataFrame:
    """4 caractéristiques par actif : rendement, volatilité, corrélation, momentum."""
    feats = pd.DataFrame(index=returns.columns)
    feats["return"]      = returns.mean() * 252
    feats["volatility"]  = returns.std() * np.sqrt(252)
    feats["correlation"] = returns.corr().mean()
    feats["momentum"]    = returns.tail(60).mean() * 252
    return feats


def explain_portfolio(returns: pd.DataFrame, profil: str):
    """
    Pour un profil donné, retourne pour chaque actif :
    - son poids dans le portefeuille
    - les contributions SHAP de chaque feature
    - une explication en langage naturel
    """
    strategy_fn = STRATEGY_MAP.get(profil, risk_parity)

    # 1. Obtenir l'allocation actuelle
    result  = strategy_fn(returns)
    weights = pd.Series(result["weights"])

    # 2. Construire les features
    features = build_asset_features(returns)
    features = features.loc[weights.index]

    # 3. Entraîner un Random Forest features → poids
    scaler = StandardScaler()
    X = scaler.fit_transform(features.values)
    y = weights.values

    model = RandomForestRegressor(n_estimators=80, max_depth=5, random_state=42)
    model.fit(X, y)

    # 4. Calculer les SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

# 5. Générer l'explication en langage naturel pour chaque actif
    explanations = []
    median_features = features.median()

    for i, ticker in enumerate(features.index):
        if weights[ticker] < 0.005:
            continue
        contribs = dict(zip(features.columns, shap_values[i]))
        sorted_feats = sorted(contribs.items(), key=lambda x: abs(x[1]), reverse=True)
        feat_name, shap_val = sorted_feats[0]

        # Valeur réelle de la feature pour cet actif vs la médiane
        actual = features.loc[ticker, feat_name]
        is_high = actual > median_features[feat_name]

        # Direction réelle (basée sur la valeur de l'actif)
        direction = "élevé(e)" if is_high else "faible"
        # Impact (basé sur le signe SHAP)
        impact = "augmente" if shap_val > 0 else "réduit"

        sentence = (
            f"{FEATURE_LABELS[feat_name].capitalize()} {direction}, "
            f"ce qui {impact} son poids dans votre portefeuille."
        )

        explanations.append({
            "ticker": ticker,
            "weight_pct": round(weights[ticker] * 100, 2),
            "explanation": sentence,
            "shap_contributions": {
                FEATURE_LABELS[k]: round(float(v), 4)
                for k, v in contribs.items()
            },
        })

    explanations.sort(key=lambda x: -x["weight_pct"])
    return explanations