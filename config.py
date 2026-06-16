# ============================================================
#  PortfolioSense — Configuration centrale
#  NE PAS MODIFIER sans accord du groupe
# ============================================================
from datetime import date
# --- Période historique ---
START_DATE = "2015-01-01"
END_DATE = date.today().strftime("%Y-%m-%d")

# --- Univers d'actifs : 35 actions S&P 500 diversifiées ---
TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMD", "INTC", "CRM",
    "JPM", "BAC", "GS", "BLK", "MS", "AXP",
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY",
    "AMZN", "TSLA", "HD", "NKE",
    "PG", "KO", "WMT",
    "XOM", "CVX",
    "CAT", "BA", "HON", "UPS",
    "PLD", "NEE",
]

# --- Paramètres financiers ---
RISK_FREE_RATE  = 0.04   # utilisé par optimisation
RISK_FREE       = 0.04   # alias pour compatibilité (risk + data)
TRADING_DAYS    = 252
WEIGHT_MIN      = 0.01
WEIGHT_MAX      = 0.25
VAR_CONFIDENCE  = 0.95
N_SIMULATIONS   = 10_000
N_REGIMES       = 3
HMM_LOOKBACK    = 252
TRAIN_WINDOW    = 504
TEST_WINDOW     = 126
BENCHMARK       = "SPY"

# --- Chemins de fichiers ---
DATA_DIR      = "data/"
RETURNS_CLEAN = DATA_DIR + "returns_clean.csv"
PRICES_RAW    = DATA_DIR + "prices_raw.csv"

# ── Commissions de transaction ──────────────────────────
COMMISSION_PAR_ORDRE = 1.0   # euros par ordre — Trade Republic par défaut

BROKERS = {
    "trade_republic": {"type": "fixe",  "valeur": 1.0},
    "boursorama":     {"type": "fixe",  "valeur": 3.99},
    "degiro":         {"type": "mixte", "valeur": 3.0, "pct": 0.00026},
    "autre":          {"type": "fixe",  "valeur": 1.0},
}

SEUIL_DERIVE         = 0.05   # 5% d'écart avant alerte dérive
HORIZON_REBALANCING  = 180    # jours entre deux rebalancements suggérés