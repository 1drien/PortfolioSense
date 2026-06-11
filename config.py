# ============================================================
#  PortfolioSense — Configuration centrale
#  NE PAS MODIFIER sans accord du groupe
# ============================================================

# --- Période historique ---
START_DATE = "2015-01-01"
END_DATE   = "2024-12-31"

# --- Univers d'actifs : tickers présents dans returns_clean.csv ---
TICKERS = [
    "AAPL", "ABBV", "AMZN", "BA",   "BAC",
    "BLK",  "CAT",  "CVX",  "GOOGL","GS",
    "HD",   "JNJ",  "JPM",  "KO",   "META",
    "MSFT", "NEE",  "NVDA", "PFE",  "PG",
    "PLD",  "TSLA", "UNH",  "WMT",  "XOM",
]

# --- Paramètres financiers ---
RISK_FREE_RATE  = 0.04   # aligné avec Membre 2
RISK_FREE       = 0.04   # alias pour compatibilité
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