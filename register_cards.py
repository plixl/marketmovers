"""
Market Movers - Card Registration Tool
Interactive tool to map RFID cards to game cards
"""

import sys
import time
from rfid_handler import create_rfid_handler
from button_handler import create_button_handler

# Card registration sequence
REGISTRATION_SEQUENCE = [
    # Player cards
    ("Player 1 Wallet", "PLACEHOLDER_P1", "player"),
    ("Player 2 Wallet", "PLACEHOLDER_P2", "player"),
    ("Player 3 Wallet", "PLACEHOLDER_P3", "player"),
    ("Player 4 Wallet", "PLACEHOLDER_P4", "player"),
    
    # Space cards
    ("Space: Payday", "PLACEHOLDER_S01", "space"),
    ("Space: Stock Exchange", "PLACEHOLDER_S02", "space"),
    ("Space: Crypto Hub", "PLACEHOLDER_S04", "space"),
    ("Space: Bond Market", "PLACEHOLDER_S06", "space"),
    ("Space: Real Estate", "PLACEHOLDER_S07", "space"),
    ("Space: Dividend", "PLACEHOLDER_S09", "space"),
    ("Space: Commodity Trade", "PLACEHOLDER_S10", "space"),
    ("Space: Startup Incubator", "PLACEHOLDER_S13", "space"),
    ("Space: Tax Audit", "PLACEHOLDER_S14", "space"),
    ("Space: Market Reset", "PLACEHOLDER_S15", "space"),
    
    # Action cards (10 unique × 2 copies each = 20)
    ("Action: Hostile Takeover #1", "PLACEHOLDER_A01", "action"),
    ("Action: Crypto Hack #1", "PLACEHOLDER_A02", "action"),
    ("Action: Insider Tip #1", "PLACEHOLDER_A03", "action"),
    ("Action: Market Manipulation #1", "PLACEHOLDER_A04", "action"),
    ("Action: Asset Swap #1", "PLACEHOLDER_A05", "action"),
    ("Action: Tax Haven #1", "PLACEHOLDER_A06", "action"),
    ("Action: Bank Loan #1", "PLACEHOLDER_A07", "action"),
    ("Action: Charity Donation #1", "PLACEHOLDER_A08", "action"),
    ("Action: Bonus Dividend #1", "PLACEHOLDER_A09", "action"),
    ("Action: Sabotage #1", "PLACEHOLDER_A10", "action"),
    
    # Event cards (9 unique × 2 copies each = 18)
    ("Event: Market Boom #1", "PLACEHOLDER_E01", "event"),
    ("Event: Recession #1", "PLACEHOLDER_E02", "event"),
    ("Event: Crypto Crash #1", "PLACEHOLDER_E03", "event"),
    ("Event: Gold Rush #1", "PLACEHOLDER_E04", "event"),
    ("Event: Interest Rate Hike #1", "PLACEHOLDER_E05", "event"),
    ("Event: Tech Bubble #1", "PLACEHOLDER_E06", "event"),
    ("Event: Global Crisis #1", "PLACEHOLDER_E07", "event"),
    ("Event: Bull Market #1", "PLACEHOLDER_E08", "event"),
    ("Event: Economic Stability #1", "PLACEHOLDER_E09", "event"),
]

def register_cards():
    """Interactive card registration"""
    print("=" * 60)
    print("MARKET MOVERS - CARD REGISTRATION TOOL")
    print("=" * 60)
    print()
    print("This tool will help you map your RFID cards to game cards.")
    print("For each card, scan it when prompted.")
    print("Press CTRL+C to exit at any time.")
    print()
    
    # Initialize hardware
    simulate = "--simulate" in sys.argv or "-s" in sys.argv
    rfid = create_rfid_handler(simulate=simulate)
    
    if simulate:
        print("⚠️  SIMULATION MODE - No actual RFID scanning")
        print()
    
    mappings = {}
    total_cards = len(REGISTRATION_SEQUENCE)
    
    print(f"Total cards to register: {total_cards}")
    print("=" * 60)
    print()
    
    for i, (card_name, placeholder, card_type) in enumerate(REGISTRATION_SEQUENCE, 1):
        print(f"[{i}/{total_cards}] {card_name}")
        print(f"  Type: {card_type}")
        print(f"  Scan the card now...")
        
        # Wait for scan (no timeout, no duplicate check)
        rfid_id = None
        
        while rfid_id is None:
            rfid_id = rfid.check_for_scan()
            time.sleep(0.1)
        
        # Save the mapping
        mappings[placeholder] = rfid_id
        print(f"  ✓ Registered: {rfid_id}")
        
        print()
        time.sleep(0.5)  # Brief pause between cards
    
    # Generate output
    print("=" * 60)
    print("REGISTRATION COMPLETE")
    print("=" * 60)
    print()
    print(f"Successfully registered: {len(mappings)}/{total_cards} cards")
    print()
    
    # Generate Python code
    print("Copy this code into card_registry.py:")
    print()
    print("CARD_MAPPINGS = {")
    
    for placeholder, rfid_id in mappings.items():
        # Find original card info
        original_line = None
        for name, ph, ctype in REGISTRATION_SEQUENCE:
            if ph == placeholder:
                print(f'    "{rfid_id}": CARD_MAPPINGS["{placeholder}"],  # {name}')
                break
    
    print("}")
    print()
    
    # Save to file
    output_file = "card_mappings_output.txt"
    with open(output_file, "w") as f:
        f.write("# Generated Card Mappings\n")
        f.write("# Copy these into card_registry.py\n\n")
        for placeholder, rfid_id in mappings.items():
            for name, ph, ctype in REGISTRATION_SEQUENCE:
                if ph == placeholder:
                    f.write(f'"{rfid_id}": CARD_MAPPINGS["{placeholder}"],  # {name}\n')
                    break
    
    print(f"✓ Mappings also saved to: {output_file}")
    print()


def quick_scan_test():
    """Quick tool to test scanning cards and see their IDs"""
    print("=" * 60)
    print("QUICK SCAN TEST")
    print("=" * 60)
    print()
    print("Scan cards to see their RFID IDs")
    print("Press CTRL+C to exit")
    print()
    
    simulate = "--simulate" in sys.argv or "-s" in sys.argv
    rfid = create_rfid_handler(simulate=simulate)
    
    scanned_ids = set()
    
    try:
        while True:
            rfid_id = rfid.check_for_scan()
            if rfid_id and rfid_id not in scanned_ids:
                scanned_ids.add(rfid_id)
                print(f"✓ Scanned: {rfid_id}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\nScanned IDs:")
        for rfid_id in sorted(scanned_ids):
            print(f"  - {rfid_id}")


def main():
    """Entry point"""
    print()
    if "--test" in sys.argv or "-t" in sys.argv:
        quick_scan_test()
    else:
        register_cards()


if __name__ == "__main__":
    main()
