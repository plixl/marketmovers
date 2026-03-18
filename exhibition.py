"""
Market Movers - Exhibition Mode
Displays a live demo on the Pi's 800x480 screen next to a trifold.

Features:
  - Simulated player portfolios with animated asset ticker
  - Live RFID scanning — scan any registered card to see it respond
  - Scan feed log showing recent card reads
  - Cycles through player portfolio views automatically

Run from your market_movers directory:
    python3 exhibition.py

Uses real RFID hardware. Buttons are shown on screen for display only (not wired up).
ESC to exit.
"""

import pygame
import sys
import time
import random
from rfid_handler import create_rfid_handler
from card_registry import get_card, CARD_MAPPINGS
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COLOR_BG, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER,
    COLOR_WARNING, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_CARD_BG,
    ASSET_PRICES,
    FONT_TITLE, FONT_LARGE, FONT_MEDIUM, FONT_SMALL,
)

# ---------------------------------------------------------------------------
# Simulated player data for display
# ---------------------------------------------------------------------------
DEMO_PLAYERS = [
    {
        "name": "Player 1",
        "color": (239, 68, 68),
        "cash": 1450,
        "assets": {"stocks": 3, "crypto": 4, "bonds": 1, "commodities": 2},
    },
    {
        "name": "Player 2",
        "color": (59, 130, 246),
        "cash": 820,
        "assets": {"stocks": 5, "crypto": 1, "bonds": 2, "commodities": 0},
    },
    {
        "name": "Player 3",
        "color": (34, 197, 94),
        "cash": 2100,
        "assets": {"stocks": 1, "crypto": 7, "bonds": 0, "commodities": 3},
    },
    {
        "name": "Player 4",
        "color": (251, 191, 36),
        "cash": 630,
        "assets": {"stocks": 2, "crypto": 0, "bonds": 3, "commodities": 5},
    },
]

ASSET_LABELS = [
    ("stocks",      "Stocks",      (59, 130, 246)),
    ("crypto",      "Crypto",      (251, 191, 36)),
    ("bonds",       "Bonds",       (34, 197, 94)),
    ("commodities", "Commodities", (168, 85, 247)),
]

TICKER_NAMES = ["Stocks", "Crypto", "Bonds", "Commodities"]


def net_worth(player):
    total = player["cash"]
    for key, _, _ in ASSET_LABELS:
        total += player["assets"][key] * ASSET_PRICES[key]
    return total


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def draw_text(screen, text, font, color, x, y, align="left"):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if align == "center":
        rect.center = (x, y)
    elif align == "right":
        rect.right = x
        rect.top = y
    else:
        rect.left = x
        rect.top = y
    screen.blit(surf, rect)
    return rect.bottom


def draw_rect(screen, color, x, y, w, h, radius=10):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=radius)


def draw_rect_outline(screen, color, x, y, w, h, radius=10, width=1):
    pygame.draw.rect(screen, color, (x, y, w, h), width=width, border_radius=radius)


def signed_color(val):
    return COLOR_SUCCESS if val >= 0 else COLOR_DANGER


def format_signed(val, suffix="%"):
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.1f}{suffix}"


# ---------------------------------------------------------------------------
# Exhibition app
# ---------------------------------------------------------------------------
class ExhibitionApp:

    PLAYER_CYCLE_SECS = 5      # Auto-advance player view every N seconds
    TICKER_DRIFT_SECS = 3      # Re-randomise ticker values every N seconds
    SCAN_FLASH_SECS   = 4      # How long to highlight a scan result
    MAX_FEED_ITEMS    = 5      # Lines in the scan feed

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
        )
        pygame.display.set_caption("Market Movers — Exhibition")
        pygame.mouse.set_visible(False)

        self.font_title  = pygame.font.Font(None, FONT_TITLE)
        self.font_large  = pygame.font.Font(None, FONT_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small  = pygame.font.Font(None, FONT_SMALL)
        self.font_tiny   = pygame.font.Font(None, 16)

        self.clock = pygame.time.Clock()

        self.rfid = create_rfid_handler(simulate=False)

        # State
        self.current_player_idx  = 0
        self.last_player_cycle   = time.time()
        self.last_ticker_drift   = time.time()

        self.ticker_values = {n: random.uniform(-15, 20) for n in TICKER_NAMES}

        self.scan_feed   = []          # list of (timestamp_str, card_name, card_type)
        self.last_scan   = None        # (card_dict, rfid_id, scan_time)
        self.scan_flash  = False

        self.running = True
        print("Exhibition mode started. Scan any registered card.")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            self._handle_events()
            self._handle_rfid()
            self._tick_auto_cycle()
            self._tick_ticker()
            self._render()
            self.clock.tick(FPS)

        pygame.quit()
        print("Exhibition mode exited.")

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def _handle_rfid(self):
        rfid_id = self.rfid.check_for_scan()
        if not rfid_id:
            return
        card = get_card(rfid_id)
        if card:
            ts = time.strftime("%H:%M:%S")
            self.scan_feed.insert(0, (ts, card["name"], card["type"], rfid_id))
            if len(self.scan_feed) > self.MAX_FEED_ITEMS:
                self.scan_feed.pop()
            self.last_scan  = (card, rfid_id, time.time())
            self.scan_flash = True
            print(f"[SCAN] {card['name']} ({card['type']}) — {rfid_id}")
        else:
            ts = time.strftime("%H:%M:%S")
            self.scan_feed.insert(0, (ts, f"Unknown ({rfid_id})", "unknown", rfid_id))
            if len(self.scan_feed) > self.MAX_FEED_ITEMS:
                self.scan_feed.pop()
            print(f"[SCAN] Unknown card: {rfid_id}")

    # ------------------------------------------------------------------
    # Timed updates
    # ------------------------------------------------------------------
    def _tick_auto_cycle(self):
        if time.time() - self.last_player_cycle >= self.PLAYER_CYCLE_SECS:
            self.current_player_idx = (self.current_player_idx + 1) % len(DEMO_PLAYERS)
            self.last_player_cycle  = time.time()

    def _tick_ticker(self):
        if time.time() - self.last_ticker_drift >= self.TICKER_DRIFT_SECS:
            for name in TICKER_NAMES:
                # Drift each value a little each tick so it feels live
                self.ticker_values[name] += random.uniform(-3, 3)
                self.ticker_values[name] = max(-40, min(60, self.ticker_values[name]))
            self.last_ticker_drift = time.time()

        # Clear flash after timeout
        if self.scan_flash and self.last_scan:
            if time.time() - self.last_scan[2] > self.SCAN_FLASH_SECS:
                self.scan_flash = False

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def _render(self):
        self.screen.fill(COLOR_BG)
        self._draw_header()
        self._draw_player_panel()       # Left column
        self._draw_scan_panel()         # Right column
        self._draw_ticker()             # Bottom bar
        pygame.display.flip()

    # --- Header --------------------------------------------------------
    def _draw_header(self):
        # Title
        draw_text(self.screen, "MARKET MOVERS", self.font_title,
                  COLOR_PRIMARY, SCREEN_WIDTH // 2, 18, align="center")
        # Subtitle
        draw_text(self.screen, "Digital banking board game — scan a card to see it in action",
                  self.font_tiny, COLOR_TEXT_DIM, SCREEN_WIDTH // 2, 44, align="center")
        # Divider
        pygame.draw.line(self.screen, COLOR_CARD_BG,
                         (0, 58), (SCREEN_WIDTH, 58), 1)

    # --- Left: player portfolio ----------------------------------------
    def _draw_player_panel(self):
        x, y = 8, 66
        panel_w = 390

        player = DEMO_PLAYERS[self.current_player_idx]

        # Player tabs (small dots)
        for i, p in enumerate(DEMO_PLAYERS):
            dot_x = x + 10 + i * 20
            r = 5 if i != self.current_player_idx else 7
            pygame.draw.circle(self.screen, p["color"], (dot_x, y + 6), r)

        # Cycle hint
        draw_text(self.screen, "auto-cycling players",
                  self.font_tiny, COLOR_TEXT_DIM, x + panel_w, y + 2, align="right")

        y += 20

        # Player card background
        card_h = 270
        draw_rect(self.screen, COLOR_CARD_BG, x, y, panel_w, card_h, radius=10)

        # Player name + colour dot
        pygame.draw.circle(self.screen, player["color"], (x + 20, y + 22), 8)
        draw_text(self.screen, player["name"], self.font_large,
                  COLOR_TEXT, x + 36, y + 12)

        # Cash
        draw_text(self.screen, "cash", self.font_tiny, COLOR_TEXT_DIM, x + 14, y + 42)
        draw_text(self.screen, f"${player['cash']:,}", self.font_large,
                  COLOR_SUCCESS, x + 14, y + 56)

        # Assets grid (2×2)
        ay = y + 96
        col_w = panel_w // 2 - 8
        for idx, (key, label, color) in enumerate(ASSET_LABELS):
            col = idx % 2
            row = idx // 2
            ax = x + 8 + col * (col_w + 8)
            aay = ay + row * 62

            draw_rect(self.screen, (20, 30, 50), ax, aay, col_w, 54, radius=6)
            draw_text(self.screen, label, self.font_tiny, COLOR_TEXT_DIM, ax + 8, aay + 6)
            qty = player["assets"][key]
            draw_text(self.screen, str(qty), self.font_large, color, ax + 8, aay + 22)
            val = qty * ASSET_PRICES[key]
            draw_text(self.screen, f"${val:,}", self.font_tiny, COLOR_TEXT_DIM,
                      ax + col_w - 6, aay + 36, align="right")

        # Net worth bar
        ny = y + card_h - 36
        pygame.draw.line(self.screen, (30, 45, 70),
                         (x + 8, ny - 4), (x + panel_w - 8, ny - 4), 1)
        draw_text(self.screen, "Net worth", self.font_tiny, COLOR_TEXT_DIM, x + 14, ny + 4)
        draw_text(self.screen, f"${net_worth(player):,}", self.font_medium,
                  COLOR_PRIMARY, x + panel_w - 14, ny + 2, align="right")

        # --- Mini leaderboard below card ---
        ly = y + card_h + 10
        draw_text(self.screen, "Leaderboard", self.font_tiny, COLOR_TEXT_DIM, x + 8, ly)
        sorted_players = sorted(DEMO_PLAYERS, key=net_worth, reverse=True)
        for rank, p in enumerate(sorted_players, 1):
            ry = ly + 16 + (rank - 1) * 22
            medal_colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50), COLOR_TEXT_DIM]
            pygame.draw.circle(self.screen, p["color"], (x + 18, ry + 8), 5)
            draw_text(self.screen, f"{rank}. {p['name']}", self.font_tiny,
                      COLOR_TEXT, x + 28, ry + 2)
            draw_text(self.screen, f"${net_worth(p):,}", self.font_tiny,
                      medal_colors[rank - 1], x + panel_w - 10, ry + 2, align="right")

    # --- Right: scan panel ---------------------------------------------
    def _draw_scan_panel(self):
        x = 406
        y = 66
        panel_w = SCREEN_WIDTH - x - 8

        # --- Scan result box ---
        result_h = 160
        if self.scan_flash and self.last_scan:
            card, rfid_id, _ = self.last_scan
            border_color = self._type_color(card["type"])
            draw_rect(self.screen, COLOR_CARD_BG, x, y, panel_w, result_h, radius=10)
            draw_rect_outline(self.screen, border_color, x, y, panel_w, result_h,
                              radius=10, width=2)

            # Type badge
            badge_color = self._type_badge_bg(card["type"])
            badge_text  = card["type"].upper()
            bw = self.font_tiny.size(badge_text)[0] + 16
            draw_rect(self.screen, badge_color, x + 10, y + 10, bw, 20, radius=4)
            draw_text(self.screen, badge_text, self.font_tiny,
                      border_color, x + 10 + bw // 2, y + 20, align="center")

            # Card name
            draw_text(self.screen, card["name"], self.font_large,
                      COLOR_TEXT, x + 10, y + 38)

            # Description
            desc = card.get("description", "")
            self._draw_wrapped(desc, self.font_tiny, COLOR_TEXT_DIM,
                               x + 10, y + 64, panel_w - 20, line_h=18)

            # RFID ID
            draw_text(self.screen, rfid_id, self.font_tiny,
                      COLOR_TEXT_DIM, x + panel_w - 10, y + result_h - 14, align="right")

        else:
            # Idle: animated "scan here" prompt
            draw_rect(self.screen, COLOR_CARD_BG, x, y, panel_w, result_h, radius=10)
            draw_rect_outline(self.screen, (40, 55, 80), x, y, panel_w, result_h,
                              radius=10, width=1)

            # Pulsing ring
            t = time.time()
            pulse = abs((t % 1.6) / 0.8 - 1.0)
            ring_r = int(22 + pulse * 10)
            ring_alpha = int(180 - pulse * 140)
            cx = x + panel_w // 2
            cy = y + 60
            ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*COLOR_PRIMARY, ring_alpha),
                               (ring_r + 2, ring_r + 2), ring_r, 2)
            self.screen.blit(ring_surf, (cx - ring_r - 2, cy - ring_r - 2))
            pygame.draw.circle(self.screen, COLOR_PRIMARY, (cx, cy), 16)
            # NFC icon lines
            for offset in (6, 11):
                pygame.draw.arc(self.screen, COLOR_BG,
                                (cx - offset, cy - offset, offset * 2, offset * 2),
                                0.3, 2.84, 2)

            draw_text(self.screen, "Scan a card", self.font_medium,
                      COLOR_TEXT, cx, y + 100, align="center")
            draw_text(self.screen, "Hold any game card near the RFID reader",
                      self.font_tiny, COLOR_TEXT_DIM, cx, y + 122, align="center")
            draw_text(self.screen, "Space  ·  Action  ·  Event  ·  Player wallet",
                      self.font_tiny, COLOR_TEXT_DIM, cx, y + 140, align="center")

        # --- Scan feed ---
        fy = y + result_h + 10
        draw_text(self.screen, "Recent scans", self.font_tiny, COLOR_TEXT_DIM, x + 8, fy)
        fy += 16

        feed_h = 22
        for i, entry in enumerate(self.scan_feed):
            ts, name, ctype, _ = entry
            ey = fy + i * feed_h
            row_color = (20, 32, 52) if i % 2 == 0 else COLOR_BG
            draw_rect(self.screen, row_color, x, ey, panel_w, feed_h - 1, radius=4)

            dot_col = self._type_color(ctype)
            pygame.draw.circle(self.screen, dot_col, (x + 10, ey + 10), 4)
            draw_text(self.screen, name, self.font_tiny, COLOR_TEXT, x + 20, ey + 5)
            draw_text(self.screen, ts, self.font_tiny, COLOR_TEXT_DIM,
                      x + panel_w - 6, ey + 5, align="right")

        if not self.scan_feed:
            draw_text(self.screen, "No scans yet — try it!",
                      self.font_tiny, COLOR_TEXT_DIM,
                      x + panel_w // 2, fy + 10, align="center")

        # --- How to play blurb ---
        blurb_y = fy + self.MAX_FEED_ITEMS * feed_h + 10
        items = [
            "Roll dice, move on the physical board",
            "Scan space card  →  buy assets digitally",
            "Draw action/event cards and scan them",
            "Most net worth after 10 rounds wins",
        ]
        for i, line in enumerate(items):
            draw_text(self.screen, f"  {i+1}.  {line}",
                      self.font_tiny, COLOR_TEXT_DIM, x + 8, blurb_y + i * 18)

        # --- Decorative button display (display only, not functional) ---
        btn_y = blurb_y + len(items) * 18 + 10
        pygame.draw.line(self.screen, (30, 45, 70),
                         (x + 8, btn_y), (x + panel_w - 8, btn_y), 1)
        btn_y += 8
        btn_data = [
            ("CONFIRM",    (34, 197, 94),   (10, 50, 25)),
            ("CANCEL",     (239, 68, 68),   (60, 15, 15)),
            ("NEXT ROUND", (59, 130, 246),  (10, 25, 60)),
        ]
        btn_w = (panel_w - 16) // 3
        for i, (label, dot_col, bg_col) in enumerate(btn_data):
            bx = x + 8 + i * (btn_w + 2)
            draw_rect(self.screen, bg_col, bx, btn_y, btn_w, 22, radius=5)
            pygame.draw.circle(self.screen, dot_col, (bx + 10, btn_y + 11), 5)
            draw_text(self.screen, label, self.font_tiny, dot_col,
                      bx + 20, btn_y + 6)

    # --- Bottom ticker -------------------------------------------------
    def _draw_ticker(self):
        bar_y = SCREEN_HEIGHT - 30
        pygame.draw.line(self.screen, COLOR_CARD_BG,
                         (0, bar_y - 1), (SCREEN_WIDTH, bar_y - 1), 1)
        draw_rect(self.screen, (10, 18, 34), 0, bar_y, SCREEN_WIDTH, 30, radius=0)

        col_w = SCREEN_WIDTH // (len(TICKER_NAMES) + 1)

        draw_text(self.screen, "LIVE MARKET",
                  self.font_tiny, COLOR_TEXT_DIM, 10, bar_y + 9)

        for i, name in enumerate(TICKER_NAMES):
            val = self.ticker_values[name]
            tx = (i + 1) * col_w + col_w // 2
            draw_text(self.screen, name, self.font_tiny,
                      COLOR_TEXT_DIM, tx - 4, bar_y + 6)
            draw_text(self.screen, format_signed(val),
                      self.font_tiny, signed_color(val),
                      tx + 50, bar_y + 6)

        # Quit hint
        draw_text(self.screen, "ESC to exit",
                  self.font_tiny, COLOR_TEXT_DIM, SCREEN_WIDTH - 8, bar_y + 9, align="right")

    # --- Helpers -------------------------------------------------------
    def _type_color(self, ctype):
        return {
            "space":  COLOR_PRIMARY,
            "action": COLOR_WARNING,
            "event":  (168, 85, 247),
            "player": COLOR_SUCCESS,
        }.get(ctype, COLOR_TEXT_DIM)

    def _type_badge_bg(self, ctype):
        return {
            "space":  (15, 40, 80),
            "action": (80, 60, 10),
            "event":  (50, 20, 80),
            "player": (10, 60, 30),
        }.get(ctype, COLOR_CARD_BG)

    def _draw_wrapped(self, text, font, color, x, y, max_w, line_h=20):
        words = text.split()
        line  = ""
        cy    = y
        for word in words:
            test = line + (" " if line else "") + word
            if font.size(test)[0] > max_w:
                if line:
                    draw_text(self.screen, line, font, color, x, cy)
                    cy += line_h
                line = word
            else:
                line = test
        if line:
            draw_text(self.screen, line, font, color, x, cy)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    app = ExhibitionApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        pygame.quit()
    except Exception as e:
        import traceback
        traceback.print_exc()
        pygame.quit()


if __name__ == "__main__":
    main()
