"""
Market Movers - UI Display
Pygame-based UI for HDMI display
"""

import pygame
import sys
from config import *

class GameUI:
    """Handles all visual display using Pygame"""
    
    def __init__(self, fullscreen=True):
        pygame.init()
        
        # Set up display
        if fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Market Movers")
        
        # Load fonts
        self.font_title = pygame.font.Font(None, FONT_TITLE)
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        self.clock = pygame.time.Clock()
        
        print("✓ Display initialized")
    
    def draw_text(self, text, font, color, x, y, align="left"):
        """Draw text at position with alignment"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        if align == "center":
            text_rect.center = (x, y)
        elif align == "right":
            text_rect.right = x
            text_rect.top = y
        else:  # left
            text_rect.left = x
            text_rect.top = y
        
        self.screen.blit(text_surface, text_rect)
        return text_rect.bottom
    
    def draw_card(self, x, y, width, height, color=COLOR_CARD_BG):
        """Draw a rounded rectangle card"""
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=15)
    
    def draw_button_hint(self, x, y, color, label):
        """Draw a button hint indicator"""
        # Draw circle
        pygame.draw.circle(self.screen, color, (x, y), 20)
        # Draw label
        self.draw_text(label, self.font_small, COLOR_TEXT, x + 35, y - 12, align="left")
    
    def render_main_screen(self, game_state, message=""):
        """Render the main game screen"""
        self.screen.fill(COLOR_BG)
        
        # Header
        header_y = 40
        self.draw_text("MARKET MOVERS", self.font_title, COLOR_PRIMARY, SCREEN_WIDTH // 2, header_y, align="center")
        
        # Round indicator
        round_text = f"Round {game_state.round}/{game_state.max_rounds}"
        self.draw_text(round_text, self.font_large, COLOR_TEXT, SCREEN_WIDTH - 50, header_y, align="right")
        
        # Current player section
        current_player = game_state.get_current_player()
        player_y = 180
        
        if current_player:
            self._render_player_info(current_player, player_y)
        else:
            self.draw_text("Scan player wallet card to begin", self.font_large, COLOR_TEXT_DIM, 
                          SCREEN_WIDTH // 2, player_y + 100, align="center")
        
        # Activity log
        log_y = 650
        self._render_activity_log(game_state.activity_log, log_y)
        
        # Message/prompt area
        if message:
            msg_y = 900
            self.draw_card(50, msg_y - 20, SCREEN_WIDTH - 100, 120, COLOR_CARD_BG)
            
            # Split multiline messages
            lines = message.split('\n')
            for i, line in enumerate(lines):
                self.draw_text(line, self.font_medium, COLOR_WARNING, SCREEN_WIDTH // 2, 
                              msg_y + (i * 40), align="center")
        
        # Button hints at bottom
        self._render_button_hints()
        
        pygame.display.flip()
        self.clock.tick(FPS)
    
    def _render_player_info(self, player, y):
        """Render current player information"""
        # Player name card
        card_width = 800
        card_x = (SCREEN_WIDTH - card_width) // 2
        self.draw_card(card_x, y, card_width, 400, COLOR_CARD_BG)
        
        # Player name with color indicator
        name_y = y + 30
        pygame.draw.circle(self.screen, player.color, (card_x + 40, name_y + 20), 15)
        self.draw_text(player.name, self.font_large, COLOR_TEXT, card_x + 70, name_y)
        
        # Cash
        cash_y = name_y + 60
        cash_color = COLOR_SUCCESS if player.cash >= 0 else COLOR_DANGER
        self.draw_text(f"Cash: ${player.cash}", self.font_large, cash_color, card_x + 40, cash_y)
        
        # Portfolio
        portfolio_y = cash_y + 80
        self.draw_text("PORTFOLIO:", self.font_medium, COLOR_TEXT_DIM, card_x + 40, portfolio_y)
        
        # Assets in 2 columns
        asset_y = portfolio_y + 50
        col1_x = card_x + 60
        col2_x = card_x + 420
        
        # Column 1
        stock_val = player.assets["stocks"] * ASSET_PRICES["stocks"]
        self.draw_text(f"📈 Stocks: {player.assets['stocks']} (${stock_val})", 
                      self.font_small, COLOR_TEXT, col1_x, asset_y)
        
        crypto_val = player.assets["crypto"] * ASSET_PRICES["crypto"]
        self.draw_text(f"🪙 Crypto: {player.assets['crypto']} (${crypto_val})", 
                      self.font_small, COLOR_TEXT, col1_x, asset_y + 35)
        
        # Column 2
        bond_val = player.assets["bonds"] * ASSET_PRICES["bonds"]
        self.draw_text(f"📊 Bonds: {player.assets['bonds']} (${bond_val})", 
                      self.font_small, COLOR_TEXT, col2_x, asset_y)
        
        commodity_val = player.assets["commodities"] * ASSET_PRICES["commodities"]
        self.draw_text(f"📦 Commodities: {player.assets['commodities']} (${commodity_val})", 
                      self.font_small, COLOR_TEXT, col2_x, asset_y + 35)
        
        # Real estate (full width)
        re_count = len(player.assets["real_estate"])
        re_val = re_count * ASSET_PRICES["real_estate"]
        self.draw_text(f"🏠 Real Estate: {re_count} (${re_val})", 
                      self.font_small, COLOR_TEXT, col1_x, asset_y + 75)
        
        # Net worth
        net_worth = player.get_net_worth()
        self.draw_text(f"NET WORTH: ${net_worth}", self.font_medium, COLOR_PRIMARY, 
                      card_x + 40, asset_y + 120)
    
    def _render_activity_log(self, log, y):
        """Render recent activity log"""
        self.draw_text("RECENT ACTIVITY:", self.font_medium, COLOR_TEXT_DIM, 50, y)
        
        log_y = y + 45
        # Show last 5 activities
        recent_logs = log[-5:] if len(log) > 5 else log
        
        for entry in recent_logs:
            # Remove timestamp for cleaner display
            if ']' in entry:
                display_text = entry.split('] ', 1)[1] if '] ' in entry else entry
            else:
                display_text = entry
            
            self.draw_text(f"→ {display_text}", self.font_small, COLOR_TEXT, 70, log_y)
            log_y += 35
    
    def _render_button_hints(self):
        """Render button hints at bottom of screen"""
        hint_y = SCREEN_HEIGHT - 60
        spacing = 300
        start_x = (SCREEN_WIDTH - (spacing * 2)) // 2
        
        self.draw_button_hint(start_x, hint_y, BTN_GREEN, "CONFIRM")
        self.draw_button_hint(start_x + spacing, hint_y, BTN_RED, "CANCEL")
        self.draw_button_hint(start_x + spacing * 2, hint_y, BTN_BLUE, "NEXT ROUND")
    
    def render_game_over(self, game_state):
        """Render game over screen with rankings"""
        self.screen.fill(COLOR_BG)
        
        # Title
        self.draw_text("GAME OVER", self.font_title, COLOR_PRIMARY, SCREEN_WIDTH // 2, 100, align="center")
        
        # Get rankings
        rankings = sorted(
            game_state.players.values(),
            key=lambda p: p.get_net_worth(),
            reverse=True
        )
        
        # Leaderboard
        self.draw_text("FINAL RANKINGS", self.font_large, COLOR_TEXT, SCREEN_WIDTH // 2, 220, align="center")
        
        podium_y = 320
        for i, player in enumerate(rankings, 1):
            # Determine medal/color
            if i == 1:
                medal = "🥇"
                color = (255, 215, 0)  # Gold
            elif i == 2:
                medal = "🥈"
                color = (192, 192, 192)  # Silver
            elif i == 3:
                medal = "🥉"
                color = (205, 127, 50)  # Bronze
            else:
                medal = f"{i}."
                color = COLOR_TEXT
            
            # Draw ranking card
            card_height = 100
            card_y = podium_y + ((i - 1) * 120)
            self.draw_card(200, card_y, SCREEN_WIDTH - 400, card_height, COLOR_CARD_BG)
            
            # Medal/rank
            self.draw_text(medal, self.font_large, color, 250, card_y + 30)
            
            # Player name
            pygame.draw.circle(self.screen, player.color, (370, card_y + 50), 15)
            self.draw_text(player.name, self.font_large, COLOR_TEXT, 400, card_y + 25)
            
            # Net worth
            net_worth = player.get_net_worth()
            self.draw_text(f"${net_worth}", self.font_large, COLOR_SUCCESS, 
                          SCREEN_WIDTH - 250, card_y + 25, align="right")
        
        # Exit hint
        self.draw_text("Press ESC to exit", self.font_small, COLOR_TEXT_DIM, 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, align="center")
        
        pygame.display.flip()
    
    def render_registration_screen(self, step, message):
        """Render card registration screen"""
        self.screen.fill(COLOR_BG)
        
        # Title
        self.draw_text("CARD REGISTRATION", self.font_title, COLOR_PRIMARY, 
                      SCREEN_WIDTH // 2, 100, align="center")
        
        # Instructions
        self.draw_text("Setting up your game cards...", self.font_medium, COLOR_TEXT_DIM, 
                      SCREEN_WIDTH // 2, 200, align="center")
        
        # Current step
        step_y = 350
        self.draw_card(200, step_y - 20, SCREEN_WIDTH - 400, 200, COLOR_CARD_BG)
        
        self.draw_text(f"Step {step}", self.font_large, COLOR_PRIMARY, 
                      SCREEN_WIDTH // 2, step_y, align="center")
        
        self.draw_text(message, self.font_medium, COLOR_TEXT, 
                      SCREEN_WIDTH // 2, step_y + 80, align="center")
        
        # Hint
        self.draw_text("Scan card when ready, or press RED to skip", self.font_small, COLOR_TEXT_DIM, 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, align="center")
        
        pygame.display.flip()
    
    def handle_events(self):
        """Handle pygame events (mainly for quitting)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def cleanup(self):
        """Clean up pygame"""
        pygame.quit()
