# ml/shap_explainer.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import sys
sys.path.insert(0, 'c:/Users/lachk/OneDrive/Bureau/CY/ing3/PFE')

from optimization.optimizer import max_sharpe, min_variance, risk_parity

# ── 1. Chargement des données ─────────────────────────────────────────────────
returns = pd.read_csv(
    "c:/Users/lachk/OneDrive/Bureau/CY/ing3/PFE/data/returns_clean.csv",
    index_col="Date",
    parse_dates=True
)
regimes = pd.read_csv(
    "c:/Users/lachk/OneDrive/Bureau/CY/ing3/PFE/data/regimes.csv",
    index_col="Date",
    parse_dates=True
)

# ── 2. Construction des features par actif ───────────────────────────────────
def build_asset_features(returns):
    """
    Pour chaque actif, calcule 4 caractéristiques :
    - rendement moyen annualisé
    - volatilité annualisée
    - corrélation moyenne aux autres actifs
    - momentum (rendement des 60 derniers jours)
    """
    features = pd.DataFrame(index=returns.columns)
    features["return"]      = returns.mean() * 252
    features["volatility"]  = returns.std() * np.sqrt(252)
    features["correlation"] = returns.corr().mean()
    features["momentum"]    = returns.tail(60).mean() * 252
    return features

# ── 3. Génération des données d'entraînement ─────────────────────────────────
def generate_training_data(returns, n_windows=50):
    """
    Génère des paires (features actif, poids alloué) sur des fenêtres
    historiques glissantes. C'est ce dont le Random Forest a besoin
    pour apprendre la relation features → poids.
    """
    STRATEGY_MAP = {
        "Bull":    max_sharpe,
        "Lateral": risk_parity,
        "Bear":    min_variance,
    }

    all_features = []
    all_weights  = []
    all_regimes  = []

    window_size = 252  # 1 an de données par fenêtre
    step        = len(returns) // n_windows

    print(f"Génération de {n_windows} fenêtres d'entraînement...")

    for i in range(n_windows):
        start = i * step
        end   = start + window_size
        if end > len(returns):
            break

        window = returns.iloc[start:end]

        # Régime majoritaire sur cette fenêtre
        window_dates  = regimes.index[regimes.index >= window.index[0]]
        window_dates  = window_dates[window_dates <= window.index[-1]]
        if len(window_dates) == 0:
            continue
        regime = regimes.loc[window_dates, "regime"].mode()[0]

        # Calcul des poids via la stratégie correspondante
        try:
            strategy_fn = STRATEGY_MAP[regime]
            result      = strategy_fn(window)
            weights     = pd.Series(result["weights"])

            # Features de chaque actif sur cette fenêtre
            feat = build_asset_features(window)

            for ticker in weights.index:
                if ticker in feat.index:
                    row = feat.loc[ticker].to_dict()
                    row["weight"] = weights[ticker]
                    row["ticker"] = ticker
                    row["regime"] = regime
                    all_features.append(row)
                    all_weights.append(weights[ticker])
                    all_regimes.append(regime)

        except Exception as e:
            continue

    df = pd.DataFrame(all_features)
    print(f"Données générées : {len(df)} observations")
    return df

# ── 4. Entraînement du Random Forest ─────────────────────────────────────────
def train_proxy_model(df):
    """
    Entraîne un Random Forest qui prédit le poids d'allocation
    d'un actif à partir de ses caractéristiques.
    """
    feature_cols = ["return", "volatility", "correlation", "momentum"]
    X = df[feature_cols].values
    y = df["weight"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=5,
        random_state=42
    )
    model.fit(X_scaled, y)

    print(f"Random Forest entraîné — R² : {model.score(X_scaled, y):.3f}")
    return model, scaler, feature_cols

# ── 5. Explication SHAP ───────────────────────────────────────────────────────
def explain_allocation(returns, regime, model, scaler, feature_cols):
    """
    Explique l'allocation courante via SHAP.
    Produit un graphique waterfall pour chaque actif.
    """
    # Features actuelles de chaque actif
    feat = build_asset_features(returns)
    X    = feat[feature_cols].values
    X_scaled = scaler.transform(X)

    # Explainer SHAP
    explainer  = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scaled)

    # DataFrame des contributions SHAP
    df_shap = pd.DataFrame(
        shap_values,
        index=feat.index,
        columns=feature_cols
    )
    df_shap["total_shap"] = df_shap.sum(axis=1)
    df_shap["predicted_weight"] = model.predict(X_scaled)

    return df_shap, explainer, X_scaled, feat

# ── 6. Graphiques ─────────────────────────────────────────────────────────────
def plot_shap_summary(df_shap, regime, feature_cols):
    """
    Graphique 1 : importance des features pour toutes les décisions
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    # Importance moyenne absolue de chaque feature
    importance = df_shap[feature_cols].abs().mean().sort_values(ascending=True)

    colors = ["#378ADD", "#1D9E75", "#EF9F27", "#E24B4A"]
    bars = ax.barh(importance.index, importance.values,
                   color=colors[:len(importance)], alpha=0.85)

    ax.set_xlabel("Contribution SHAP moyenne (|valeur|)", fontsize=11)
    ax.set_title(
        f"Importance des features dans les décisions d'allocation\n"
        f"Régime actuel : {regime}",
        fontsize=13, fontweight="bold", pad=12
    )
    ax.grid(axis="x", alpha=0.3)

    # Labels sur les barres
    for bar, val in zip(bars, importance.values):
        ax.text(val + 0.0001, bar.get_y() + bar.get_height()/2,
                f"{val:.4f}", va="center", fontsize=10)

    plt.tight_layout()
    path = "c:/Users/lachk/OneDrive/Bureau/CY/ing3/PFE/shap_importance.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Graphique sauvegardé → shap_importance.png")


def plot_shap_top_assets(df_shap, regime, feature_cols, top_n=5):
    """
    Graphique 2 : décomposition SHAP pour les top actifs
    """
    top_assets = df_shap.nlargest(top_n, "predicted_weight")

    fig, axes = plt.subplots(1, top_n, figsize=(16, 5), sharey=True)
    fig.patch.set_facecolor("#FAFAFA")
    fig.suptitle(
        f"Décomposition SHAP — Top {top_n} actifs | Régime {regime}",
        fontsize=13, fontweight="bold"
    )

    colors_pos = "#1D9E75"
    colors_neg = "#E24B4A"

    for idx, (ticker, row) in enumerate(top_assets.iterrows()):
        ax = axes[idx]
        ax.set_facecolor("#FAFAFA")

        values = row[feature_cols]
        colors = [colors_pos if v >= 0 else colors_neg for v in values]

        bars = ax.barh(feature_cols, values, color=colors, alpha=0.85)
        ax.axvline(x=0, color="#444441", linewidth=0.8)
        ax.set_title(
            f"{ticker}\n{row['predicted_weight']:.1%}",
            fontsize=11, fontweight="bold"
        )
        ax.grid(axis="x", alpha=0.3)

        for bar, val in zip(bars, values):
            ax.text(
                val + (0.0001 if val >= 0 else -0.0001),
                bar.get_y() + bar.get_height()/2,
                f"{val:+.4f}", va="center",
                ha="left" if val >= 0 else "right",
                fontsize=9
            )

    plt.tight_layout()
    path = "c:/Users/lachk/OneDrive/Bureau/CY/ing3/PFE/shap_top_assets.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Graphique sauvegardé → shap_top_assets.png")


# ── 7. Explication textuelle ──────────────────────────────────────────────────
def print_shap_explanation(df_shap, regime, feature_cols, top_n=5):
    """
    Génère une explication en langage naturel des décisions d'allocation.
    C'est ce qui va dans le rapport Section 6.5
    """
    top_assets = df_shap.nlargest(top_n, "predicted_weight")

    feature_names = {
        "return":      "rendement historique",
        "volatility":  "volatilité",
        "correlation": "corrélation aux autres actifs",
        "momentum":    "momentum récent",
    }

    print(f"\n── Explication SHAP — Régime {regime} ───────────────────────────")
    for ticker, row in top_assets.iterrows():
        contributions = row[feature_cols].sort_values(key=abs, ascending=False)
        print(f"\n{ticker} → pondération recommandée : {row['predicted_weight']:.1%}")
        for feat, val in contributions.items():
            direction = "favorise" if val > 0 else "pénalise"
            print(f"  • {feature_names[feat]:35s} {direction} ({val:+.4f})")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Génération des données d'entraînement
    df_train = generate_training_data(returns, n_windows=50)

    # Entraînement du modèle proxy
    model, scaler_rf, feature_cols = train_proxy_model(df_train)

    # Régime actuel
    current_regime = regimes["regime"].iloc[-1]
    print(f"\nRégime actuel : {current_regime}")

    # Explication SHAP
    df_shap, explainer, X_scaled, feat = explain_allocation(
        returns, current_regime, model, scaler_rf, feature_cols
    )

    # Explication textuelle
    print_shap_explanation(df_shap, current_regime, feature_cols)

    # Graphique 1
    plot_shap_summary(df_shap, current_regime, feature_cols)

    # Graphique 2 — avec try/except pour voir l'erreur
    try:
        plot_shap_top_assets(df_shap, current_regime, feature_cols)
        print("Graphique top assets généré !")
    except Exception as e:
        print(f"Erreur graphique top assets : {e}")

    # Sauvegarde
    df_shap.to_csv(
        "c:/Users/lachk/OneDrive/Bureau/CY/ing3/PFE/data/shap_values.csv"
    )
    print("\nValeurs SHAP sauvegardées → data/shap_values.csv")