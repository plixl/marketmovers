# Market Movers - Digital Banking Unit

A hybrid physical/digital board game using RFID technology for contactless banking and asset management. Players roll dice and move on a physical board, while their portfolios are managed digitally through RFID card scans.

## 🎮 Game Overview

- **Players**: 2-4 players
- **Objective**: Highest net worth after 10 rounds (or last player standing)
- **Starting Cash**: $1,000 per player
- **Assets**: Stocks, Crypto, Bonds, Commodities, Real Estate

## 🛠️ Hardware Requirements

### Required Components
1. **Raspberry Pi 5**
2. **PiicoDev RFID Module** (NFC 13.56MHz) - SKU: CE08086
3. **3× PiicoDev Button Modules**
4. **HDMI Display** (1080p recommended)
5. **60 RFID/NFC Cards** (NTAG213 or Classic compatible)

### Card Breakdown
- 4 Player Wallet Cards
- 15 Board Space Cards
- 20 Action Cards
- 18 Event Cards
- 3 Spare cards

## 📦 Software Installation

### 1. Install Dependencies

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python packages
pip install pygame --break-system-packages

# Install PiicoDev libraries
cd ~
git clone https://github.com/CoreElectronics/CE-PiicoDev-Unified.git
git clone https://github.com/CoreElectronics/CE-PiicoDev-RFID-MicroPython-Module.git
git clone https://github.com/CoreElectronics/CE-PiicoDev-Button-MicroPython-Module.git

# Copy PiicoDev modules to market_movers directory
cp CE-PiicoDev-Unified/PiicoDev_Unified.py market_movers/
cp CE-PiicoDev-RFID-MicroPython-Module/PiicoDev_RFID.py market_movers/
cp CE-PiicoDev-Button-MicroPython-Module/PiicoDev_Button.py market_movers/
```

### 2. Setup Game Files

Copy all game files to `/home/pi/market_movers/`:
- `main.py`
- `config.py`
- `game_state.py`
- `card_processor.py`
- `card_registry.py`
- `rfid_handler.py`
- `button_handler.py`
- `ui_display.py`
- `register_cards.py`

## 🏷️ Card Registration

Before playing, you need to map your RFID cards to game cards.

### Method 1: Automated Registration Tool

```bash
cd ~/market_movers
python3 register_cards.py
```

Follow the on-screen prompts to scan each card. The tool will generate mappings that you can copy into `card_registry.py`.

### Method 2: Quick Scan Test

To just see your card IDs:

```bash
python3 register_cards.py --test
```

Scan cards and note their IDs, then manually edit `card_registry.py` to replace `PLACEHOLDER_*` values.

### Method 3: Manual Mapping

1. Scan each card using the test tool
2. Open `card_registry.py`
3. Replace placeholders with actual RFID IDs:

```python
# Before
"PLACEHOLDER_P1": {
    "type": "player",
    "name": "Player 1",
    ...
}

# After (example)
"04:A3:B2:C1:D4:E5:F6": {
    "type": "player",
    "name": "Player 1",
    ...
}
```

## 🎯 Hardware Setup

### Button Connections

Connect 3 PiicoDev buttons with different I2C addresses:

| Button Color | Function | I2C Address | ASW Settings |
|-------------|----------|-------------|--------------|
| Green | CONFIRM | 0x42 | [OFF, OFF] |
| Red | CANCEL | 0x43 | [OFF, ON] |
| Blue | NEXT ROUND | 0x44 | [ON, OFF] |

Adjust addresses in `button_handler.py` if using different settings.

### RFID Module Connection

- Default I2C address: `0x2C`
- If using multiple RFID readers, adjust address using ASW switches
- Connect via PiicoDev connector to Raspberry Pi

## 🚀 Running the Game

### Normal Mode (with hardware)

```bash
cd ~/market_movers
python3 main.py
```

### Simulation Mode (testing without hardware)

```bash
python3 main.py --simulate
```

In simulation mode:
- Window mode instead of fullscreen
- No actual RFID/button hardware needed
- Use for testing game logic

## 🎲 How to Play

### Game Start
1. Run the game
2. Each player scans their wallet card to register
3. First player begins their turn

### Taking a Turn
1. Roll physical dice and move your token on the board
2. **Scan your player wallet card** (identifies who you are)
3. **Scan the space card** for where you landed
4. Follow on-screen prompts
5. Use buttons to confirm/cancel actions

### Board Spaces

| Space | Effect |
|-------|--------|
| Payday | Collect $200 |
| Stock Exchange | Buy/sell stocks ($100 each) |
| Crypto Hub | Buy/sell crypto ($50 each) |
| Bond Market | Buy bonds ($200 each) |
| Commodity Trade | Buy commodities ($75 each) |
| Real Estate | Buy property ($500, locked 2 rounds) |
| Dividend | Earn 7.5% on stocks/bonds |
| Action Space | Draw action card |
| Event Space | Draw event card |
| Global Event | Major market event |
| Startup Incubator | 50/50 gamble ($300 win / $100 loss) |
| Tax Audit | Pay $150 |
| Market Reset | All assets revalue |

### Asset Purchasing

When you land on a trading space (Stock Exchange, Crypto Hub, etc.):
1. Space card scanned → Prompt appears
2. **Scan the same space card again** to buy 1 unit
3. Repeat to buy more
4. Press **GREEN button** when done

### Action Cards

Some action cards require a target:
1. Scan your wallet
2. Scan action card
3. Scan target player's wallet
4. Action executes automatically

### Event Cards

Event cards affect ALL players:
1. Scan your wallet
2. Scan event card
3. Effects apply globally

### Advancing Rounds

When all players finish their turns:
- Press **BLUE button** to advance to next round
- Assets automatically revalue with random returns
- Game ends after 10 rounds or when only 1 player remains

## 🎮 Button Controls

| Button | Function |
|--------|----------|
| 🟢 GREEN | Confirm purchases, advance prompts |
| 🔴 RED | Cancel actions, reset turn |
| 🔵 BLUE | Advance to next round |

## 📊 Asset Types

| Asset | Price | Risk | Return Range |
|-------|-------|------|--------------|
| Stocks | $100 | Medium | -10% to +15% |
| Crypto | $50 | High | -40% to +60% |
| Bonds | $200 | Low | +2% to +5% |
| Commodities | $75 | Medium | -5% to +10% |
| Real Estate | $500 | Stable | Locked 2 rounds |

## 📝 Game Files

| File | Purpose |
|------|---------|
| `main.py` | Main game loop |
| `config.py` | Game settings & constants |
| `game_state.py` | Player data & game logic |
| `card_processor.py` | Card effects & rules |
| `card_registry.py` | RFID ID mappings |
| `rfid_handler.py` | RFID scanning |
| `button_handler.py` | Button input |
| `ui_display.py` | Pygame UI rendering |
| `register_cards.py` | Card registration tool |

## 🔧 Troubleshooting

### RFID Not Scanning
- Check I2C connection: `i2cdetect -y 1`
- Verify RFID module address (default: 0x2C)
- Ensure cards are NTAG213 or Classic compatible
- Hold card steady for 1 second

### Buttons Not Working
- Check I2C addresses match `button_handler.py`
- Verify ASW switch positions
- Test with `i2cdetect -y 1`

### Display Issues
- For fullscreen issues, run in windowed mode: edit `ui_display.py`, set `fullscreen=False`
- Check HDMI connection
- Verify 1080p resolution support

### Unknown Card Errors
- Re-run `register_cards.py`
- Verify `card_registry.py` has correct RFID IDs
- Check for typos in card mappings

## 📄 Logs

Game activity is logged to:
- **Console**: Real-time events
- **File**: `market_movers_log.txt`
- **Save File**: `game_save.json` (auto-saves every action)

## 🎓 For Teachers/Facilitators

### Educational Goals
- Financial literacy
- Risk management
- Portfolio diversification
- Market dynamics

### Game Variants
Edit `config.py` to customize:
- Starting cash
- Number of rounds
- Asset prices
- Return ranges

### Classroom Setup
- 2-4 players per unit
- ~20-30 minutes per game
- Discuss strategies after each round

## 🔄 Updates & Customization

### Adding New Cards
1. Edit `card_registry.py`
2. Add new entry to `CARD_MAPPINGS`
3. Implement handler in `card_processor.py`

### Changing Rules
Edit `config.py` for global settings, or `card_processor.py` for specific card behaviors.

## 📞 Support

For issues:
1. Check `market_movers_log.txt`
2. Run in simulation mode to test logic
3. Verify hardware connections with `i2cdetect -y 1`

## 📜 License

Educational use permitted. See project documentation for details.

---

**Happy Trading! 📈💰**
