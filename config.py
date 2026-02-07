"""
Market Movers - Game Configuration
All game constants and settings
"""

# Game Settings
MAX_ROUNDS = 10
STARTING_CASH = 1000
MIN_PLAYERS = 2
MAX_PLAYERS = 4

# Asset Prices
ASSET_PRICES = {
    "stocks": 100,
    "crypto": 50,
    "bonds": 200,
    "commodities": 75,
    "real_estate": 500
}

# Asset Return Ranges (min, max percentages)
ASSET_RETURNS = {
    "stocks": {"min": -0.10, "max": 0.15},
    "crypto": {"min": -0.40, "max": 0.60},
    "commodities": {"min": -0.05, "max": 0.10},
    "bonds": {"min": 0.02, "max": 0.05}
}

# Real Estate Lock Duration (rounds)
REAL_ESTATE_LOCK_ROUNDS = 2

# Display Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 30

# Colors (RGB)
COLOR_BG = (15, 23, 42)           # Dark blue-gray
COLOR_PRIMARY = (59, 130, 246)    # Blue
COLOR_SUCCESS = (34, 197, 94)     # Green
COLOR_DANGER = (239, 68, 68)      # Red
COLOR_WARNING = (251, 191, 36)    # Yellow
COLOR_TEXT = (248, 250, 252)      # Off-white
COLOR_TEXT_DIM = (148, 163, 184)  # Gray
COLOR_CARD_BG = (30, 41, 59)      # Card background

# Button Colors
BTN_GREEN = (34, 197, 94)
BTN_RED = (239, 68, 68)
BTN_BLUE = (59, 130, 246)

# Font Sizes
FONT_TITLE = 32
FONT_LARGE = 24
FONT_MEDIUM = 18
FONT_SMALL = 14

# Logging
LOG_FILE = "market_movers_log.txt"

# Space Income/Costs
PAYDAY_AMOUNT = 200
TAX_AUDIT_AMOUNT = 150
DIVIDEND_PERCENT = 0.075  # 7.5% of stocks/bonds

# Action Card Success Rates
HOSTILE_TAKEOVER_SUCCESS = 0.80  # 80% success rate
HOSTILE_TAKEOVER_FINE = 50

STARTUP_SUCCESS_RATE = 0.50  # 50% chance
STARTUP_WIN_AMOUNT = 300
STARTUP_LOSE_AMOUNT = 100

# Scan Timeout (seconds)
SCAN_TIMEOUT = 30
