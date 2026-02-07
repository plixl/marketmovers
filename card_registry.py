"""
Market Movers - Card Registry
Maps RFID IDs to card types and properties

INSTRUCTIONS:
1. Run the game in "registration mode" (press RED button on startup)
2. Follow prompts to scan each card
3. The system will generate the actual RFID mappings
4. Or manually replace PLACEHOLDER_XXX with actual RFID IDs from your cards
"""

# Card Mappings - Replace placeholders with actual RFID IDs
CARD_MAPPINGS = {
    # ==================== PLAYER WALLET CARDS ====================
    "PLACEHOLDER_P1": {
        "type": "player",
        "name": "Player 1",
        "color": (239, 68, 68)  # Red
    },
    "PLACEHOLDER_P2": {
        "type": "player",
        "name": "Player 2",
        "color": (59, 130, 246)  # Blue
    },
    "PLACEHOLDER_P3": {
        "type": "player",
        "name": "Player 3",
        "color": (34, 197, 94)  # Green
    },
    "PLACEHOLDER_P4": {
        "type": "player",
        "name": "Player 4",
        "color": (251, 191, 36)  # Yellow
    },
    
    # ==================== BOARD SPACE CARDS ====================
    "PLACEHOLDER_S01": {
        "type": "space",
        "name": "Payday",
        "description": "Collect $200 salary"
    },
    "PLACEHOLDER_S02": {
        "type": "space",
        "name": "Stock Exchange",
        "description": "Buy/sell stocks ($100 each)"
    },
    "PLACEHOLDER_S03": {
        "type": "space",
        "name": "Action Space",
        "description": "Draw an action card"
    },
    "PLACEHOLDER_S04": {
        "type": "space",
        "name": "Crypto Hub",
        "description": "Buy/sell crypto ($50 each)"
    },
    "PLACEHOLDER_S05": {
        "type": "space",
        "name": "Event Space",
        "description": "Draw an event card"
    },
    "PLACEHOLDER_S06": {
        "type": "space",
        "name": "Bond Market",
        "description": "Buy bonds ($200 each)"
    },
    "PLACEHOLDER_S07": {
        "type": "space",
        "name": "Real Estate",
        "description": "Buy property ($500, locked 2 rounds)"
    },
    "PLACEHOLDER_S08": {
        "type": "space",
        "name": "Action Space",
        "description": "Draw an action card"
    },
    "PLACEHOLDER_S09": {
        "type": "space",
        "name": "Dividend",
        "description": "Stocks/bonds pay 7.5% dividend"
    },
    "PLACEHOLDER_S10": {
        "type": "space",
        "name": "Commodity Trade",
        "description": "Buy/sell commodities ($75 each)"
    },
    "PLACEHOLDER_S11": {
        "type": "space",
        "name": "Global Event",
        "description": "Major market event affects all"
    },
    "PLACEHOLDER_S12": {
        "type": "space",
        "name": "Action Space",
        "description": "Draw an action card"
    },
    "PLACEHOLDER_S13": {
        "type": "space",
        "name": "Startup Incubator",
        "description": "50/50 gamble: Win $300 or lose $100"
    },
    "PLACEHOLDER_S14": {
        "type": "space",
        "name": "Tax Audit",
        "description": "Pay $150 tax"
    },
    "PLACEHOLDER_S15": {
        "type": "space",
        "name": "Market Reset",
        "description": "All assets revalue randomly"
    },
    
    # ==================== ACTION CARDS ====================
    "PLACEHOLDER_A01": {
        "type": "action",
        "name": "Hostile Takeover",
        "description": "Steal 1 stock from target (80% success, 20% fail = pay $50)",
        "requires_target": True
    },
    "PLACEHOLDER_A02": {
        "type": "action",
        "name": "Crypto Hack",
        "description": "Steal 20% of target's crypto value",
        "requires_target": True
    },
    "PLACEHOLDER_A03": {
        "type": "action",
        "name": "Insider Tip",
        "description": "Peek at next event card",
        "requires_target": False
    },
    "PLACEHOLDER_A04": {
        "type": "action",
        "name": "Market Manipulation",
        "description": "Choose one asset type: all players' values change +15%",
        "requires_target": False
    },
    "PLACEHOLDER_A05": {
        "type": "action",
        "name": "Asset Swap",
        "description": "Swap one asset type with target player",
        "requires_target": True
    },
    "PLACEHOLDER_A06": {
        "type": "action",
        "name": "Tax Haven",
        "description": "Immune to next Tax Audit",
        "requires_target": False
    },
    "PLACEHOLDER_A07": {
        "type": "action",
        "name": "Bank Loan",
        "description": "Borrow $500 (must repay $600 in 2 rounds)",
        "requires_target": False
    },
    "PLACEHOLDER_A08": {
        "type": "action",
        "name": "Charity Donation",
        "description": "Donate $100, gain immunity from one attack",
        "requires_target": False
    },
    "PLACEHOLDER_A09": {
        "type": "action",
        "name": "Bonus Dividend",
        "description": "Your stocks pay double dividend this round",
        "requires_target": False
    },
    "PLACEHOLDER_A10": {
        "type": "action",
        "name": "Sabotage",
        "description": "Target loses next dividend payment",
        "requires_target": True
    },
    
    # ==================== EVENT CARDS ====================
    "PLACEHOLDER_E01": {
        "type": "event",
        "name": "Market Boom",
        "description": "All stocks +15%, crypto +25%",
        "effects": {
            "stocks": 0.15,
            "crypto": 0.25
        }
    },
    "PLACEHOLDER_E02": {
        "type": "event",
        "name": "Recession",
        "description": "Stocks -20%, bonds +5%",
        "effects": {
            "stocks": -0.20,
            "bonds": 0.05
        }
    },
    "PLACEHOLDER_E03": {
        "type": "event",
        "name": "Crypto Crash",
        "description": "All crypto -30%",
        "effects": {
            "crypto": -0.30
        }
    },
    "PLACEHOLDER_E04": {
        "type": "event",
        "name": "Gold Rush",
        "description": "Commodities +20%",
        "effects": {
            "commodities": 0.20
        }
    },
    "PLACEHOLDER_E05": {
        "type": "event",
        "name": "Interest Rate Hike",
        "description": "Bonds +10%, stocks -5%",
        "effects": {
            "bonds": 0.10,
            "stocks": -0.05
        }
    },
    "PLACEHOLDER_E06": {
        "type": "event",
        "name": "Tech Bubble",
        "description": "Crypto +40%, stocks +10%",
        "effects": {
            "crypto": 0.40,
            "stocks": 0.10
        }
    },
    "PLACEHOLDER_E07": {
        "type": "event",
        "name": "Global Crisis",
        "description": "All assets -10% except bonds +8%",
        "effects": {
            "stocks": -0.10,
            "crypto": -0.10,
            "commodities": -0.10,
            "bonds": 0.08
        }
    },
    "PLACEHOLDER_E08": {
        "type": "event",
        "name": "Bull Market",
        "description": "Stocks +12%, commodities +8%",
        "effects": {
            "stocks": 0.12,
            "commodities": 0.08
        }
    },
    "PLACEHOLDER_E09": {
        "type": "event",
        "name": "Economic Stability",
        "description": "All assets +5%",
        "effects": {
            "stocks": 0.05,
            "crypto": 0.05,
            "bonds": 0.05,
            "commodities": 0.05
        }
    },
}

# Reverse lookup: get card info by RFID ID
def get_card(rfid_id):
    """Get card information by RFID ID"""
    return CARD_MAPPINGS.get(rfid_id, None)

# Check if ID is a player card
def is_player_card(rfid_id):
    """Check if RFID ID is a player wallet card"""
    card = get_card(rfid_id)
    return card and card["type"] == "player"

# Check if ID is a space card
def is_space_card(rfid_id):
    """Check if RFID ID is a board space card"""
    card = get_card(rfid_id)
    return card and card["type"] == "space"

# Check if ID is an action card
def is_action_card(rfid_id):
    """Check if RFID ID is an action card"""
    card = get_card(rfid_id)
    return card and card["type"] == "action"

# Check if ID is an event card
def is_event_card(rfid_id):
    """Check if RFID ID is an event card"""
    card = get_card(rfid_id)
    return card and card["type"] == "event"
