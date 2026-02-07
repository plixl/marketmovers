"""
Market Movers - Button Handler
Manages 3 PiicoDev button inputs
"""

try:
    from PiicoDev_Switch import PiicoDev_Switch
    BUTTON_AVAILABLE = True
except ImportError:
    print("WARNING: PiicoDev_Button not found. Using keyboard simulation.")
    BUTTON_AVAILABLE = False

import time

class ButtonHandler:
    """Handles 3-button input"""
    
    # Button IDs
    BTN_CONFIRM = 0  # Green button
    BTN_CANCEL = 1   # Red button
    BTN_ROUND = 2    # Blue button
    
    def __init__(self):
        self.buttons = {}
        self.last_press_time = {}
        self.debounce_time = 0.3  # Prevent accidental double-presses
        
        if BUTTON_AVAILABLE:
            try:
                # Initialize 3 buttons with different I2C addresses
                # Adjust addresses based on your hardware setup
                self.buttons[self.BTN_CONFIRM] = PiicoDev_Switch( id=[1,0,0,0])
                self.buttons[self.BTN_CANCEL] = PiicoDev_Switch( id=[2,0,0,0])
                self.buttons[self.BTN_ROUND] = PiicoDev_Switch( id=[3,0,0,0])
                
                # Initialize debounce times
                for btn_id in self.buttons:
                    self.last_press_time[btn_id] = 0
                
                print("✓ Buttons initialized (GREEN=Confirm, RED=Cancel, BLUE=Round)")
            except Exception as e:
                print(f"✗ Button initialization failed: {e}")
                self.buttons = {}
        else:
            print("✗ Button module not available")
    
    def is_pressed(self, button_id):
        """
        Check if a button is pressed (with debouncing)
        Args:
            button_id: BTN_CONFIRM, BTN_CANCEL, or BTN_ROUND
        Returns: True if pressed, False otherwise
        """
        if button_id not in self.buttons:
            return False
        
        try:
            current_time = time.time()
            
            # Check if enough time has passed since last press
            if (current_time - self.last_press_time[button_id]) < self.debounce_time:
                return False
            
            # Check button state
            if self.buttons[button_id].isPressed():
                self.last_press_time[button_id] = current_time
                return True
        except Exception as e:
            print(f"Button read error: {e}")
        
        return False
    
    def check_any_button(self):
        """
        Check all buttons and return which one was pressed
        Returns: button_id or None
        """
        for btn_id in [self.BTN_CONFIRM, self.BTN_CANCEL, self.BTN_ROUND]:
            if self.is_pressed(btn_id):
                return btn_id
        return None
    
    def wait_for_button(self, timeout=30):
        """
        Wait for any button press with timeout
        Returns: button_id or None if timeout
        """
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            btn = self.check_any_button()
            if btn is not None:
                return btn
            time.sleep(0.1)
        
        return None


class SimulatedButtonHandler:
    """
    Simulated button handler for testing without hardware
    Maps keyboard keys to buttons
    """
    
    BTN_CONFIRM = 0
    BTN_CANCEL = 1
    BTN_ROUND = 2
    
    def __init__(self):
        self.pending_button = None
        print("✓ Simulated buttons initialized")
        print("  Keyboard: G=Green/Confirm, R=Red/Cancel, B=Blue/Round")
    
    def is_pressed(self, button_id):
        """Check if button was pressed (simulated)"""
        if self.pending_button == button_id:
            self.pending_button = None
            return True
        return False
    
    def check_any_button(self):
        """Check for any button press"""
        if self.pending_button is not None:
            btn = self.pending_button
            self.pending_button = None
            return btn
        return None
    
    def simulate_press(self, button_id):
        """Manually trigger a button press (for testing)"""
        self.pending_button = button_id
    
    def wait_for_button(self, timeout=30):
        """Wait for button (not implemented in simulation)"""
        return None


# Factory function
def create_button_handler(simulate=False):
    """
    Create appropriate button handler
    Args:
        simulate: If True, use simulated handler even if hardware available
    """
    if simulate or not BUTTON_AVAILABLE:
        return SimulatedButtonHandler()
    else:
        return ButtonHandler()
