"""
Market Movers - Card Processor
Handles all card-specific logic (spaces, actions, events)
"""

import random
from config import *

class CardProcessor:
    """Processes different card types and their effects"""
    
    def __init__(self, game_state):
        self.game = game_state
    
    def process_space_card(self, space_card, player):
        """Process board space card effects"""
        space_name = space_card["name"]
        
        # Define handlers for each space
        handlers = {
            "Payday": self.handle_payday,
            "Stock Exchange": self.handle_stock_exchange,
            "Action Space": self.handle_action_space,
            "Crypto Hub": self.handle_crypto_hub,
            "Event Space": self.handle_event_space,
            "Bond Market": self.handle_bond_market,
            "Real Estate": self.handle_real_estate,
            "Dividend": self.handle_dividend,
            "Commodity Trade": self.handle_commodity_trade,
            "Global Event": self.handle_global_event,
            "Startup Incubator": self.handle_startup,
            "Tax Audit": self.handle_tax_audit,
            "Market Reset": self.handle_market_reset
        }
        
        handler = handlers.get(space_name)
        if handler:
            return handler(player)
        
        return {"success": False, "message": f"Unknown space: {space_name}"}
    
    def handle_payday(self, player):
        """Give player $200"""
        player.add_cash(PAYDAY_AMOUNT)
        self.game.log_activity(f"{player.name} collected ${PAYDAY_AMOUNT} from Payday")
        return {
            "success": True,
            "message": f"Payday! +${PAYDAY_AMOUNT}",
            "auto_complete": True
        }
    
    def handle_stock_exchange(self, player):
        """Initiate stock purchase"""
        return {
            "success": True,
            "message": f"Stock Exchange: ${ASSET_PRICES['stocks']} per stock\nScan again to buy, or press GREEN to finish",
            "await_purchase": "stocks",
            "auto_complete": False
        }
    
    def handle_action_space(self, player):
        """Prompt to scan action card"""
        return {
            "success": True,
            "message": "Action Space! Scan an Action card",
            "await_action_card": True,
            "auto_complete": False
        }
    
    def handle_crypto_hub(self, player):
        """Initiate crypto purchase"""
        return {
            "success": True,
            "message": f"Crypto Hub: ${ASSET_PRICES['crypto']} per crypto\nScan again to buy, or press GREEN to finish",
            "await_purchase": "crypto",
            "auto_complete": False
        }
    
    def handle_event_space(self, player):
        """Prompt to scan event card"""
        return {
            "success": True,
            "message": "Event Space! Scan an Event card",
            "await_event_card": True,
            "auto_complete": False
        }
    
    def handle_bond_market(self, player):
        """Initiate bond purchase"""
        return {
            "success": True,
            "message": f"Bond Market: ${ASSET_PRICES['bonds']} per bond\nScan again to buy, or press GREEN to finish",
            "await_purchase": "bonds",
            "auto_complete": False
        }
    
    def handle_real_estate(self, player):
        """Purchase real estate"""
        if player.can_afford(ASSET_PRICES["real_estate"]):
            player.buy_asset("real_estate")
            # Set purchase round
            player.assets["real_estate"][-1]["round_purchased"] = self.game.round
            self.game.log_activity(f"{player.name} bought Real Estate for ${ASSET_PRICES['real_estate']}")
            return {
                "success": True,
                "message": f"Real Estate purchased! -${ASSET_PRICES['real_estate']}\n(Locked for {REAL_ESTATE_LOCK_ROUNDS} rounds)",
                "auto_complete": True
            }
        else:
            return {
                "success": False,
                "message": f"Not enough cash! Need ${ASSET_PRICES['real_estate']}",
                "auto_complete": True
            }
    
    def handle_dividend(self, player):
        """Pay dividends on stocks and bonds"""
        stock_value = player.assets["stocks"] * ASSET_PRICES["stocks"]
        bond_value = player.assets["bonds"] * ASSET_PRICES["bonds"]
        total_dividend = int((stock_value + bond_value) * DIVIDEND_PERCENT)
        
        if total_dividend > 0:
            player.add_cash(total_dividend)
            self.game.log_activity(f"{player.name} received ${total_dividend} in dividends")
            return {
                "success": True,
                "message": f"Dividend Payment! +${total_dividend}",
                "auto_complete": True
            }
        else:
            return {
                "success": True,
                "message": "No stocks or bonds to pay dividends",
                "auto_complete": True
            }
    
    def handle_commodity_trade(self, player):
        """Initiate commodity purchase"""
        return {
            "success": True,
            "message": f"Commodity Trade: ${ASSET_PRICES['commodities']} per unit\nScan again to buy, or press GREEN to finish",
            "await_purchase": "commodities",
            "auto_complete": False
        }
    
    def handle_global_event(self, player):
        """Prompt to scan event card (same as Event Space)"""
        return {
            "success": True,
            "message": "Global Event! Scan an Event card",
            "await_event_card": True,
            "auto_complete": False
        }
    
    def handle_startup(self, player):
        """50/50 gamble"""
        success = random.random() < STARTUP_SUCCESS_RATE
        
        if success:
            player.add_cash(STARTUP_WIN_AMOUNT)
            self.game.log_activity(f"{player.name} won ${STARTUP_WIN_AMOUNT} from Startup!")
            return {
                "success": True,
                "message": f"🎉 Startup Success! +${STARTUP_WIN_AMOUNT}",
                "auto_complete": True
            }
        else:
            player.deduct_cash(STARTUP_LOSE_AMOUNT)
            self.game.log_activity(f"{player.name} lost ${STARTUP_LOSE_AMOUNT} on Startup")
            return {
                "success": True,
                "message": f"💥 Startup Failed! -${STARTUP_LOSE_AMOUNT}",
                "auto_complete": True
            }
    
    def handle_tax_audit(self, player):
        """Player pays tax"""
        # Check if player has tax haven immunity
        if "tax_haven" in player.active_effects:
            player.active_effects.remove("tax_haven")
            self.game.log_activity(f"{player.name} used Tax Haven immunity")
            return {
                "success": True,
                "message": "Tax Haven activated! No tax paid",
                "auto_complete": True
            }
        
        player.deduct_cash(TAX_AUDIT_AMOUNT)
        self.game.log_activity(f"{player.name} paid ${TAX_AUDIT_AMOUNT} in taxes")
        return {
            "success": True,
            "message": f"Tax Audit! -${TAX_AUDIT_AMOUNT}",
            "auto_complete": True
        }
    
    def handle_market_reset(self, player):
        """Revalue all assets randomly"""
        self.game.log_activity("MARKET RESET - All assets revalued!")
        
        for p in self.game.players.values():
            if not p.is_bankrupt:
                self.game.apply_round_returns(p)
        
        return {
            "success": True,
            "message": "Market Reset! All assets revalued",
            "auto_complete": True
        }
    
    def process_action_card(self, action_card, player, target_player=None):
        """Process action card effects"""
        action_name = action_card["name"]
        
        handlers = {
            "Hostile Takeover": self.action_hostile_takeover,
            "Crypto Hack": self.action_crypto_hack,
            "Insider Tip": self.action_insider_tip,
            "Market Manipulation": self.action_market_manipulation,
            "Asset Swap": self.action_asset_swap,
            "Tax Haven": self.action_tax_haven,
            "Bank Loan": self.action_bank_loan,
            "Charity Donation": self.action_charity,
            "Bonus Dividend": self.action_bonus_dividend,
            "Sabotage": self.action_sabotage
        }
        
        handler = handlers.get(action_name)
        if handler:
            return handler(player, target_player)
        
        return {"success": False, "message": f"Unknown action: {action_name}"}
    
    def action_hostile_takeover(self, player, target):
        """Steal 1 stock from target (80% success)"""
        if not target:
            return {"success": False, "message": "Scan target player's card"}
        
        if target.assets["stocks"] < 1:
            return {"success": False, "message": f"{target.name} has no stocks to steal!"}
        
        success = random.random() < HOSTILE_TAKEOVER_SUCCESS
        
        if success:
            target.assets["stocks"] -= 1
            player.assets["stocks"] += 1
            self.game.log_activity(f"{player.name} used Hostile Takeover on {target.name}: stole 1 stock")
            return {"success": True, "message": f"Hostile Takeover successful! Stole 1 stock from {target.name}"}
        else:
            player.deduct_cash(HOSTILE_TAKEOVER_FINE)
            self.game.log_activity(f"{player.name}'s Hostile Takeover failed: paid ${HOSTILE_TAKEOVER_FINE}")
            return {"success": True, "message": f"Hostile Takeover failed! Pay ${HOSTILE_TAKEOVER_FINE} fine"}
    
    def action_crypto_hack(self, player, target):
        """Steal 20% of target's crypto"""
        if not target:
            return {"success": False, "message": "Scan target player's card"}
        
        crypto_value = target.assets["crypto"] * ASSET_PRICES["crypto"]
        if crypto_value == 0:
            return {"success": False, "message": f"{target.name} has no crypto!"}
        
        stolen_value = int(crypto_value * 0.20)
        stolen_units = int(target.assets["crypto"] * 0.20)
        
        target.assets["crypto"] -= stolen_units
        player.add_cash(stolen_value)
        
        self.game.log_activity(f"{player.name} used Crypto Hack on {target.name}: stole ${stolen_value}")
        return {"success": True, "message": f"Crypto Hack! Stole ${stolen_value} from {target.name}"}
    
    def action_insider_tip(self, player, target):
        """Reveal next event (informational only)"""
        self.game.log_activity(f"{player.name} used Insider Tip")
        return {
            "success": True,
            "message": "Insider Tip activated!\n(Next Event card will reveal market info)"
        }
    
    def action_market_manipulation(self, player, target):
        """Boost one asset type by 15% for all players"""
        # This would require UI input to choose asset type
        # For now, randomly choose
        asset_type = random.choice(["stocks", "crypto", "bonds", "commodities"])
        
        for p in self.game.players.values():
            if not p.is_bankrupt:
                p.apply_asset_change(asset_type, 0.15)
        
        self.game.log_activity(f"{player.name} manipulated the market: {asset_type} +15% for all")
        return {"success": True, "message": f"Market Manipulation! All {asset_type} +15%"}
    
    def action_asset_swap(self, player, target):
        """Swap one asset type with target"""
        if not target:
            return {"success": False, "message": "Scan target player's card"}
        
        # Randomly choose asset type to swap
        asset_type = random.choice(["stocks", "crypto", "bonds", "commodities"])
        
        player.assets[asset_type], target.assets[asset_type] = \
            target.assets[asset_type], player.assets[asset_type]
        
        self.game.log_activity(f"{player.name} swapped {asset_type} with {target.name}")
        return {"success": True, "message": f"Asset Swap! Traded {asset_type} with {target.name}"}
    
    def action_tax_haven(self, player, target):
        """Grant immunity to next tax audit"""
        player.active_effects.append("tax_haven")
        self.game.log_activity(f"{player.name} activated Tax Haven")
        return {"success": True, "message": "Tax Haven! Immune to next Tax Audit"}
    
    def action_bank_loan(self, player, target):
        """Borrow $500, must repay $600 in 2 rounds"""
        player.add_cash(500)
        player.active_effects.append({"type": "loan", "due_round": self.game.round + 2, "amount": 600})
        self.game.log_activity(f"{player.name} took a bank loan: +$500 (repay $600 by round {self.game.round + 2})")
        return {"success": True, "message": f"Bank Loan! +$500\n(Repay $600 by round {self.game.round + 2})"}
    
    def action_charity(self, player, target):
        """Donate $100, gain attack immunity"""
        if player.can_afford(100):
            player.deduct_cash(100)
            player.active_effects.append("charity_shield")
            self.game.log_activity(f"{player.name} donated $100 to charity")
            return {"success": True, "message": "Charity! -$100, immunity from next attack"}
        else:
            return {"success": False, "message": "Not enough cash to donate!"}
    
    def action_bonus_dividend(self, player, target):
        """Double dividend this round"""
        player.active_effects.append("bonus_dividend")
        self.game.log_activity(f"{player.name} activated Bonus Dividend")
        return {"success": True, "message": "Bonus Dividend! Your stocks pay double next dividend"}
    
    def action_sabotage(self, player, target):
        """Target loses next dividend"""
        if not target:
            return {"success": False, "message": "Scan target player's card"}
        
        target.active_effects.append("no_dividend")
        self.game.log_activity(f"{player.name} sabotaged {target.name}")
        return {"success": True, "message": f"Sabotage! {target.name} loses next dividend"}
