"""
Market Movers - Main Game Loop
Orchestrates RFID, buttons, game logic, and UI
"""

import sys
import time
from game_state import GameState
from card_processor import CardProcessor
from rfid_handler import create_rfid_handler
from button_handler import create_button_handler
from ui_display import GameUI
from card_registry import *
from config import *

class MarketMoversGame:
    """Main game controller"""
    
    def __init__(self, simulate=False):
        print("=" * 50)
        print("MARKET MOVERS - Banking Unit")
        print("=" * 50)
        
        # Initialize components
        self.game_state = GameState()
        self.card_processor = CardProcessor(self.game_state)
        self.rfid = create_rfid_handler(simulate=simulate)
        self.buttons = create_button_handler(simulate=simulate)
        self.ui = GameUI(fullscreen=not simulate)  # Windowed mode for simulation
        
        # Game flow state
        self.current_message = "Scan a player wallet card to begin"
        self.awaiting_action_card = False
        self.awaiting_event_card = False
        self.awaiting_target = False
        self.awaiting_purchase = None  # Asset type being purchased
        self.purchase_quantity = 0
        self.pending_action = None
        self.last_space_card = None
        
        print("\n✓ Game initialized!")
        print("Ready to play!\n")
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle pygame events
            if not self.ui.handle_events():
                running = False
                break
            
            # Check for game over
            if self.game_state.game_over:
                self.ui.render_game_over(self.game_state)
                time.sleep(0.1)
                continue
            
            # Check for RFID scans
            rfid_id = self.rfid.check_for_scan()
            if rfid_id:
                self.handle_rfid_scan(rfid_id)
            
            # Check for button presses
            button = self.buttons.check_any_button()
            if button is not None:
                self.handle_button_press(button)
            
            # Render UI
            self.ui.render_main_screen(self.game_state, self.current_message)
            
            # Small delay to prevent CPU overuse
            time.sleep(0.05)
        
        # Cleanup
        self.game_state.save_state()
        self.ui.cleanup()
        print("\nGame saved. Thanks for playing!")
    
    def handle_rfid_scan(self, rfid_id):
        """Process RFID card scan"""
        print(f"[SCAN] {rfid_id}")
        
        # Get card info
        card = get_card(rfid_id)
        
        if not card:
            self.current_message = f"Unknown card: {rfid_id}\nPlease register this card"
            print(f"  → Unknown card")
            return
        
        # Route to appropriate handler
        if card["type"] == "player":
            self.handle_player_scan(rfid_id, card)
        elif card["type"] == "space":
            self.handle_space_scan(rfid_id, card)
        elif card["type"] == "action":
            self.handle_action_scan(rfid_id, card)
        elif card["type"] == "event":
            self.handle_event_scan(rfid_id, card)
    
    def handle_player_scan(self, rfid_id, card):
        """Handle player wallet card scan"""
        # Register player if new
        if rfid_id not in self.game_state.players:
            self.game_state.register_player(rfid_id, card["name"], card["color"])
            self.current_message = f"{card['name']} registered!\nScan your card again to start your turn"
            return
        
        player = self.game_state.get_player(rfid_id)
        
        # Check if player is bankrupt
        if player.is_bankrupt:
            self.current_message = f"{player.name} is bankrupt!"
            return
        
        # Check if we're awaiting a target player
        if self.awaiting_target:
            self.handle_target_scan(rfid_id, card)
            return
        
        # Set as current player
        self.game_state.set_current_player(rfid_id)
        self.current_message = f"{player.name}'s turn!\nScan a space or action card"
        
        # Reset pending states
        self.awaiting_action_card = False
        self.awaiting_event_card = False
        self.awaiting_purchase = None
        self.purchase_quantity = 0
        
        print(f"  → {player.name} selected (${player.cash})")
    
    def handle_space_scan(self, rfid_id, card):
        """Handle board space card scan"""
        current_player = self.game_state.get_current_player()
        
        if not current_player:
            self.current_message = "Scan your player wallet card first!"
            return
        
        space_name = card["name"]
        print(f"  → Space: {space_name}")
        
        # Check if this is a repeat scan for purchasing
        if self.awaiting_purchase and rfid_id == self.last_space_card:
            self.handle_purchase_repeat(current_player)
            return
        
        # Process space effect
        result = self.card_processor.process_space_card(card, current_player)
        
        if result["success"]:
            self.current_message = result["message"]
            
            # Check for special states
            if result.get("await_action_card"):
                self.awaiting_action_card = True
            elif result.get("await_event_card"):
                self.awaiting_event_card = True
            elif result.get("await_purchase"):
                self.awaiting_purchase = result["await_purchase"]
                self.purchase_quantity = 0
                self.last_space_card = rfid_id
            
            # Auto-complete if no further action needed
            if result.get("auto_complete"):
                self.game_state.check_bankruptcy()
        else:
            self.current_message = result["message"]
    
    def handle_action_scan(self, rfid_id, card):
        """Handle action card scan"""
        # Check if we're on an action space or if action was awaited
        if not self.awaiting_action_card:
            current_player = self.game_state.get_current_player()
            if not current_player:
                self.current_message = "Scan your player wallet card first!"
                return
        
        current_player = self.game_state.get_current_player()
        action_name = card["name"]
        print(f"  → Action: {action_name}")
        
        # Check if action requires target
        if card.get("requires_target"):
            self.awaiting_target = True
            self.pending_action = card
            self.current_message = f"{action_name}\nScan target player's wallet card"
        else:
            # Execute action immediately
            result = self.card_processor.process_action_card(card, current_player)
            self.current_message = result["message"]
            self.awaiting_action_card = False
    
    def handle_event_scan(self, rfid_id, card):
        """Handle event card scan"""
        if not self.awaiting_event_card:
            self.current_message = "Event cards can only be used on Event spaces"
            return
        
        event_name = card["name"]
        print(f"  → Event: {event_name}")
        
        # Apply event to all players
        self.game_state.apply_event(card)
        self.current_message = f"{event_name}\n{card['description']}"
        self.awaiting_event_card = False
        
        self.game_state.check_bankruptcy()
    
    def handle_target_scan(self, rfid_id, card):
        """Handle target player scan for action cards"""
        if card["type"] != "player":
            self.current_message = "Please scan a player wallet card as target"
            return
        
        current_player = self.game_state.get_current_player()
        target_player = self.game_state.get_player(rfid_id)
        
        if not target_player:
            self.current_message = "Unknown player!"
            return
        
        if target_player.id == current_player.id:
            self.current_message = "Cannot target yourself!"
            return
        
        # Execute action with target
        result = self.card_processor.process_action_card(
            self.pending_action, 
            current_player, 
            target_player
        )
        
        self.current_message = result["message"]
        self.awaiting_target = False
        self.pending_action = None
        
        self.game_state.check_bankruptcy()
    
    def handle_purchase_repeat(self, player):
        """Handle repeated space scan to purchase assets"""
        asset_type = self.awaiting_purchase
        price = ASSET_PRICES[asset_type]
        
        if player.can_afford(price):
            player.buy_asset(asset_type, 1)
            self.purchase_quantity += 1
            self.game_state.log_activity(f"{player.name} bought 1 {asset_type} for ${price}")
            self.current_message = f"Bought {self.purchase_quantity} {asset_type}! (${price} each)\nScan again to buy more, or press GREEN to finish"
            print(f"  → Purchased 1 {asset_type} (total: {self.purchase_quantity})")
        else:
            self.current_message = f"Not enough cash! Need ${price}\nPress GREEN to finish"
    
    def handle_button_press(self, button_id):
        """Handle button press"""
        if button_id == self.buttons.BTN_CONFIRM:
            self.handle_confirm()
        elif button_id == self.buttons.BTN_CANCEL:
            self.handle_cancel()
        elif button_id == self.buttons.BTN_ROUND:
            self.handle_next_round()
    
    def handle_confirm(self):
        """Handle GREEN button (confirm)"""
        print("[BUTTON] Confirm")
        
        # Complete pending purchase
        if self.awaiting_purchase:
            self.current_message = f"Purchase complete! Bought {self.purchase_quantity} {self.awaiting_purchase}"
            self.awaiting_purchase = None
            self.purchase_quantity = 0
            self.last_space_card = None
        else:
            # Generic confirmation
            self.current_message = "Action confirmed"
    
    def handle_cancel(self):
        """Handle RED button (cancel)"""
        print("[BUTTON] Cancel")
        
        # Cancel pending actions
        if self.awaiting_purchase:
            self.current_message = "Purchase cancelled"
            self.awaiting_purchase = None
            self.purchase_quantity = 0
            self.last_space_card = None
        elif self.awaiting_target:
            self.current_message = "Action cancelled"
            self.awaiting_target = False
            self.pending_action = None
        elif self.awaiting_action_card or self.awaiting_event_card:
            self.current_message = "Waiting for card cancelled"
            self.awaiting_action_card = False
            self.awaiting_event_card = False
        else:
            # Reset current player
            if self.game_state.current_player:
                player = self.game_state.get_current_player()
                self.current_message = f"{player.name}'s turn cancelled"
            self.game_state.current_player = None
            self.current_message = "Turn cancelled. Scan player card to begin"
    
    def handle_next_round(self):
        """Handle BLUE button (next round)"""
        print("[BUTTON] Next Round")
        
        if self.game_state.round >= self.game_state.max_rounds:
            self.game_state.end_game()
        else:
            self.game_state.advance_round()
            self.current_message = f"Round {self.game_state.round} started!"
            
            # Reset turn
            self.game_state.current_player = None
            self.awaiting_purchase = None
            self.awaiting_action_card = False
            self.awaiting_event_card = False
            self.awaiting_target = False


def main():
    """Entry point"""
    # Check for simulation mode argument
    simulate = "--simulate" in sys.argv or "-s" in sys.argv
    
    if simulate:
        print("\n⚠️  SIMULATION MODE")
        print("Hardware not required for testing\n")
    
    # Create and run game
    game = MarketMoversGame(simulate=simulate)
    
    try:
        game.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
        game.game_state.save_state()
        game.ui.cleanup()
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        game.game_state.save_state()
        game.ui.cleanup()


if __name__ == "__main__":
    main()
