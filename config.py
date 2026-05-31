# ============================================================
#  PortfolioSense — Configuration centrale
#  NE PAS MODIFIER sans accord du groupe
# ============================================================

# --- Période historique ---
START_DATE = "2015-01-01"
END_DATE   = "2024-12-31"

# --- Univers d'actifs : 25 actions S&P 500 diversifiées ---
TICKERS = [
    # Technologie (5)
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "NVDA",   # Nvidia
    "GOOGL",  # Alphabet
    "META",   # Meta

    # Finance (4)
    "JPM",    # JPMorgan Chase
    "BAC",    # Bank of America
    "GS",     # Goldman Sachs
    "BLK",    # BlackRock

    # Santé (4)
    "JNJ",    # Johnson & Johnson
    "UNH",    # UnitedHealth
    "PFE",    # Pfizer
    "ABBV",   # AbbVie

    # Consommation discrétionnaire (3)
    "AMZN",   # Amazon
    "TSLA",   # Tesla
    "HD",     # Home Depot

    # Consommation de base (3)
    "PG",     # Procter & Gamble
    "KO",     # Coca-Cola
    "WMT",    # Walmart

    # Énergie (2)
    "XOM",    # ExxonMobil
    "CVX",    # Chevron

    # Industrie (2)
    "CAT",    # Caterpillar
    "BA",     # Boeing

    # Immobilier (1)
    "PLD",    # Prologis

    # Services aux collectivités (1)
    "NEE",    # NextEra Energy
]

# --- Contraintes du portefeuille (à confirmer en réunion) ---
WEIGHT_MIN   = 0.01   # 1% minimum par actif
WEIGHT_MAX   = 0.25   # 25% maximum par actif
RISK_FREE    = 0.04   # Taux sans risque annualisé (proxy : T-Bill US)
VAR_CONFIDENCE = 0.95 # Niveau de confiance VaR (95%)
N_REGIMES    = 3      # Nombre d'états HMM : Bull / Bear / Lateral

# --- Chemins de fichiers ---
DATA_DIR         = "data/"
RETURNS_CLEAN    = DATA_DIR + "returns_clean.csv"
PRICES_RAW       = DATA_DIR + "prices_raw.csv"