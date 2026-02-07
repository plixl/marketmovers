"""
Market Movers - Game State Management
Handles player data, game rounds, and state tracking
"""

import json
import random
from datetime import datetime
from config import *

class Player:
    """Represents a single player with their portfolio"""
    
    def __init__(self, rfid_id, name, color):
        self.id = rfid_id
        self.name = name
        self.color = color
        self.cash = STARTING_CASH
        self.assets = {
            "stocks": 0,
            "crypto": 0,
            "bonds": 0,
            "commodities": 0,
            "real_estate": []  # List of dicts: {"round_purchased": X}
        }
        self.active_effects = []  # Special status effects
        self.is_bankrupt = False
        
    def get_net_worth(self):
        """Calculate total net worth"""
        total = self.cash
        
        # Add asset values
        total += self.assets["stocks"] * ASSET_PRICES["stocks"]
        total += self.assets["crypto"] * ASSET_PRICES["crypto"]
        total += self.assets["bonds"] * ASSET_PRICES["bonds"]
        total += self.assets["commodities"] * ASSET_PRICES["commodities"]
        total += len(self.assets["real_estate"]) * ASSET_PRICES["real_estate"]
        
        return total
    
    def can_afford(self, amount):
        """Check if player has enough cash"""
        return self.cash >= amount
    
    def add_cash(self, amount):
        """Add cash to player"""
        self.cash += amount
        if self.cash < 0:
            self.is_bankrupt = True
    
    def deduct_cash(self, amount):
        """Deduct cash from player"""
        self.cash -= amount
        if self.cash < 0:
            self.is_bankrupt = True
    
    def buy_asset(self, asset_type, quantity=1):
        """Buy assets if player can afford them"""
        if asset_type == "real_estate":
            # Real estate is one-time purchase
            cost = ASSET_PRICES[asset_type]
            if self.can_afford(cost):
                self.deduct_cash(cost)
                self.assets["real_estate"].append({"round_purchased": 0})  # Round will be set externally
                return True
            return False
        else:
            # Regular assets
            cost = ASSET_PRICES[asset_type] * quantity
            if self.can_afford(cost):
                self.deduct_cash(cost)
                self.assets[asset_type] += quantity
                return True
            return False
    
    def sell_asset(self, asset_type, quantity=1):
        """Sell assets"""
        if asset_type == "real_estate":
            if len(self.assets["real_estate"]) > 0:
                self.assets["real_estate"].pop()
                self.add_cash(ASSET_PRICES[asset_type])
                return True
            return False
        else:
            if self.assets[asset_type] >= quantity:
                self.assets[asset_type] -= quantity
                self.add_cash(ASSET_PRICES[asset_type] * quantity)
                return True
            return False
    
    def apply_asset_change(self, asset_type, percentage):
        """Apply percentage change to asset value (for events/round updates)"""
        if asset_type in ["stocks", "crypto", "bonds", "commodities"]:
            current_value = self.assets[asset_type] * ASSET_PRICES[asset_type]
            change = int(current_value * percentage)
            # Update by changing the quantity equivalent
            new_value = current_value + change
            self.assets[asset_type] = max(0, int(new_value / ASSET_PRICES[asset_type]))
    
    def unlock_real_estate(self, current_round):
        """Unlock real estate that's past the lock period"""
        # Real estate unlocks automatically after REAL_ESTATE_LOCK_ROUNDS
        # This is just tracked for display purposes
        pass
    
    def to_dict(self):
        """Convert player to dictionary for saving"""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "cash": self.cash,
            "assets": self.assets,
            "active_effects": self.active_effects,
            "is_bankrupt": self.is_bankrupt
        }
    
    @staticmethod
    def from_dict(data):
        """Create player from dictionary"""
        player = Player(data["id"], data["name"], data["color"])
        player.cash = data["cash"]
        player.assets = data["assets"]
        player.active_effects = data.get("active_effects", [])
        player.is_bankrupt = data.get("is_bankrupt", False)
        return player


class GameState:
    """Manages the overall game state"""
    
    def __init__(self):
        self.round = 1
        self.max_rounds = MAX_ROUNDS
        self.players = {}  # {rfid_id: Player}
        self.current_player = None
        self.awaiting_target = False
        self.pending_action = None
        self.pending_asset_purchase = None  # {"player": id, "asset": type, "quantity": X}
        self.activity_log = []
        self.game_started = False
        self.game_over = False
        
    def register_player(self, rfid_id, name, color):
        """Register a new player"""
        if rfid_id not in self.players:
            self.players[rfid_id] = Player(rfid_id, name, color)
            self.log_activity(f"{name} joined the game!")
            return True
        return False
    
    def set_current_player(self, rfid_id):
        """Set the active player"""
        if rfid_id in self.players:
            self.current_player = rfid_id
            return True
        return False
    
    def get_current_player(self):
        """Get the current player object"""
        if self.current_player:
            return self.players.get(self.current_player)
        return None
    
    def get_player(self, rfid_id):
        """Get player by RFID ID"""
        return self.players.get(rfid_id)
    
    def get_active_players(self):
        """Get list of non-bankrupt players"""
        return [p for p in self.players.values() if not p.is_bankrupt]
    
    def advance_round(self):
        """Move to next round and apply round updates"""
        self.round += 1
        
        if self.round > self.max_rounds:
            self.end_game()
            return
        
        # Apply random returns to all player assets
        for player in self.players.values():
            if not player.is_bankrupt:
                self.apply_round_returns(player)
        
        self.log_activity(f"=== ROUND {self.round} STARTED ===")
    
    def apply_round_returns(self, player):
        """Apply random asset returns for a player"""
        for asset_type, return_range in ASSET_RETURNS.items():
            if player.assets[asset_type] > 0:
                # Random return within range
                return_rate = random.uniform(return_range["min"], return_range["max"])
                old_value = player.assets[asset_type] * ASSET_PRICES[asset_type]
                player.apply_asset_change(asset_type, return_rate)
                new_value = player.assets[asset_type] * ASSET_PRICES[asset_type]
                change = new_value - old_value
                
                if change != 0:
                    sign = "+" if change > 0 else ""
                    self.log_activity(f"{player.name}'s {asset_type}: {sign}${change}")
    
    def apply_event(self, event_card):
        """Apply event card effects to all players"""
        event_name = event_card["name"]
        effects = event_card.get("effects", {})
        
        self.log_activity(f"EVENT: {event_name} - {event_card['description']}")
        
        for player in self.players.values():
            if not player.is_bankrupt:
                for asset_type, percentage in effects.items():
                    if player.assets[asset_type] > 0:
                        old_value = player.assets[asset_type] * ASSET_PRICES[asset_type]
                        player.apply_asset_change(asset_type, percentage)
                        new_value = player.assets[asset_type] * ASSET_PRICES[asset_type]
                        change = new_value - old_value
                        
                        if change != 0:
                            sign = "+" if change > 0 else ""
                            self.log_activity(f"  {player.name}'s {asset_type}: {sign}${change}")
    
    def log_activity(self, message):
        """Add activity to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.activity_log.append(log_entry)
        
        # Keep only last 50 entries
        if len(self.activity_log) > 50:
            self.activity_log.pop(0)
        
        # Also write to file
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    
    def end_game(self):
        """End the game and calculate winners"""
        self.game_over = True
        self.log_activity("=== GAME OVER ===")
        
        # Sort players by net worth
        rankings = sorted(
            self.players.values(),
            key=lambda p: p.get_net_worth(),
            reverse=True
        )
        
        self.log_activity("FINAL RANKINGS:")
        for i, player in enumerate(rankings, 1):
            self.log_activity(f"{i}. {player.name}: ${player.get_net_worth()}")
    
    def check_bankruptcy(self):
        """Check if any players are bankrupt"""
        active_players = self.get_active_players()
        if len(active_players) <= 1 and len(self.players) > 1:
            # Only one player left
            self.end_game()
    
    def save_state(self, filename="game_save.json"):
        """Save game state to file"""
        data = {
            "round": self.round,
            "max_rounds": self.max_rounds,
            "players": {pid: p.to_dict() for pid, p in self.players.items()},
            "current_player": self.current_player,
            "game_started": self.game_started,
            "game_over": self.game_over,
            "activity_log": self.activity_log[-20:]  # Save last 20 entries
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_state(filename="game_save.json"):
        """Load game state from file"""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            
            game = GameState()
            game.round = data["round"]
            game.max_rounds = data["max_rounds"]
            game.players = {pid: Player.from_dict(p) for pid, p in data["players"].items()}
            game.current_player = data["current_player"]
            game.game_started = data["game_started"]
            game.game_over = data["game_over"]
            game.activity_log = data.get("activity_log", [])
            
            return game
        except:
            return GameState()
