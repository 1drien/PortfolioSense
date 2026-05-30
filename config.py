# config.py

RISK_FREE_RATE = 0.05
TRADING_DAYS   = 252
WEIGHT_MIN     = 0.01
WEIGHT_MAX     = 0.25
N_SIMULATIONS  = 10_000
N_REGIMES      = 3
HMM_LOOKBACK   = 252
TRAIN_WINDOW   = 504
TEST_WINDOW    = 126
BENCHMARK      = "SPY"
TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "META",
    "JPM", "BAC", "GS", "BLK", "AXP",
    "JNJ", "UNH", "PFE", "ABBV", "MRK",
    "XOM", "CVX", "COP",
    "AMZN", "TSLA", "HD", "MCD",
    "CAT", "LMT", "PG",
]