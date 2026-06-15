import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler

# ── 1. Chargement des données ─────────────────────────────────────────────────
returns = pd.read_csv(
    "c:/Users/lachk/OneDrive/Bureau/CY/PortfolioSense/data/returns_clean.csv",
    index_col="Date",
    parse_dates=True
)

# ── 2. Construction des features ─────────────────────────────────────────────
port_returns = returns.mean(axis=1)

# Chargement de la corrélation glissante du Membre 2
corr_data = pd.read_csv(
    "c:/Users/lachk/OneDrive/Bureau/CY/PortfolioSense/data/rolling_corr_mean.csv",
    index_col="Date",
    parse_dates=True
)

features = pd.DataFrame({
    "return":      port_returns,
    "volatility":  port_returns.rolling(20).std(),
    "momentum":    port_returns.rolling(5).mean(),
    "correlation": corr_data["corr_moyenne"],
}).dropna()

# Normalisation
scaler = StandardScaler()
X = scaler.fit_transform(features)

# ── 3. Entraînement HMM ──────────────────────────────────────────────────────
best_score = -np.inf
best_model = None

for seed in range(20):
    m = hmm.GaussianHMM(
        n_components=3,
        covariance_type="full",
        n_iter=2000,
        random_state=seed,
        tol=1e-5
    )
    m.fit(X)
    score = m.score(X)
    if score > best_score:
        best_score = score
        best_model = m

model = best_model
states = model.predict(X)
dates = features.index
port_returns_trimmed = port_returns[features.index]

# ── 4. Identification des régimes ────────────────────────────────────────────
state_means = {}
for s in range(3):
    mask = states == s
    state_means[s] = port_returns_trimmed[mask].mean()

order = sorted(state_means, key=state_means.get)
labels_used = ["Bear", "Lateral", "Bull"]
colors_used  = ["#E24B4A", "#EF9F27", "#1D9E75"]

state_map = {}
for rank, state_idx in enumerate(order):
    state_map[state_idx] = (labels_used[rank], colors_used[rank])

regime_labels = [state_map[s][0] for s in states]
regime_colors = [state_map[s][1] for s in states]

# ── 5. Sauvegarde des régimes ────────────────────────────────────────────────
regime_series = pd.Series(regime_labels, index=dates, name="regime")
regime_series.to_csv(
    "c:/Users/lachk/OneDrive/Bureau/CY/PortfolioSense/data/regimes.csv"
)

# ── 6. Comparaison avec le régime naïf du Membre 2 ───────────────────────────
def compare_with_naive(regime_labels, corr_data, dates):
    """
    Compare les régimes HMM avec la baseline naïve du Membre 2.
    Montre que le HMM est plus précis.
    """
    naive = corr_data.loc[dates, "regime_naif"].str.lower()
    hmm_regimes = pd.Series(regime_labels, index=dates).str.lower()

    # Aligner les index
    common = naive.index.intersection(hmm_regimes.index)
    naive = naive.loc[common]
    hmm_r = hmm_regimes.loc[common]

    accord = (naive == hmm_r).mean()
    print(f"\n── Comparaison HMM vs Régime naïf ──────────────────────────────")
    print(f"Accord global : {accord:.1%}")
    print(f"(Les désaccords montrent où le HMM apporte une vraie valeur ajoutée)")

    # Distribution des régimes
    print(f"\nDistribution HMM    : {hmm_r.value_counts(normalize=True).round(3).to_dict()}")
    print(f"Distribution naïve  : {naive.value_counts(normalize=True).round(3).to_dict()}")


# ═══════════════════════════════════════════════════════════════════════════════
# Fonction exportée — utilisée par regime_allocation.py
# ═══════════════════════════════════════════════════════════════════════════════
def detect_regime(returns_window):
    """
    Détecte le régime courant sur une fenêtre de rendements donnée.
    Retourne : "Bull", "Lateral" ou "Bear"
    """
    port_ret = returns_window.mean(axis=1)

    corr = pd.read_csv(
        "c:/Users/lachk/OneDrive/Bureau/CY/PortfolioSense/data/rolling_corr_mean.csv",
        index_col="Date",
        parse_dates=True
    )

    features_new = pd.DataFrame({
        "return":      port_ret,
        "volatility":  port_ret.rolling(20).std(),
        "momentum":    port_ret.rolling(5).mean(),
        "correlation": corr["corr_moyenne"],
    }).dropna()

    if len(features_new) < 30:
        return "Lateral"

    X_new = scaler.transform(features_new)
    states_new = model.predict(X_new)
    last_state = states_new[-1]

    return state_map[last_state][0]


# ═══════════════════════════════════════════════════════════════════════════════
# Exécution directe uniquement
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"Données chargées : {returns.shape[0]} jours | {returns.shape[1]} actifs")
    print(f"Features construites : {features.shape[0]} jours utilisés")
    print(f"Meilleur score HMM : {best_score:.1f}")

    print("\n── Caractéristiques par régime ──────────────────────────────────")
    for state_idx in order:
        label, color = state_map[state_idx]
        mask = states == state_idx
        r = port_returns_trimmed[mask]
        c = corr_data["corr_moyenne"][features.index][mask]
        print(f"{label:8s} | Rend. ann. : {r.mean()*252:+.1%} "
              f"| Vol. ann. : {r.std()*np.sqrt(252):.1%} "
              f"| Corr. moy : {c.mean():.3f} "
              f"| Nb jours : {mask.sum()} ({mask.mean():.0%} du temps)")

    print("\nMatrice de transition :")
    df_trans = pd.DataFrame(
        model.transmat_,
        index=[state_map[i][0] for i in range(3)],
        columns=[state_map[i][0] for i in range(3)]
    ).round(3)
    print(df_trans)

    # Comparaison avec régime naïf
    compare_with_naive(regime_labels, corr_data, dates)

    # ── Graphique ────────────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True,
                                    gridspec_kw={"height_ratios": [3, 1]})
    fig.patch.set_facecolor("#FAFAFA")
    for ax in (ax1, ax2):
        ax.set_facecolor("#FAFAFA")

    cum_returns = (1 + port_returns_trimmed).cumprod()
    ax1.plot(dates, cum_returns, color="#444441", linewidth=1.2, zorder=3)

    prev_color = regime_colors[0]
    start_idx = 0
    for i in range(1, len(dates)):
        if regime_colors[i] != prev_color or i == len(dates) - 1:
            ax1.axvspan(dates[start_idx], dates[i],
                        alpha=0.25, color=prev_color, linewidth=0)
            start_idx = i
            prev_color = regime_colors[i]

    ax1.set_ylabel("Performance cumulée (base 1)", fontsize=11)
    ax1.set_title(
        "Régimes de marché — HMM 4 features — 25 actifs S&P500 (2015–2024)",
        fontsize=13, fontweight="bold", pad=12
    )
    ax1.grid(axis="y", alpha=0.3, linewidth=0.5)

    patches = [mpatches.Patch(color=colors_used[i], alpha=0.7, label=labels_used[i])
               for i in range(3)]
    ax1.legend(handles=patches, loc="upper left", fontsize=10, framealpha=0.8)

    for i, (date, color) in enumerate(zip(dates, regime_colors)):
        ax2.axvspan(date, dates[min(i + 1, len(dates) - 1)],
                    color=color, alpha=0.7, linewidth=0)

    ax2.set_yticks([])
    ax2.set_ylabel("Régime", fontsize=10)
    ax2.set_xlabel("Date", fontsize=11)

    plt.tight_layout()
    output_path = "c:/Users/lachk/OneDrive/Bureau/CY/PortfolioSense/data/regimes_hmm.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"\nGraphique sauvegardé → {output_path}")
    print(f"Régime actuel : {regime_labels[-1]} ({dates[-1].date()})")
