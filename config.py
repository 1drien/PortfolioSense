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
    # Technologie (8)
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "NVDA",   # Nvidia
    "GOOGL",  # Alphabet
    "META",   # Meta
    "AMD",    # Advanced Micro Devices
    "INTC",   # Intel
    "CRM",    # Salesforce

    # Finance (6)
    "JPM",    # JPMorgan Chase
    "BAC",    # Bank of America
    "GS",     # Goldman Sachs
    "BLK",    # BlackRock
    "MS",     # Morgan Stanley
    "AXP",    # American Express

    # Santé (6)
    "JNJ",    # Johnson & Johnson
    "UNH",    # UnitedHealth
    "PFE",    # Pfizer
    "ABBV",   # AbbVie
    "MRK",    # Merck
    "LLY",    # Eli Lilly

    # Consommation discrétionnaire (4)
    "AMZN",   # Amazon
    "TSLA",   # Tesla
    "HD",     # Home Depot
    "NKE",    # Nike

    # Consommation de base (3)
    "PG",     # Procter & Gamble
    "KO",     # Coca-Cola
    "WMT",    # Walmart

    # Énergie (2)
    "XOM",    # ExxonMobil
    "CVX",    # Chevron

    # Industrie (3)
    "CAT",    # Caterpillar
    "BA",     # Boeing
    "HON",    # Honeywell
    "UPS",    # United Parcel Service

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