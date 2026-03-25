"""
Market Movers - Exhibition Mode
Run from your market_movers directory:  python3 exhibition.py

Behaviour:
  - Idle: fullscreen "scan a card to begin" prompt
  - Scan player card: show that player's portfolio (stays on screen)
  - Scan event card: apply effects to ALL demo players, highlight changes on screen
  - Scan action/space card: show the card as a banner over the portfolio
  - Bottom ticker drifts continuously
  - ESC to exit
"""

import pygame
import time
import random
import copy
from rfid_handler import create_rfid_handler
from card_registry import get_card
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    COLOR_BG, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER,
    COLOR_WARNING, COLOR_TEXT, COLOR_TEXT_DIM, COLOR_CARD_BG,
    ASSET_PRICES,
    FONT_TITLE, FONT_LARGE, FONT_MEDIUM, FONT_SMALL,
)

# ---------------------------------------------------------------------------
# Demo player state — mutated live by event scans
# ---------------------------------------------------------------------------
INITIAL_PLAYERS = [
    {"name": "Player 1", "color": (239, 68, 68),  "cash": 1450,
     "assets": {"stocks": 3, "crypto": 4, "bonds": 1, "commodities": 2}},
    {"name": "Player 2", "color": (59, 130, 246), "cash": 820,
     "assets": {"stocks": 5, "crypto": 1, "bonds": 2, "commodities": 0}},
    {"name": "Player 3", "color": (34, 197, 94),  "cash": 2100,
     "assets": {"stocks": 1, "crypto": 7, "bonds": 0, "commodities": 3}},
    {"name": "Player 4", "color": (251, 191, 36), "cash": 630,
     "assets": {"stocks": 2, "crypto": 0, "bonds": 3, "commodities": 5}},
]

ASSET_LABELS = [
    ("stocks",      "Stocks",      (59, 130, 246)),
    ("crypto",      "Crypto",      (251, 191, 36)),
    ("bonds",       "Bonds",       (34, 197, 94)),
    ("commodities", "Commodities", (168, 85, 247)),
]

TICKER_NAMES   = ["Stocks", "Crypto", "Bonds", "Commodities"]
BANNER_SECS    = 5     # card banner auto-dismisses after this
FLASH_SECS     = 3     # asset change highlights fade after this


def net_worth(player):
    total = player["cash"]
    for key, _, _ in ASSET_LABELS:
        total += player["assets"][key] * ASSET_PRICES[key]
    return total


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def draw_text(screen, text, font, color, x, y, align="left"):
    surf = font.render(str(text), True, color)
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


def fill_rect(screen, color, x, y, w, h, r=8):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=r)


def outline_rect(screen, color, x, y, w, h, r=8, lw=1):
    pygame.draw.rect(screen, color, (x, y, w, h), width=lw, border_radius=r)


def signed_pct(val):
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.1f}%"


def signed_color(val):
    return COLOR_SUCCESS if val >= 0 else COLOR_DANGER


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
class ExhibitionApp:

    TICKER_DRIFT_SECS = 3

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
        )
        pygame.display.set_caption("Market Movers — Exhibition")
        pygame.mouse.set_visible(False)

        self.fn_title  = pygame.font.Font(None, FONT_TITLE)
        self.fn_large  = pygame.font.Font(None, FONT_LARGE)
        self.fn_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.fn_small  = pygame.font.Font(None, FONT_SMALL)
        self.fn_tiny   = pygame.font.Font(None, 16)

        self.clock = pygame.time.Clock()
        self.rfid  = create_rfid_handler(simulate=False)

        # Deep-copy so we can mutate without touching INITIAL_PLAYERS
        self.players = copy.deepcopy(INITIAL_PLAYERS)

        # UI state
        self.mode = "idle"           # "idle" | "portfolio"
        self.active_player_idx = 0
        self.banner      = None      # card dict shown as overlay banner
        self.banner_time = 0
        self.asset_changes    = {}   # {asset_key: pct} — from last event card
        self.asset_flash_time = 0
        self.scan_feed = []          # [(time_str, card_name, type_color)]

        self.ticker_values    = {n: random.uniform(-15, 20) for n in TICKER_NAMES}
        self.last_ticker_drift = time.time()

        self.running = True
        print("Exhibition mode started. ESC to exit.")

    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            self._handle_events()
            self._handle_rfid()
            self._tick()
            self._render()
            self.clock.tick(FPS)
        pygame.quit()

    # ------------------------------------------------------------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    # ------------------------------------------------------------------
    def _handle_rfid(self):
        rfid_id = self.rfid.check_for_scan()
        if not rfid_id:
            return
        card = get_card(rfid_id)
        if not card:
            print(f"[SCAN] Unknown: {rfid_id}")
            return

        ctype = card["type"]
        print(f"[SCAN] {card['name']} ({ctype})")

        # Add to scan feed
        self.scan_feed.insert(0, (time.strftime("%H:%M:%S"), card["name"],
                                  self._type_color(ctype)))
        if len(self.scan_feed) > 4:
            self.scan_feed.pop()

        if ctype == "player":
            self._on_player_card(card)
        elif ctype == "event":
            self._on_event_card(card)
        else:
            # action or space — show as banner, don't change portfolios
            self.banner      = card
            self.banner_time = time.time()
            if self.mode == "idle":
                self.mode = "portfolio"

    def _on_player_card(self, card):
        # Match card name to one of our demo players
        idx = 0
        for i, p in enumerate(self.players):
            if p["name"] == card["name"]:
                idx = i
                break
        self.active_player_idx = idx
        self.mode   = "portfolio"
        self.banner = None
        self.asset_changes = {}
        print(f"  → Showing {self.players[idx]['name']}")

    def _on_event_card(self, card):
        effects = card.get("effects", {})
        # Apply to ALL players
        for p in self.players:
            for asset_key, pct in effects.items():
                old = p["assets"].get(asset_key, 0)
                p["assets"][asset_key] = max(0, round(old * (1 + pct)))
        self.asset_changes    = effects.copy()
        self.asset_flash_time = time.time()
        self.banner      = card
        self.banner_time = time.time()
        if self.mode == "idle":
            self.mode = "portfolio"
        print(f"  → Event applied: {effects}")

    # ------------------------------------------------------------------
    def _tick(self):
        if self.banner and time.time() - self.banner_time > BANNER_SECS:
            self.banner = None
        if self.asset_changes and time.time() - self.asset_flash_time > FLASH_SECS:
            self.asset_changes = {}
        if time.time() - self.last_ticker_drift > self.TICKER_DRIFT_SECS:
            for name in TICKER_NAMES:
                self.ticker_values[name] += random.uniform(-3, 3)
                self.ticker_values[name] = max(-40, min(60, self.ticker_values[name]))
            self.last_ticker_drift = time.time()

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------
    def _render(self):
        self.screen.fill(COLOR_BG)
        if self.mode == "idle":
            self._draw_idle()
        else:
            self._draw_portfolio()
            if self.banner:
                self._draw_banner()
        self._draw_ticker()
        pygame.display.flip()

    # --- Idle ----------------------------------------------------------
    def _draw_idle(self):
        cx = SCREEN_WIDTH // 2
        cy = (SCREEN_HEIGHT - 30) // 2

        draw_text(self.screen, "MARKET MOVERS", self.fn_title,
                  COLOR_PRIMARY, cx, cy - 110, align="center")
        draw_text(self.screen, "Digital banking board game",
                  self.fn_medium, COLOR_TEXT_DIM, cx, cy - 78, align="center")

        # Pulsing NFC ring
        t     = time.time()
        pulse = abs((t % 1.8) / 0.9 - 1.0)
        rr    = int(28 + pulse * 12)
        alpha = int(180 - pulse * 150)
        surf  = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*COLOR_PRIMARY, alpha), (rr + 2, rr + 2), rr, 2)
        self.screen.blit(surf, (cx - rr - 2, cy - rr + 8))
        pygame.draw.circle(self.screen, COLOR_PRIMARY, (cx, cy + 10 + rr - 28), 20)
        for off in (7, 13):
            pygame.draw.arc(self.screen, COLOR_BG,
                            (cx - off, cy + 10 + rr - 28 - off, off * 2, off * 2),
                            0.3, 2.84, 2)

        draw_text(self.screen, "Scan your player card to begin",
                  self.fn_large, COLOR_TEXT, cx, cy + 55, align="center")
        draw_text(self.screen, "Then scan event, action, or space cards",
                  self.fn_tiny, COLOR_TEXT_DIM, cx, cy + 80, align="center")

        # Legend
        legend = [("Player", COLOR_SUCCESS), ("Space", COLOR_PRIMARY),
                  ("Action", COLOR_WARNING),  ("Event", (168, 85, 247))]
        lx = cx - 200
        for i, (label, col) in enumerate(legend):
            bx = lx + i * 105
            pygame.draw.circle(self.screen, col, (bx, cy + 114), 6)
            draw_text(self.screen, label, self.fn_tiny, COLOR_TEXT_DIM, bx + 12, cy + 108)

    # --- Portfolio -----------------------------------------------------
    def _draw_portfolio(self):
        TICKER_H = 30
        usable_h = SCREEN_HEIGHT - TICKER_H
        PAD      = 12
        player   = self.players[self.active_player_idx]

        # Header strip
        fill_rect(self.screen, COLOR_CARD_BG, 0, 0, SCREEN_WIDTH, 52, r=0)
        pygame.draw.circle(self.screen, player["color"], (PAD + 14, 26), 10)
        draw_text(self.screen, player["name"], self.fn_large, COLOR_TEXT, PAD + 30, 13)
        draw_text(self.screen, "MARKET MOVERS  —  exhibition",
                  self.fn_tiny, COLOR_TEXT_DIM, SCREEN_WIDTH - PAD, 18, align="right")

        # Player selector dots top-right
        for i, p in enumerate(self.players):
            dx = SCREEN_WIDTH - PAD - (len(self.players) - 1 - i) * 20
            r  = 7 if i == self.active_player_idx else 4
            pygame.draw.circle(self.screen, p["color"], (dx, 38), r)

        pygame.draw.line(self.screen, (30, 45, 70), (0, 52), (SCREEN_WIDTH, 52), 1)

        # Layout columns
        col_y   = 60
        left_w  = 350
        right_w = SCREEN_WIDTH - left_w - PAD * 3
        left_x  = PAD
        right_x = left_x + left_w + PAD

        # Cash + net worth
        draw_text(self.screen, "Cash", self.fn_tiny, COLOR_TEXT_DIM, left_x, col_y)
        draw_text(self.screen, f"${player['cash']:,}", self.fn_title,
                  COLOR_SUCCESS if player["cash"] >= 0 else COLOR_DANGER,
                  left_x, col_y + 16)

        draw_text(self.screen, "Net worth", self.fn_tiny, COLOR_TEXT_DIM,
                  left_x + left_w, col_y, align="right")
        draw_text(self.screen, f"${net_worth(player):,}", self.fn_large,
                  COLOR_PRIMARY, left_x + left_w, col_y + 16, align="right")

        pygame.draw.line(self.screen, (30, 45, 70),
                         (left_x, col_y + 52), (left_x + left_w, col_y + 52), 1)

        # 2×2 asset cards
        card_w = (left_w - PAD) // 2
        card_h = 78
        for idx, (key, label, col) in enumerate(ASSET_LABELS):
            cx = left_x + (idx % 2) * (card_w + PAD)
            cy = col_y + 60 + (idx // 2) * (card_h + 8)
            qty = player["assets"][key]
            val = qty * ASSET_PRICES[key]

            # Flash background on event change
            if key in self.asset_changes:
                pct = self.asset_changes[key]
                age = time.time() - self.asset_flash_time
                fade = max(0.0, 1.0 - age / FLASH_SECS)
                base_pos = (34, 197, 94) if pct >= 0 else (239, 68, 68)
                bg = tuple(int(12 + base_pos[c] * 0.25 * fade) for c in range(3))
            else:
                bg = (20, 30, 50)

            fill_rect(self.screen, bg, cx, cy, card_w, card_h, r=8)

            draw_text(self.screen, label, self.fn_tiny, COLOR_TEXT_DIM, cx + 8, cy + 6)
            draw_text(self.screen, str(qty), self.fn_large, col, cx + 8, cy + 24)
            draw_text(self.screen, f"${val:,}", self.fn_tiny, COLOR_TEXT_DIM,
                      cx + card_w - 8, cy + 30, align="right")

            # Change badge
            if key in self.asset_changes:
                pct = self.asset_changes[key]
                ind_col = COLOR_SUCCESS if pct >= 0 else COLOR_DANGER
                draw_text(self.screen, signed_pct(pct * 100),
                          self.fn_tiny, ind_col,
                          cx + card_w - 8, cy + card_h - 18, align="right")

        # RIGHT: scan feed
        draw_text(self.screen, "Recent scans", self.fn_tiny, COLOR_TEXT_DIM, right_x, col_y)
        fy      = col_y + 18
        feed_h  = 26
        for i, (ts, name, tcol) in enumerate(self.scan_feed):
            ey = fy + i * feed_h
            fill_rect(self.screen, (20, 32, 52) if i % 2 == 0 else COLOR_BG,
                      right_x, ey, right_w, feed_h - 2, r=4)
            pygame.draw.circle(self.screen, tcol, (right_x + 10, ey + 12), 4)
            draw_text(self.screen, name, self.fn_tiny, COLOR_TEXT, right_x + 20, ey + 8)
            draw_text(self.screen, ts, self.fn_tiny, COLOR_TEXT_DIM,
                      right_x + right_w - 4, ey + 8, align="right")

        if not self.scan_feed:
            draw_text(self.screen, "No scans yet",
                      self.fn_tiny, COLOR_TEXT_DIM,
                      right_x + right_w // 2, fy + 12, align="center")

        # Leaderboard
        lb_y = fy + max(1, len(self.scan_feed)) * feed_h + 16
        pygame.draw.line(self.screen, (30, 45, 70),
                         (right_x, lb_y - 6), (right_x + right_w, lb_y - 6), 1)
        draw_text(self.screen, "Leaderboard", self.fn_tiny, COLOR_TEXT_DIM, right_x, lb_y)
        sorted_p = sorted(self.players, key=net_worth, reverse=True)
        medal    = [(255, 215, 0), (192, 192, 192), (205, 127, 50), COLOR_TEXT_DIM]
        for rank, p in enumerate(sorted_p, 1):
            ry      = lb_y + 18 + (rank - 1) * 28
            is_me   = p["name"] == self.players[self.active_player_idx]["name"]
            fill_rect(self.screen, (25, 38, 62) if is_me else COLOR_BG,
                      right_x, ry - 2, right_w, 24, r=4)
            pygame.draw.circle(self.screen, p["color"], (right_x + 10, ry + 9), 5)
            draw_text(self.screen, f"{rank}.  {p['name']}",
                      self.fn_tiny, COLOR_TEXT, right_x + 22, ry + 5)
            draw_text(self.screen, f"${net_worth(p):,}",
                      self.fn_tiny, medal[rank - 1],
                      right_x + right_w - 4, ry + 5, align="right")

        # Decorative button strip
        btn_y = usable_h - 34
        pygame.draw.line(self.screen, (30, 45, 70), (0, btn_y - 2), (SCREEN_WIDTH, btn_y - 2), 1)
        btns = [("CONFIRM", (34, 197, 94), (10, 40, 20)),
                ("CANCEL",  (239, 68, 68), (50, 12, 12)),
                ("NEXT ROUND", (59, 130, 246), (10, 20, 55))]
        bw = SCREEN_WIDTH // 3
        for i, (label, col, bg) in enumerate(btns):
            bx = i * bw
            fill_rect(self.screen, bg, bx + 4, btn_y, bw - 8, 28, r=6)
            pygame.draw.circle(self.screen, col, (bx + 18, btn_y + 14), 6)
            draw_text(self.screen, label, self.fn_tiny, col, bx + 30, btn_y + 9)

    # --- Card banner ---------------------------------------------------
    def _draw_banner(self):
        card       = self.banner
        ctype      = card["type"]
        border_col = self._type_color(ctype)

        bx, by = 50, 70
        bw, bh = SCREEN_WIDTH - 100, 170
        fill_rect(self.screen, (10, 18, 36), bx, by, bw, bh, r=14)
        outline_rect(self.screen, border_col, bx, by, bw, bh, r=14, lw=2)

        # Type badge
        badge = ctype.upper()
        bdw   = self.fn_tiny.size(badge)[0] + 18
        fill_rect(self.screen, self._type_badge_bg(ctype), bx + 14, by + 12, bdw, 22, r=4)
        draw_text(self.screen, badge, self.fn_tiny, border_col,
                  bx + 14 + bdw // 2, by + 23, align="center")

        draw_text(self.screen, card["name"], self.fn_large,
                  COLOR_TEXT, bx + 14, by + 44)

        self._wrapped(card.get("description", ""), self.fn_tiny, COLOR_TEXT_DIM,
                      bx + 14, by + 70, bw - 28)

        # Event effects line
        if ctype == "event" and "effects" in card:
            ex = bx + 14
            ey = by + 108
            for asset, pct in card["effects"].items():
                col = COLOR_SUCCESS if pct >= 0 else COLOR_DANGER
                draw_text(self.screen, f"{asset.capitalize()}  {signed_pct(pct * 100)}",
                          self.fn_tiny, col, ex, ey)
                ex += 130

        # Countdown bar
        remain = max(0.0, 1.0 - (time.time() - self.banner_time) / BANNER_SECS)
        fill_rect(self.screen, (30, 45, 70), bx + 14, by + bh - 10, bw - 28, 4, r=2)
        fill_rect(self.screen, border_col, bx + 14, by + bh - 10,
                  int((bw - 28) * remain), 4, r=2)

    # --- Ticker --------------------------------------------------------
    def _draw_ticker(self):
        bar_y = SCREEN_HEIGHT - 30
        pygame.draw.line(self.screen, COLOR_CARD_BG,
                         (0, bar_y - 1), (SCREEN_WIDTH, bar_y - 1), 1)
        fill_rect(self.screen, (10, 18, 34), 0, bar_y, SCREEN_WIDTH, 30, r=0)
        draw_text(self.screen, "MARKET", self.fn_tiny, COLOR_TEXT_DIM, 8, bar_y + 9)
        col_w = (SCREEN_WIDTH - 80) // len(TICKER_NAMES)
        for i, name in enumerate(TICKER_NAMES):
            val = self.ticker_values[name]
            tx  = 72 + i * col_w
            draw_text(self.screen, name, self.fn_tiny, COLOR_TEXT_DIM, tx, bar_y + 6)
            draw_text(self.screen, signed_pct(val), self.fn_tiny,
                      signed_color(val), tx + 76, bar_y + 6)
        draw_text(self.screen, "ESC to exit", self.fn_tiny,
                  COLOR_TEXT_DIM, SCREEN_WIDTH - 8, bar_y + 9, align="right")

    # --- Helpers -------------------------------------------------------
    def _type_color(self, ctype):
        return {"space": COLOR_PRIMARY, "action": COLOR_WARNING,
                "event": (168, 85, 247), "player": COLOR_SUCCESS
                }.get(ctype, COLOR_TEXT_DIM)

    def _type_badge_bg(self, ctype):
        return {"space": (15, 40, 80), "action": (70, 50, 10),
                "event": (45, 15, 75), "player": (10, 55, 25)
                }.get(ctype, COLOR_CARD_BG)

    def _wrapped(self, text, font, color, x, y, max_w, line_h=18):
        words, line, cy = text.split(), "", y
        for word in words:
            test = (line + " " + word).strip()
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
def main():
    app = ExhibitionApp()
    try:
        app.run()
    except KeyboardInterrupt:
        pygame.quit()
    except Exception:
        import traceback
        traceback.print_exc()
        pygame.quit()


if __name__ == "__main__":
    main()
