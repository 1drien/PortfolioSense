# ============================================================
#  PortfolioSense — Configuration centrale
#  NE PAS MODIFIER sans accord du groupe
# ============================================================
from datetime import date

# --- Période historique ---
START_DATE = "2015-01-01"
END_DATE   = date.today().strftime("%Y-%m-%d")   # dynamique : jusqu'à aujourd'hui

# --- Univers d'actifs ---
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