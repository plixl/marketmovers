"""
Market Movers - UI Display
Pygame-based UI optimized for 5-inch (800x480) display
"""

import pygame
import sys
from config import *

class GameUI:
    """Handles all visual display using Pygame - optimized for small screens"""
    
    def __init__(self, fullscreen=True):
        pygame.init()
        
        # Set up display
        if fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Market Movers")
        
        # Load fonts - smaller for 5-inch screen
        self.font_title = pygame.font.Font(None, FONT_TITLE)
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        self.clock = pygame.time.Clock()
        
        print("✓ Display initialized (5-inch optimized)")
    
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
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=8)
    
    def render_main_screen(self, game_state, message=""):
        """Render the main game screen - compact layout"""
        self.screen.fill(COLOR_BG)
        
        # Header - compact
        self.draw_text("MARKET MOVERS", self.font_large, COLOR_PRIMARY, SCREEN_WIDTH // 2, 10, align="center")
        round_text = f"Round {game_state.round}/{game_state.max_rounds}"
        self.draw_text(round_text, self.font_small, COLOR_TEXT_DIM, SCREEN_WIDTH - 10, 10, align="right")
        
        # Current player section - compact
        current_player = game_state.get_current_player()
        
        if current_player:
            self._render_compact_player(current_player, 50)
        else:
            self.draw_text("Scan wallet to begin", self.font_medium, COLOR_TEXT_DIM, 
                          SCREEN_WIDTH // 2, 100, align="center")
        
        # Message area - prominent
        if message:
            msg_y = 250
            self.draw_card(10, msg_y, SCREEN_WIDTH - 20, 100, COLOR_CARD_BG)
            
            # Split lines
            lines = message.split('\n')
            for i, line in enumerate(lines[:3]):  # Max 3 lines
                self.draw_text(line, self.font_medium, COLOR_WARNING, SCREEN_WIDTH // 2, 
                              msg_y + 15 + (i * 28), align="center")
        
        # Recent activity - bottom
        self._render_compact_log(game_state.activity_log, 370)
        
        # Button hints - very bottom
        self._render_compact_buttons()
        
        pygame.display.flip()
        self.clock.tick(FPS)
    
    def _render_compact_player(self, player, y):
        """Render player info - ultra compact for 5-inch"""
        # Name and cash only
        name_color = player.color
        
        # Player indicator dot + name
        pygame.draw.circle(self.screen, name_color, (20, y + 10), 8)
        self.draw_text(player.name, self.font_medium, COLOR_TEXT, 35, y + 2)
        
        # Cash - prominent
        cash_color = COLOR_SUCCESS if player.cash >= 0 else COLOR_DANGER
        self.draw_text(f"${player.cash}", self.font_large, cash_color, SCREEN_WIDTH - 10, y, align="right")
        
        # Assets - single line, compact
        assets_y = y + 35
        
        # Stocks
        if player.assets["stocks"] > 0:
            stock_val = player.assets["stocks"] * ASSET_PRICES["stocks"]
            self.draw_text(f"📈{player.assets['stocks']}=${stock_val}", 
                          self.font_small, COLOR_TEXT, 20, assets_y)
        
        # Crypto
        if player.assets["crypto"] > 0:
            crypto_val = player.assets["crypto"] * ASSET_PRICES["crypto"]
            self.draw_text(f"🪙{player.assets['crypto']}=${crypto_val}", 
                          self.font_small, COLOR_TEXT, 150, assets_y)
        
        # Bonds
        if player.assets["bonds"] > 0:
            bond_val = player.assets["bonds"] * ASSET_PRICES["bonds"]
            self.draw_text(f"📊{player.assets['bonds']}=${bond_val}", 
                          self.font_small, COLOR_TEXT, 280, assets_y)
        
        # Second line of assets
        assets_y2 = assets_y + 25
        
        # Commodities
        if player.assets["commodities"] > 0:
            comm_val = player.assets["commodities"] * ASSET_PRICES["commodities"]
            self.draw_text(f"📦{player.assets['commodities']}=${comm_val}", 
                          self.font_small, COLOR_TEXT, 20, assets_y2)
        
        # Real Estate
        re_count = len(player.assets["real_estate"])
        if re_count > 0:
            re_val = re_count * ASSET_PRICES["real_estate"]
            self.draw_text(f"🏠{re_count}=${re_val}", 
                          self.font_small, COLOR_TEXT, 150, assets_y2)
        
        # Net worth
        net_worth = player.get_net_worth()
        self.draw_text(f"Worth: ${net_worth}", self.font_medium, COLOR_PRIMARY, 
                      SCREEN_WIDTH - 10, assets_y + 10, align="right")
    
    def _render_compact_log(self, log, y):
        """Render last 3 activities only - very compact"""
        self.draw_text("Recent:", self.font_small, COLOR_TEXT_DIM, 10, y)
        
        log_y = y + 20
        recent_logs = log[-3:] if len(log) > 3 else log
        
        for entry in recent_logs:
            # Strip timestamp
            if ']' in entry:
                display_text = entry.split('] ', 1)[1] if '] ' in entry else entry
            else:
                display_text = entry
            
            # Truncate if too long
            if len(display_text) > 60:
                display_text = display_text[:57] + "..."
            
            self.draw_text(display_text, self.font_small, COLOR_TEXT_DIM, 15, log_y)
            log_y += 18
    
    def _render_compact_buttons(self):
        """Render button hints - minimal"""
        hint_y = SCREEN_HEIGHT - 25
        
        # Just colored dots with labels
        # Green
        pygame.draw.circle(self.screen, BTN_GREEN, (50, hint_y), 10)
        self.draw_text("OK", self.font_small, COLOR_TEXT, 65, hint_y - 7)
        
        # Red
        pygame.draw.circle(self.screen, BTN_RED, (150, hint_y), 10)
        self.draw_text("CANCEL", self.font_small, COLOR_TEXT, 165, hint_y - 7)
        
        # Blue
        pygame.draw.circle(self.screen, BTN_BLUE, (280, hint_y), 10)
        self.draw_text("ROUND+", self.font_small, COLOR_TEXT, 295, hint_y - 7)
    
    def render_game_over(self, game_state):
        """Render game over screen - compact"""
        self.screen.fill(COLOR_BG)
        
        # Title
        self.draw_text("GAME OVER", self.font_title, COLOR_PRIMARY, SCREEN_WIDTH // 2, 20, align="center")
        
        # Rankings
        rankings = sorted(
            game_state.players.values(),
            key=lambda p: p.get_net_worth(),
            reverse=True
        )
        
        self.draw_text("Rankings:", self.font_medium, COLOR_TEXT, SCREEN_WIDTH // 2, 60, align="center")
        
        # Compact leaderboard
        rank_y = 100
        for i, player in enumerate(rankings, 1):
            # Medal
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            # Draw compact entry
            pygame.draw.circle(self.screen, player.color, (30, rank_y + 10), 8)
            self.draw_text(medal, self.font_medium, COLOR_TEXT, 50, rank_y)
            self.draw_text(player.name, self.font_medium, COLOR_TEXT, 100, rank_y)
            
            net_worth = player.get_net_worth()
            self.draw_text(f"${net_worth}", self.font_medium, COLOR_SUCCESS, 
                          SCREEN_WIDTH - 20, rank_y, align="right")
            
            rank_y += 40
        
        # Exit hint
        self.draw_text("ESC to exit", self.font_small, COLOR_TEXT_DIM, 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20, align="center")
        
        pygame.display.flip()
    
    def render_registration_screen(self, step, message):
        """Render card registration screen - compact"""
        self.screen.fill(COLOR_BG)
        
        # Title
        self.draw_text("CARD SETUP", self.font_large, COLOR_PRIMARY, 
                      SCREEN_WIDTH // 2, 20, align="center")
        
        # Step
        self.draw_text(f"Step {step}", self.font_medium, COLOR_TEXT_DIM, 
                      SCREEN_WIDTH // 2, 60, align="center")
        
        # Message
        self.draw_card(20, 120, SCREEN_WIDTH - 40, 150, COLOR_CARD_BG)
        
        # Split message into lines
        lines = message.split('\n')
        msg_y = 140
        for line in lines[:4]:  # Max 4 lines
            self.draw_text(line, self.font_medium, COLOR_TEXT, 
                          SCREEN_WIDTH // 2, msg_y, align="center")
            msg_y += 30
        
        # Hint
        self.draw_text("Scan card or RED to skip", self.font_small, COLOR_TEXT_DIM, 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, align="center")
        
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
