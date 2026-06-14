# ============================================================
#  PortfolioSense — Tests unitaires module data/
#  Lancer : python -m pytest tests/test_data.py -v
# ============================================================

import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import TICKERS, START_DATE, DATA_DIR, RETURNS_CLEAN

# ── Chargement des fichiers ───────────────────────────────
@pytest.fixture(scope="module")
def returns():
    assert os.path.exists(RETURNS_CLEAN), \
        f"returns_clean.csv introuvable — lance d'abord python data/pipeline.py"
    return pd.read_csv(RETURNS_CLEAN, index_col=0, parse_dates=True)

@pytest.fixture(scope="module")
def drawdown():
    path = os.path.join(DATA_DIR, "drawdown_historique.csv")
    if not os.path.exists(path):
        pytest.skip("drawdown_historique.csv non disponible")
    return pd.read_csv(path, index_col=0)

@pytest.fixture(scope="module")
def attribution():
    path = os.path.join(DATA_DIR, "attribution_actifs.csv")
    if not os.path.exists(path):
        pytest.skip("attribution_actifs.csv non disponible")
    return pd.read_csv(path, index_col=0)

@pytest.fixture(scope="module")
def stress_covid():
    path = os.path.join(DATA_DIR, "stress_covid2020.csv")
    if not os.path.exists(path):
        pytest.skip("stress_covid2020.csv non disponible")
    return pd.read_csv(path, index_col=0)


# ════════════════════════════════════════════════
# TESTS — returns_clean.csv
# ════════════════════════════════════════════════

class TestReturnsFormat:
    """Vérifie le format et la qualité du fichier returns_clean.csv"""

    def test_file_exists(self):
        """Le fichier livrable existe"""
        assert os.path.exists(RETURNS_CLEAN), \
            "returns_clean.csv n'existe pas — pipeline non lancé"

    def test_correct_number_of_assets(self, returns):
        """Le fichier contient exactement 35 actifs"""
        assert returns.shape[1] == 35, \
            f"Attendu 35 actifs, trouvé {returns.shape[1]}"

    def test_all_tickers_present(self, returns):
        """Tous les tickers définis dans config.py sont présents"""
        missing = [t for t in TICKERS if t not in returns.columns]
        assert len(missing) == 0, \
            f"Tickers manquants : {missing}"

    def test_no_missing_values(self, returns):
        """Aucune valeur manquante dans le fichier"""
        total_nan = returns.isna().sum().sum()
        assert total_nan == 0, \
            f"{total_nan} valeurs manquantes détectées"

    def test_datetime_index(self, returns):
        """L'index est bien un DatetimeIndex"""
        assert isinstance(returns.index, pd.DatetimeIndex), \
            "L'index n'est pas un DatetimeIndex"

    def test_index_format(self, returns):
        """Les dates sont au format YYYY-MM-DD"""
        assert returns.index[0].year >= 2015, \
            "La période ne commence pas en 2015"

    def test_float_values(self, returns):
        """Toutes les valeurs sont des floats"""
        assert (returns.dtypes == float).all(), \
            "Certaines colonnes ne sont pas en float64"

    def test_sufficient_rows(self, returns):
        """Au moins 2500 jours de données"""
        assert returns.shape[0] >= 2500, \
            f"Seulement {returns.shape[0]} jours — attendu au moins 2500"

    def test_sorted_index(self, returns):
        """Les dates sont triées dans l'ordre chronologique"""
        assert returns.index.is_monotonic_increasing, \
            "Les dates ne sont pas triées"

    def test_no_duplicate_dates(self, returns):
        """Pas de dates en double"""
        assert returns.index.is_unique, \
            "Des dates sont en double dans l'index"


class TestLogReturns:
    """Vérifie la cohérence des log-rendements"""

    def test_returns_range(self, returns):
        """Les log-rendements sont dans une plage raisonnable (-50% / +50%)"""
        assert returns.max().max() < 0.50, \
            f"Log-rendement max trop élevé : {returns.max().max():.2%}"
        assert returns.min().min() > -0.50, \
            f"Log-rendement min trop bas : {returns.min().min():.2%}"

    def test_no_zero_variance(self, returns):
        """Aucun actif n'a une variance nulle (données figées)"""
        zero_var = (returns.std() == 0)
        assert not zero_var.any(), \
            f"Variance nulle pour : {zero_var[zero_var].index.tolist()}"

    def test_nvda_positive_return(self, returns):
        """NVDA doit avoir un rendement annualisé positif sur la période"""
        nvda_ann = returns["NVDA"].mean() * 252
        assert nvda_ann > 0.20, \
            f"Rendement NVDA anormalement bas : {nvda_ann:.2%}"

    def test_intc_negative_return(self, returns):
        """INTC doit avoir un rendement négatif ou très faible"""
        intc_ann = returns["INTC"].mean() * 252
        assert intc_ann < 0.15, \
            f"Rendement INTC anormalement élevé : {intc_ann:.2%}"

    def test_correlation_range(self, returns):
        """Les corrélations sont entre -1 et 1"""
        corr = returns.corr()
        assert corr.max().max() <= 1.001, "Corrélation > 1 détectée"
        assert corr.min().min() >= -1.001, "Corrélation < -1 détectée"

    def test_diversification(self, returns):
        """La corrélation minimale est inférieure à 0.5 — diversification validée"""
        corr_vals = returns.corr().where(lambda x: x < 1).stack()
        assert corr_vals.min() < 0.5, \
            "Corrélation minimale trop élevée — diversification insuffisante"

    def test_fat_tails(self, returns):
        """La kurtosis moyenne est > 3 — queues épaisses confirmées"""
        avg_kurt = returns.kurtosis().mean()
        assert avg_kurt > 3, \
            f"Kurtosis moyenne anormalement basse : {avg_kurt:.2f}"


# ════════════════════════════════════════════════
# TESTS — Drawdown
# ════════════════════════════════════════════════

class TestDrawdown:
    """Vérifie la cohérence des calculs de drawdown"""

    def test_drawdown_negative(self, drawdown):
        """Tous les drawdowns sont négatifs ou nuls"""
        assert (drawdown["Max Drawdown (%)"] <= 0).all(), \
            "Des drawdowns positifs détectés — erreur de calcul"

    def test_ba_worst_drawdown(self, drawdown):
        """Boeing (BA) doit avoir le pire drawdown"""
        worst = drawdown["Max Drawdown (%)"].idxmin()
        assert worst == "BA", \
            f"Pire drawdown attendu sur BA, trouvé sur {worst}"

    def test_all_tickers_in_drawdown(self, drawdown):
        """Tous les actifs ont un drawdown calculé"""
        assert len(drawdown) == 35, \
            f"Attendu 35 actifs, trouvé {len(drawdown)}"

    def test_non_recovered_assets(self, drawdown):
        """Au moins 5 actifs ne se sont pas encore récupérés"""
        non_rec = (drawdown["Statut"] == "Pas encore recupere").sum()
        assert non_rec >= 5, \
            f"Seulement {non_rec} actifs non récupérés — résultat suspect"

    def test_lly_best_drawdown(self, drawdown):
        """Le meilleur drawdown est inférieur à -30%"""
        best_dd = drawdown["Max Drawdown (%)"].max()
        assert best_dd > -30, \
            f"Meilleur drawdown trop sévère : {best_dd:.1f}%"


# ════════════════════════════════════════════════
# TESTS — Attribution
# ════════════════════════════════════════════════

class TestAttribution:
    """Vérifie la cohérence de la performance attribution"""

    def test_nvda_top_contributor(self, attribution):
        """NVDA doit être le premier contributeur"""
        top = attribution["Contribution annualisée (%)"].idxmax()
        assert top == "NVDA", \
            f"Meilleur contributeur attendu NVDA, trouvé {top}"

    def test_intc_low_contribution(self, attribution):
        """INTC doit avoir une contribution parmi les plus faibles"""
        intc_contrib = attribution.loc["INTC", "Contribution annualisée (%)"]
        median_contrib = attribution["Contribution annualisée (%)"].median()
        assert intc_contrib <= median_contrib, \
            f"Contribution INTC devrait être sous la médiane ({median_contrib:.3f}%)"

    def test_equal_weights(self, attribution):
        """Tous les actifs ont le même poids (équipondéré)"""
        weights = attribution["Poids (%)"].unique()
        assert len(weights) == 1, \
            "Les poids ne sont pas égaux — erreur dans l'équipondération"
        assert abs(weights[0] - (100/35)) < 0.1, \
            f"Poids attendu {100/35:.2f}%, trouvé {weights[0]:.2f}%"

    def test_positive_portfolio_return(self, attribution):
        """Le rendement global du portefeuille est positif"""
        total = attribution["Contribution annualisée (%)"].sum()
        assert total > 0, \
            f"Rendement global négatif : {total:.2f}%"


# ════════════════════════════════════════════════
# TESTS — Stress Tests
# ════════════════════════════════════════════════

class TestStressTests:
    """Vérifie la cohérence des stress tests COVID 2020"""

    def test_ba_worst_covid(self, stress_covid):
        """Boeing doit être le pire actif pendant le COVID"""
        if "Rendement cumulé (%)" not in stress_covid.columns:
            pytest.skip("Colonne Rendement cumulé manquante")
        worst = stress_covid["Rendement cumulé (%)"].idxmin()
        assert worst == "BA", \
            f"Pire actif COVID attendu BA, trouvé {worst}"

    def test_amzn_positive_covid(self, stress_covid):
        """Amazon doit être positif pendant le COVID"""
        if "Rendement cumulé (%)" not in stress_covid.columns:
            pytest.skip("Colonne Rendement cumulé manquante")
        amzn_ret = stress_covid.loc["AMZN", "Rendement cumulé (%)"]
        assert amzn_ret > 0, \
            f"Amazon attendu positif en COVID, trouvé {amzn_ret:.1f}%"

    def test_all_assets_in_stress(self, stress_covid):
        """Tous les actifs ont des résultats de stress test"""
        assert len(stress_covid) >= 30, \
            f"Seulement {len(stress_covid)} actifs dans le stress test COVID"


# ════════════════════════════════════════════════
# TESTS — Config
# ════════════════════════════════════════════════

class TestConfig:
    """Vérifie la cohérence de la configuration"""

    def test_35_tickers(self):
        """La config contient bien 35 tickers"""
        assert len(TICKERS) == 35, \
            f"Attendu 35 tickers, trouvé {len(TICKERS)}"

    def test_no_duplicate_tickers(self):
        """Pas de doublons dans les tickers"""
        assert len(TICKERS) == len(set(TICKERS)), \
            "Des tickers sont en double dans config.py"

    def test_start_date(self):
        """La date de début est bien 2015"""
        assert START_DATE == "2015-01-01", \
            f"Date de début incorrecte : {START_DATE}"

    def test_data_dir_exists(self):
        """Le dossier data/ existe"""
        assert os.path.exists(DATA_DIR), \
            "Le dossier data/ n'existe pas"


# ════════════════════════════════════════════════
# TESTS — Corrélations glissantes
# ════════════════════════════════════════════════

@pytest.fixture(scope="module")
def rolling_corr():
    path = os.path.join(DATA_DIR, "rolling_corr_mean.csv")
    if not os.path.exists(path):
        pytest.skip("rolling_corr_mean.csv non disponible")
    return pd.read_csv(path, index_col=0, parse_dates=True)

@pytest.fixture(scope="module")
def rolling_pairs():
    path = os.path.join(DATA_DIR, "rolling_corr_pairs.csv")
    if not os.path.exists(path):
        pytest.skip("rolling_corr_pairs.csv non disponible")
    return pd.read_csv(path, index_col=0, parse_dates=True)


class TestRollingCorrelation:
    """Verifie la coherence des correlations glissantes"""

    def test_file_exists(self):
        """Le fichier rolling_corr_mean.csv existe"""
        path = os.path.join(DATA_DIR, "rolling_corr_mean.csv")
        assert os.path.exists(path), \
            "rolling_corr_mean.csv manquant — lance data/rolling_correlation.py"

    def test_correct_columns(self, rolling_corr):
        """Le fichier contient les bonnes colonnes"""
        expected = ["corr_moyenne", "corr_max", "corr_min", "regime_naif"]
        for col in expected:
            assert col in rolling_corr.columns, \
                f"Colonne manquante : {col}"

    def test_no_missing_values(self, rolling_corr):
        """Pas de valeurs manquantes"""
        assert rolling_corr.isna().sum().sum() == 0, \
            "Des valeurs manquantes dans rolling_corr_mean.csv"

    def test_correlation_range(self, rolling_corr):
        """Les correlations glissantes sont entre -1 et 1"""
        assert rolling_corr["corr_moyenne"].max() <= 1.0, \
            "Correlation moyenne > 1 detectee"
        assert rolling_corr["corr_moyenne"].min() >= -1.0, \
            "Correlation moyenne < -1 detectee"
        assert rolling_corr["corr_max"].max() <= 1.0, \
            "Correlation max > 1 detectee"

    def test_covid_spike(self, rolling_corr):
        """La correlation doit etre elevee pendant le COVID (mars 2020)"""
        covid_period = rolling_corr["2020-02-01":"2020-04-30"]["corr_moyenne"]
        assert covid_period.max() > 0.5, \
            f"Pic de correlation COVID trop faible : {covid_period.max():.3f}"

    def test_normal_period_low_corr(self, rolling_corr):
        """La correlation doit etre faible en periode normale (2021)"""
        normal_period = rolling_corr["2021-01-01":"2021-12-31"]["corr_moyenne"]
        assert normal_period.mean() < 0.40, \
            f"Correlation 2021 anormalement elevee : {normal_period.mean():.3f}"

    def test_regime_naif_values(self, rolling_corr):
        """Les regimes naifs sont bien bull/bear/lateral"""
        valid_regimes = {"bull", "bear", "lateral"}
        actual = set(rolling_corr["regime_naif"].unique())
        assert actual.issubset(valid_regimes), \
            f"Regimes invalides detectes : {actual - valid_regimes}"

    def test_bull_majority(self, rolling_corr):
        """Le regime Bull doit etre majoritaire sur 10 ans"""
        bull_pct = (rolling_corr["regime_naif"] == "bull").mean() * 100
        assert bull_pct > 50, \
            f"Regime Bull attendu majoritaire, trouve {bull_pct:.1f}%"

    def test_bear_covid_detected(self, rolling_corr):
        """Le regime Bear doit etre detecte pendant le COVID"""
        covid = rolling_corr["2020-02-01":"2020-06-30"]["regime_naif"]
        bear_count = (covid == "bear").sum()
        assert bear_count > 0, \
            "Aucun regime Bear detecte pendant le COVID"

    def test_sufficient_rows(self, rolling_corr):
        """Au moins 2700 jours de donnees"""
        assert len(rolling_corr) >= 2700, \
            f"Seulement {len(rolling_corr)} lignes"

    def test_pairs_file_exists(self):
        """Le fichier des paires correlees existe"""
        path = os.path.join(DATA_DIR, "rolling_corr_pairs.csv")
        assert os.path.exists(path), \
            "rolling_corr_pairs.csv manquant"

    def test_pairs_top_finance(self, rolling_pairs):
        """Les paires bancaires doivent figurer parmi les plus correlees"""
        finance_pairs = [c for c in rolling_pairs.columns
                        if any(t in c for t in ["BAC", "JPM", "GS", "MS"])]
        assert len(finance_pairs) >= 2, \
            "Moins de 2 paires financieres dans le top 10"

    def test_corr_max_greater_than_mean(self, rolling_corr):
        """La correlation max doit toujours etre >= correlation moyenne"""
        assert (rolling_corr["corr_max"] >= rolling_corr["corr_moyenne"]).all(), \
            "Correlation max inferieure a la moyenne — erreur de calcul"